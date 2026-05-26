import streamlit as st
import google.generativeai as genai
import random
import time
from PIL import Image
import urllib.parse
import streamlit.components.v1 as components
import json

# --- 1. SİSTEM ÇEKİRDEĞİ ---
st.set_page_config(page_title="Eymen AI V2 | Ultimate Premium", layout="centered")

if "sessions" not in st.session_state: st.session_state.sessions = {"Sohbet 1": []}
if "current_session" not in st.session_state: st.session_state.current_session = "Sohbet 1"

# --- 2. PREMIUM CSS MİMARİSİ (Sızdırmaz Yapı) ---
st.markdown("""
<style>
    .stApp { background: #0b0f19; color: #e2e8f0; }
    .premium-chat-input { border: 2px solid #3b82f6 !important; border-radius: 20px !important; }
    .img-canvas { border: 3px solid #3b82f6; border-radius: 15px; width: 100%; transition: 0.5s; }
    .tts-btn { background: #10b981; color: white; padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. KILI KIRK YARAN GÖRSEL İŞLEMCİ (Vision & Photoshop Engine) ---
def vision_master_layer(prompt):
    """Kişiyi/Nesneyi analiz eder, fiziksel betimlemeyi 8k fotoğraf moduna çevirir."""
    genai.configure(api_key=st.secrets.get("KEY_1", "FALLBACK_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    analysis = model.generate_content(f"Analyze the following request for a visual creation. Identify the subject (person/object), describe their physical attributes, lighting, and texture for a professional photoshoot: {prompt}. Return only a high-fidelity description for an image generator.").text
    return analysis

def render_final_image(prompt):
    """Görseli HTML5 üzerinden render ettirir."""
    analysis = vision_master_layer(prompt)
    safe_str = urllib.parse.quote(f"{analysis}, 8k, ultra-detailed, cinematic, {prompt}")
    seed = random.randint(100000, 999999)
    url = f"https://image.pollinations.ai/prompt/{safe_str}?width=1920&height=1080&seed={seed}&nologo=true&enhance=true"
    return url

# --- 4. SESLİ OKUMA (KESİN ÇALIŞMA GARANTİLİ) ---
def get_tts_logic(text):
    safe_text = json.dumps(text.replace("\n", " "))
    return f"""
    <button class="tts-btn" onclick='let u = new SpeechSynthesisUtterance({safe_text}); u.lang="tr-TR"; window.speechSynthesis.speak(u);'>🔊 Sesli Yanıt</button>
    """

# --- 5. ANA İŞLETİM DÖNGÜSÜ (V2 Mimarisi) ---
st.title("Eymen AI V2 Premium")

# Mesajları Görüntüle
for msg in st.session_state.sessions[st.session_state.current_session]:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image":
            st.markdown(f'<img src="{msg["content"]}" class="img-canvas">', unsafe_allow_html=True)
        else:
            st.write(msg["content"])

# Giriş Kutusu - "Premium" hissi veren placeholder
prompt = st.chat_input("Eymen AI V2'ye bir şeyler sor, dünyayı keşfet...")

if prompt:
    st.session_state.sessions[st.session_state.current_session].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)

    with st.chat_message("assistant"):
        # Görsel mi?
        if any(x in prompt.lower() for x in ["çiz", "oluştur", "foto", "resim", "yap"]):
            with st.status("V2 Görsel Zekası çalışıyor...", expanded=True) as status:
                st.write("Analiz ediliyor...")
                url = render_final_image(prompt)
                st.write("Görsel render edildi.")
                # BURASI ÖNEMLİ: st.image yerine HTML img ile kesin render
                st.markdown(f'<img src="{url}" class="img-canvas">', unsafe_allow_html=True)
                
                status.update(label="İşlem Başarılı: Görsel hazır.", state="complete")
                
                res = "İstediğin görseli V2 Photoshop motoru ile en ince detaylarına kadar işledim."
                st.markdown(get_tts_logic(res), unsafe_allow_html=True)
                st.session_state.sessions[st.session_state.current_session].append({"role": "assistant", "content": url, "type": "image"})
        else:
            # Sohbet
            response = "Eymen AI V2 Analizi: " + prompt # Buraya derinlik eklenebilir
            st.write(response)
            st.markdown(get_tts_logic(response), unsafe_allow_html=True)
            st.session_state.sessions[st.session_state.current_session].append({"role": "assistant", "content": response})
