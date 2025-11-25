import streamlit as st
import streamlit.components.v1 as components

def render():
    # --- Konfigurasi Halaman ---
    st.set_page_config(layout="wide")
    st.title("Customer Churn Prediction & Analysis (Kaggle Embed)")
    if 'show_kaggle' not in st.session_state:
        st.session_state.show_kaggle = False #Ini memastikan variabel `show_kaggle` ada di *state* dan disetel ke `False` (sembunyi) saat aplikasi pertama kali dimuat.
    #tampilan kaggle notebook
    if st.button("🔗 Tampilkan/Sembunyikan Notebook"):
        st.session_state.show_kaggle = not st.session_state.show_kaggle
    
    if st.session_state.show_kaggle:
        # --- Kode Iframe dari Kaggle ---
        # Ambil seluruh tag <iframe> yang Anda berikan
        # Pastikan Anda mengutip (quote) string HTML dengan benar
        html_code = """
        <style>
            /* 1. Gaya untuk Wrapper */
            .iframe-container {
                position: relative; /* Penting untuk penempatan spinner */
                margin: 0 auto;
                width: 100%;
                max-width: 950px;
                height: 800px; /* Tentukan tinggi wrapper sesuai iframe */
                border: 1px solid #ddd; /* Opsional: Untuk melihat batas area */
                overflow: hidden; /* Pastikan semua konten di dalam batas */
            }

            /* 2. Gaya untuk Iframe */
            .iframe-content {
                width: 100%;
                height: 100%;
                opacity: 0; /* Mulai tersembunyi */
                transition: opacity 0.8s ease-in-out; /* Transisi fade-in mulus */
                border: none; /* Hilangkan border bawaan iframe */
            }

            /* 3. Gaya untuk Loading Spinner */
            .loading-spinner {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: #f0f0f0; /* Warna latar saat loading */
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 10; /* Pastikan spinner di atas iframe */
                transition: opacity 0.5s ease-out; /* Transisi menghilang */
            }

            /* Gaya dasar spinner (Contoh: Animasi putar sederhana) */
            .spinner {
                border: 4px solid rgba(0, 0, 0, 0.1);
                border-top: 4px solid #3498db; /* Warna spinner */
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite; /* Animasi putar */
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>

        <div class="iframe-container">
            <div id="loading-indicator" class="loading-spinner">
                <div class="spinner"></div>
                <p style="margin-top: 60px; color: #555;">Memuat konten Kaggle...</p>
            </div>

            <iframe 
                id="kaggle-iframe"
                class="iframe-content"
                src="https://www.kaggle.com/embed/sardiirfansyah/customer-churn-prediction-analysis?kernelSessionId=281349664" 
                frameborder="0" 
                scrolling="auto" 
                title="📊CUSTOMER CHURN PREDICTION &amp; ANALYSIS 📈"
                
                /* 4. Logika JavaScript Saat Iframe Selesai Dimuat */
                onload="
                    document.getElementById('loading-indicator').style.opacity = '0'; 
                    document.getElementById('loading-indicator').style.zIndex = '-1'; 
                    this.style.opacity = '1';
                "> 
            </iframe>
        </div>
        """
        st.write("tunggu sebentar hingga notebook termuat sepenuhnya...")
        # Tanamkan (embed) kode HTML menggunakan komponen Streamlit
        # height harus diset agar komponen memiliki ruang yang cukup di Streamlit
        components.html(
            html_code, 
            height=850, # Set sedikit lebih besar dari height iframe (800)
            scrolling=True 
        )
