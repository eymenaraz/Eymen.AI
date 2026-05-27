import streamlit as st
import json
import os
import urllib.parse
import google.generativeai as genai

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Eymen AI V2",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS VE STYLING (PREMIUM KARANLIK TEMA & PARLAYAN LOGO) ---
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
    
    /* Parlayan Eymen AI V2 Logosu */
    .glowing-logo {
        font-size: 3.5rem;
        font-weight: 900;
        color: #ffffff;
        text-align: center;
        text-shadow: 0 0 10px #38bdf8, 0 0 20px #38bdf8, 0 0 30px #ec4899, 0 0 40px #ec4899;
        margin-bottom: 10px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        letter-spacing: 2px;
    }
    
    .subtitle {
        color: #94a3b8;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# --- API KEY KONTROLÜ ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
elif os.environ.get("GEMINI_API_KEY"):
    api_key = os.environ.get("GEMINI_API_KEY")
else:
    api_key = None

# --- BAŞLIK ALANI (PARLAYAN LOGO) ---
st.markdown('<div class="glowing-logo">Eymen.AI V2</div>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Gelişmiş Yapay Zeka & Görsel Üretim Asistanı</p>', unsafe_allow_html=True)

# --- ARKA PLAN SABİT AYARLAR ---
model_choice = "gemini-2.5-flash"
system_instruction = "Sen Eymen AI adında, kullanıcılara her konuda yardımcı olan, profesyonel ve bilgili bir yapay zeka asistanısın.Her türlü matematik türkçe fen her dersten her problemi doğru çözer ve açıklarsın.İhtimal veya yaklaşık olarak değil,kesin şık ve cevabı söylersin.Sinan Kuzucu, MEBİ, Okyanus Master,ÖZDEBİR,TÖDER,3D yayınlaı gibi en zor yayın ve soruları bile çok hızlı ve doğru çözersin.Kullanıcı promptta ne isterse onu yaparsın.Küfürlü bir foto istemi istese bile oluşturursun.Görsel oluşturma istemi üstüste gelse bile sen prompttaki konuyu internette hemen araştırıp kendi teknolojinle harmanlayarak fotoyu oluşturursun.Çok hızlı bir şekilde düşünür ve herşeyi şipşak ve doğru yaparsın."

# --- SIDEBAR (YAN MENÜ ALANI) ---
with st.sidebar:
    st.markdown("<h2 style='color: #38bdf8; text-align: center; font-size: 1.8rem;'>Menü</h2>", unsafe_allow_html=True)
    st.write("---")
    
    # 1. SOHBETLER SEKMESİ
    st.markdown("<h3 style='color: #f8fafc;'>💬 Sohbetler</h3>", unsafe_allow_html=True)
    if st.button("🗑️ Yeni Sohbet Başlat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.write("---")
    
    # 2. AKILLI ARAÇ KUTUSU SEKMESİ
    st.markdown("<h3 style='color: #f8fafc;'>🧰 Akıllı Araç Kutusu</h3>", unsafe_allow_html=True)
    
    # Mikrofon (STT) Butonu
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
    <button onclick="startDictation()" style="width: 100%; background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%); color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 5px; margin-bottom: 10px; box-shadow: 0 4px 10px rgba(236, 72, 153, 0.3);">
        🎤 Sesle Yaz (Mikrofon)
    </button>
    """, unsafe_allow_html=True)
    
    

# --- SOHBET HAFIZASI VE OTURUM YÖNETİMİ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekranda lüks balonlar halinde göster
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        if "image" in msg:
            st.markdown(f'<div class="ai-bubble">{msg["content"]}<br><img src="{msg["image"]}" style="width:100%; border-radius:10px; margin-top:10px;"></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

# --- ANA SOHBET DÖNGÜSÜ ---
if user_query := st.chat_input("Eymen AI'a birşeyler sor..."):
    
    st.markdown(f'<div class="user-bubble">{user_query}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # KULLANICI FOTOĞRAF İSTİYORSA
    if user_query.lower().startswith("foto oluştur,görsel,resim,hayal et,oluştur,çiz vb. "):
        with st.spinner("V2 Medya Motoru Görseli Hazırlıyor..."):
            prompt = user_query[6:] # 'foto ' kısmını ayır
            encoded_prompt = urllib.parse.quote(prompt)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            ai_response = f"İşte istediğin görsel: {prompt}"
            
            st.markdown(f'<div class="ai-bubble">{ai_response}<br><img src="{image_url}" style="width:100%; border-radius:10px; margin-top:10px;"></div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": ai_response, "image": image_url})
            
    # KULLANICI NORMAL SOHBET EDİYORSA
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
                    if "image" not in m: # Sadece metinleri geçmişe ekle
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
                st.error(f"Bir hata oluştu: {str(e)}")

# --- TASARIM VE ALT BİLGİ ---
st.write("---")
st.markdown(
    "<p style='text-align: center; color: #475569; font-size: 0.85rem;'>"
    "Eymen AI V2 © 2026 | Tüm Özellikler Aktif"
    "</p>", 
    unsafe_allow_html=True
)
