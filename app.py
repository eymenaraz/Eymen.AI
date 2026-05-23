import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pytz
from PIL import Image

st.set_page_config(page_title="Eymen AI", layout="centered")

# --- CSS: MÜKEMMEL SABİTLİK ---
st.markdown("""
    <style>
    /* Alt paneli sabitle */
    .footer { position: fixed; bottom: 0; left: 0; width: 100%; padding: 10px; background: var(--background-color); z-index: 999; }
    /* Mesajları yukarı it */
    .main { padding-bottom: 120px; }
    /* Avatarları sil */
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] { display: none !important; }
    /* Upload butonunu küçült ve sığdır */
    .stFileUploader { width: 50px !important; margin: 0; }
    .stFileUploader label { display: none !important; }
    .stButton button { width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- MODEL ---
def get_model():
    tr_tz = pytz.timezone('Europe/Istanbul')
    tr_time = datetime.now(tr_tz).strftime("%d-%m-%Y %H:%M:%S")
    genai.configure(api_key=st.secrets.get("KEY_1"))
    return genai.GenerativeModel('gemini-2.5-flash',
        system_instruction=f"Tarih/Saat: {tr_time}. Eymen AI. Analitik, hızlı, gerçekçi asistansın.")

if "messages" not in st.session_state: st.session_state.messages = []

# Mesajları Göster
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image": st.image(msg["content"], use_container_width=True)
        else: st.markdown(msg["content"])

# --- SABİT ALT PANEL ---
st.markdown('<div class="footer">', unsafe_allow_html=True)
with st.container():
    col_up, col_in, col_btn = st.columns([0.15, 0.70, 0.15])
    
    with col_up:
        uploaded_file = st.file_uploader("➕", type=["jpg", "png"], label_visibility="collapsed")
    with col_in:
        prompt = st.text_input("", placeholder="Eymen AI'ye sor...", label_visibility="collapsed")
    with col_btn:
        send = st.button("➤")
st.markdown('</div>', unsafe_allow_html=True)

# --- İŞLEM ---
if send and prompt:
    model = get_model()
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            if uploaded_file:
                img = Image.open(uploaded_file)
                st.image(img, use_container_width=True)
                response = model.generate_content([prompt, img])
            elif "çiz" in prompt.lower() or "oluştur" in prompt.lower():
                img_url = f"https://pollinations.ai/p/{prompt}?width=512&height=512&nologo=true"
                st.image(img_url, use_container_width=True)
                st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
            else:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun()
        except: st.error("Hata oluştu.")
