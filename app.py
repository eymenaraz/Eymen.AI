import streamlit as st
import google.generativeai as genai

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Eymen AI", page_icon="🤖", layout="centered")

# --- MODERN VE ADAPTİF TASARIM (DARK/LIGHT MOD UYUMLU) ---
st.markdown("""
    <style>
    /* Ana başlık stili */
    .stApp h1 {
        font-family: 'Segoe UI', sans-serif;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Mesaj balonları için modern gölge ve kenarlık */
    [data-testid="stChatMessage"] {
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Yazı kutusu stili */
    .stChatInput {
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BAŞLIK ---
st.title("🤖 Eymen AI")
st.markdown("<p style='text-align: center;'>Modern ve Hızlı Yapay Zeka Deneyimi</p>", unsafe_allow_html=True)

# --- BAĞLANTI AYARLARI ---
API_KEY = "AIzaSyCY_ZsASlHUCQ6h7NA9ETnfHz2QcslNL6E"
MODEL_NAME = "models/gemini-2.5-flash"

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    st.error(f"Sistem başlatılamadı: {e}")

# --- SOHBET MANTIĞI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Geçmişi listele
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı girişi
if prompt := st.chat_input("Mesajını buraya yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            # Yanıtı parça parça (stream) alarak daha profesyonel bir his veriyoruz
            response = model.generate_content(prompt, stream=True)
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error("Bir hata oluştu, lütfen sayfayı yenile.")
