import streamlit as st
import google.generativeai as genai

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Eymen AI", page_icon="🤖", layout="centered")

# --- MODERN TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1 { color: #40E0D0 !important; font-family: sans-serif; text-align: center; }
    [data-testid="stChatMessage"] { background-color: #F0F8FF; border-radius: 15px; padding: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ Eymen AI")

# --- API AYARLARI (GÜÇLENDİRİLMİŞ) ---
# Kendi anahtarını buraya sabitliyoruz ki hata payı kalmasın
API_KEY = "AIzaSyCPQanGNqt9zxU4fvib3EjRkL__J9UDgEE"

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Sistem yapılandırma hatası. Lütfen sayfayı yenile.")
    st.stop()

# --- SOHBET GEÇMİŞİ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- SOHBET ALANI ---
if prompt := st.chat_input("Eymen AI'ye bir şey sor..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            # Yapay zeka ile bağlantı
            response = model.generate_content(prompt, stream=True)
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception:
            st.warning("İnternet veya servis hatası oluştu. Lütfen tekrar dene.")
