from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.time_delta import TimeDeltaSensor
from datetime import datetime, timedelta
import logging

# ─────────────────────────────────────────
# Default args partagés
# ─────────────────────────────────────────
default_args = {
    'owner': 'airflow',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

# ─────────────────────────────────────────
# DAG : Jumia — Scraping quotidien + dbt
# ─────────────────────────────────────────
with DAG(
    dag_id='jumia_pipeline',
    default_args=default_args,
    description='Pipeline complet Jumia : scraping → Kafka → dbt → rapport',
    schedule_interval='0 6 * * *',   # Tous les jours à 06h00
    start_date=datetime(2026, 3, 26),
    catchup=False,
    tags=['jumia', 'scraping', 'dbt'],
) as dag:

    # ── 1. Vérifier que Kafka est disponible ──────────────────────────────
    check_kafka = BashOperator(
        bash_command='nc -z kafka 29092 && echo "Kafka OK"',
        task_id='check_kafka',
        retries=3,
        retry_delay=timedelta(seconds=30),
    )

    # ── 2. Scraping Jumia → publie dans Kafka topic prix-jumia ────────────
    scrape_jumia = BashOperator(
        task_id='scraper_jumia',
        bash_command=(
            'cd /opt/airflow/dags && '
            'scrapy crawl jumia '
            '-s KAFKA_BOOTSTRAP_SERVERS=kafka:29092 '
            '-s KAFKA_TOPIC=prix-jumia '
            '-L INFO'
        ),
        execution_timeout=timedelta(minutes=30),
    )

    # ── 3. Attendre 2 min que NiFi traite les messages Kafka → BigQuery ───
    wait_nifi = TimeDeltaSensor(
        task_id='attendre_nifi',
        delta=timedelta(minutes=2),
    )

    # ── 4. dbt run — modèles Jumia ────────────────────────────────────────
    dbt_run_jumia = BashOperator(
        task_id='dbt_run_jumia',
        bash_command=(
            'cd /opt/airflow/jumia_dbt && '
            'dbt run --profiles-dir /opt/airflow/jumia_dbt --select jumia '
            '--vars \'{"source": "jumia"}\''
        ),
        execution_timeout=timedelta(minutes=15),
    )

    # ── 5. dbt test — valider la qualité des données ──────────────────────
    dbt_test_jumia = BashOperator(
        task_id='dbt_test_jumia',
        bash_command=(
            'cd /opt/airflow/jumia_dbt && '
            'dbt test --profiles-dir /opt/airflow/jumia_dbt --select jumia'
        ),
        execution_timeout=timedelta(minutes=10),
    )

    # ── 6. Log de succès ─────────────────────────────────────────────────
    def log_success(**context):
        execution_date = context['execution_date']
        logging.info(f"✅ Pipeline Jumia terminé avec succès — {execution_date}")
        logging.info("Données disponibles dans BigQuery : jumia_price_intelligence")

    notify_success = PythonOperator(
        task_id='log_succes',
        python_callable=log_success,
        provide_context=True,
    )

    # ── Ordre d'exécution ────────────────────────────────────────────────
    check_kafka >> scrape_jumia >> wait_nifi >> dbt_run_jumia >> dbt_test_jumia >> notify_success