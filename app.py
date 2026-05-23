import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pytz
from PIL import Image

st.set_page_config(page_title="Eymen AI", layout="wide")

# --- CSS: AVATARLARI YOK ET, CHAT'İ KİLİTLE ---
st.markdown("""
    <style>
    /* Avatar Gizleme */
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] { display: none !important; }
    
    /* Mesaj alanı yüksekliğini ayarla ve scroll'u zorla */
    .stApp { display: flex; flex-direction: column; height: 100vh; }
    .stChatFloatingInputContainer { background-color: transparent !important; }
    
    /* Input kutusunun altına boşluk bırak */
    .main { padding-bottom: 100px; }
    </style>
""", unsafe_allow_html=True)

# --- MODEL ---
def get_model():
    tr_tz = pytz.timezone('Europe/Istanbul')
    tr_time = datetime.now(tr_tz).strftime("%d-%m-%Y %H:%M:%S")
    genai.configure(api_key=st.secrets.get("KEY_1"))
    return genai.GenerativeModel('gemini-2.5-flash', 
        system_instruction=f"Tarih/Saat: {tr_time}. Eymen AI'sin. Sadece sorulduğunda bilgi ver, gereksiz konuşma. Zeki ve analitik ol.")

if "messages" not in st.session_state: st.session_state.messages = []

# --- SOHBETİ SCROLL EDİLEBİLİR ALAN ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image": st.image(msg["content"], use_container_width=True)
        else: st.markdown(msg["content"])

# --- ALT PANEL: İNPUT İÇİNDE ARTI BUTONU ---
# Kolon mantığı ile input'un yanına + butonu koyuyoruz
col1, col2 = st.columns([0.1, 0.9])

with col1:
    # Dosya yükleme butonunu küçülttük ve "➕" ikonuna dönüştürdük
    uploaded_file = st.file_uploader("➕", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

with col2:
    prompt = st.chat_input("Eymen AI'ye sor...")

# --- İŞLEM MANTIĞI ---
if prompt:
    model = get_model()
    st.session_state.messages.append({"role": "user", "content": prompt})
    
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
                img_url = f"https://pollinations.ai/p/{prompt.replace('çiz', '').strip()}?width=512&height=512&nologo=true"
                st.image(img_url, use_container_width=True)
                st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
            
            else:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception:
            st.error("Bir hata oluştu.")
    st.rerun()
