import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pytz
from PIL import Image

st.set_page_config(page_title="Eymen AI", layout="centered")

# --- MODERN CSS TASARIM ---
st.markdown("""
    <style>
    /* Avatarları tamamen gizle */
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] { display: none !important; }
    
    /* Input kutusunu modernize et, köşeleri yuvarlat */
    .stChatInputContainer { 
        position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); 
        width: 90%; background: #f0f2f6; border-radius: 25px; padding: 5px 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    
    /* Artı butonunu küçült ve kutu içine göm */
    .stFileUploader { width: 40px !important; margin-right: 10px; }
    .stFileUploader label { display: none !important; }
    
    /* Mesajları yukarı it */
    .main { padding-bottom: 150px; }
    </style>
""", unsafe_allow_html=True)

# --- MODEL ---
def get_model():
    tr_tz = pytz.timezone('Europe/Istanbul')
    tr_time = datetime.now(tr_tz).strftime("%d-%m-%Y %H:%M:%S")
    genai.configure(api_key=st.secrets.get("KEY_1"))
    return genai.GenerativeModel('gemini-2.5-flash', 
        system_instruction=f"Tarih/Saat: {tr_time}. Eymen AI. Sadece sorulduğunda bilgi ver, gereksiz konuşma. Zeki ve analizci ol.")

if "messages" not in st.session_state: st.session_state.messages = []

# --- SOHBET GÖRÜNTÜLEME ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image": st.image(msg["content"], use_container_width=True)
        else: st.markdown(msg["content"])

# --- SABİT ALT PANEL (Artı + Chat) ---
st.markdown('<div class="stChatInputContainer">', unsafe_allow_html=True)
cols = st.columns([0.15, 0.85])
with cols[0]:
    uploaded_file = st.file_uploader("➕", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
with cols[1]:
    prompt = st.chat_input("Eymen AI'ye sor...")
st.markdown('</div>', unsafe_allow_html=True)

# --- İŞLEM VE OTOMATİK SCROLL ---
if prompt:
    model = get_model()
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun() # Mesajı ekleyip sayfayı güncelliyoruz ki en alta insin

# Eğer kullanıcı yeni mesaj gönderdiyse asistanın cevabını işleyelim
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        try:
            if uploaded_file:
                img = Image.open(uploaded_file)
                st.image(img, use_container_width=True)
                response = model.generate_content([prompt, img])
            elif any(k in prompt.lower() for k in ["çiz", "oluştur", "generate"]):
                img_url = f"https://pollinations.ai/p/{prompt.replace('çiz', '').strip()}?width=512&height=512&nologo=true"
                st.image(img_url, use_container_width=True)
                st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
            else:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun() # Cevap gelince de en alta otomatik kaydır
        except Exception:
            st.error("Bir hata oluştu.")
