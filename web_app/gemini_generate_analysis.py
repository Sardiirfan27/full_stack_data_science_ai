from google import genai 
from google.genai import types
from google.cloud import bigquery
from google.cloud import bigquery_storage
from google.oauth2 import service_account
import pandas as pd
import re

import os
from dotenv import load_dotenv
load_dotenv()

# Load environment variables
load_dotenv()

try:
    GCP_CREDENTIALS = os.getenv("GCP_CREDENTIALS")  
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")
    BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE")
    credentials = service_account.Credentials.from_service_account_file(GCP_CREDENTIALS)
    bq_client = bigquery.Client(credentials=credentials, project=GCP_PROJECT_ID)
    bqstorage_client = bigquery_storage.BigQueryReadClient(credentials=credentials)
    MODEL_NAME = 'gemini-2.0-flash-001' 
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
except Exception as e:
    # Ini akan ditampilkan jika kredensial tidak disetel di env
    print(f"Error Konfigurasi Kredensial: {e}")
    print("Pastikan variabel lingkungan GCP_PROJECT_ID, BIGQUERY_DATASET, dan GEMINI_API_KEY telah disetel.")
  
  
#-----------------------------------------------------------
# FUNGSI BERSIHKAN OUTPUT LLM
#-----------------------------------------------------------
def clean_output(text: str) -> str:
    """Menghapus tanda backtick dan baris kosong di awal dan akhir teks."""
    return re.sub(r"```.*?\n|```", "", text).strip()

# -----------------------------------------------------------
# I. FUNGSI OTOMATISASI SKEMA
# -----------------------------------------------------------

def get_formatted_schema(table_name: str) -> str:
    """
    Mengambil skema kolom dari tabel BigQuery dan memformatnya 
    ke dalam string yang ideal untuk prompt Gemini.
    """
    try:
        #table_ref = bq_client.dataset(BIGQUERY_DATASET).table(table_name)
        table_ref= f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.{table_name}"
        table = bq_client.get_table(table_ref)
        
        # Format skema dalam bentuk teks yang mudah dibaca LLM
        schema_text = f"--- SKEMA BIGQUERY ({BIGQUERY_DATASET}.{table_name}) ---\n"
        for field in table.schema:
            # OPTIMASI KUALITAS: Tambahkan deskripsi kolom (jika ada)
            #description = f" - {field.description}" if field.description else ""
            #schema_text += f" - {field.name} ({field.field_type}{description})\n"
            schema_text += f" - {field.name} ({field.field_type})\n"
            
        return schema_text
        
    except Exception as e:
        return f"ERROR_SCHEMA: Gagal mengambil skema tabel {table_name}. Detail: {e}"
    
# -----------------------------------------------------------
# II. FUNGSI GENERASI SQL (OTAK ANALISIS)
# -----------------------------------------------------------
def generate_sql_from_question(schema: str, question: str) -> str | None:
    """Meminta Gemini membuat kueri SQL berdasarkan pertanyaan dan skema."""
    
    system_instruction = (
        "Anda adalah Expert DS yang mahir Google BigQuery. "
        "Jawab HANYA dengan kode SQL, tanpa penjelasan, atau teks lainnya. "
        "Pastikan semuanya fungsi agregasi menggunakan AS. "
        "Gunakan format: SELECT ... FROM `{}`.`{}`.`{}`".format(GCP_PROJECT_ID, BIGQUERY_DATASET, BIGQUERY_TABLE), 
    )
    
    prompt = f"{schema}\n\n--- PERTANYAAN PENGGUNA ---\n{question}"
    
    try:
        # Menggunakan gemini_model yang sudah diinisialisasi
        # Gunakan parameter 'temperature' yang rendah (0.0)
        # karena kita ingin hasil yang deterministik dan akurat, bukan kreatif.
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0 
            )
        )
        print(response.text)
        # Bersihkan output LLM
        return clean_output(response.text)

    except Exception as e:
        print(f"❌ Error Gemini API: {e}")
        return None

# -----------------------------------------------------------
# III. FUNGSI EKSEKUSI KUERI
# -----------------------------------------------------------

