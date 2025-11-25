import os
import chromadb
import numpy as np
from google import genai
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from functools import lru_cache
from google.genai import types
import logging
import time
import pandas as pd
from pathlib import Path
import json

# ===========================
# Load environment
# ===========================
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY tidak ditemukan.")

client = genai.Client(api_key=API_KEY)
GEMINI_MODEL = "gemini-2.5-flash-lite"
EMBED_MODEL = "models/text-embedding-004"
COLLECTION_NAME = "telco_collection_v2_optimized" # Ganti nama koleksi

# ===========================
# Logging
# ===========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)

# Implementasi Batching dan Optimasi Embedding Function
class GeminiEmbeddingFunction(embedding_functions.EmbeddingFunction):
    """
    Fungsi embedding kustom yang dirancang untuk berinteraksi dengan 
    Google Gemini API melalui client yang disediakan.

    Kelas ini mengimplementasikan teknik optimasi penting:
    1. Batching: Mengirim beberapa dokumen sekaligus untuk meningkatkan kecepatan 
       dan mengurangi overhead jaringan.
    2. Exponential Backoff: Menerapkan logika coba ulang dengan jeda waktu yang 
       terus meningkat untuk mengatasi error API sementara (seperti rate limiting),
       sehingga meningkatkan keandalan.

    Atribut:
        client (google.genai.Client): Klien Gemini API yang sudah terautentikasi.
        model (str): Nama model embedding yang digunakan (misalnya, "models/text-embedding-004").
        batch_size (int): Jumlah maksimum dokumen yang diproses dalam satu panggilan API.
                          (Default: 64).
    """
    def __init__(self, client, model):
        self.client = client
        self.model = model
        self.batch_size = 64 # Ukuran batch yang baik untuk efisiensi

    def __call__(self, texts):
        vectors = []
        
        # Iterasi teks dalam batch
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            # Retry logic dengan Exponential Backoff
            for attempt in range(3):
                try:
                    res = self.client.models.embed_content(
                        model=self.model,
                        contents=batch, # Kirim seluruh batch teks
                        config=types.EmbedContentConfig(
                            task_type="RETRIEVAL_DOCUMENT",
                            #  Output dimensi lebih kecil (768) lebih cepat dan hemat memori
                            output_dimensionality=768 
                        )
                    )
                    
                    for embedding in res.embeddings:
                        vectors.append(np.array(embedding.values))
                    
                    logging.info(f"Berhasil embed batch {i//self.batch_size + 1}/{len(texts)//self.batch_size + 1}")
                    break
                except Exception as e:
                    logging.warning(f"Embedding batch gagal, retry ({attempt+1}/3)... {e}")
                    # Menunggu waktu yang lebih lama setiap kali gagal (2^0, 2^1, 2^2 detik)
                    time.sleep(2 ** attempt) 
            else:
                logging.error(f"Embedding batch gagal total pada indeks {i}.")
                raise
                
        return vectors


# ===========================
# Load Knowledge Documents (Tidak Berubah, Tapi Diperkuat Kualitasnya)
# ===========================

BASE_DIR = Path(__file__).resolve().parent
DOCS_BASE = BASE_DIR / "knowledge_docs"
# print(DOCS_BASE) # Hapus print ini

