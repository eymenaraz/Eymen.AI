import streamlit as st
import google.generativeai as genai
import time

# Sayfa ayarları
st.set_page_config(page_title="Eymen AI", layout="centered", page_icon="⚡")

# Özel CSS ile arayüzü şıklaştır (Figma gerekmez, doğrudan modern tasarım)
st.markdown("""
    <style>
    .stChatInput {background-color: #1e1e1e;}
    .stChatMessage {border-radius: 15px; padding: 10px;}
    </style>
""", unsafe_allow_html=True)

# API Anahtarları
keys = [st.secrets["KEY_1"], st.secrets["KEY_2"], st.secrets["KEY_3"]]

def get_model():
    # 2.5 veya 2.0 modelini burada belirtiyoruz
    model_name = 'gemini-3.0-flash' 
    genai.configure(api_key=keys[0]) # İlk anahtarla başla
    return genai.GenerativeModel(
        model_name=model_name,
        system_instruction="""Sen Eymen AI'sin. 
        - Kendini her zaman Eymen AI olarak tanıt.
        - Kullanıcının dilinde anında cevap ver.
        - Çok hızlı, enerjik ve modern bir tarzın olsun.
        - Cevapların net ve özlü olsun."""
    )

st.title("⚡ Eymen AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesaj geçmişini göster
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Giriş kutusu
if prompt := st.chat_input("Eymen AI'ye bir şey sor..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            model = get_model()
            # Yazma efekti (üç nokta ile)
            message_placeholder.markdown("Eymen AI yazıyor... ▌")
            
            response = model.generate_content(prompt, stream=True)
            
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error("Bir bağlantı hatası oluştu, lütfen tekrar dene.")
            # Hata durumunda loga düşmesi için
            st.write(f"Hata detayları: {str(e)}")
