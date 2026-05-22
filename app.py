import streamlit as st
import google.generativeai as genai
import time

st.set_page_config(page_title="Eymen AI", layout="centered")

# API Anahtarı
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception:
    st.error("API Anahtarı hatası!")
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
        # Kota Yönetimi: İstek atarken hata alırsa bekle ve tekrar dene
        for attempt in range(3): # 3 kez tekrar deneme hakkı
            try:
                response = model.generate_content(prompt)
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                break 
            except Exception as e:
                if "ResourceExhausted" in str(e):
                    time.sleep(2) # 2 saniye bekle ve tekrar dene
                    continue 
                else:
                    st.error("Bağlantı hatası.")
                    break
