import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pytz
from PIL import Image

st.set_page_config(page_title="Eymen AI", layout="centered")

# --- CSS: SABİT TASARIM ---
st.markdown("""
    <style>
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] { display: none !important; }
    /* Alt paneli sabitle */
    .stChatInput { position: fixed; bottom: 20px; z-index: 1000; }
    /* Logonun altındaki yükleme alanı */
    .upload-area { margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- YENİ SOHBET / GEÇMİŞ YÖNETİMİ ---
if "sessions" not in st.session_state: st.session_state.sessions = {"Sohbet 1": []}
if "current_session" not in st.session_state: st.session_state.current_session = "Sohbet 1"

with st.sidebar:
    st.title("Eymen AI Sohbetler")
    if st.button("➕ Yeni Sohbet"):
        new_name = f"Sohbet {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[new_name] = []
        st.session_state.current_session = new_name
    
    for session_name in st.session_state.sessions:
        if st.button(session_name):
            st.session_state.current_session = session_name

# --- ANA EKRAN ---
st.markdown('<div style="text-align: center;"><img src="https://i.hizliresim.com/gvewvtj.png" width="150"></div>', unsafe_allow_html=True)

# Upload butonu logonun altında
with st.container():
    uploaded_file = st.file_uploader("Dosya Yükle", type=["jpg", "png"], label_visibility="collapsed")

# Sohbeti Görüntüle
messages = st.session_state.sessions[st.session_state.current_session]
for msg in messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image": st.image(msg["content"], use_container_width=True)
        else: st.markdown(msg["content"])

# --- İŞLEM MANTIĞI ---
if prompt := st.chat_input("Eymen AI'ye sor..."):
    # Sohbet ismini güncelleme (Basitçe ilk mesajdan başlık üret)
    if len(messages) == 0:
        st.session_state.sessions[st.session_state.current_session] = [f"{prompt[:15]}..."]
    
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        genai.configure(api_key=st.secrets.get("KEY_1"))
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        try:
            if uploaded_file:
                img = Image.open(uploaded_file)
                st.image(img, use_container_width=True)
                response = model.generate_content([prompt, img])
            elif "çiz" in prompt.lower():
                img_url = f"https://pollinations.ai/p/{prompt}?width=512&height=512&nologo=true"
                st.image(img_url, use_container_width=True)
                messages.append({"role": "assistant", "content": img_url, "type": "image"})
                st.rerun()
            else:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                messages.append({"role": "assistant", "content": response.text})
        except: st.error("Hata oluştu.")
    st.rerun()
