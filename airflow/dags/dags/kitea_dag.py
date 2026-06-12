from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.time_delta import TimeDeltaSensor
from datetime import datetime, timedelta
import logging

default_args = {
    'owner': 'airflow',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

# ─────────────────────────────────────────
# DAG : Kitea — Scraping quotidien + dbt
# ─────────────────────────────────────────
with DAG(
    dag_id='kitea_pipeline',
    default_args=default_args,
    description='Pipeline complet Kitea : scraping → Kafka → dbt → rapport',
    schedule_interval='0 8 * * *',   # Tous les jours à 08h00 (1h après IKEA)
    start_date=datetime(2026, 3, 26),
    catchup=False,
    tags=['kitea', 'scraping', 'dbt'],
) as dag:

    # ── 1. Vérifier que Kafka est disponible ──────────────────────────────
    check_kafka = BashOperator(
        task_id='check_kafka',
        bash_command='nc -z kafka 29092 && echo "Kafka OK"',
        retries=3,
        retry_delay=timedelta(seconds=30),
    )

    # ── 2. Scraping Kitea → publie dans Kafka topic prix-kitea ───────────
    scrape_kitea = BashOperator(
        task_id='scraper_kitea',
        bash_command=(
            'cd /opt/airflow/dags && '
            'scrapy crawl kitea '
            '-s KAFKA_BOOTSTRAP_SERVERS=kafka:29092 '
            '-s KAFKA_TOPIC=prix-kitea '
            '-L INFO'
        ),
        execution_timeout=timedelta(minutes=30),
    )

    # ── 3. Attendre que NiFi traite les messages Kafka → BigQuery ─────────
    wait_nifi = TimeDeltaSensor(
        task_id='attendre_nifi',
        delta=timedelta(minutes=2),
    )

    # ── 4. dbt run — modèles Kitea ────────────────────────────────────────
    dbt_run_kitea = BashOperator(
        task_id='dbt_run_kitea',
        bash_command=(
            'cd /opt/airflow/jumia_dbt && '
            'dbt run --profiles-dir /opt/airflow/jumia_dbt --select stg_kitea '
            '--vars \'{"source": "kitea"}\''
        ),
        execution_timeout=timedelta(minutes=15),
    )

    # ── 5. dbt test — valider la qualité des données ──────────────────────
    dbt_test_kitea = BashOperator(
        task_id='dbt_test_kitea',
        bash_command=(
            'cd /opt/airflow/jumia_dbt && '
            'dbt test --profiles-dir /opt/airflow/jumia_dbt --select stg_kitea'
        ),
        execution_timeout=timedelta(minutes=10),
    )

    # ── 6. Log de succès ──────────────────────────────────────────────────
    def log_success(**context):
        execution_date = context['execution_date']
        logging.info(f"✅ Pipeline Kitea terminé avec succès — {execution_date}")
        logging.info("Données disponibles dans BigQuery : jumia_price_intelligence")

    notify_success = PythonOperator(
        task_id='log_succes',
        python_callable=log_success,
        provide_context=True,
    )

    # ── Ordre d'exécution ────────────────────────────────────────────────
    check_kafka >> scrape_kitea >> wait_nifi >> dbt_run_kitea >> dbt_test_kitea >> notify_success