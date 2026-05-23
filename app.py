import streamlit as st
import google.generativeai as genai

# --- AYARLAR ---
LOGO_URL = "https://hizliresim.com/gvewvtj"
LIGHT_AVATAR = "https://hizliresim.com/8w6lqzo"
DARK_AVATAR = "https://hizliresim.com/bsfo6dy"

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

# Başlık
st.markdown(f'<div style="text-align: center;"><img src="{LOGO_URL}" width="150"></div>', unsafe_allow_html=True)

# --- EYMEN AI MODELİ ---
keys = [st.secrets["KEY_1"], st.secrets["KEY_2"], st.secrets["KEY_3"]]

def get_model():
    for key in keys:
        try:
            genai.configure(api_key=key)
            # Eymen AI kişiliği ve çok dilli yetenek talimatı
            return genai.GenerativeModel(
                model_name='gemini-2.0-flash', 
                system_instruction="""Sen Eymen AI'sin. 
                Hızlı, enerjik ve zekisin. Kullanıcının sorduğu dilde (Türkçe, İngilizce, Almanca vb.) akıcı ve 
                doğal konuşursun. Karmaşık sorunları hızlı düşünür, net çözümler üretirsin."""
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

    # Görsel Oluşturma Yeteneği
    if "çiz" in prompt.lower() or "oluştur" in prompt.lower() or "generate" in prompt.lower():
        with st.chat_message("assistant", avatar=avatar_to_use):
            img_prompt = prompt.replace("çiz", "").replace("oluştur", "").replace("generate", "").strip()
            img_url = f"https://pollinations.ai/p/{img_prompt}?width=512&height=512&nologo=true"
            st.image(img_url)
            st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
    
    # Çok Dilli Hızlı Sohbet
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
                    st.error("Eymen AI şu an düşünmekte zorlanıyor, tekrar dene!")
            else:
                st.error("API Anahtarı hatası.")
