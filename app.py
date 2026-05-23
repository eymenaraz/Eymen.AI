import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pytz
from PIL import Image

st.set_page_config(page_title="Eymen AI", layout="centered", initial_sidebar_state="collapsed")

# --- CSS: AVATARLARI SIFIRLA VE ARTIBUTONU TASARLA ---
st.markdown("""
    <style>
    /* Streamlit avatarını gizle */
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] { display: none !important; }
    
    /* Mobil uyumlu chat input düzeni */
    .stChatInputContainer { display: flex; align-items: center; }
    
    /* Artı Butonu Stili */
    .stFileUploader { width: 50px !important; margin-right: 10px; }
    
    /* Sohbetin en alta sabitlenmesi */
    .main { display: flex; flex-direction: column; }
    </style>
""", unsafe_allow_html=True)

# Başlık
st.markdown('<div style="text-align: center;"><h2>Eymen AI</h2></div>', unsafe_allow_html=True)

# --- MODEL ---
def get_model():
    tr_tz = pytz.timezone('Europe/Istanbul')
    tr_time = datetime.now(tr_tz).strftime("%d-%m-%Y %H:%M:%S")
    genai.configure(api_key=st.secrets.get("KEY_1"))
    return genai.GenerativeModel('gemini-2.5-flash', 
        system_instruction=f"Tarih: {tr_time}. Eymen AI'sin. Zeki, gerçekçi, analizci bir asistansın.")

if "messages" not in st.session_state: st.session_state.messages = []

# --- SOHBET GÖRÜNTÜLEME ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image":
            st.image(msg["content"], use_container_width=True)
        else:
            st.markdown(msg["content"])

# --- ALT PANEL (Artı Butonu + Input) ---
# Düzen: Bir sütun 50px (buton), diğeri kalan kısım (input)
row1, row2 = st.columns([0.15, 0.85])
with row1:
    uploaded_file = st.file_uploader("➕", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
with row2:
    prompt = st.chat_input("Eymen AI'ye sor veya çizdir...")

# --- İŞLEM MANTIĞI ---
if prompt:
    model = get_model()
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # 1. Fotoğraf Analizi
            if uploaded_file:
                img = Image.open(uploaded_file)
                st.image(img, use_container_width=True)
                response = model.generate_content([prompt, img])
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            # 2. Resim Oluşturma
            elif any(k in prompt.lower() for k in ["çiz", "oluştur", "generate"]):
                img_url = f"https://pollinations.ai/p/{prompt.replace('çiz', '').strip()}?width=512&height=512&nologo=true"
                st.image(img_url, use_container_width=True)
                st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
            
            # 3. Normal Sohbet
            else:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("Bir hata oluştu, lütfen tekrar dene.")
    st.rerun()
