import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pytz
from PIL import Image

st.set_page_config(page_title="Eymen AI", layout="centered")

# --- CSS: RESPONSIVE ---
st.markdown("""
    <style>
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] { display: none !important; }
    .stChatInput { max-width: 800px; margin: auto; }
    </style>
""", unsafe_allow_html=True)

# --- MODEL VE SİSTEM TALİMATI ---
def get_model():
    tr_tz = pytz.timezone('Europe/Istanbul')
    tr_time = datetime.now(tr_tz).strftime("%d-%m-%Y %H:%M:%S")
    genai.configure(api_key=st.secrets.get("KEY_1"))
    return genai.GenerativeModel('gemini-2.5-flash',
        system_instruction=f"""Sen Eymen AI'sin. Bugün: {tr_time}. 
        Matematik ve mantık problemlerini adım adım, analitik bir şekilde çöz. 
        Görsel analizlerinde tutarlı ol. Gereksiz tarih/saat bilgisi verme, sorulursa söyle.""")

# --- SOHBET YÖNETİMİ ---
if "sessions" not in st.session_state: st.session_state.sessions = {"Yeni Sohbet": []}
if "current_session" not in st.session_state: st.session_state.current_session = "Yeni Sohbet"

with st.sidebar:
    st.title("Sohbetler")
    if st.button("➕ Yeni Sohbet"):
        st.session_state.sessions["Yeni Sohbet"] = []
        st.session_state.current_session = "Yeni Sohbet"
    for name in list(st.session_state.sessions.keys()):
        if st.button(name): st.session_state.current_session = name

# --- ANA EKRAN ---
st.markdown('<div style="text-align: center;"><img src="https://i.hizliresim.com/gvewvtj.png" width="100"></div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Dosya Yükle", type=["jpg", "png"], label_visibility="collapsed")

messages = st.session_state.sessions[st.session_state.current_session]
for msg in messages:
    if isinstance(msg, dict):
        with st.chat_message(msg["role"]):
            if msg.get("type") == "image": st.image(msg["content"], use_container_width=True)
            else: st.markdown(msg["content"])

# --- İŞLEM MANTIĞI ---
if prompt := st.chat_input("Eymen AI'ye sor (Matematik, analiz, çizim...):"):
    
    # 1. Sohbet İsmini Belirle (Eğer ilk mesajsa)
    if len(messages) == 0:
        model = get_model()
        title_response = model.generate_content(f"Bu sohbetin konusu: '{prompt}'. Buna 3 kelimelik kısa bir başlık ver.")
        new_title = title_response.text.strip().replace('"', '')
        st.session_state.sessions[new_title] = st.session_state.sessions.pop("Yeni Sohbet")
        st.session_state.current_session = new_title
        messages = st.session_state.sessions[new_title]

    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = get_model()
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
        except: st.error("İşlem sırasında bir hata oluştu.")
    st.rerun()
