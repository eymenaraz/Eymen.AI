import streamlit as st
import google.generativeai as genai

# Mobil tarayıcılar için en hafif yapılandırma
st.set_page_config(page_title="Eymen AI", layout="centered", initial_sidebar_state="collapsed")

# API Anahtarı
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("API Anahtarı eksik!")
    st.stop()

# Model: Hız için system_instruction ile başlatıyoruz
if "model" not in st.session_state:
    st.session_state.model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction="Sen Eymen AI'sin. Kısa, net, hızlı ve modern cevaplar ver. Gereksiz uzun cümlelerden kaçın."
    )

st.title("⚡ Eymen AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesaj geçmişini hızlıca yükle
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Giriş Kutusu - st.rerun() kaldırıldı (Hata almanı engeller)
if prompt := st.chat_input("Eymen AI'ye sor..."):
    # Kullanıcı mesajını anında ekrana bas
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Yanıtı al
    with st.chat_message("assistant"):
        try:
            # Buradaki stream=True özelliği, yapay zeka yazar yazmaz ekrana basar
            # Bu sayede "çok düşünüyor" hissinden kurtulursun
            response = st.session_state.model.generate_content(prompt, stream=True)
            placeholder = st.empty()
            full_text = ""
            for chunk in response:
                full_text += chunk.text
                placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)
            
            st.session_state.messages.append({"role": "assistant", "content": full_text})
        except Exception:
            st.error("Bağlantı zaman aşımı! İnternetini kontrol et.")
