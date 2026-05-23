import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pytz
from PIL import Image

st.set_page_config(page_title="Eymen AI", layout="centered")

# --- CSS: ŞIK TASARIM VE SABİT ALT PANEL ---
st.markdown("""
    <style>
    /* Avatar gizleme */
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] { display: none !important; }
    
    /* Alt panel sabitleme */
    .stApp { padding-bottom: 80px; }
    .fixed-bottom { position: fixed; bottom: 0; width: 100%; padding: 10px; background: white; z-index: 100; }
    </style>
""", unsafe_allow_html=True)

# --- MODEL AYARLARI ---
def get_model():
    tr_tz = pytz.timezone('Europe/Istanbul')
    tr_time = datetime.now(tr_tz).strftime("%d-%m-%Y %H:%M:%S")
    genai.configure(api_key=st.secrets.get("KEY_1"))
    return genai.GenerativeModel('gemini-2.5-flash', 
        system_instruction=f"Tarih/Saat: {tr_time}. Sen Eymen AI. Gereksiz yere tarih saat bilgisi verme, sadece sorulduğunda ver. Analitik, zeki, hızlı bir asistansın.")

if "messages" not in st.session_state: st.session_state.messages = []

# Sohbeti Görüntüle
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image": st.image(msg["content"], use_container_width=True)
        else: st.markdown(msg["content"])

# --- SABİT ALT PANEL ---
with st.container():
    st.markdown('<div class="fixed-bottom">', unsafe_allow_html=True)
    
    # + Butonu ve Dosya Yükleme (Sadece tıkladığında açılır)
    with st.expander("➕"):
        uploaded_file = st.file_uploader("Dosya/Fotoğraf seç:", type=["jpg", "png", "jpeg"])
    
    prompt = st.chat_input("Eymen AI'ye sor veya çizdir...")
    st.markdown('</div>', unsafe_allow_html=True)

# --- İŞLEM MANTIĞI ---
if prompt:
    model = get_model()
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. Fotoğraf Analizi
        if uploaded_file:
            img = Image.open(uploaded_file)
            st.image(img, use_container_width=True)
            response = model.generate_content([prompt, img])
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        
        # 2. Resim Oluşturma
        elif any(k in prompt.lower() for k in ["çiz", "oluştur", "generate"]):
            img_url = f"https://pollinations.ai/p/{prompt.replace('çiz', '').strip()}?width=512&height=512&nologo=true"
            st.image(img_url, use_container_width=True)
            st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
        
        # 3. Normal Sohbet
        else:
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
    st.rerun()
