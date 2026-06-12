from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime, timedelta
import logging

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
    'email_on_failure': False,
}

# ─────────────────────────────────────────────────────────────────────────
# DAG : Rapport hebdomadaire — dbt all sources + analyse statistique Python
# S'exécute le dimanche à 10h après que les 3 pipelines aient tourné
# ─────────────────────────────────────────────────────────────────────────
with DAG(
    dag_id='weekly_report_pipeline',
    default_args=default_args,
    description='Rapport hebdo : dbt all_products + statistiques Python',
    schedule_interval='0 10 * * 0',   # Dimanche à 10h00
    start_date=datetime(2026, 3, 26),
    catchup=False,
    tags=['rapport', 'dbt', 'stats', 'weekly'],
) as dag:

    # ── 1. Attendre que le pipeline Jumia du jour soit terminé ────────────
    wait_jumia = ExternalTaskSensor(
        task_id='attendre_jumia',
        external_dag_id='jumia_pipeline',
        external_task_id='log_succes',
        timeout=3600,
        mode='reschedule',
        poke_interval=60,
        allowed_states=['success'],
    )

    # ── 2. Attendre que le pipeline IKEA du jour soit terminé ─────────────
    wait_ikea = ExternalTaskSensor(
        task_id='attendre_ikea',
        external_dag_id='ikea_pipeline',
        external_task_id='log_succes',
        timeout=3600,
        mode='reschedule',
        poke_interval=60,
        allowed_states=['success'],
    )

    # ── 3. Attendre que le pipeline Kitea du jour soit terminé ────────────
    wait_kitea = ExternalTaskSensor(
        task_id='attendre_kitea',
        external_dag_id='kitea_pipeline',
        external_task_id='log_succes',
        timeout=3600,
        mode='reschedule',
        poke_interval=60,
        allowed_states=['success'],
    )

    # ── 4. dbt run — modèle all_products (union des 3 sources) ───────────
    dbt_run_all = BashOperator(
        task_id='dbt_run_all_products',
        bash_command=(
            'cd /opt/airflow/jumia_dbt && '
            'dbt run --profiles-dir /opt/airflow/jumia_dbt --select all_products'
        ),
        execution_timeout=timedelta(minutes=20),
    )

    # ── 5. dbt run — agrégations hebdomadaires multi-sources ─────────────
    dbt_run_agg = BashOperator(
        task_id='dbt_run_aggregations',
        bash_command=(
            'cd /opt/airflow/jumia_dbt && '
            'dbt run --profiles-dir /opt/airflow/jumia_dbt --select agg_prix_categorie weekly_stats'
        ),
        execution_timeout=timedelta(minutes=15),
    )

    # ── 6. dbt test — valider tous les modèles ────────────────────────────
    dbt_test_all = BashOperator(
        task_id='dbt_test_all',
        bash_command=(
            'cd /opt/airflow/jumia_dbt && '
            'dbt test --profiles-dir /opt/airflow/jumia_dbt'
        ),
        execution_timeout=timedelta(minutes=15),
    )

    # ── 7. Analyse statistique Python ────────────────────────────────────
    def run_statistical_analysis(**context):
        """
        Analyse descriptive + inférentielle sur les données de la semaine.
        Lit depuis BigQuery, calcule les stats, log les résultats.
        """
        try:
            from google.cloud import bigquery
            import pandas as pd
            from scipy import stats

            client = bigquery.Client(project='diesel-patrol-491520-j8')

            # Lire les données de la semaine depuis BigQuery
            query = """
                SELECT
                    source,
                    marque,
                    prix,
                    ancien_prix,
                    remise,
                    date_scraping
                FROM `diesel-patrol-491520-j8.jumia_price_intelligence.all_products`
                WHERE date_scraping >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
            """
            df = client.query(query).to_dataframe()

            if df.empty:
                logging.warning("⚠️ Aucune donnée disponible pour l'analyse.")
                return

            # ── Statistiques descriptives ──────────────────────────────
            logging.info("=== STATISTIQUES DESCRIPTIVES ===")
            logging.info(f"Nombre total de produits : {len(df)}")
            logging.info(f"Sources : {df['source'].value_counts().to_dict()}")
            logging.info(f"Prix moyen global : {df['prix'].mean():.2f} MAD")
            logging.info(f"Prix médian global : {df['prix'].median():.2f} MAD")
            logging.info(f"Écart-type des prix : {df['prix'].std():.2f} MAD")
            logging.info(f"Prix min : {df['prix'].min():.2f} MAD")
            logging.info(f"Prix max : {df['prix'].max():.2f} MAD")
            logging.info(f"Remise moyenne : {df['remise'].mean():.2f}%")

            # Par source
            for source in df['source'].unique():
                sub = df[df['source'] == source]
                logging.info(
                    f"  [{source.upper()}] "
                    f"n={len(sub)} | "
                    f"prix_moy={sub['prix'].mean():.2f} | "
                    f"remise_moy={sub['remise'].mean():.2f}%"
                )

            # ── Test t : Jumia vs IKEA ────────────────────────────────
            jumia_prix = df[df['source'] == 'jumia']['prix'].dropna()
            ikea_prix  = df[df['source'] == 'ikea']['prix'].dropna()

            if len(jumia_prix) > 1 and len(ikea_prix) > 1:
                t_stat, p_value = stats.ttest_ind(jumia_prix, ikea_prix)
                logging.info("=== TEST T : Jumia vs IKEA ===")
                logging.info(f"t-statistic : {t_stat:.4f}")
                logging.info(f"p-value     : {p_value:.4f}")
                if p_value < 0.05:
                    logging.info("→ Différence de prix SIGNIFICATIVE entre Jumia et IKEA (p < 0.05)")
                else:
                    logging.info("→ Pas de différence significative entre Jumia et IKEA (p >= 0.05)")

            # ── ANOVA : variation des prix par source ─────────────────
            groupes = [df[df['source'] == s]['prix'].dropna() for s in df['source'].unique()]
            groupes = [g for g in groupes if len(g) > 1]

            if len(groupes) >= 2:
                f_stat, p_anova = stats.f_oneway(*groupes)
                logging.info("=== ANOVA : prix par source ===")
                logging.info(f"F-statistic : {f_stat:.4f}")
                logging.info(f"p-value     : {p_anova:.4f}")
                if p_anova < 0.05:
                    logging.info("→ Variation significative des prix entre les sources")
                else:
                    logging.info("→ Pas de variation significative entre les sources")

            logging.info("✅ Analyse statistique terminée avec succès")

        except ImportError as e:
            logging.warning(f"Librairie manquante : {e} — analyse ignorée")
        except Exception as e:
            logging.error(f"Erreur lors de l'analyse statistique : {e}")
            raise

    stats_analysis = PythonOperator(
        task_id='analyse_statistique',
        python_callable=run_statistical_analysis,
        provide_context=True,
        execution_timeout=timedelta(minutes=20),
    )

    # ── 8. Log de fin de rapport ─────────────────────────────────────────
    def log_rapport_done(**context):
        week = context['execution_date'].strftime('%Y-W%U')
        logging.info(f"📊 Rapport hebdomadaire {week} généré avec succès")
        logging.info("Prochaine exécution : dimanche prochain à 10h00")

    log_done = PythonOperator(
        task_id='log_rapport_termine',
        python_callable=log_rapport_done,
        provide_context=True,
    )

    # ── Ordre d'exécution ────────────────────────────────────────────────
    [wait_jumia, wait_ikea, wait_kitea] >> dbt_run_all >> dbt_run_agg >> dbt_test_all >> stats_analysis >> log_done