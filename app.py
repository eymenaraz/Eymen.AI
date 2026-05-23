import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

st.set_page_config(page_title="Eymen AI", layout="centered")

# --- MODERN VE DİNAMİK CSS ---
# Light/Dark mode için dinamik renkler ve sabit alt panel
st.markdown("""
    <style>
    /* Avatarlar ve gereksiz bileşenler silindi */
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"], .stAppDeployButton { display: none !important; }
    
    /* Sabit Alt Panel */
    .chat-footer {
        position: fixed; bottom: 0; left: 0; width: 100%; padding: 15px;
        background-color: var(--background-color); border-top: 1px solid #ddd;
    }
    
    /* Input Tasarımı */
    .input-container { display: flex; align-items: center; gap: 10px; }
    .plus-btn { cursor: pointer; font-size: 24px; font-weight: bold; }
    
    /* Dosya yükleme gizli (sadece + tıklandığında tetiklenir) */
    .hidden-upload { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- MODEL VE SOHBET ---
if "messages" not in st.session_state: st.session_state.messages = []
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image": st.image(msg["content"], use_container_width=True)
        else: st.markdown(msg["content"])

# --- SABİT ALT PANEL (HTML YAPISI) ---
st.markdown('<div class="chat-footer">', unsafe_allow_html=True)
col1, col2 = st.columns([0.1, 0.9])

with col1:
    # + Butonu: Tıklandığında dosya seçtirir
    uploaded_file = st.file_uploader("➕", type=["png", "jpg"], label_visibility="collapsed")
with col2:
    prompt = st.chat_input("Eymen AI'ye sor...")
st.markdown('</div>', unsafe_allow_html=True)

# --- İŞLEM MANTIĞI (Dinamik) ---
if prompt:
    genai.configure(api_key=st.secrets.get("KEY_1"))
    model = genai.GenerativeModel('gemini-2.5-flash')
    
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
                st.rerun()
            else:
                response = model.generate_content(prompt)
                st.markdown(response.text)
            
            if 'response' in locals():
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        except: st.error("Hata oluştu.")
    st.rerun()
