# etl/etl_bigquery.py
import pandas as pd
from sqlalchemy import create_engine, text
from google.cloud import bigquery
from google.oauth2 import service_account
import os
import pandas as pd
from dotenv import load_dotenv
import argparse

load_dotenv()

# Load environment variables
POSTGRES_HOST =  os.getenv("AIRFLOW_POSTGRES_HOST") #"localhost"
POSTGRES_PORT = os.getenv("AIRFLOW_POSTGRES_PORT") # 5434
POSTGRES_DB = os.getenv("AIRFLOW_POSTGRES_DB")
POSTGRES_USER = os.getenv("AIRFLOW_POSTGRES_USER", "ml_user")
POSTGRES_PASSWORD = os.getenv("AIRFLOW_POSTGRES_PASSWORD", "ml_pass")


GCP_CREDENTIALS = os.getenv("GCP_CREDENTIALS")  # Path to your service account key
PROJECT_ID = os.getenv("PROJECT_ID")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")
BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE")
STAGING_TABLE = BIGQUERY_TABLE + "_staging"

    
# ========================
#  ETL FUNCTION
# ========================

def extract_data():
    """Data extraction and data transformation (aggregation, joining multiple tables) with SQL"""
    
    # check postgrecsql connection
    try:
        pg_engine = create_engine(
            f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))  # simple test query
        print("✅ Connected to PostgreSQL")
    except Exception as e:
        raise RuntimeError(f"❌ Error connecting to PostgreSQL: {e}")
    
    # query for data extraction
    query = """
    SELECT
            c.customer_id AS "customerID",
            c.gender AS "gender",
            c.senior_citizen AS "SeniorCitizen",
            c.partner AS "Partner",
            c.dependents AS "Dependents",
             --  Calculate tenure in months
            CASE
                WHEN con.contract_type = 'Month-to-month' THEN 
                    COUNT(CASE WHEN t.paid = TRUE THEN 1 END)
                WHEN con.contract_type = 'One year' THEN 
                    12
                WHEN con.contract_type = 'Two year' THEN 
                    24
                ELSE 0
            END::INT AS "tenure",

            con.phone_service AS "PhoneService",
            con.multiple_lines AS "MultipleLines",
            con.internet_service AS "InternetService",
            con.online_security AS "OnlineSecurity",
            con.online_backup AS "OnlineBackup",
            con.device_protection AS "DeviceProtection",
            con.tech_support AS "TechSupport",
            con.streaming_tv AS "StreamingTV",
            con.streaming_movies AS "StreamingMovies",
            con.contract_type AS "Contract",
            con.paperless_billing AS "PaperlessBilling",
            con.payment_method AS "PaymentMethod",
            con.monthly_charges AS "MonthlyCharges",
            
            -- Sum only the amounts of transactions that are paid
            SUM(CASE WHEN t.paid = TRUE THEN t.amount ELSE 0 END)::NUMERIC AS "TotalCharges",

            -- COALESCE handles customers without transactions/status
            COALESCE(cs.churn, 'No') AS "Churn"

        FROM customers c
        -- Join churn label from the view
        JOIN contracts con 
            ON c.customer_id = con.customer_id
        LEFT JOIN transactions t 
            ON c.customer_id = t.customer_id
        LEFT JOIN customers_status cs
            ON c.customer_id = cs.customer_id

        GROUP BY 
            c.customer_id, c.gender, c.senior_citizen, c.partner, c.dependents,
            con.phone_service, con.multiple_lines,  
            con.internet_service, con.online_security, con.tech_support, con.online_backup,
            con.device_protection, con.streaming_movies, con.streaming_tv,
            con.contract_type, con.payment_method, con.paperless_billing, con.monthly_charges,
            cs.churn

        ORDER BY c.customer_id;
    """
    try:
        df = pd.read_sql(query, pg_engine)
        conn.close()
        print(f"✅ Query successful, {len(df)} rows retrieved")
        return df #  return dataframe as output of data extraction
    except Exception as e:
        raise RuntimeError(f"❌ Error executing query: {e}") # stop execution if connection fails
    

def transform_data(df):
    """
    Transform the extracted data before loading to BigQuery.
    Converting boolean columns (True/False) into 'Yes'/'No'.
    """
    try:
       # convert SeniorCitizen data type from boolean to integer
        df["SeniorCitizen"] = df["SeniorCitizen"].astype(int) 
       # Select all Boolean columns
        bool_cols = df.select_dtypes(include='bool').columns
        # Convert all Boolean columns to a vector
        df[bool_cols] = df[bool_cols].replace({True: "Yes", False: "No"})
        # drop duplicated columns
        # we don't need to run drop duplicates, 
        # because the previous query already used groupby based on customer id and the results were unique.
        #df = df.drop_duplicates(subset=["customerID"])
        print("✅ Transformation successful.")
        return df
    except Exception as e:
        raise RuntimeError(f"❌ Error transforming data: {e}") # stop execution if transformation fails

