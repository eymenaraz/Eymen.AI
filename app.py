import streamlit as st
import google.generativeai as genai

# Mobil uyumlu ayarlar
st.set_page_config(page_title="Eymen AI", layout="centered")

# API Anahtarı
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("API Anahtarı bulunamadı! Lütfen Settings > Secrets kısmından ekle.")
    st.stop()

# KİMLİK AYARI (Sadeleştirildi: Sadece isim belirtildi)
system_instruction = "Sen Eymen AI'sin. Kullanıcı sana Eymen AI, Eym veya Eymen şeklinde hitap edebilir. Kısa, net ve modern cevaplar ver."

# Model Tanımı
if "model" not in st.session_state:
    st.session_state.model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction=system_instruction
    )

st.title("⚡ Eymen AI")

# Sohbet Geçmişi
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları göster
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Giriş Kutusu
if prompt := st.chat_input("Bir şeyler yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            response = st.session_state.model.generate_content(prompt)
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            # Sayfanın en güncel halini göstermek için rerun
            st.rerun()
        except Exception as e:
            st.error("Bağlantı hatası.")
