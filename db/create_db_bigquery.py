from google.cloud import bigquery
from google.oauth2 import service_account


# Setup credentials & client
key_path = "gcp_service_key.json"  # Path to your service account key
credentials = service_account.Credentials.from_service_account_file(key_path)
project_id = "axial-entropy-351511"
client = bigquery.Client(project=project_id, credentials=credentials)

# Dataset and table
dataset_id = "telco_customers_churn"
table_id = "customers_summary"
dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")

# Create dataset if it doesn't exist
try:
    client.get_dataset(dataset_ref)
    print(f"Dataset '{dataset_id}' already exists.")
except Exception:
    client.create_dataset(dataset_ref)
    print(f"Dataset '{dataset_id}' has been created successfully.")

# Load CSV into table
file_path = "../data/WA_Fn-UseC_-Telco-Customer-Churn.csv"
table_ref = f"{project_id}.{dataset_id}.{table_id}"

schema = [
    bigquery.SchemaField("customerID", "STRING"),
    bigquery.SchemaField("gender", "STRING"),
    bigquery.SchemaField("SeniorCitizen", "INTEGER"),
    bigquery.SchemaField("Partner", "STRING"),
    bigquery.SchemaField("Dependents", "STRING"),
    bigquery.SchemaField("tenure", "INTEGER"),
    bigquery.SchemaField("PhoneService", "STRING"),
    bigquery.SchemaField("MultipleLines", "STRING"),
    bigquery.SchemaField("InternetService", "STRING"),
    bigquery.SchemaField("OnlineSecurity", "STRING"),
    bigquery.SchemaField("OnlineBackup", "STRING"),
    bigquery.SchemaField("DeviceProtection", "STRING"),
    bigquery.SchemaField("TechSupport", "STRING"),
    bigquery.SchemaField("StreamingTV", "STRING"),
    bigquery.SchemaField("StreamingMovies", "STRING"),
    bigquery.SchemaField("Contract", "STRING"),
    bigquery.SchemaField("PaperlessBilling", "STRING"),
    bigquery.SchemaField("PaymentMethod", "STRING"),
    bigquery.SchemaField("MonthlyCharges", "FLOAT"),
    bigquery.SchemaField("TotalCharges", "FLOAT"),
    bigquery.SchemaField("Churn", "STRING"),
]

job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    schema=schema,
    #autodetect=True,      # Automatically detect schema
    write_disposition="WRITE_TRUNCATE" # Overwrite existing table
)


with open(file_path, "rb") as f:
    load_job = client.load_table_from_file(f, table_ref, job_config=job_config)

load_job.result()  # Wait for the load job to complete
print(f"Loaded {load_job.output_rows} rows into {table_ref}.")