def load_telco_docs(
    json_file=DOCS_BASE / "telco_services.json",
    ):
    """
    Memuat dokumen pengetahuan dan memformatnya menjadi list of strings.
    """
    if json_file.exists():
        with open(json_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                logging.error(f"Gagal decode JSON: {e}")
                return []
        
        docs_list = []
        
        # Q: Kualitas: Pastikan 'doc_string' padat dan fokus pada inti informasi
        if "paket_dan_biaya" in data and isinstance(data["paket_dan_biaya"], list):
            for paket in data["paket_dan_biaya"]:
                nama = paket.get("nama_paket", "Paket Tidak Diketahui")
                tipe_internet = paket.get("internet", "N/A")
                kecepatan = paket.get("kecepatan_mbps", "N/A")
                biaya_dasar = paket.get("biaya_dasar_usd", 0.00)
                biaya_final = paket.get("contoh_perhitungan", {}).get("biaya_final_usd", {})
                
                # 🎯 KUALITAS: Membuat string dokumen yang sangat informatif dan terstruktur.
                doc_string = f"""
Nama Paket: {nama}. Jenis Layanan Internet: {tipe_internet}. Kecepatan: {kecepatan} Mbps.
Biaya Dasar (tanpa add-on): ${biaya_dasar:.2f}. 
Biaya Add-on: ${data.get("aturan_biaya", {}).get("biaya_addon_usd", 10):.2f}.
Biaya Total Bulan + 1 add-on ke Bulan: ${biaya_final.get("month_to_month", 'N/A')}.
Biaya Total Kontrak 1 Tahun + 1 add-on (Diskon 5%): ${(biaya_final.get("one_year", '0')*12)}/tahun atau setara dengan ${biaya_final.get("one_year", 'N/A')}/bulan.
Biaya Total Kontrak 2 Tahun + 1 add-on (Diskon 10%): ${(biaya_final.get("two_year", 0)*24)}/tahun atau setara dengan ${biaya_final.get("two_year", 'N/A')}/bulan.
Layanan Tambahan: {', '.join(data.get("layanan_tambahan", []))}.
"""
                docs_list.append(doc_string.strip())
        
        if docs_list:
            logging.info(f"Loaded {len(docs_list)} docs from JSON: {json_file.name}")
            return docs_list
        else:
            logging.warning("JSON terload, tetapi tidak ada data 'paket_dan_biaya' yang valid.")
            return []
    else:
        logging.error(f"File dokumen tidak ditemukan: {json_file}")
        return []

def seed_collection(collection):
    """Fungsi untuk proses seeding dokumen (memasukkan dokumen ke ChromaDB)."""
    logging.info("Koleksi kosong, mulai insert dokumen...")
    docs = load_telco_docs()

    if not docs:
        logging.error("Dokumen kosong. Chroma tidak bisa dibuat.")
        return

    ids = [f"doc_{i}" for i in range(len(docs))]
    collection.add(ids=ids, documents=docs) 
    logging.info(f"{len(docs)} dokumen berhasil dimasukkan ke Chroma DB.")
    
# ===========================
# Load Chroma Vector Store (Optimasi Caching)
# ===========================
# Mengubah maxsize ke nilai yang lebih kecil, karena hanya butuh satu koleksi.
@lru_cache(maxsize=1) 
def load_collection():
    """Memuat atau membuat koleksi ChromaDB, seeding jika kosong."""
    
    chroma_path = "./chroma_telco"
    Path(chroma_path).mkdir(exist_ok=True)
    
    chroma_client = chromadb.PersistentClient(chroma_path)

    # Pastikan koleksi terambil/terbuat
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=GeminiEmbeddingFunction(client,model=EMBED_MODEL) 
    )

    # Jika koleksi kosong → seed pertama kali (atau jika dokumen baru dihapus)
    if collection.count() == 0:
        seed_collection(collection)
        
    return collection
# ===========================
# Retrieval 
# ===========================
def retrieve_context(collection, query, k=3):
    """Mencari dokumen yang paling relevan."""
    try:
        result = collection.query(
            query_texts=[query],
            n_results=k,
            include=["documents"]
        )
        docs = result.get("documents", [[]])[0]
        return docs
    except Exception as e:
        logging.error(f"Retrieval error: {e}")
        return []


# ===========================
# Chatbot — RAG Generation (Optimasi Streaming)
# ===========================
def get_chatbot_response(user_message):
    # load_collection() cepat karena @lru_cache
    collection = load_collection() 

    docs = retrieve_context(collection, user_message)

    if not docs:
        return "Maaf, saya tidak menemukan informasi terkait di database kami."

    context = "\n---\n".join(docs)

    prompt = f"""
    Anda adalah AI-NOID Assistant sebagai CS pintar.
    Jawab secara objektif, ringkas, ramah dan seperti sales yang menawarkan produk.
    Gunakan informasi dari KONTEKS secara eksklusif dan ringkas.
    Jika user beri sapaan, balas dengan bhs ramah.
    Jika tidak tahu jawabannya, katakan "Maaf, saya tidak memiliki informasi tersebut.
    

    ### KONTEKS:
    {context}

    ### USER:
    {user_message}

    """
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        # 🎯 CEPAT: Menggunakan stream=True sudah baik, karena user menerima respons lebih cepat
        response = model.generate_content(prompt,stream=True) 
        return response
    except Exception as e:
        logging.warning(f"Generate error, retry... {e}")
        time.sleep(1)

    return "Maaf, sistem sedang mengalami gangguan. Coba lagi nanti. 🛠️"


def check_dataframe_collection():
    """Fungsi untuk memeriksa hasil koleksi ChromaDB."""
    sample_data = load_collection().get(include=['documents', 'embeddings'])
    df = pd.DataFrame({
        "IDs": sample_data['ids'][:3],
        "Documents": sample_data['documents'][:3],
        "Embeddings": [str(emb)[:100] + "..." for emb in sample_data['embeddings'][:3]]  # Truncate embeddings
    })

    return df
