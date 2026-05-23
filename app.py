import streamlit as st
import google.generativeai as genai
import time, random
from PIL import Image

st.set_page_config(page_title="Eymen AI", layout="centered")

# CSS: Avatar ve gereksiz ikonları tamamen sil
st.markdown("""
    <style>
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"], .stAppDeployButton { display: none !important; }
    .stChatInput { max-width: 800px; margin: auto; }
    </style>
""", unsafe_allow_html=True)

# API ROTASYON FONKSİYONU
def get_model_with_retry(prompt, img=None):
    # Anahtarları bir listeye al
    keys = [st.secrets[f"KEY_{i}"] for i in range(1, 11)]
    
    # 5 kez farklı anahtar dene
    for attempt in range(5):
        try:
            api_key = random.choice(keys)
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            if img:
                return model.generate_content([prompt, img])
            return model.generate_content(prompt)
            
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                time.sleep(2) # Limit aşılırsa bekle
                continue
            else:
                raise e
    return None

# SOHBET YÖNETİMİ
if "sessions" not in st.session_state: st.session_state.sessions = {"Sohbet 1": []}
if "current_session" not in st.session_state: st.session_state.current_session = "Sohbet 1"

with st.sidebar:
    if st.button("➕ Yeni Sohbet"):
        name = f"Sohbet {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[name] = []
        st.session_state.current_session = name
    for name in list(st.session_state.sessions.keys()):
        if st.button(name): st.session_state.current_session = name

# ANA EKRAN
st.markdown('<div style="text-align: center;"><h2>Eymen AI</h2></div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Dosya", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

messages = st.session_state.sessions[st.session_state.current_session]
for msg in messages:
    if isinstance(msg, dict):
        with st.chat_message(msg["role"]):
            if msg.get("type") == "image": st.image(msg["content"], use_container_width=True)
            else: st.markdown(msg["content"])

# İŞLEM
if prompt := st.chat_input(""):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            img = Image.open(uploaded_file) if uploaded_file else None
            
            if "çiz" in prompt.lower() or "oluştur" in prompt.lower():
                img_url = f"https://pollinations.ai/p/{prompt}?width=512&height=512&nologo=true"
                st.image(img_url, use_container_width=True)
                messages.append({"role": "assistant", "content": img_url, "type": "image"})
            else:
                response = get_model_with_retry(prompt, img)
                if response:
                    st.markdown(response.text)
                    messages.append({"role": "assistant", "content": response.text})
                else:
                    st.error("Kota aşıldı.Bu sorunu düzeltmek için bize biraz zaman lazım.Devam edecek geliştirmeleri bekleyin")
            st.rerun()
        except Exception:
            st.error("Bir sistem hatası oluştu.")
