import streamlit as st
import google.generativeai as genai

# --- AYARLAR ---
LOGO_URL = "https://i.hizliresim.com/gvewvtj.png"
LIGHT_AVATAR = "https://i.hizliresim.com/8w6lqzo.png"
DARK_AVATAR = "https://i.hizliresim.com/bsfo6dy.png"

st.set_page_config(page_title="Eymen AI", layout="centered")

theme_base = st.get_option("theme.base")
avatar_to_use = DARK_AVATAR if theme_base == "dark" else LIGHT_AVATAR

st.markdown("""
    <style>
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] { display: none !important; }
    .stChatMessage { padding: 10px; }
    </style>
""", unsafe_allow_html=True)

# GÜNCELLENDİ: Logo boyutu 250px'e çıkarıldı (Eski Eymen AI yazısı kadar büyük)
st.markdown(f'<div style="text-align: center; margin-bottom: 20px;"><img src="{LOGO_URL}" width="250"></div>', unsafe_allow_html=True)

def get_model():
    keys = [st.secrets.get("KEY_1"), st.secrets.get("KEY_2"), st.secrets.get("KEY_3")]
    for key in keys:
        if key:
            try:
                genai.configure(api_key=key)
                return genai.GenerativeModel('gemini-2.5-flash')
            except: continue
    return None

if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=avatar_to_use if msg["role"] == "assistant" else None):
        if msg.get("type") == "image":
            st.markdown(f'<img src="{msg["content"]}" style="width:100%; border-radius:10px;">', unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

if prompt := st.chat_input("Eymen AI'ye sor veya çizdir..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    if any(keyword in prompt.lower() for keyword in ["çiz", "oluştur", "generate"]):
        with st.chat_message("assistant", avatar=avatar_to_use):
            img_prompt = prompt.replace("çiz", "").replace("oluştur", "").replace("generate", "").strip()
            img_url = f"https://pollinations.ai/p/{img_prompt}?width=512&height=512&nologo=true"
            st.markdown(f'<img src="{img_url}" style="width:100%; border-radius:10px;">', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
    
    else:
        with st.chat_message("assistant", avatar=avatar_to_use):
            placeholder = st.empty()
            full_response = ""
            model = get_model()
            if model:
                try:
                    response = model.generate_content(prompt, stream=True)
                    for chunk in response:
                        full_response += chunk.text
                        placeholder.markdown(full_response + "▌")
                    placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"Eymen AI hata verdi: {e}")
            else:
                st.error("API Anahtarı bulunamadı!")
