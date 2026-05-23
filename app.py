import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- AYARLAR ---
LOGO_URL = "https://i.hizliresim.com/gvewvtj.png"
LIGHT_AVATAR = "https://i.hizliresim.com/8w6lqzo.png"
DARK_AVATAR = "https://i.hizliresim.com/bsfo6dy.png"

st.set_page_config(page_title="Eymen AI", layout="centered", initial_sidebar_state="collapsed")

# --- TEMA VE CSS ---
theme_base = st.get_option("theme.base")
avatar_to_use = DARK_AVATAR if theme_base == "dark" else LIGHT_AVATAR
dot_color = "#ffffff" if theme_base == "dark" else "#000000"

st.markdown(f"""
    <style>
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] {{ display: none !important; }}
    .typing {{ display: flex; gap: 5px; margin-top: 10px; }}
    .dot {{ width: 8px; height: 8px; background-color: {dot_color}; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; }}
    .dot:nth-child(1) {{ animation-delay: -0.32s; }}
    .dot:nth-child(2) {{ animation-delay: -0.16s; }}
    @keyframes bounce {{ 0%, 80%, 100% {{ transform: scale(0); }} 40% {{ transform: scale(1); }} }}
    </style>
""", unsafe_allow_html=True)

st.markdown(f'<div style="text-align: center; margin-bottom: 25px;"><img src="{LOGO_URL}" width="250"></div>', unsafe_allow_html=True)

# --- EYMEN AI MODELİ ---
def get_model():
    # Şu anki zamanı al
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    keys = [st.secrets.get("KEY_1"), st.secrets.get("KEY_2"), st.secrets.get("KEY_3")]
    for key in keys:
        if key:
            try:
                genai.configure(api_key=key)
                return genai.GenerativeModel(
                    model_name='gemini-2.5-flash',
                    system_instruction=f"""Sen Eymen AI'sin. Bugünün tarihi ve saati: {now}. 
                    Sen bir gündelik asistan ve yapay zekasın. 
                    - Hava durumu, güncel olaylar gibi konularda bilgi sahibisin.
                    - Kullanıcıya yardımcı ol, hızlı cevap ver.
                    - Eğer görsel istenirse 'çiz' veya 'oluştur' komutlarını anla.
                    - Tarih ve saati her an bildiğini unutma."""
                )
            except: continue
    return None

if "messages" not in st.session_state: st.session_state.messages = []

# Mesajları Görüntüle
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=avatar_to_use if msg["role"] == "assistant" else None):
        if msg.get("type") == "image":
            st.markdown(f'<img src="{msg["content"]}" style="width:100%; border-radius:10px;">', unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# --- SOHBET VE ÇİZİM ---
if prompt := st.chat_input("Eymen AI'ye sor (Tarih, Hava Durumu, Görsel...):"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    # Görsel Oluşturma
    if any(keyword in prompt.lower() for keyword in ["çiz", "oluştur", "generate"]):
        with st.chat_message("assistant", avatar=avatar_to_use):
            img_prompt = prompt.replace("çiz", "").replace("oluştur", "").replace("generate", "").strip()
            img_url = f"https://pollinations.ai/p/{img_prompt}?width=300&height=300&nologo=true"
            st.markdown(f'<img src="{img_url}" style="width:100%; border-radius:10px;">', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
    
    else:
        with st.chat_message("assistant", avatar=avatar_to_use):
            placeholder = st.empty()
            placeholder.markdown('<div class="typing"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>', unsafe_allow_html=True)
            
            model = get_model()
            if model:
                try:
                    response = model.generate_content(prompt, stream=True)
                    full_response = ""
                    for chunk in response:
                        full_response += chunk.text
                        placeholder.markdown(full_response + "▌")
                    placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    placeholder.markdown(f"Eymen AI hata verdi: {e}")
            else:
                placeholder.markdown("API Anahtarı bulunamadı!")
