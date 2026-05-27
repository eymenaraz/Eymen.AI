import streamlit as st
import json
import os
import urllib.parse
import google.generativeai as genai

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Eymen.AI - Premium Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS VE STYLING (PREMIUM KARANLIK TEMA) ---
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
    
    /* Başlık Alanı */
    .main-title {
        background: linear-gradient(90deg, #38bdf8, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
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
# Streamlit secrets panelinde 10 key de olsa, kod "GEMINI_API_KEY" yazanı bulup çeker.
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
elif os.environ.get("GEMINI_API_KEY"):
    api_key = os.environ.get("GEMINI_API_KEY")
else:
    api_key = None

# --- BAŞLIK ALANI ---
st.markdown('<p class="main-title">Eymen.AI</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Google Gemini & Görsel Üretim Destekli Asistan</p>', unsafe_allow_html=True)

# --- SIDEBAR (YAN MENÜ ALANI) ---
with st.sidebar:
    st.markdown("<h2 style='color: #38bdf8; text-align: center;'>Eymen.AI Ayarlar</h2>", unsafe_allow_html=True)
    st.write("---")
    
    model_choice = st.selectbox(
        "Kullanılacak Model",
        ["gemini-1.5-flash", "gemini-1.5-pro"],
        index=0
    )
    
    system_instruction = st.text_area(
        "Sistem Talimatı (AI Karakteri)",
        value="Sen Eymen.AI adında, kullanıcılara her konuda yardımcı olan, profesyonel ve bilgili bir yapay zeka asistanısın.",
        height=100
    )
    
    st.write("---")
    
    st.markdown("<b style='color: #f8fafc;'>Sesli İstem (Mikrofon)</b>", unsafe_allow_html=True)
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
    <button onclick="startDictation()" style="width: 100%; background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%); color: white; border: none; padding: 10px; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 5px; margin-bottom: 15px;">
        🎤 Mikrofonu Aç (Türkçe Konuş)
    </button>
    """, unsafe_allow_html=True)
    
    st.write("---")
    st.info("💡 Fotoğraf üretmek için mesaja '/foto' yazarak başlayın. (Örnek: /foto kırmızı bir araba)")

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
if user_query := st.chat_input("Eymen.AI'a bir mesaj yazın, '/foto' ile görsel isteyin veya mikrofona konuşun..."):
    
    st.markdown(f'<div class="user-bubble">{user_query}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # KULLANICI FOTOĞRAF İSTİYORSA
    if user_query.lower().startswith("/foto "):
        with st.spinner("Eymen.AI görseli oluşturuyor..."):
            prompt = user_query[6:] # '/foto ' kısmını ayır
            encoded_prompt = urllib.parse.quote(prompt)
            # Ücretsiz ve anlık görsel oluşturma API'si
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            ai_response = f"İşte istediğin görsel: {prompt}"
            
            st.markdown(f'<div class="ai-bubble">{ai_response}<br><img src="{image_url}" style="width:100%; border-radius:10px; margin-top:10px;"></div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": ai_response, "image": image_url})
            
    # KULLANICI NORMAL SOHBET EDİYORSA
    else:
        if not api_key:
            st.error("Lütfen Google Gemini API anahtarınızı Streamlit Secrets panelinde GEMINI_API_KEY olarak ayarlayın.")
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
                
                with st.spinner("Eymen.AI düşünüyor..."):
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
    "Eymen.AI © 2026 | Tüm Özellikler Aktif (Sıfır Hata)"
    "</p>", 
    unsafe_allow_html=True
)
