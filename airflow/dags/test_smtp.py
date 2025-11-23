from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from airflow.utils.email import send_email

default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 10, 21),
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 0,
}

def test_email():
    send_email(
        to=["sardiirfan27@gmail.com","ainoid27@gmail.com"],   # ganti dengan emailmu
        subject="Test Email Airflow SMTP",
        html_content="<h3>✅ Airflow SMTP berhasil!</h3>"
    )
    print("Email berhasil dikirim!")

with DAG(
    dag_id="test_smtp",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["test"]
) as dag:

    t1 = PythonOperator(
        task_id="send_test_email",
        python_callable=test_email
    )
