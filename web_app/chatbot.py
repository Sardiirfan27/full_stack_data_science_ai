import os
import chromadb
import numpy as np
import google.generativeai as genai 
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()
# Import type untuk menghindari error jika diperlukan, meskipun tidak digunakan
# di fungsi generate_content yang sudah dikoreksi tanpa safety settings.
# from google.generativeai.types import HarmCategory, HarmBlockThreshold, SafetySetting 

# =========================
# KONFIGURASI API & MODEL
# =========================
# Ambil kunci dari environment variable. Ini adalah praktik terbaik.
gemini_api_key = os.getenv("GEMINI_API_KEY") 

if not gemini_api_key:
    print("ERROR: Variabel lingkungan GEMINI_API_KEY tidak ditemukan. Harap atur sebelum menjalankan.")
    exit()

# Konfigurasi klien global
genai.configure(api_key=gemini_api_key)

GEMINI_MODEL_NAME = "gemini-2.5-flash"
EMBEDDING_MODEL_NAME = "models/text-embedding-004" 

# ============================================================
# 0. DATA TELCO (Sumber Pengetahuan)
# ============================================================
telco_data_documents = [
    "Paket Indihome 100 Mbps menawarkan kecepatan download/upload simetris. Harga promosi saat ini adalah Rp 375.000 per bulan (belum termasuk PPN). Paket ini termasuk layanan UseeTV Basic. FUP berlaku setelah pemakaian 1000 GB. Cocok untuk 5-8 pengguna aktif.",
    "XL Home menawarkan paket 100 Mbps dengan harga flat Rp 349.000 per bulan. Tidak ada FUP yang diberlakukan. Termasuk gratis streaming Vidio Platinum 3 bulan. Kecepatan simetris. Saat ini tersedia di Jabodetabek dan Bandung.",
    "Latency adalah waktu tunda atau jeda waktu yang dibutuhkan sebuah paket data untuk melakukan perjalanan. Latency tinggi (di atas 100ms) buruk untuk game online dan video conference.",
    "Jaringan 5G menawarkan kecepatan hingga 10 Gbps dan latency yang sangat rendah (sekitar 1-10ms), namun memerlukan perangkat yang kompatibel dan saat ini jangkauannya masih terbatas di kota-kota besar.",
    "Paket Mobile Data Telkomsel prabayar termurah saat ini adalah Combo Sakti 15GB seharga Rp 70.000 per 30 hari, mencakup kuota utama dan bonus media sosial.",
    "FUP (Fair Usage Policy) adalah kebijakan penggunaan wajar, di mana setelah batas kuota tertentu (misal 500GB) tercapai, kecepatan internet akan diturunkan secara signifikan."
]


# ============================================================
# 1. EMBEDDING FUNCTION
# ============================================================
class GeminiEmbeddingFunction(embedding_functions.EmbeddingFunction):
    """Fungsi embedding yang disesuaikan untuk ChromaDB menggunakan genai.embed_content."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name

    def __call__(self, texts):
        vectors = []
        task_type = "RETRIEVAL_DOCUMENT" 

        for txt in texts:
            # Menggunakan 'content' sesuai format SDK genai terbaru
            result = genai.embed_content(
                model=self.model_name,
                content=txt,
                task_type=task_type
            )
            # Hasil embedding ada di key ['embedding']
            vectors.append(np.array(result["embedding"]))

        return vectors


# ============================================================
# 2. INDEXING CHROMADB
# ============================================================
def index_telco_data_gemini(documents):
    """Membuat atau memuat koleksi ChromaDB dan mengisi dokumen jika kosong."""
    print("--- 1. INDEXING: Membangun Vector DB dengan Gemini Embeddings ---")
    
    chroma_client = chromadb.PersistentClient("./chroma_telco")

    gemini_ef = GeminiEmbeddingFunction(
        model_name=EMBEDDING_MODEL_NAME
    )

    collection = chroma_client.get_or_create_collection(
        name="telco_collection",
        embedding_function=gemini_ef
    )

    if collection.count() == 0:
        ids = [f"doc-{i}" for i in range(len(documents))]
        collection.add(documents=documents, ids=ids)
        print(f"   -> Berhasil memasukkan {len(documents)} dokumen ke ChromaDB.")
    else:
        print(f"   -> Koleksi sudah berisi {collection.count()} dokumen. Melewati indexing.")

    return collection


# ============================================================
# 3. RETRIEVAL
# ============================================================
def retrieve_context(collection, query):
    """Mencari dokumen yang paling relevan berdasarkan query."""
    
    results = collection.query(
        query_texts=[query],
        n_results=3,
        include=["documents"]
    )
    return results["documents"][0]


# ============================================================
# 4. GENERATION (TANPA SAFETY SETTINGS)
# ============================================================
def rag_generate_response(user_prompt, collection):
    """Menggabungkan Retrieval dan Generasi Jawaban menggunakan Gemini Flash."""
    
    # 1. Retrieval
    docs = retrieve_context(collection, user_prompt)

    # 2. Augmentation
    context = "\n---\n".join(docs)

    full_prompt = (
        "Anda adalah Telco Insight Assistant. Berikan jawaban yang informatif dan obyektif. "
        "Gunakan konteks berikut untuk menjawab pertanyaan pengguna, terutama untuk harga dan perbandingan. "
        "Selalu berikan **disclaimer** bahwa harga dapat berubah sewaktu-waktu. \n\n"
        f"### KONTEKS DATA TERBARU:\n{context}\n\n"
        f"### PERTANYAAN PENGGUNA:\n{user_prompt}"
    )

    # 3. Generation (Menggunakan GenerativeModel)
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    
    # Panggilan tanpa safety_settings
    response = model.generate_content(
        full_prompt
    )

    return response.text


# ============================================================
# 5. MAIN TEST
# ============================================================
if __name__ == "__main__":
    
    # 1. INDEXING
    collection = index_telco_data_gemini(telco_data_documents)
    
    print("\n--- TELCO INSIGHT CHATBOT AKTIF ---")

    # 2. TESTING RAG
    q1 = "Bandingkan harga Indihome 100 Mbps dan XL Home, dan apakah XL Home memberlakukan FUP?"
    print(f"\nPERTANYAAN 1: {q1}")
    print("\n[JAWABAN TELCO ASISTEN 1]:")
    print(rag_generate_response(q1, collection))

    print("\n" + "=" * 50 + "\n")

    q2 = "Apa beda latency dan FUP?"
    print(f"\nPERTANYAAN 2: {q2}")
    print("\n[JAWABAN TELCO ASISTEN 2]:")
    print(rag_generate_response(q2, collection))