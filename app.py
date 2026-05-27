import streamlit as st
import json, urllib.parse, random, string, math
import google.generativeai as genai
from google.api_core import exceptions

st.set_page_config(page_title="Eymen AI V2", page_icon="🤖", layout="wide")

# --- CSS VE LOGO ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f8fafc; }
    .brand { font-size: 2.5rem; font-weight: 900; color: #38bdf8; text-align: center; text-shadow: 0 0 10px #38bdf8; }
    .user-bubble { background: #3b82f6; color: white; padding: 12px; border-radius: 15px; margin: 5px 0; }
    .ai-bubble { background: #1e293b; color: #e2e8f0; padding: 12px; border-radius: 15px; margin: 5px 0; border: 1px solid #334155; }
</style>
<div class="brand">EYMEN AI V2</div>
""", unsafe_allow_html=True)

# --- API YÖNETİMİ ---
def get_model():
    keys = [st.secrets.get(f"KEY_{i}") for i in range(1, 11) if st.secrets.get(f"KEY_{i}")]
    random.shuffle(keys)
    for key in keys:
        try:
            genai.configure(api_key=key)
            return genai.GenerativeModel("gemini-2.5-flash")
        except: continue
    return None

# --- SOHBET YÖNETİMİ ---
if "chats" not in st.session_state: st.session_state.chats = {"Sohbet 1": []}
if "current_chat" not in st.session_state: st.session_state.current_chat = "Sohbet 1"

# --- YAN MENÜ ---
with st.sidebar:
    st.header("🗂️ Sohbetlerin")
    # Yeni Sohbet Ekle
    if st.button("➕ Yeni Sohbet"):
        new_name = f"Sohbet {len(st.session_state.chats) + 1}"
        st.session_state.chats[new_name] = []
    
    # Sohbet Listesi ve Silme
    for chat_name in list(st.session_state.chats.keys()):
        cols = st.columns([3, 1])
        if cols[0].button(chat_name, key=f"btn_{chat_name}"):
            st.session_state.current_chat = chat_name
        if cols[1].button("🗑️", key=f"del_{chat_name}"):
            del st.session_state.chats[chat_name]
            if st.session_state.current_chat == chat_name: st.session_state.current_chat = list(st.session_state.chats.keys())[0]
            st.rerun()

    st.write("---")
    # ARAÇLAR
    with st.expander("🧮 Hesap Makinesi"):
        if "calc" not in st.session_state: st.session_state.calc = ""
        st.text(st.session_state.calc)
        if st.button("√x"): st.session_state.calc = str(math.sqrt(float(eval(st.session_state.calc)))); st.rerun()
        if st.button("C"): st.session_state.calc = ""

    with st.expander("🪄 QR Kod"):
        txt = st.text_input("Metin:")
        if st.button("Oluştur"): st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(txt)}")

    with st.expander("🔑 Şifre Üretici"):
        n = st.slider("Hane", 4, 32, 12)
        if st.button("Üret"): st.code("".join(random.choices(string.ascii_letters + string.digits, k=n)))

# --- SOHBET EKRANI ---
messages = st.session_state.chats[st.session_state.current_chat]
for msg in messages:
    if msg["role"] == "user": st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else: 
        st.markdown(f'<div class="ai-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
        if "image" in msg: st.image(msg["image"])

if user_query := st.chat_input("Mesajın..."):
    messages.append({"role": "user", "content": user_query})
    triggers = ["görsel oluştur", "çiz", "hayal et", "resim", "fotoğraf"]
    if any(t in user_query.lower() for t in triggers):
        url = f"https://pollinations.ai/p/{urllib.parse.quote(user_query)}?width=1024&height=1024&seed={random.randint(1,99999)}&nologo=true"
        messages.append({"role": "assistant", "content": "Görsel:", "image": url})
    else:
        model = get_model()
        if model:
            res = model.generate_content(user_query)
            messages.append({"role": "assistant", "content": res.text})
    st.rerun()
