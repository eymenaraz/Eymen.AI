import streamlit as st
import google.generativeai as genai

# RESİM LİNKLERİNİ BURAYA YAPIŞTIR
LOGO_URL = "https://hizliresim.com/gvewvtj"
LIGHT_AVATAR = "https://hizliresim.com/8w6lqzo"
DARK_AVATAR = "https://hizliresim.com/bsfo6dy"

st.set_page_config(page_title="Eymen AI", layout="centered")

# CSS: Temaya göre avatarı otomatik değiştir ve ikonları gizle
st.markdown(f"""
    <style>
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] {{ display: none !important; }}
    
    /* Dark modda Dark Avatar, Light modda Light Avatar göster */
    [data-testid="stChatMessage"]:has(img[alt="assistant"]) {{
        background-image: url('{LIGHT_AVATAR}');
    }}
    
    @media (prefers-color-scheme: dark) {{
        .stApp {{ background-color: #0d1117; }}
    }}
    </style>
""", unsafe_allow_html=True)

# Başlık (Logolu)
st.markdown(f"<div style='display:flex; justify-content:center;'><img src='{LOGO_URL}' width='150'></div>", unsafe_allow_html=True)

# Avatar mantığı: Streamlit tema bilgisine göre link seçimi
# Bu yöntem kütüphane hatası vermez
if st.get_option("theme.base") == "dark":
    avatar_link = DARK_AVATAR
else:
    avatar_link = LIGHT_AVATAR

# ... (API ve Mesajlaşma Kodların Buraya)

# Asistan mesajı yazdırırken:
with st.chat_message("assistant", avatar=avatar_link):
    st.markdown(full_response)
