import streamlit as st
import google.generativeai as genai
import random

st.set_page_config(page_title="Eymen AI", layout="centered")

# API Anahtarlarını buraya liste halinde yaz
API_KEYS = [
    st.secrets["AIzaSyCgMHSn5X2jIRw6Xth_kTQUrzy7LaTwyHE"],
    st.secrets["AIzaSyARKOES_6-qLyp9lB6V01Y0SAQ_Rz3xQoM"],
    st.secrets["AIzaSyAw2q-ZpGwh7yS52EzKdqd2LXyLSslVq4o"]
]

def get_model():
    """Rastgele bir API anahtarı seçer ve modeli başlatır."""
    key = random.choice(API_KEYS)
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
            model = get_model() # Her mesajda yeni bir anahtar seçer
            response = model.generate_content(prompt)
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            if "ResourceExhausted" in str(e):
                st.error("⚠️ Kotan doldu, lütfen biraz bekle.")
            else:
                st.error("Bir hata oluştu.")
