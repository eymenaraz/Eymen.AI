import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pytz
from PIL import Image

# Sayfa ayarları
st.set_page_config(page_title="Eymen AI", layout="centered")

# --- CSS: MÜKEMMEL MODERN TASARIM ---
st.markdown("""
    <style>
    /* Avatarları ve gereksiz Streamlit yazılarını sil */
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"], .stAppDeployButton { display: none !important; }
    
    /* Input kutusunu ekranın en altına sabitle */
    .stChatInput { position: fixed; bottom: 0; left: 0; width: 100%; padding: 10px; z-index: 1000; }
    
    /* File uploader (Artı butonu) optimizasyonu */
    .stFileUploader { width: 45px !important; margin-right: 10px; }
    .stFileUploader label, .stFileUploader div[data-testid="stCaptionContainer"] { display: none !important; }
    .stFileUploader button { height: 40px !important; }
    
    /* Sohbet alanı için alt boşluk */
    .main { padding-bottom: 120px; }
    </style>
""", unsafe_allow_html=True)

# --- MODEL AYARLARI ---
def get_model():
    tr_tz = pytz.timezone('Europe/Istanbul')
    tr_time = datetime.now(tr_tz).strftime("%d-%m-%Y %H:%M:%S")
    genai.configure(api_key=st.secrets.get("KEY_1"))
    return genai.GenerativeModel('gemini-2.5-flash',
        system_instruction=f"Tarih/Saat: {tr_time}. Eymen AI. Gereksiz bilgi verme. Analitik, zeki, hızlı, gerçekçi asistansın.")

if "messages" not in st.session_state: st.session_state.messages = []

# --- ARAYÜZ ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image": st.image(msg["content"], use_container_width=True)
        else: st.markdown(msg["content"])

# --- SABİT ALT PANEL (Artı + Input) ---
col1, col2 = st.columns([0.15, 0.85])
with col1:
    uploaded_file = st.file_uploader("➕", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
with col2:
    prompt = st.chat_input("Eymen AI'ye sor...")

# --- İŞLEM MANTIĞI ---
if prompt:
    model = get_model()
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Kullanıcı mesajını göster ve sayfayı en alta al
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            if uploaded_file:
                img = Image.open(uploaded_file)
                st.image(img, use_container_width=True)
                response = model.generate_content([prompt, img])
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            elif any(k in prompt.lower() for k in ["çiz", "oluştur", "generate"]):
                img_url = f"https://pollinations.ai/p/{prompt}?width=512&height=512&nologo=true"
                st.image(img_url, use_container_width=True)
                st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
            else:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception:
            st.error("Bir hata oluştu.")
    st.rerun()
