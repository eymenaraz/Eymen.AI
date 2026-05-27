import streamlit as st
import json
import urllib.parse
import random
import string
import math
import google.generativeai as genai
from google.api_core import exceptions

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Eymen AI V2 - Full System", page_icon="🤖", layout="wide")

# --- CSS (Arayüz) ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f8fafc; }
    .user-bubble { background: #3b82f6; color: white; padding: 12px; border-radius: 15px; margin: 5px 0 5px auto; width: fit-content; }
    .ai-bubble { background: #1e293b; color: #e2e8f0; padding: 12px; border-radius: 15px; margin: 5px auto 5px 0; width: fit-content; border: 1px solid #334155; }
    .tts-button { background: #0ea5e9; color: white; border: none; border-radius: 8px; padding: 5px 10px; cursor: pointer; margin-top: 5px; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# --- API YÖNETİMİ ---
def get_model():
    keys = [st.secrets.get(f"KEY_{i}") for i in range(1, 11) if st.secrets.get(f"KEY_{i}")]
    random.shuffle(keys)
    for key in keys:
        try:
            genai.configure(api_key=key)
            return genai.GenerativeModel("gemini-2.5-flash")
        except: continue
    return None

# --- SOHBETİ EKRANA YAZDIRMA ---
if "messages" not in st.session_state: st.session_state.messages = []
for msg in st.session_state.messages:
    if msg["role"] == "user": 
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
        if "image" in msg: st.image(msg["image"], use_container_width=True)
        safe_text = json.dumps(msg["content"])
        st.markdown(f'<button class="tts-button" onclick="window.speechSynthesis.speak(new SpeechSynthesisUtterance({safe_text}))">🔊 Sesli Dinle</button>', unsafe_allow_html=True)

# --- SOHBET VE FOTOĞRAF MOTORU ---
if user_query := st.chat_input("Eymen AI'ye bir şeyler sorun veya görsel oluşturun..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    triggers = ["görsel oluştur", "çiz", "hayal et", "resim", "fotoğraf"]
    if any(t in user_query.lower() for t in triggers):
        img_url = f"https://pollinations.ai/p/{urllib.parse.quote(user_query)}?width=1024&height=1024&seed={random.randint(1000,999999)}&nologo=true"
        st.session_state.messages.append({"role": "assistant", "content": "İşte görselin:", "image": img_url})
    else:
        model = get_model()
        if model:
            try:
                response = model.generate_content(user_query)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except exceptions.ResourceExhausted:
                st.error("⚠️ Tüm API anahtarlarının kotası dolu! Lütfen bekleyin veya yeni anahtar tanımlayın.")
        else:
            st.error("⚠️ Aktif API anahtarı bulunamadı!")
    st.rerun()

# --- SIDEBAR ARAÇLARI ---
with st.sidebar:
    st.header("🧰 Araç Kutusu")
    if st.button("🗑️ Sohbeti Temizle"): st.session_state.messages = []; st.rerun()
    
    # 1. HESAP MAKİNESİ
    with st.expander("🧮 Gelişmiş Hesap Makinesi"):
        if "calc" not in st.session_state: st.session_state.calc = ""
        st.text_input("Sonuç", value=st.session_state.calc, disabled=True)
        cols = st.columns(4)
        buttons = ["7","8","9","/","4","5","6","*","1","2","3","-","0",".","+","C"]
        for i, btn in enumerate(buttons):
            if cols[i%4].button(btn):
                if btn == "C": st.session_state.calc = ""
                else: st.session_state.calc += btn
                st.rerun()
        if st.button("Karekök (√)"):
            try: st.session_state.calc = str(math.sqrt(float(eval(st.session_state.calc))))
            except: st.session_state.calc = "Hata"
            st.rerun()
        if st.button("HESAPLA (=)"):
            try: st.session_state.calc = str(eval(st.session_state.calc))
            except: st.session_state.calc = "Hata"
            st.rerun()

    # 2. QR OLUŞTURUCU
    with st.expander("🪄 QR Kod Oluşturucu"):
        qr_txt = st.text_input("QR için metin:")
        if st.button("QR Üret"):
            st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(qr_txt)}")

    # 3. ŞİFRE OLUŞTURUCU
    with st.expander("🔑 Şifre Oluşturucu"):
        n = st.slider("Hane Sayısı", 4, 32, 12)
        if st.button("Şifre Üret"):
            chars = string.ascii_letters + string.digits + "!@#$%"
            st.code("".join(random.choice(chars) for _ in range(n)))