def execute_bigquery_query(sql_query: str) -> pd.DataFrame:
    """Mengeksekusi kueri di BigQuery dan mengembalikan hasilnya sebagai Pandas DataFrame."""
    print("🚀 Mengeksekusi kueri di BigQuery...")
    try:
        query_job = bq_client.query(sql_query)
        # Mengubah hasil menjadi Pandas DataFrame
        df = query_job.to_dataframe(bqstorage_client=bqstorage_client)
        print(f"✅ Kueri berhasil dieksekusi.")
        return df
    except Exception as e:
        print(f"❌ Gagal mengeksekusi kueri BigQuery. Detail: {e}")
        return pd.DataFrame()
   
# -----------------------------------------------------------
# IV. FUNGSI GENERASI KODE CHART
# -----------------------------------------------------------   
def generate_python_code(question: str, structure_data: str) -> str | None:
    """Meminta Gemini membuat kode Plotly Express berdasarkan pertanyaan dan head DataFrame."""
    
    system_instruction = (
        "Kamu adalah Expert DS & BI."
        "Kamu memiliki dataframe 'df_result'. "
        "Hasilkan kode python streamlit dan plotly sesuai dengan pertanyaan."
        "Pastikan kode diawali dengan 'import library' dan juga atur margin l,r,t,b =20. "
        "Jwb HANYA dengan kode inti PYTHON, tanpa penjelasan, atau teks lainnya, hindari if__name__ == '__main__' dan pembuatan fungsi."
        "Jelaskan insight dengan st.markdown, insight bisnis untuk stackholder. "
        "Gunakan st.container didalamnya st.col, contoh col1=chart, col2=insight." 
    )
    
    prompt = f"""
    --- PERTANYAAN USER ---
    {question}

    --- STRUKTUR DAN CONTOH DATA (DataFrame bernama 'df_result') ---
    {structure_data}
    
    HASILKAN KODE PYTHON LENGKAP MENGGUNAKAN PLOTLY DAN STREAMLIT:
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME, # Menggunakan model yang sama
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        # bersihkan output
        return clean_output(response.text) 
    except Exception as e:
        print(f"❌ Error Gemini API saat generate kode chart: {e}")
        return None

# -----------------------------------------------------------
# V. ALUR UTAMA (MAIN FLOW)
# -----------------------------------------------------------

def main_analysis_flow(user_question: str) -> tuple[pd.DataFrame | None, str | None]:
    """Menjalankan seluruh alur analisis dan menghasilkan chart."""
    
    #  Ambil Skema Otomatis
    schema_text = get_formatted_schema(BIGQUERY_TABLE)
    
    if schema_text.startswith("ERROR_SCHEMA"):
        print(schema_text)
        return None, None

    # Generasi SQL oleh Gemini
    print(f"\n🧠 Pertanyaan: {user_question}")
    sql_query = generate_sql_from_question(schema_text, user_question)
    
    if not sql_query:
        print("\n❌ Gagal membuat kueri SQL.")
        return None, None
    
    # Eksekusi Kueri
    df_result = execute_bigquery_query(sql_query)
    if df_result.empty:
        print("\n⚠️ Hasil kosong dikembalikan dari BigQuery.")
        return None, None
    
    # Dapatkan 5 baris pertama data sebagai string (untuk konteks LLM)
    df_head_str = df_result.head().to_markdown(index=False)
    df_types_str = df_result.dtypes.to_string() # Ambil tipe data
    
    prompt_data_context = f"Kolom dan Tipe Data:\n{df_types_str}\n\nContoh Data:\n{df_head_str}"
    
    #5. Panggil fungsi generator kode chart
    python_code = generate_python_code(user_question, prompt_data_context)
    
    return df_result, python_code
         
# --- CONTOH PENGGUNAAN SKRIP (Jalankan ini untuk menguji) ---
if __name__ == '__main__':
    
    # Ganti dengan pertanyaan analisis yang Anda inginkan
    analysis_question = "Hitung jumlah pelanggan berdasarkan jenis kontrak (Contract). Urutkan dari tertinggi ke terendah."
    
    df_final, chart_code = main_analysis_flow(analysis_question)
    
    if chart_code is not None:
        print("\nHasil kode chart:")
        print(chart_code)
    
    if df_final is not None:
        print("\nSkrip berhasil dan DataFrame siap untuk visualisasi di Streamlit.")