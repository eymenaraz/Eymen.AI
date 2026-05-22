import streamlit as st
import google.generativeai as genai
import random

st.set_page_config(page_title="Eymen AI", layout="centered")

# API Anahtarlarını tanımla
def get_model():
    # Secrets'taki isimleri burada çağırıyoruz
    keys = [st.secrets["KEY_1"], st.secrets["KEY_2"], st.secrets["KEY_3"]]
    
    # Rastgele bir anahtar seç
    key = random.choice(keys)
    genai.configure(api_key=key)
    return genai.GenerativeModel('gemini-2.5-flash')

st.title("⚡ Eymen AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları göster
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Eymen AI'ye sor..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            # Modeli çağır
            model = get_model()
            response = model.generate_content(prompt)
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            if "ResourceExhausted" in str(e):
                st.error("⚠️ Kotan doldu! Lütfen sayfayı 1-2 dakika sonra yenile.")
            else:
                st.error("Bir hata oluştu, lütfen tekrar dene.")
