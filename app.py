import streamlit as st
import google.generativeai as genai

# En hafif sayfa ayarları
st.set_page_config(page_title="Eymen AI", layout="centered")

# API Anahtarı (Secrets)
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# Model
model = genai.GenerativeModel('gemini-2.5-flash')

st.title("⚡ Eymen AI")

# Sohbet geçmişini tut
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları yazdır
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Giriş kutusu
if prompt := st.chat_input("Eymen AI'ye sor..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        # stream=False yapıyoruz (Daha az yük, daha hızlı yanıt)
        response = model.generate_content(prompt)
        st.write(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
