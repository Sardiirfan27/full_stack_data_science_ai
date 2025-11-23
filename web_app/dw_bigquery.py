import pandas as pd
import argparse
import os
from dotenv import load_dotenv
from google.cloud import bigquery
from google.cloud import bigquery_storage
from google.oauth2 import service_account


# Load environment variables
load_dotenv()
# --- BigQuery Configuration ---
GCP_CREDENTIALS = os.getenv("GCP_CREDENTIALS")  # Path to your service account key file
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")
BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE")


def load_data():
    """Loads ALL columns from BigQuery table into a DataFrame."""
     
    if not all([GCP_PROJECT_ID, BIGQUERY_DATASET, BIGQUERY_TABLE]):
        raise EnvironmentError(
            " ❌Missing BigQuery config. Ensure .env has GCP_PROJECT_ID, BIGQUERY_DATASET, BIGQUERY_TABLE, GCP_CREDENTIALS"
        )

    # BigQuery Connection
    table_id = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"
    credentials = service_account.Credentials.from_service_account_file(GCP_CREDENTIALS)
    bq_client = bigquery.Client(credentials=credentials, project=GCP_PROJECT_ID)
    bqstorage_client = bigquery_storage.BigQueryReadClient(credentials=credentials)

    # Query ALL columns
    query = f"""
    SELECT
        t.* EXCEPT(TotalCharges),
        COALESCE(TotalCharges, 0) AS TotalCharges
    FROM `{table_id}` t
    """
    try:
        df = bq_client.query(query).to_dataframe(bqstorage_client=bqstorage_client)
        print(f"✅ Successfully loaded {len(df)} rows from BigQuery.")
    except Exception as e:
        raise RuntimeError(f"❌ Error executing BigQuery query: {e}")

    # Return raw dataframe without dropping/transformations
    return df
