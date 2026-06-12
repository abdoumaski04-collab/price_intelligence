"""
bigtable_pipeline_dag.py
=========================
DAG Airflow qui orchestre :
1. kafka_to_bigtable.py  → consomme Kafka → écrit dans Bigtable Emulator
2. bigtable_to_bigquery.py → lit Bigtable → écrit dans BigQuery
3. dbt run → transforme les données dans BigQuery

Schedule : toutes les 6 heures (après les scrapers)
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging

default_args = {
    'owner': 'airflow',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

with DAG(
    dag_id='bigtable_pipeline',
    default_args=default_args,
    description='Pipeline : Kafka → Bigtable Emulator → BigQuery → dbt',
    schedule_interval='0 */6 * * *',   # toutes les 6 heures
    start_date=datetime(2026, 3, 26),
    catchup=False,
    tags=['bigtable', 'bigquery', 'dbt', 'kafka'],
) as dag:

    # ── 1. Vérifier que l'émulateur Bigtable est accessible ──────────────────
    def check_bigtable(**context):
        import os
        import socket
        host, port = os.getenv(
            'BIGTABLE_EMULATOR_HOST', 'bigtable-emulator:8086'
        ).split(':')
        try:
            sock = socket.create_connection((host, int(port)), timeout=10)
            sock.close()
            logging.info(f"✅ Bigtable Emulator accessible sur {host}:{port}")
        except Exception as e:
            raise Exception(f"❌ Bigtable Emulator inaccessible : {e}")

    check_bigtable_task = PythonOperator(
        task_id='verifier_bigtable_emulator',
        python_callable=check_bigtable,
        provide_context=True,
    )

    # ── 2. Kafka → Bigtable (tourne 5 minutes puis s'arrête) ─────────────────
    kafka_to_bigtable = BashOperator(
        task_id='kafka_to_bigtable',
        bash_command=(
            'export BIGTABLE_EMULATOR_HOST=bigtable-emulator:8086 && '
            'export KAFKA_BOOTSTRAP_SERVERS=kafka:29092 && '
            'export GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/gcp-key.json && '
            # timeout 300 = tourne 5 minutes max puis s'arrête proprement
            'timeout 300 python3 /opt/airflow/dags/kafka_to_bigtable.py || true'
        ),
        execution_timeout=timedelta(minutes=10),
    )

    # ── 3. Bigtable → BigQuery ────────────────────────────────────────────────
    bigtable_to_bigquery = BashOperator(
        task_id='bigtable_to_bigquery',
        bash_command=(
            'export BIGTABLE_EMULATOR_HOST=bigtable-emulator:8086 && '
            'export GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/gcp-key.json && '
            'python3 /opt/airflow/dags/bigtable_to_bigquery.py'
        ),
        execution_timeout=timedelta(minutes=15),
    )

    # ── 4. dbt run — transformer les données dans BigQuery ───────────────────
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command=(
            'cd /opt/airflow/jumia_dbt && '
            'dbt run --profiles-dir /opt/airflow/jumia_dbt'
        ),
        execution_timeout=timedelta(minutes=20),
    )

    # ── 5. dbt test — valider la qualité des données ──────────────────────────
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command=(
            'cd /opt/airflow/jumia_dbt && '
            'dbt test --profiles-dir /opt/airflow/jumia_dbt'
        ),
        execution_timeout=timedelta(minutes=15),
    )

    # ── 6. Log de succès ──────────────────────────────────────────────────────
    def log_success(**context):
        execution_date = context['execution_date']
        logging.info(f"✅ Pipeline Bigtable terminé — {execution_date}")
        logging.info("Données disponibles dans BigQuery : jumia_price_intelligence")

    log_done = PythonOperator(
        task_id='log_succes',
        python_callable=log_success,
        provide_context=True,
    )

    # ── Ordre d'exécution ─────────────────────────────────────────────────────
    check_bigtable_task >> kafka_to_bigtable >> bigtable_to_bigquery >> dbt_run >> dbt_test >> log_done