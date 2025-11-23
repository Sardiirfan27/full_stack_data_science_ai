import pandas as pd
import argparse
import os
from dotenv import load_dotenv
from google.cloud import bigquery
from google.cloud import bigquery_storage
from google.oauth2 import service_account


load_dotenv()

GCP_CREDENTIALS = os.getenv("GCP_CREDENTIALS")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")
BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE")

def load_bigquery_data():
    """Load raw data from BigQuery table into pandas DataFrame."""
    
    # Environment Check
    if not all([GCP_PROJECT_ID, BIGQUERY_DATASET, BIGQUERY_TABLE, GCP_CREDENTIALS]):
        raise EnvironmentError("Missing BigQuery config in .env")

    # BigQuery Connection Setup
    table_id = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"
    try:
        credentials = service_account.Credentials.from_service_account_file(GCP_CREDENTIALS)
        bq_client = bigquery.Client(credentials=credentials, project=GCP_PROJECT_ID)
        bqstorage_client = bigquery_storage.BigQueryReadClient(credentials=credentials)
        df = bq_client.query(f"SELECT * FROM `{table_id}`").to_dataframe(bqstorage_client=bqstorage_client)
        print(f"✅ Loaded {len(df)} rows from BigQuery table {table_id}")
        return df
    except Exception as e:
        raise RuntimeError(f"Error loading data from BigQuery: {e}")
