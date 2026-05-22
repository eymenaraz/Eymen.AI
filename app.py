import streamlit as st
import google.generativeai as genai
import time

st.set_page_config(page_title="Eymen AI", layout="centered")

# API Anahtarı
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error("API yapılandırma hatası!")
    st.stop()

st.title("⚡ Eymen AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Eymen AI'ye sor..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            # İstek gönder
            response = model.generate_content(prompt)
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            # Kota dolduğunda kullanıcıya bunu söyle
            if "ResourceExhausted" in str(e):
                st.warning("⚠️ Şu an çok fazla istek var. Lütfen 1 dakika bekleyip tekrar dene.")
            else:
                st.error("Bir hata oluştu.")
