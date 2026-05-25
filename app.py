import streamlit as st
import google.generativeai as genai
import random
import time
from PIL import Image
import urllib.parse 
import streamlit.components.v1 as components 
import io

st.set_page_config(page_title="Eymen AI", page_icon="🧠", layout="centered")

# --- AVATARLAR VE LOGO ---
BOT_AVATAR = "https://i.hizliresim.com/gvewvtj.png"
USER_AVATAR = "👤"

# --- CSS ---
st.markdown("""
    <style>
    .stChatInput { padding-bottom: env(safe-area-inset-bottom, 20px) !important; }
    .stApp { transform: translate3d(0,0,0); }
    .header-box { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
    .block-container { padding-top: 2rem !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="header-box">
        <img src="{BOT_AVATAR}" width="50" style="border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
        <h2 style="margin: 0;">Eymen AI</h2>
    </div>
""", unsafe_allow_html=True)

# --- SİSTEM ---
SYS_INST = "Sen Eymen AI'sin. Çok zeki, her konuda uzman bir asistansın. Doğal, direkt ve yardımcı ol."

def generate_with_retry(contents):
    valid_keys = [st.secrets.get(f"KEY_{i}", "") for i in range(1, 11) if st.secrets.get(f"KEY_{i}", "").startswith("AIza")]
    if not valid_keys: return "SİSTEM HATASI: API anahtarı bulunamadı."
    random.shuffle(valid_keys)
    for api_key in valid_keys:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYS_INST)
            return model.generate_content(contents).text
        except: continue
    return "Hata: Bağlantı kurulamadı."

# --- SOHBET ---
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
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(name, key=f"btn_{name}"): 
                st.session_state.current_session = name
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{name}"):
                del st.session_state.sessions[name]
                if not st.session_state.sessions: st.session_state.sessions = {"Sohbet 1": []}
                st.session_state.current_session = list(st.session_state.sessions.keys())[0]
                st.rerun()
    
    st.markdown("---")
    st.subheader("📥 İndir")
    current_msgs = st.session_state.sessions[st.session_state.current_session]
    if current_msgs:
        txt = "\n\n".join([f"{m['role']}: {m['content']}" for m in current_msgs if m.get("type") != "image"])
        st.download_button("Bu Sohbeti İndir", txt.encode('utf-8'), "notlar.txt")

    # --- ARAÇ KUTUSU ---
    components.html("""
        <div style="background:#f1f3f6; padding:10px; border-radius:10px; font-family:sans-serif;">
            <p style="font-weight:bold; margin:0;">🧮 Hesap Makinesi</p>
            <input type="text" id="scr" style="width:100%;" disabled value="0">
            <button onclick="document.getElementById('scr').value = eval(document.getElementById('scr').value)">=</button>
            <button onclick="document.getElementById('scr').value = ''">C</button>
        </div>
    """, height=150)

# --- DIŞARI TIKLAMA KAPATMA ---
components.html("""
    <script>
        window.parent.document.addEventListener('click', (e) => {
            const side = window.parent.document.querySelector('[data-testid="stSidebar"]');
            const btn = window.parent.document.querySelector('[data-testid="collapsedControl"]');
            if (side && !side.contains(e.target) && !btn.contains(e.target) && side.getAttribute('aria-expanded') === 'true') {
                btn.click();
            }
        });
    </script>
""", height=0)

# --- İŞLEMLER ---
uploaded_file = st.file_uploader("Dosya Yükle")
messages = st.session_state.sessions[st.session_state.current_session]
for msg in messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Mesaj yaz..."):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        res = generate_with_retry(prompt)
        st.markdown(res)
        messages.append({"role": "assistant", "content": res})
