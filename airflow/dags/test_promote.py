from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.utils.log.logging_mixin import LoggingMixin
from ml.promote_model import promote_model  # pastikan path benar
import os

log = LoggingMixin().log

# -------------------------
# Default args
# -------------------------
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}

# -------------------------
# DAG definition
# -------------------------
@dag(
    dag_id="test_promotion_task",
    description="Test DAG for MLflow model promotion",
    default_args=default_args,
    schedule_interval=None,  # manual trigger only
    start_date=datetime(2025, 10, 1),
    catchup=False,
    tags=["ml", "promotion"],
)
def test_promotion_dag():

    @task()
    def promotion_task():
        """Test MLflow model promotion"""
        try:
            log.info("🔔 Promotion task started")
            log.info(f"MLFLOW_TRACKING_URI = {os.getenv('MLFLOW_TRACKING_URI')}")
            promote_model()
            log.info("✅ Promotion task finished successfully")
        except Exception as e:
            log.error(f"❌ Promotion failed : {e}")
            raise

    promotion_task()

# Instantiate DAG
dag = test_promotion_dag() 
