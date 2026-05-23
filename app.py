import streamlit as st
import google.generativeai as genai
import random
from datetime import datetime
import pytz
from PIL import Image

st.set_page_config(page_title="Eymen AI", layout="centered")

# --- CSS: MODERN MOBİL UYUM ---
st.markdown("""
    <style>
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] { display: none !important; }
    .stChatInput { max-width: 800px; margin: auto; }
    </style>
""", unsafe_allow_html=True)

# --- API ROTASYON MANTIĞI ---
def get_model():
    # secrets içindeki KEY_1'den KEY_10'a kadar olanları çek
    keys = [st.secrets[f"KEY_{i}"] for i in range(1, 11)]
    genai.configure(api_key=random.choice(keys))
    
    tr_tz = pytz.timezone('Europe/Istanbul')
    tr_time = datetime.now(tr_tz).strftime("%d-%m-%Y %H:%M:%S")
    
    return genai.GenerativeModel('gemini-2.5-flash',
        system_instruction=f"""Bugün: {tr_time}. Sen Eymen AI, LGS hazırlık sürecinde öğrencisin.
        Matematik, geometri (Pisagor, eğim, cisimler) konularında uzmansın. 
        Analitik düşünürsün, soruları adım adım çözersin. 
        Gereksiz konuşma, öz ve doğru bilgi ver.""")

# --- SOHBET YÖNETİMİ ---
if "sessions" not in st.session_state: st.session_state.sessions = {"Yeni Sohbet": []}
if "current_session" not in st.session_state: st.session_state.current_session = "Yeni Sohbet"

with st.sidebar:
    st.header("Sohbetlerin")
    if st.button("➕ Yeni Sohbet"):
        st.session_state.sessions["Yeni Sohbet"] = []
        st.session_state.current_session = "Yeni Sohbet"
    for name in list(st.session_state.sessions.keys()):
        if st.button(name): st.session_state.current_session = name

# --- ANA EKRAN VE YÜKLEME ---
st.markdown('<div style="text-align: center;"><h1>Eymen AI</h1></div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Dosya Yükle", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

messages = st.session_state.sessions[st.session_state.current_session]
for msg in messages:
    if isinstance(msg, dict):
        with st.chat_message(msg["role"]):
            if msg.get("type") == "image": st.image(msg["content"], use_container_width=True)
            else: st.markdown(msg["content"])

# --- İŞLEM MANTIĞI ---
if prompt := st.chat_input("LGS sorusu sor, analiz et veya çizdir..."):
    # Başlıklandırma
    if st.session_state.current_session == "Yeni Sohbet" and len(messages) == 0:
        new_title = prompt[:20].strip() + "..."
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
            elif "çiz" in prompt.lower() or "oluştur" in prompt.lower():
                img_url = f"https://pollinations.ai/p/{prompt}?width=512&height=512&nologo=true"
                st.image(img_url, use_container_width=True)
                messages.append({"role": "assistant", "content": img_url, "type": "image"})
                st.rerun()
            else:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                messages.append({"role": "assistant", "content": response.text})
            st.rerun()
        except Exception:
            st.error("API limitlerine ulaşıldı veya bir hata oluştu. Lütfen tekrar dene.")
