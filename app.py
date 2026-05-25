import streamlit as st
import google.generativeai as genai
import random
import time
from PIL import Image
import urllib.parse
import streamlit.components.v1 as components
import io

st.set_page_config(page_title="Eymen AI", page_icon="🧠", layout="centered")

st.markdown("""<style>.stChatInput { padding-bottom: 20px !important; }</style>""", unsafe_allow_html=True)

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
    
    # Hesap Makinesi (İlk Tasarım + Karekök)
    components.html("""
        <div style="background:#f1f3f6; padding:10px; border-radius:10px; font-family:sans-serif;">
            <p style="font-weight:bold; margin:0 0 5px 0;">🧮 Hesap Makinesi</p>
            <input type="text" id="scr" style="width:100%; border:1px solid #ccc; border-radius:5px; padding:5px; margin-bottom:5px;" value="0">
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:5px;">
                <button onclick="document.getElementById('scr').value += '7'">7</button>
                <button onclick="document.getElementById('scr').value += '8'">8</button>
                <button onclick="document.getElementById('scr').value += '9'">9</button>
                <button onclick="document.getElementById('scr').value += '4'">4</button>
                <button onclick="document.getElementById('scr').value += '5'">5</button>
                <button onclick="document.getElementById('scr').value += '6'">6</button>
                <button onclick="document.getElementById('scr').value += '1'">1</button>
                <button onclick="document.getElementById('scr').value += '2'">2</button>
                <button onclick="document.getElementById('scr').value += '3'">3</button>
                <button onclick="document.getElementById('scr').value += '0'">0</button>
                <button onclick="document.getElementById('scr').value += '+'">+</button>
                <button onclick="document.getElementById('scr').value += '-'">-</button>
                <button onclick="document.getElementById('scr').value += '*'">×</button>
                <button onclick="document.getElementById('scr').value += '/'">÷</button>
                <button onclick="document.getElementById('scr').value = Math.sqrt(eval(document.getElementById('scr').value))">√</button>
                <button onclick="document.getElementById('scr').value = eval(document.getElementById('scr').value)" style="background:#4CAF50; color:white;">=</button>
                <button onclick="document.getElementById('scr').value = ''" style="grid-column: span 2;">C</button>
            </div>
        </div>
    """, height=280)

components.html("""<script>
const parentDoc = window.parent.document;
parentDoc.addEventListener('click', (e) => {
    const side = parentDoc.querySelector('[data-testid="stSidebar"]');
    const btn = parentDoc.querySelector('[data-testid="collapsedControl"]');
    if (side && btn && side.getAttribute('aria-expanded') === 'true') {
        if (!side.contains(e.target) && !btn.contains(e.target)) { btn.click(); }
    }
}, true);
</script>""", height=0)

for msg in st.session_state.sessions[st.session_state.current_session]:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image": st.image(msg["content"])
        else: st.markdown(msg["content"])

if prompt := st.chat_input("Eymen AI'ye birşeyler sor..."):
    st.session_state.sessions[st.session_state.current_session].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        if any(w in prompt.lower() for w in ["çiz", "oluştur", "yap", "üret"]) and ("resim" in prompt.lower() or "görsel" in prompt.lower()):
            with st.spinner("Oluşturuluyor..."):
                url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&seed={random.randint(1,99999)}"
                st.image(url)
                st.session_state.sessions[st.session_state.current_session].append({"role": "assistant", "content": url, "type": "image"})
        else:
            with st.spinner("Eymen AI düşünüyor..."):
                res = generate_with_retry(prompt)
                st.markdown(res)
                st.session_state.sessions[st.session_state.current_session].append({"role": "assistant", "content": res})
