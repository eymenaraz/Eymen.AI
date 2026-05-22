import streamlit as st
import google.generativeai as genai

# Sayfa Yapılandırması
st.set_page_config(page_title="Eymen AI", page_icon="⚡", layout="centered")

# CSS: Modern, minimalist ve sisteme (Dark/Light) tam uyumlu
st.markdown("""
    <style>
    /* Chat giriş kutusu için sabit konum */
    .stChatInput { position: fixed; bottom: 20px; }
    
    /* Mesaj kartlarını sistem rengine uyumlu yap */
    [data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 10px;
    }
    
    /* Başlık stili */
    .title-text {
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 20px;
        color: inherit;
    }
    </style>
    """, unsafe_allow_html=True)

# Başlık
st.markdown("<div class='title-text'>⚡ Eymen AI</div>", unsafe_allow_html=True)

# API Bağlantısı (Secrets üzerinden)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("API Anahtarı hatası! Lütfen Streamlit ayarlarından 'GOOGLE_API_KEY' secret'ını kontrol et.")
    st.stop()

# Model Tanımı
if "model" not in st.session_state:
    st.session_state.model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction="Sen Eymen AI'sin. Modern, zeki, hızlı ve nazik bir asistansın. Kullanıcı sana Eymen AI, Eym veya Eymen diyebilir."
    )

# Sohbet Geçmişi
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları göster
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Sohbet girişi (En altta sabit)
if prompt := st.chat_input("Mesajını yaz, Eymen AI yanıtlasın..."):
    # Kullanıcı mesajı
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # AI Yanıtı
    with st.chat_message("assistant"):
        with st.spinner("Düşünüyor..."):
            try:
                response = st.session_state.model.generate_content(prompt)
                full_response = response.text
                st.write(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error("Bağlantı hatası: Anahtarını ve internetini kontrol et.")
