import streamlit as st
import google.generativeai as genai

# Sayfa Yapılandırması
st.set_page_config(page_title="Eymen AI", page_icon="logo.png", layout="centered")

# CSS: İkonları gizle ve modern tasarım
st.markdown("""
    <style>
    [data-testid="chatAvatarIcon-user"] { display: none; }
    [data-testid="chatAvatarIcon-assistant"] { display: none; }
    .stChatMessage { padding: 10px; }
    </style>
""", unsafe_allow_html=True)

# Başlık Kısmı
col1, col2 = st.columns([1, 5])
with col1:
    st.image("logo.png", width=70)
with col2:
    st.markdown("<h1 style='margin-top: 10px;'>Eymen AI</h1>", unsafe_allow_html=True)

# API Anahtarları (Sıralı)
keys = [st.secrets["KEY_1"], st.secrets["KEY_2"], st.secrets["KEY_3"]]

def get_model():
    for key in keys:
        try:
            genai.configure(api_key=key)
            return genai.GenerativeModel(
                model_name='gemini-2.0-flash',
                system_instruction="Sen Eymen AI'sin. Hızlı, modern ve enerjik bir yapay zekasın."
            )
        except:
            continue
    return None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları Görüntüle
for msg in st.session_state.messages:
    # Avatar seçimi: CSS veya JS ile tema kontrolü yerine basit bir mantık
    avatar = "profil_light.png" 
    with st.chat_message(msg["role"], avatar=avatar if msg["role"] == "assistant" else None):
        if msg.get("type") == "image":
            st.image(msg["content"])
        else:
            st.markdown(msg["content"])

# Giriş Kutusu
if prompt := st.chat_input("Eymen AI'ye sor veya çizdir..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=None):
        st.markdown(prompt)

    # Görsel Oluşturma
    if "çiz" in prompt.lower() or "oluştur" in prompt.lower():
        with st.chat_message("assistant", avatar="profil_light.png"):
            img_prompt = prompt.replace("çiz", "").replace("oluştur", "").strip()
            img_url = f"https://pollinations.ai/p/{img_prompt}?width=512&height=512&nologo=true"
            st.image(img_url)
            st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
    
    # Sohbet
    else:
        with st.chat_message("assistant", avatar="profil_light.png"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                model = get_model()
                response = model.generate_content(prompt, stream=True)
                for chunk in response:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception:
                st.error("Bir bağlantı hatası oluştu.")
