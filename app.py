import streamlit as st
import google.generativeai as genai
import random, time
from datetime import datetime
import pytz
from PIL import Image

st.set_page_config(page_title="Eymen AI", layout="centered")

# --- CSS: AVATARLARI SİL, MODLARI AYARLA ---
st.markdown("""
    <style>
    /* Avatarları ve Streamlit logolarını tamamen gizle */
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"], .stAppDeployButton { display: none !important; }
    
    /* Input'u sadeleştir */
    .stChatInput { max-width: 800px; margin: auto; }
    
    /* Mobil uyumlu yapı */
    @media (max-width: 600px) { .stChatInput { width: 95% !important; } }
    </style>
""", unsafe_allow_html=True)

# --- MODEL ROTASYON VE HATALARI ÇÖZME ---
def get_model():
    # 10 anahtardan rastgele birini seç
    keys = [st.secrets[f"KEY_{i}"] for i in range(1, 11)]
    api_key = random.choice(keys)
    genai.configure(api_key=api_key)
    
    return genai.GenerativeModel('gemini-2.5-flash',
        system_instruction="""Sen Eymen AI'sin. Her türlü matematik, geometri ve mantık sorusunu 
        adım adım, analitik ve net şekilde çözersin. Fotoğraf analizi ve görsel oluşturma konusunda uzmansın. 
        Sadece gerekli bilgiyi ver, gereksiz konuşma Ayrıca sana nasılsın diye sorulduğunda duygularım yok vb deme.""")

# --- SOHBET YÖNETİMİ ---
if "sessions" not in st.session_state: st.session_state.sessions = {"Sohbet 1": []}
if "current_session" not in st.session_state: st.session_state.current_session = "Sohbet 1"

with st.sidebar:
    if st.button("➕ Yeni Sohbet"):
        new_name = f"Sohbet {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[new_name] = []
        st.session_state.current_session = new_name
    for name in list(st.session_state.sessions.keys()):
        if st.button(name): st.session_state.current_session = name

# --- ANA EKRAN ---
st.markdown('<div style="text-align: center;"><h2>Eymen AI</h2></div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Dosya Yükle", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

messages = st.session_state.sessions[st.session_state.current_session]
for msg in messages:
    if isinstance(msg, dict):
        with st.chat_message(msg["role"]):
            if msg.get("type") == "image": st.image(msg["content"], use_container_width=True)
            else: st.markdown(msg["content"])

# --- İŞLEM ---
if prompt := st.chat_input("Eymen AI a birşeyler sor"): # Burayı boş bıraktım, yazı yazmayacak
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = get_model()
            if uploaded_file:
                img = Image.open(uploaded_file)
                st.image(img, use_container_width=True)
                response = model.generate_content([prompt, img])
                messages.append({"role": "assistant", "content": response.text})
            elif "çiz" in prompt.lower() or "oluştur" in prompt.lower():
                img_url = f"https://pollinations.ai/p/{prompt}?width=512&height=512&nologo=true"
                st.image(img_url, use_container_width=True)
                messages.append({"role": "assistant", "content": img_url, "type": "image"})
            else:
                response = model.generate_content(prompt)
                messages.append({"role": "assistant", "content": response.text})
            st.rerun()
        except Exception:
            # Hata anında farklı bir anahtarla tekrar deneme mantığı
            st.warning("Limit aşıldı, farklı anahtara geçiliyor...")
            time.sleep(1)
            st.rerun()
