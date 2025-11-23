from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.utils.task_group import TaskGroup
from airflow.utils.log.logging_mixin import LoggingMixin
import sys
import os
import pandas as pd

# # ------------------------------------------------
# # access etl and ml folders
# # ------------------------------------------------
# sys.path.append("/opt/project/etl")
# sys.path.append("/opt/project/ml")

from etl.etl_to_bigquery import extract_data, transform_data, load_to_bigquery
# from ml.data_loader import load_data
from ml.train import train_model
from ml.promote_model import promote_model  # new!

log = LoggingMixin().log
# ------------------------------------------------
# Default args
# ------------------------------------------------
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "email": ["ainoid27@gmail.com"],  # opsional
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# ------------------------------------------------
# DAG definition with decorator
# ------------------------------------------------
@dag(
    dag_id="etl_ml_pipeline_v1",
    description="ETL + ML pipeline: PostgreSQL → BigQuery → ML",
    default_args=default_args,
    schedule_interval="0 6 1 */3 *",  # the DAG will run on the 1st day every 3 months at 6:00 AM
    start_date=datetime(2025, 10, 15),
    catchup=False,
    tags=["etl", "bigquery", "postgres"],
)
def etl_ml_pipeline():
    """Pipeline ETL → ML"""
    # -------------------------
    # ETL TaskGroup
    # -------------------------
    with TaskGroup("etl_group", tooltip="Extract → Transform → Load") as etl_group:

        @task()
        def extract():
            """Extract data from PostgreSQL into a DataFrame."""
            log.info("🚀 Extracting data from PostgreSQL...")
            df = extract_data()
            log.info(f"✅ Extraction completed. Rows extracted: {len(df)}")
            return df.to_json()

        @task()
        def transform(df_json: str):
            """Clean, transform, and enrich data."""
            log.info("🧩 Transforming data...")
            df = pd.read_json(df_json)
            df_transformed = transform_data(df)
            log.info(f"✅ Transformation completed. Rows remaining: {len(df_transformed)}")
            return df_transformed.to_json()

        @task()
        def load(df_json: str):
            """Load transformed DataFrame into BigQuery."""
            log.info("📤 Loading data to BigQuery...")
            df = pd.read_json(df_json)
            load_to_bigquery(df)
            log.info("✅ Load completed successfully.")

        # Task execution ordering
        raw_data = extract()
        transformed_data = transform(raw_data)
        load(transformed_data)

    # ------------------------------------------------
    # Machine Learning task
    # ------------------------------------------------
    @task()
    def ml_experiment_task():
        """
        Train the model, evaluate metrics, and track everything in MLflow.
        """
        log.info("🎯 Starting model training & experiment logging...")
        train_model()
        log.info("✅ Model training and logging completed.")

    # ------------------------------------------------
    # Model Promotion task
    # ------------------------------------------------
    @task()
    def promote_model_task():
        try:
            log.info("🚦 Evaluating model for promotion...")
            promote_model()
            log.info("✅ Model promotion step completed.")
        except Exception as e:
            log.error(f"❌ Promotion failed: {e}")
            raise

    # ------------------------------------------------
    # DAG dependency flow
    # ------------------------------------------------
    etl_group >> ml_experiment_task() >> promote_model_task()


# Instantiate DAG
etl_ml_pipeline()
