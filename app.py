import streamlit as st
import google.generativeai as genai

# Sayfa ayarları
st.set_page_config(page_title="Eymen AI", page_icon="🤖")

st.markdown("<h1 style='color: #40E0D0; text-align: center;'>✨ Eymen AI</h1>", unsafe_allow_html=True)

# API Anahtarı
API_KEY = "AIzaSyBmYhJCNrzfg7WFMuhjGiUPc9jxaMG0rbo"

# Bağlantı denemesi
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"API Yapılandırma Hatası: {e}")

# Sohbet geçmişi
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı girişi
if prompt := st.chat_input("Eymen AI'ye bir şey sor..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("Bağlantı hatası: API anahtarını kontrol et veya ağını kontrol et.")
            st.write(f"Detay: {e}")
