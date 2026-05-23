import streamlit as st
import google.generativeai as genai

# --- AYARLAR (Doğrudan Resim Linkleri) ---
LOGO_URL = "https://i.hizliresim.com/gvewvtj.png"
LIGHT_AVATAR = "https://i.hizliresim.com/8w6lqzo.png"
DARK_AVATAR = "https://i.hizliresim.com/bsfo6dy.png"

st.set_page_config(page_title="Eymen AI", layout="centered")

# --- TEMA VE CSS ---
theme_base = st.get_option("theme.base")
avatar_to_use = DARK_AVATAR if theme_base == "dark" else LIGHT_AVATAR

st.markdown("""
    <style>
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] { display: none !important; }
    .stChatMessage { padding: 10px; }
    </style>
""", unsafe_allow_html=True)

# Başlık (Logo)
st.markdown(f'<div style="text-align: center;"><img src="{LOGO_URL}" width="150"></div>', unsafe_allow_html=True)

# --- EYMEN AI MODELİ ---
keys = [st.secrets["KEY_1"], st.secrets["KEY_2"], st.secrets["KEY_3"]]

def get_model():
    for key in keys:
        try:
            genai.configure(api_key=key)
            return genai.GenerativeModel(
                model_name='gemini-1.5-flash', 
                system_instruction="Sen Eymen AI'sin. Hızlı, enerjik ve zekisin. Kullanıcının sorduğu dilde akıcı konuşur, karmaşık sorunları hızlıca çözersin."
            )
        except: continue
    return None

if "messages" not in st.session_state: st.session_state.messages = []

# Mesajları Görüntüle
for msg in st.session_state.messages:
    current_avatar = avatar_to_use if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=current_avatar):
        if msg.get("type") == "image": st.image(msg["content"])
        else: st.markdown(msg["content"])

# --- SOHBET VE ÇİZİM ---
if prompt := st.chat_input("Eymen AI'ye sor veya bir şey çizdir..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=None): st.markdown(prompt)

    if any(x in prompt.lower() for x in ["çiz", "oluştur", "generate"]):
        with st.chat_message("assistant", avatar=avatar_to_use):
            img_prompt = prompt.replace("çiz", "").replace("oluştur", "").replace("generate", "").strip()
            img_url = f"https://pollinations.ai/p/{img_prompt}?width=512&height=512&nologo=true"
            st.image(img_url)
            st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
    
    else:
        with st.chat_message("assistant", avatar=avatar_to_use):
            message_placeholder = st.empty()
            full_response = ""
            model = get_model()
            if model:
                try:
                    response = model.generate_content(prompt, stream=True)
                    for chunk in response:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception:
                    st.error("Eymen AI düşünmekte zorlanıyor! API anahtarlarını kontrol et.")
            else:
                st.error("Model yüklenemedi. API anahtarlarını 'Secrets' kısmına eklediğinden emin ol.")
