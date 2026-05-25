import streamlit as st
import google.generativeai as genai
import random
import time
from PIL import Image
import urllib.parse 
import streamlit.components.v1 as components 
import io

st.set_page_config(page_title="Eymen AI", page_icon="🧠", layout="centered")

# --- CSS VE TASARIM ---
st.markdown("""
    <style>
    .stChatInput { padding-bottom: 20px !important; }
    .header-box { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- SİSTEM AYARLARI ---
SYS_INST = "Sen Eymen AI'sin. Çok zeki, hızlı ve direkt bir asistansın."

def generate_with_retry(contents):
    keys = [st.secrets.get(f"KEY_{i}", "") for i in range(1, 11) if st.secrets.get(f"KEY_{i}", "").startswith("AIza")]
    if not keys: return "API Hatası."
    random.shuffle(keys)
    for k in keys:
        try:
            genai.configure(api_key=k)
            return genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYS_INST).generate_content(contents).text
        except: continue
    return "Bağlantı hatası."

# --- SOHBET YÖNETİMİ ---
if "sessions" not in st.session_state: st.session_state.sessions = {"Sohbet 1": []}
if "current_session" not in st.session_state: st.session_state.current_session = "Sohbet 1"

with st.sidebar:
    st.header("Sohbetler")
    if st.button("➕ Yeni"):
        name = f"Sohbet {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[name] = []
        st.session_state.current_session = name
        st.rerun()
    
    for name in list(st.session_state.sessions.keys()):
        if st.button(name, key=f"btn_{name}"): st.session_state.current_session = name; st.rerun()

    components.html("""
        <div style="background:#fff; padding:15px; border-radius:12px; border:1px solid #ddd; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
            <input type="text" id="val" style="width:100%; margin-bottom:10px; padding:8px; border:1px solid #ccc; border-radius:4px;" value="0">
            <button onclick="document.getElementById('val').value = eval(document.getElementById('val').value)" style="width:100%; background:#007bff; color:white; border:none; padding:8px; border-radius:4px;">Hesapla</button>
        </div>
    """, height=120)

# --- ROBUST SİDEBAR KAPATICI (GÜÇLENDİRİLMİŞ) ---
components.html("""
    <script>
        const parentDoc = window.parent.document;
        parentDoc.addEventListener('click', (e) => {
            const side = parentDoc.querySelector('[data-testid="stSidebar"]');
            const btn = parentDoc.querySelector('[data-testid="collapsedControl"]');
            if (side && btn && side.getAttribute('aria-expanded') === 'true') {
                if (!side.contains(e.target) && !btn.contains(e.target)) {
                    btn.click();
                }
            }
        }, true);
    </script>
""", height=0)

# --- MESAJLAŞMA ---
for msg in st.session_state.sessions[st.session_state.current_session]:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image": st.image(msg["content"])
        else: st.markdown(msg["content"])

if prompt := st.chat_input("Eymen AI'ye sor..."):
    st.session_state.sessions[st.session_state.current_session].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        # Görsel üretme mantığını daralttım (Sadece komut içerdiğinde çalışır)
        cmd_words = ["çiz", "oluştur", "yap", "üret", "getir", "hazırla", "göster"]
        has_cmd = any(word in prompt.lower() for word in cmd_words)
        has_img_target = "resim" in prompt.lower() or "görsel" in prompt.lower()
        
        if has_cmd and has_img_target:
            with st.spinner("Görsel oluşturuluyor..."):
                url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&seed={random.randint(1,99999)}"
                st.image(url)
                st.session_state.sessions[st.session_state.current_session].append({"role": "assistant", "content": url, "type": "image"})
        else:
            with st.spinner("Eymen AI düşünüyor..."):
                res = generate_with_retry(prompt)
                st.markdown(res)
                st.session_state.sessions[st.session_state.current_session].append({"role": "assistant", "content": res})
