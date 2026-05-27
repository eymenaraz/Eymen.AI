import streamlit as st
import json
import os
import urllib.parse
import random
import string
import math
import google.generativeai as genai

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Eymen AI V2 - Premium",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS VE STYLING ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f8fafc; }
    .tts-button { background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%); color: white; border: none; border-radius: 8px; padding: 6px 12px; font-size: 0.8rem; cursor: pointer; margin-top: 5px; }
    .user-bubble { background: #3b82f6; color: white; padding: 12px; border-radius: 15px; margin: 5px 0 5px auto; max-width: 80%; width: fit-content; }
    .ai-bubble { background: #1e293b; color: #e2e8f0; padding: 12px; border-radius: 15px; margin: 5px auto 5px 0; max-width: 80%; width: fit-content; border: 1px solid #334155; }
</style>
""", unsafe_allow_html=True)

# --- MODEL VE API ---
@st.cache_resource
def get_model():
    for i in range(1, 11):
        key = st.secrets.get(f"KEY_{i}")
        if key:
            try:
                genai.configure(api_key=key)
                return genai.GenerativeModel("gemini-2.5-flash")
            except: continue
    return None

model = get_model()

# --- SİSTEM ---
if "messages" not in st.session_state: st.session_state.messages = []

# Mesajları Ekrana Bas
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
        if "image" in msg: st.image(msg["image"], use_container_width=True)
        
        # SESLİ OKUMA TETİKLEYİCİ
        safe_text = json.dumps(msg["content"])
        st.markdown(f'<button class="tts-button" onclick="window.speechSynthesis.speak(new SpeechSynthesisUtterance({safe_text}))">🔊 Sesli Dinle</button>', unsafe_allow_html=True)

# --- SOHBET VE FOTOĞRAF MOTORU ---
if user_query := st.chat_input("Eymen AI V2'ye yazın..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # FOTOĞRAF KONTROLÜ
    triggers = ["görsel oluştur", "çiz", "hayal et", "resim", "fotoğraf"]
    if any(t in user_query.lower() for t in triggers):
        # API limitini aşmamak için statik ama dinamik parametreli link
        seed = random.randint(1000, 9999)
        img_url = f"https://pollinations.ai/p/{urllib.parse.quote(user_query)}?width=1024&height=1024&seed={seed}&nologo=true"
        st.session_state.messages.append({"role": "assistant", "content": "İşte istediğin görsel:", "image": img_url})
    else:
        # GEMINI YANITI
        if model:
            response = model.generate_content(user_query)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        else:
            st.error("API Anahtarı bulunamadı.")
    st.rerun()

# --- YAN MENÜ ARAÇLARI ---
with st.sidebar:
    st.title("🧰 Araç Kutusu")
    if st.button("🗑️ Sohbeti Sil"): st.session_state.messages = []; st.rerun()
    
    with st.expander("🔑 QR Kod Üretici"):
        txt = st.text_input("Metin/Link:")
        if st.button("Oluştur"): st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(txt)}")

    with st.expander("⏳ Pomodoro"):
        timer = st.slider("Dakika", 1, 60, 25)
        if st.button("Başlat"): st.info(f"{timer} dakikalık çalışma başladı!")
