import streamlit as st
from view.chatbot_logic import load_collection, retrieve_context, GEMINI_MODEL, API_KEY
#import google.generativeai as genai
from google import genai
from google.genai import types 
import random
import time



#pengaturan avatar  
avatars = {  
    "user": "./asset/user-icon.png",  
    "assistant": './asset/ai_noid.png' # ":material/smart_toy:"  
}  

# CSS loader (animasi memutar)
# CSS loader + teks di kiri
loader_with_text = """
<style>
.loader-container {
    display: flex;
    align-items: center;
    justify-content: flex-start;  /* kiri */
    gap: 10px; /* jarak antara loader dan teks */
    margin-top: 10px;
    margin-bottom: 10px;
}
.loader {
  border: 4px solid #f3f3f3; /* abu-abu terang */
  border-top: 4px solid #3498db; /* biru */
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.loader-text {
    font-size: 14px;
    color: #555;
}
</style>

<div class="loader-container">
    <div class="loader"></div>
    <div class="loader-text">Sedang memproses...</div>
</div>
"""

def load_context(user_message):
    collection = load_collection()

    docs = retrieve_context(collection, user_message)
    if not docs:
        return "Maaf, saya tidak menemukan informasi terkait di database kami."
    context = "\n---\n".join(docs)
    return context

# Fungsi untuk menampilkan riwayat chat  
def display_message(message):  
    role = message.role
    avatar = avatars["user"] if role == "user" else avatars["assistant"]  
    with st.chat_message(role, avatar=avatar):  
        if role == "user":  
            st.text(message.parts[0].text)  
        else:  
            st.markdown(message.parts[0].text)  
            
def render():
    st.title("🤖 Telco Chatbot (RAG)")

    st.markdown("""
    Chatbot ini menggunakan **Gemini + ChromaDB** untuk menjawab pertanyaan berdasarkan knowledge Telco.
    """)
    # Inisialisasi riwayat chat di session state jika belum ada
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Preload collection dan Reload Button
    # Memastikan caching collection di-clear saat reload
    # Menggunakan st.container untuk membungkus tombol dan memberikan key untuk CSS
    flex = st.container(key="chatbot_buttons", horizontal=True)
    button1 = flex.button("🔄 Reload Knowledge", )
    botton2 = flex.button("🗑️ Hapus Riwayat Chat")
    if button1:
        load_collection.cache_clear()
        load_collection()
        st.session_state.messages = []
        st.success("Knowledge base berhasil direload! Riwayat chat dikosongkan.")
        st.rerun() # Refresh tampilan untuk state baru
    if botton2:
        st.session_state.messages = []
        st.rerun() # Refresh tampilan

    st.markdown("---")
    
    ## Definisikan model gemini untuk menyimpan sesi chat
    client = genai.Client(api_key=API_KEY)
    chat=client.chats.create(model=GEMINI_MODEL,
                             history=st.session_state.messages)

    ## 💬 Menampilkan Riwayat Chat ##
    # Iterasi dan tampilkan semua pesan yang tersimpan
    for message in chat.get_history():
        display_message(message)

    # Input Pengguna menggunakan st.chat_input untuk interaksi yang lebih baik
    if user_input := st.chat_input("Tanyakan tentang paket, biaya, atau layanan Telco..."):
        
        # Tampilkan pesan pengguna di antarmuka
        with st.chat_message("user", avatar=avatars["user"]):
            st.markdown(user_input)
        
        # Proses respons dari Chatbot RAG
        with st.chat_message("assistant", avatar=avatars["assistant"]):
            
            # Panggil fungsi RAG untuk load konteks
            context = load_context(user_message=user_input)
            prompt = f"""
            Anda adalah AI-NOID Telco Assistant.
            Jawab secara objektif, ringkas dan ramah + emoji.
            Jika user beri sapaan, balas dengan bhs ramah.
            Jika tidak tahu jawabannya, katakan "Maaf, saya tidak memiliki informasi tersebut."
            ### KONTEKS:
            {context}
            
            """
            message_placeholder = st.empty()   
            message_placeholder.markdown(loader_with_text , unsafe_allow_html=True)
            full_response = ""
            response = chat.send_message(
                    user_input,
                    config=types.GenerateContentConfig(
                        system_instruction=prompt
                    )
            )
            # print(f'respose: {response.candidates[0].content.parts[0].text}')
            response_text=response.candidates[0].content.parts[0].text
            word_count = 0  
            random_int = random.randint(4, 9)  
            for word in response_text:  
                full_response += word  
                word_count += 1  
                if word_count == random_int:  
                    time.sleep(0.05)  
                    message_placeholder.markdown(full_response + "")  
                    word_count = 0  
                    random_int = random.randint(4, 9)  
            message_placeholder.markdown(full_response)  
                    
                # print(f'chunk: {chunk}')
                # word_count = 0  
                # random_int = random.randint(4, 9)  
                # for word in chunk.text:  
                #     full_response += word  
                #     word_count += 1  
                #     if word_count == random_int:  
                #         time.sleep(0.05)  
                #         message_placeholder.markdown(full_response + "_")  
                #         word_count = 0  
                #         random_int = random.randint(4, 9)  
            message_placeholder.markdown(full_response) 
                
                # # Tampilkan respons dari model
                # st.markdown(response)

        # 4. Tambahkan respons chatbot ke riwayat
        st.session_state.messages=chat.get_history()



# Jika ini adalah file utama yang dijalankan
if __name__ == "__main__":
    render()