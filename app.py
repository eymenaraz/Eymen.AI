import streamlit as st
import google.generativeai as genai
import random
import time
from PIL import Image
import urllib.parse
import streamlit.components.v1 as components
import io

st.set_page_config(page_title="Eymen AI", page_icon="🧠", layout="centered")

BOT_AVATAR = "https://i.hizliresim.com/gvewvtj.png"
USER_AVATAR = "👤"

st.markdown("""
    <style>
    .stChatInput { padding-bottom: env(safe-area-inset-bottom, 20px) !important; }
    .stApp { height: 100vh; overflow: auto; -webkit-overflow-scrolling: touch; }
    .header-box { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="header-box">
        <img src="{BOT_AVATAR}" width="50" style="border-radius: 10px;">
        <h2 style="margin: 0;">Eymen AI</h2>
    </div>
""", unsafe_allow_html=True)

SYS_INST = "Sen Eymen AI'sin. Her konuda uzmansın. Görsel ve video oluşturma yeteneğin var. Biri resim veya video isterse bunu mutlaka Pollinations kullanarak oluştur. Doğal, direkt ve çok zekisin."

def generate_with_retry(contents):
    valid_keys = [st.secrets.get(f"KEY_{i}", "") for i in range(1, 11) if st.secrets.get(f"KEY_{i}", "").startswith("AIza")]
    if not valid_keys: return "Sistem hatası: API anahtarı bulunamadı."
    random.shuffle(valid_keys)
    for api_key in valid_keys:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYS_INST)
            response = model.generate_content(contents)
            return response.text
        except: continue
    return "Hata: Kota doldu."

if "sessions" not in st.session_state: st.session_state.sessions = {"Sohbet 1": []}
if "current_session" not in st.session_state: st.session_state.current_session = "Sohbet 1"

with st.sidebar:
    st.header("Sohbet Geçmişi")
    if st.button("➕ Yeni Sohbet"):
        name = f"Sohbet {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[name] = []
        st.session_state.current_session = name
        st.rerun()
    
    for name in list(st.session_state.sessions.keys()):
        if st.button(name): st.session_state.current_session = name; st.rerun()
        
    st.subheader("🛠️ Akıllı Araç Kutusu")
    components.html("""
        <div style="background:#f1f3f6; padding:15px; border-radius:10px;">
            <input type="text" id="screen" style="width:100%;" value="0">
            <button onclick="document.getElementById('screen').value=eval(document.getElementById('screen').value)">Hesapla</button>
            <hr>
            <button onclick="let s=window.speechSynthesis; let msg=new SpeechSynthesisUtterance(document.getElementById('last_msg').innerText); s.speak(msg);">🔊 Oku</button>
        </div>
    """, height=200)

uploaded_file = st.file_uploader("Dosya Yükle", type=["jpg", "png", "pdf"])
messages = st.session_state.sessions[st.session_state.current_session]

for msg in messages:
    with st.chat_message(msg["role"], avatar=USER_AVATAR if msg["role"] == "user" else BOT_AVATAR):
        if msg.get("type") == "image": st.image(msg["content"])
        elif msg.get("type") == "video": st.video(msg["content"])
        else: st.markdown(msg["content"])

if prompt := st.chat_input("Eymen AI'ye sor..."):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR): st.markdown(prompt)
    
    with st.chat_message("assistant", avatar=BOT_AVATAR):
        if any(w in prompt.lower() for w in ["resim", "çiz", "görsel"]):
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
            st.image(url)
            messages.append({"role": "assistant", "content": url, "type": "image"})
        elif "video" in prompt.lower():
            url = f"https://pollinations.ai/p/{urllib.parse.quote(prompt)}?model=video"
            st.video(url)
            messages.append({"role": "assistant", "content": url, "type": "video"})
        else:
            ans = generate_with_retry([prompt])
            st.markdown(f'<div id="last_msg">{ans}</div>', unsafe_allow_html=True)
            messages.append({"role": "assistant", "content": ans})
