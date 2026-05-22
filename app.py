import streamlit as st
import google.generativeai as genai

# Mobil uyumlu geniş ekran ayarı
st.set_page_config(page_title="Eymen AI", layout="centered")

# API Anahtarı (Secrets'tan al)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("API Anahtarı bulunamadı! Lütfen Secrets kısmına ekle.")
    st.stop()

# Model Tanımı
if "model" not in st.session_state:
    st.session_state.model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction="Sen Eymen AI'sin. Eymen tarafından geliştirildin. Kullanıcı sana Eymen AI, Eym veya Eymen diyebilir."
    )

# Başlık
st.title("⚡ Eymen AI")

# Sohbet Geçmişi
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları Göster
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Mobil ve PC Uyumlu Giriş Kutusu (Otomatik Alt Kısma Yerleşir)
if prompt := st.chat_input("Mesajını yaz ve gönder..."):
    # Kullanıcı mesajı
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Yapay Zeka Yanıtı
    with st.chat_message("assistant"):
        try:
            response = st.session_state.model.generate_content(prompt)
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            # Yanıt gelince sayfayı yenilemek yerine sadece mesajı ekle
            st.rerun() 
        except Exception as e:
            st.error("Bir bağlantı hatası oluştu.")
