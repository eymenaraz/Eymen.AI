import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pytz
from PIL import Image

# --- AYARLAR ---
LOGO_URL = "https://i.hizliresim.com/gvewvtj.png"
LIGHT_AVATAR = "https://i.hizliresim.com/8w6lqzo.png"
DARK_AVATAR = "https://i.hizliresim.com/bsfo6dy.png"

st.set_page_config(page_title="Eymen AI", layout="centered", initial_sidebar_state="collapsed")

# --- CSS VE TEMA ---
theme_base = st.get_option("theme.base")
avatar_to_use = DARK_AVATAR if theme_base == "dark" else LIGHT_AVATAR
st.markdown("""
    <style>
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown(f'<div style="text-align: center; margin-bottom: 25px;"><img src="{LOGO_URL}" width="250"></div>', unsafe_allow_html=True)

# --- MODEL AYARLARI ---
def get_model():
    tr_tz = pytz.timezone('Europe/Istanbul')
    tr_time = datetime.now(tr_tz).strftime("%d-%m-%Y %H:%M:%S")
    
    key = st.secrets.get("KEY_1")
    genai.configure(api_key=key)
    return genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction=f"Sen Eymen AI'sin. Tarih: {tr_time}. Hem metin hem görsel analiz yeteneğine sahip bir asistansın. Matematik problemlerini çözebilir, fotoğrafları inceleyebilirsin."
    )

if "messages" not in st.session_state: st.session_state.messages = []

# --- DOSYA YÜKLEME ---
uploaded_file = st.file_uploader("Bir fotoğraf yükle (Matematik/Analiz):", type=["jpg", "jpeg", "png"])

# --- MESAJLAŞMA VE ANALİZ ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=avatar_to_use if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])

if prompt := st.chat_input("Eymen AI'ye sor (Görsel oluştur veya yüklediğin görseli analiz et..."):
    model = get_model()
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    # 1. Fotoğraf Analizi (Matematik vb.)
    if uploaded_file:
        img = Image.open(uploaded_file)
        with st.chat_message("assistant", avatar=avatar_to_use):
            response = model.generate_content([prompt, img])
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

    # 2. Görsel Oluşturma
    elif any(keyword in prompt.lower() for keyword in ["çiz", "oluştur", "generate"]):
        with st.chat_message("assistant", avatar=avatar_to_use):
            img_prompt = prompt.replace("çiz", "").replace("oluştur", "").replace("generate", "").strip()
            img_url = f"https://pollinations.ai/p/{img_prompt}?width=512&height=512&nologo=true&seed=1"
            st.markdown(f'<img src="{img_url}" style="width:100%; border-radius:10px;">', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": f"![Görsel]({img_url})"})
    
    # 3. Normal Sohbet
    else:
        with st.chat_message("assistant", avatar=avatar_to_use):
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
