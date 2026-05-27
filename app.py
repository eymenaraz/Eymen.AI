import streamlit as st
import json
import os
import urllib.parse
import random
import string
import math
import google.generativeai as genai

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Eymen AI V2,"
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS VE STYLING (ÖZEL NEON LOGO VE PREMIUM TEMALAR) ---
st.markdown("""
<style>
    /* Ana Arka Plan */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    /* Yan Menü (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid #1e293b;
    }
    
    /* Sohbet Giriş Kutusu */
    .stTextInput input {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
    }
    
    .stTextInput input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important;
    }
    
    /* Kullanıcı Mesaj Balonu */
    .user-bubble {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        padding: 14px 18px;
        border-radius: 20px 20px 4px 20px;
        margin: 10px 0 10px auto;
        max-width: 75%;
        width: fit-content;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Asistan Mesaj Balonu */
    .ai-bubble {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #e2e8f0;
        padding: 14px 18px;
        border-radius: 20px 20px 20px 4px;
        margin: 10px auto 10px 0;
        max-width: 75%;
        width: fit-content;
        border: 1px solid #27272a;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Çift Renkli Neon Parlayan Logo Tasarımı */
    .logo-container {
        text-align: center;
        margin-bottom: 5px;
        padding: 10px;
    }
    .brand-eymen {
        font-size: 3.5rem;
        font-weight: 900;
        color: #1e4ed8;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        letter-spacing: 1px;
        text-shadow: 0 0 8px #1e4ed8, 0 0 20px #1e4ed8, 0 0 30px #3b82f6;
    }
    .brand-v2 {
        font-size: 3.5rem;
        font-weight: 900;
        color: #38bdf8;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        letter-spacing: 1px;
        text-shadow: 0 0 8px #38bdf8, 0 0 20px #38bdf8, 0 0 35px #0ea5e9;
        margin-left: 15px;
    }
    
    .subtitle {
        color: #94a3b8;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# --- ÇOKLU API KEY OTOMATİK TARAMA SİSTEMİ ---
# Secrets panelindeki KEY_1'den KEY_10'a kadar olan anahtarları sırayla test eder
@st.cache_resource
def get_working_api_key():
    for i in range(1, 11):
        key_name = f"KEY_{i}"
        if key_name in st.secrets:
            potential_key = st.secrets[key_name]
            try:
                # Anahtarın çalışıp çalışmadığını test etmek için minik bir çağrı yapıyoruz
                genai.configure(api_key=potential_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                model.generate_content("test", generation_config={"max_output_tokens": 1})
                return potential_key
            except Exception:
                continue
    return None

api_key = get_working_api_key()

# --- BAŞLIK ALANI (ÖZEL NEON TASARIM) ---
st.markdown('<div class="logo-container"><span class="brand-eymen">Eymen AI</span><span class="brand-v2">V2</span></div>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Gelişmiş Yapay Zeka & Akıllı Araç Seti</p>', unsafe_allow_html=True)

# --- ARKA PLAN SABİT AYARLAR ---
model_choice = "gemini-2.5-flash"
system_instruction = "Sen Eymen AI V2 adında, kullanıcılara her konuda yardımcı olan, profesyonel, zeki ve bilgili bir yapay zeka asistanısın.Her türlü problemi her türlü sınıf derecesinden her dersten her problemi şak diye doğru çözer ve hızlıca açıklar hızlıca doğru çözersin Einstein gibi matematik dehasısın.Görsel oluştururken de prompttaki istemi internette aratıp kend teknolojinle harmanlayarak görseli çok hızlıca doğru şekilde istemler üstüste gelse bile oluşturursun."

# --- SIDEBAR (YAN MENÜ ALANI) ---
with st.sidebar:
    st.markdown("<h2 style='color: #38bdf8; text-align: center; font-size: 1.6rem;'>Menü Navigasyon</h2>", unsafe_allow_html=True)
    st.write("---")
    
    # 1. SOHBETLER SEKMESİ
    st.markdown("<h3 style='color: #f8fafc;'>💬 Sohbetler</h3>", unsafe_allow_html=True)
    if st.button("🗑️ Mevcut Sohbeti Sıfırla", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.write("---")
    
    # 2. AKILLI ARAÇ KUTUSU SEKMESİ
    st.markdown("<h3 style='color: #f8fafc;'>🧰 Akıllı Araç Kutusu</h3>", unsafe_allow_html=True)
    
    # Mikrofon Butonu (STT)
    st.markdown("""
    <script>
    function startDictation() {
        if (window.hasOwnProperty('webkitSpeechRecognition')) {
            var recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = "tr-TR";
            recognition.start();
            
            recognition.onresult = function(e) {
                var text = e.results[0][0].transcript;
                var inputs = window.parent.document.getElementsByTagName('textarea');
                for (var i = 0; i < inputs.length; i++) {
                    if (inputs[i].placeholder && inputs[i].placeholder.includes('yazın')) {
                        inputs[i].value = text;
                        inputs[i].dispatchEvent(new Event('input', { bubbles: true }));
                        break;
                    }
                }
                recognition.stop();
            };
            recognition.onerror = function(e) {
                recognition.stop();
            }
        }
    }
    </script>
    <button onclick="startDictation()" style="width: 100%; background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%); color: white; border: none; padding: 10px; border-radius: 8px; font-weight: bold; cursor: pointer; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);">
        🎤 Sesle Konuş (Mikrofon)
    </button>
    """, unsafe_allow_html=True)
    
    # GELİŞMİŞ HESAP MAKİNESİ (KAREKÖK DESTEKLİ)
    with st.expander("🧮 Gelişmiş Hesap Makinesi"):
        if "calc_val" not in st.session_state:
            st.session_state.calc_val = ""
            
        st.text_input("Ekran", value=st.session_state.calc_val, disabled=True, key="calc_screen")
        
        # Buton Düzenleri
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("7"): st.session_state.calc_val += "7"
        if col2.button("8"): st.session_state.calc_val += "8"
        if col3.button("9"): st.session_state.calc_val += "9"
        if col4.button("/"): st.session_state.calc_val += "/"
        
        if col1.button("4"): st.session_state.calc_val += "4"
        if col2.button("5"): st.session_state.calc_val += "5"
        if col3.button("6"): st.session_state.calc_val += "6"
        if col4.button("*"): st.session_state.calc_val += "*"
        
        if col1.button("1"): st.session_state.calc_val += "1"
        if col2.button("2"): st.session_state.calc_val += "2"
        if col3.button("3"): st.session_state.calc_val += "3"
        if col4.button("-"): st.session_state.calc_val += "-"
        
        if col1.button("0"): st.session_state.calc_val += "0"
        if col2.button("."): st.session_state.calc_val += "."
        if col3.button("+"): st.session_state.calc_val += "+"
        if col4.button("C"): 
            st.session_state.calc_val = ""
            st.rerun()
            
        # Özel Fonksiyonlar (Karekök ve Üs)
        c_sqrt, c_sqr, c_eq = st.columns([1, 1, 2])
        if c_sqrt.button("√x"):
            try:
                st.session_state.calc_val = str(math.sqrt(float(eval(st.session_state.calc_val))))
            except:
                st.session_state.calc_val = "Hata"
            st.rerun()
        if c_sqr.button("x²"):
            try:
                st.session_state.calc_val = str(float(eval(st.session_state.calc_val))**2)
            except:
                st.session_state.calc_val = "Hata"
            st.rerun()
        if c_eq.button("=", use_container_width=True):
            try:
                st.session_state.calc_val = str(eval(st.session_state.calc_val))
            except:
                st.session_state.calc_val = "Hata"
            st.rerun()

    # AKILLI ŞİFRE OLUŞTURUCU
    with st.expander("🔑 Akıllı Şifre Oluşturucu"):
        length = st.slider("Hane Sayısı (Uzunluk)", min_value=4, max_value=32, value=12)
        use_digits = st.checkbox("Sayılar Olsun (0-9)", value=True)
        use_special = st.checkbox("Semboller Olsun (!@#$)", value=True)
        
        if st.button("Şifre Üret", use_container_width=True):
            chars = string.ascii_letters
            if use_digits: chars += string.digits
            if use_special: chars += string.punctuation
            generated_password = "".join(random.choice(chars) for _ in range(length))
            st.code(generated_password, language="")

# --- SOHBET HAFIZASI VE OTURUM YÖNETİMİ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        if "image" in msg:
            st.markdown(f'<div class="ai-bubble">{msg["content"]}<br><img src="{msg["image"]}" style="width:100%; border-radius:10px; margin-top:10px; border:1px solid #334155;"></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

# --- ANA SOHBET DÖNGÜSÜ ---
if user_query := st.chat_input("Eymen AI V2'ye birşeyler sorun..."):
    
    st.markdown(f'<div class="user-bubble">{user_query}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # GELİŞTİRİLMİŞ ULTRA GÖRSEL ÜRETİM MOTORU
    if user_query.lower().startswith("/foto "):
        with st.spinner("V2 Medya Motoru Görseli Hazırlıyor..."):
            prompt = user_query[6:]
            encoded_prompt = urllib.parse.quote(prompt)
            # Gelişmiş görsel parametreleri ile beslenen yüksek kaliteli motor bağlantısı
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
            ai_response = f"✨ İstediğin özel görsel başarıyla üretildi: **{prompt}**"
            
            st.markdown(f'<div class="ai-bubble">{ai_response}<br><img src="{image_url}" style="width:100%; border-radius:10px; margin-top:10px; border:1px solid #334155;"></div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": ai_response, "image": image_url})
            
    # NORMAL YAPAY ZEKA SOHBETİ
    else:
        if not api_key:
            st.error("Kotanızı doldurdunuz.Bu sorunu düzeltmek için biraz zamana ihtiyacımız var,lütfen yeni geliştirmeleri bekleyin.")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name=model_choice,
                    system_instruction=system_instruction
                )
                
                formatted_history = []
                for m in st.session_state.messages[:-1]:
                    if "image" not in m:
                        role = "user" if m["role"] == "user" else "model"
                        formatted_history.append({"role": role, "parts": [m["content"]]})
                
                chat = model.start_chat(history=formatted_history)
                
                with st.spinner("Eymen AI V2 düşünüyor..."):
                    response = chat.send_message(user_query)
                    ai_response = response.text
                
                st.markdown(f'<div class="ai-bubble">{ai_response}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
                # --- YEREL SESLİ OKUMA (TTS) ---
                escaped_response = json.dumps(ai_response)
                tts_html = f"""
                <script>
                var msg = new SpeechSynthesisUtterance({escaped_response});
                msg.lang = 'tr-TR';
                window.speechSynthesis.speak(msg);
                </script>
                """
                st.markdown(tts_html, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Sistem hatası meydana geldi: {str(e)}")

# --- ALT BİLGİ ---
st.write("---")
st.markdown(
    "<p style='text-align: center; color: #475569; font-size: 0.85rem;'>"
    "Eymen AI V2 © 2026 | Güçlendirilmiş Nihai Sürüm"
    "</p>", 
    unsafe_allow_html=True
)
