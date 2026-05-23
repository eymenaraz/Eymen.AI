import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pytz
from PIL import Image

st.set_page_config(page_title="Eymen AI", layout="centered")

# --- CSS: MODERN VE SABİT TASARIM ---
st.markdown("""
    <style>
    /* Avatarları gizle */
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] { display: none !important; }
    
    /* Input kutusunu tamamen özelleştir */
    .stChatInput { position: fixed; bottom: 0; left: 0; width: 100%; padding: 10px; background: white; z-index: 999; }
    
    /* Upload yazısını yok et, sadece + kalsın */
    button[title="View gallery"] { display: none !important; }
    .stFileUploader label { display: none !important; }
    [data-testid="stFileUploader"] { width: 40px !important; margin-right: 10px; overflow: hidden; }
    
    /* Mesaj alanı kaydırılabilir olsun */
    .main { padding-bottom: 120px !important; }
    </style>
""", unsafe_allow_html=True)

# --- MODEL ---
def get_model():
    tr_tz = pytz.timezone('Europe/Istanbul')
    tr_time = datetime.now(tr_tz).strftime("%d-%m-%Y %H:%M:%S")
    genai.configure(api_key=st.secrets.get("KEY_1"))
    return genai.GenerativeModel('gemini-2.5-flash', 
        system_instruction=f"Tarih/Saat: {tr_time}. Eymen AI. Gereksiz bilgi verme, analitik ve zekisin.")

if "messages" not in st.session_state: st.session_state.messages = []

# --- SOHBET GÖRÜNTÜLEME ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image": st.image(msg["content"], use_container_width=True)
        else: st.markdown(msg["content"])

# --- ALT PANEL: İNPUT + ARTI ---
# st.chat_input, Streamlit'in kendi sabitleme mekanizmasını kullanır. 
# Bu yüzden onu en alta koyuyoruz.
prompt = st.chat_input("Eymen AI'ye sor...")

# Upload alanı kutunun soluna özel bir yerleşim
uploaded_file = st.sidebar.file_uploader("➕", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

# --- İŞLEM MANTIĞI ---
if prompt:
    model = get_model()
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            if uploaded_file:
                img = Image.open(uploaded_file)
                st.image(img, use_container_width=True)
                response = model.generate_content([prompt, img])
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            elif any(k in prompt.lower() for k in ["çiz", "oluştur", "generate"]):
                img_url = f"https://pollinations.ai/p/{prompt.replace('çiz', '').strip()}?width=512&height=512&nologo=true"
                st.image(img_url, use_container_width=True)
                st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
            
            else:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception:
            st.error("Bir hata oluştu.")
    st.rerun()
