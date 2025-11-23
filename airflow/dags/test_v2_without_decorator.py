from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

# ------------------------------------------------
# Path setup agar bisa import file dari folder etl/
# ------------------------------------------------
sys.path.append("/opt/project/etl")

# Import ETL functions
from etl_to_bigquery import extract_data, transform_data, load_to_bigquery

# ------------------------------------------------
# Default args for DAG
# ------------------------------------------------
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "email": ["your_email@example.com"],  # bisa dikosongkan kalau belum perlu
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
}

# ------------------------------------------------
# DAG Definition
# ------------------------------------------------
with DAG(
    dag_id="etl_to_bigquery_dag_v2",
    description="ETL pipeline from PostgreSQL to BigQuery",
    default_args=default_args,
    schedule_interval=timedelta(days=1),  # jalan tiap 1 hari
    start_date=datetime(2025, 10, 13),
    catchup=False,
    tags=["etl", "bigquery", "postgres"],
) as dag:

    # -------------------------
    # Task 1: Extract Data
    # -------------------------
    def extract_task(**kwargs):
        print("🚀 Extracting data from PostgreSQL...")
        df = extract_data()
        kwargs["ti"].xcom_push(key="extracted_df", value=df.to_json())
        print("✅ Extraction complete.")

    extract = PythonOperator(
        task_id="extract_data",
        python_callable=extract_task,
        provide_context=True,
    )

    # -------------------------
    # Task 2: Transform Data
    # -------------------------
    def transform_task(**kwargs):
        print("🧩 Transforming data...")
        import pandas as pd

        # Ambil data dari XCom
        df_json = kwargs["ti"].xcom_pull(task_ids="extract_data", key="extracted_df")
        df = pd.read_json(df_json)
        df_transformed = transform_data(df)

        kwargs["ti"].xcom_push(key="transformed_df", value=df_transformed.to_json())
        print("✅ Transformation complete.")

    transform = PythonOperator(
        task_id="transform_data",
        python_callable=transform_task,
        provide_context=True,
    )

    # -------------------------
    # Task 3: Load to BigQuery
    # -------------------------
    def load_task(**kwargs):
        print("📤 Loading data to BigQuery...")
        import pandas as pd

        df_json = kwargs["ti"].xcom_pull(task_ids="transform_data", key="transformed_df")
        df = pd.read_json(df_json)
        load_to_bigquery(df)
        print("✅ Load completed successfully.")

    load = PythonOperator(
        task_id="load_to_bigquery",
        python_callable=load_task,
        provide_context=True,
    )

    # -------------------------
    # Task Order
    # -------------------------
    extract >> transform >> load