def load_to_bigquery(df):
    """
    Load transformed data to BigQuery using a staging-to-target approach.
    This ensures data consistency and prevents duplication by merging new records
    into the final production table.

    Workflow:
    1.  Upload data to a temporary staging table.
    2.  Merge staging data into the target table based on a unique key (CustomerID).
    """
     # Define table identifiers
    staging_id = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.{STAGING_TABLE}"
    target_id = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"
    
    # check BigQuery connection
    try:
        credentials = service_account.Credentials.from_service_account_file(GCP_CREDENTIALS)
        bq_client = bigquery.Client(project=GCP_PROJECT_ID, credentials=credentials)
        bq_client.get_dataset(BIGQUERY_DATASET)
        print("✅ Connected to BigQuery")
    except Exception as e:
        raise RuntimeError(f"❌ Error connecting to BigQuery: {e}")
    
    # Get Schema from Target Table
    try:
        target_table = bq_client.get_table(target_id)
        target_schema = target_table.schema
        print(f"✅ Successfully retrieved schema from target table: {BIGQUERY_TABLE}")
        #print(target_schema)
    except Exception as e:
        print(f"⚠️ Target table '{BIGQUERY_TABLE}' not found. Schema will be inferred from DataFrame.")
    
    
    # upload data to a staging table 
    try:
        # Configure load job (overwrite staging each time)
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",  # Replace existing data in staging table
            schema=target_schema,
        )
        
        # Upload DataFrame to staging table
        # If the staging table doesn't exist, BigQuery will automatically create it
        # using the schema inferred from the DataFrame.
        job = bq_client.load_table_from_dataframe(df, staging_id, job_config=job_config)
        job.result()  # Wait until upload is complete
        print(f"✅ Uploaded to staging table: {STAGING_TABLE}")
    except Exception as e:
        raise RuntimeError(f"❌ Error uploading to staging table: {e}")
        
    
    # Merge data from staging → target table 
    # try:
    #     # DML operations such as INSERT, UPDATE, and MERGE are **billable** in BigQuery
    #     # because they modify table data directly.
    #     # These operations are NOT covered by the BigQuery free tier.
    #     # 💡 Alternative (free option): use CREATE OR REPLACE TABLE ... AS SELECT ...
        
    #     # This SQL ensures that only new CustomerIDs are inserted.
    #     merge_query = f"""
    #     MERGE `{target_id}` AS target
    #     USING `{staging_id}` AS source
    #     ON target.CustomerID = source.CustomerID
    #     WHEN NOT MATCHED THEN
    #       INSERT ROW
    #     """
    #     bq_client.query(merge_query).result()
    #     print("✅ Merge completed successfully")
        
    #     # Delete staging table after merge
    #     # Helps keep your dataset clean and avoid unnecessary storage usage.
    #     # client.delete_table(staging_id, not_found_ok=True)
    #     # print("Staging table cleaned up")
        
    # except Exception as e:
    #     raise RuntimeError(f"❌ Error merging data: {e}")
    
    # --- Alternative (free option):Combine staging + target ---
    try:
        # Check if the main (target) table already exists
        tables = [t.table_id for t in bq_client.list_tables(BIGQUERY_DATASET)]
        if BIGQUERY_TABLE in tables:
            print(f"✅ Target table '{BIGQUERY_TABLE}' exists. Combining with staging data...")
            # Use UNION DISTINCT to avoid duplicate CustomerID entries
            combine_query = f"""
            CREATE OR REPLACE TABLE `{target_id}` AS
            SELECT * FROM `{target_id}`
            UNION DISTINCT
            SELECT * FROM `{staging_id}`;
            """
        else:
            pass
        # Run query
        bq_client.query(combine_query).result()
        print(f"✅ The staging and target tables were successfully merged and saved to: {BIGQUERY_TABLE}")
        
        # Delete staging table after merge
        # Helps keep your dataset clean and avoid unnecessary storage usage.
        bq_client.delete_table(staging_id, not_found_ok=True)
        print("Staging table cleaned up")

    except Exception as e:
        raise RuntimeError(f"❌ Error combining tables: {e}")
    

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="ETL Process for Customer Churn Data.")
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Run ETL process but skip loading to BigQuery. Prints head of transformed data."
    )
    args = parser.parse_args()

    # 1. Extraction (Always run)
    df = extract_data()
    
    # 2. Transformation (Always run)
    df_transformed = transform_data(df)
    
    # 3. Load (Conditional based on --test flag)
    if args.test:
        print("\n--- TEST MODE ACTIVE ---")
        print("💡 Skipping load to BigQuery.")
        print("\nTransformed Data Head (First 5 Rows):")
        print(df_transformed.head(3))
        print(f"\nTotal Rows: {len(df_transformed)}")
        print(df_transformed.dtypes)
        print("--- TEST MODE COMPLETE ---")
    else:
        # Load data to BigQuery
        load_to_bigquery(df_transformed)


