import streamlit as st
from view import dashboard, predict,chatbot_ui, kaggle_notebook
#ignore warnings
import warnings
warnings.filterwarnings(
    "ignore",
    message=".*width.*"
)

# --- Global Style ---
st.set_page_config(
    page_title="Telco Churn Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load CSS (optional)
with open('style/style.css',"r", encoding="utf-8") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- Initialize state ---
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# --- SIDEBAR ---
with st.sidebar:
    # 🟢 Container 1: Header
    header = st.container()
    with header:
        st.image("https://cdn.dribbble.com/userupload/19805829/file/original-cb925c0b18eb169378d862ac77e7f739.gif", width=1000)
        st.title("Customer Churn Dashboard")
        st.markdown("---")

    # 🟣 Container 2: Navigation
    nav = st.container()
    with nav:
        st.markdown(
            "<h2 style='font-size:1.5rem; font-weight:700; color:#fff;'>📂 Navigation</h2>",
            unsafe_allow_html=True
        )
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
        if st.button("🔮 Predict Churn", use_container_width=True):
            st.session_state.page = "predict"
        if st.button("🤖 Telco Chatbot", use_container_width=True):
            st.session_state.page = "chatbot"
        if st.button("📊 Kaggle Notebook", use_container_width=True):
            st.session_state.page = "kaggle_notebook"
        st.markdown("---")
        

    # 🔵 Container 3: User Info / Footer
    # footer = st.container()
    # with footer:
    #     st.markdown("👤 **Logged in as:** `guest_user`")
    #     if st.button("🚪 Logout", width=True):
    #         st.session_state.page = "dashboard"
    #         st.success("You have been logged out!")
    #     st.markdown("---")
    #     st.caption("© 2025 Telco AI Dashboard")

# --- MAIN CONTENT ---
if st.session_state.page == "dashboard":
    dashboard.render()
elif st.session_state.page == "predict":
    predict.render()
elif st.session_state.page == "chatbot":
    chatbot_ui.render()
elif st.session_state.page == "kaggle_notebook":
    kaggle_notebook.render()
