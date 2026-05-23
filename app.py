import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pytz
from PIL import Image

# --- AYARLAR ---
LOGO_URL = "https://i.hizliresim.com/gvewvtj.png"
DARK_AVATAR = "https://i.hizliresim.com/bsfo6dy.png"
LIGHT_AVATAR = "https://i.hizliresim.com/8w6lqzo.png"

st.set_page_config(page_title="Eymen AI", layout="centered")

# --- CSS (Artı Butonu ve Mobil Uyum) ---
st.markdown("""
    <style>
    [data-testid="stFileUploader"] { margin-bottom: 10px; }
    .stChatInput { margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

st.markdown(f'<div style="text-align: center;"><img src="{LOGO_URL}" width="200"></div>', unsafe_allow_html=True)

# --- MODEL AYARLARI ---
def get_model():
    tr_tz = pytz.timezone('Europe/Istanbul')
    tr_time = datetime.now(tr_tz).strftime("%d-%m-%Y %H:%M:%S")
    
    key = st.secrets.get("KEY_1")
    genai.configure(api_key=key)
    return genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction=f"""Sen Eymen AI'sin. Şu an {tr_time}. 
        Zeki, gerçekçi ve analitik bir asistansın. 
        - Eğer bir fotoğraf yüklendiyse, onu çok dikkatli incele. 
        - Emin değilsen veya fotoğraf belirsizse asla sallama, 'Fotoğraftan bunu net çıkaramadım' de.
        - Matematik sorularında çözüm adımlarını göstererek ilerle. 
        - Görsel oluştururken hızlı ve yaratıcı ol."""
    )

if "messages" not in st.session_state: st.session_state.messages = []

# --- ARAYÜZ ---
uploaded_file = st.file_uploader("➕ Fotoğraf Ekle", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Eymen AI'ye sor..."):
    model = get_model()
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. Fotoğraf varsa analiz et
        if uploaded_file:
            img = Image.open(uploaded_file)
            st.image(img, width=200)
            response = model.generate_content([prompt, img])
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        # 2. Görsel oluşturma (Hızlı)
        elif any(k in prompt.lower() for k in ["çiz", "oluştur", "generate"]):
            img_prompt = prompt.replace("çiz", "").replace("oluştur", "").replace("generate", "").strip()
            img_url = f"https://pollinations.ai/p/{img_prompt}?width=512&height=512&nologo=true&seed=0"
            st.markdown(f"![{img_prompt}]({img_url})")
            st.session_state.messages.append({"role": "assistant", "content": f"![Görsel]({img_url})"})
            
        # 3. Normal Analitik Cevap
        else:
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
