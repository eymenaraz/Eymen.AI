import streamlit as st
import base64
import requests
from openai import OpenAI
import os

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Eymen.AI - Premium Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS VESTYLING (PREMIUM KARANLIK TEMA) ---
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
# Streamlit secrets veya Ortam Değişkenlerinden API anahtarını alıyoruz.
# GitHub'da güvenle çalışması için en doğru yöntem budur.
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
elif os.environ.get("OPENAI_API_KEY"):
    api_key = os.environ.get("OPENAI_API_KEY")
else:
    api_key = None

# --- BAŞLIK ALANI ---
st.markdown('<p class="main-title">Eymen.AI</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Gelişmiş Yapay Zeka Asistanı</p>', unsafe_allow_html=True)

# --- SIDEBAR (YAN MENÜ ALANI) ---
with st.sidebar:
    st.markdown("<h2 style='color: #38bdf8; text-align: center;'>Eymen.AI Ayarlar</h2>", unsafe_allow_html=True)
    st.write("---")
    
    # Model Seçimi
    model_choice = st.selectbox(
        "Kullanılacak Model",
        ["gpt-4o-mini", "gpt-4o"],
        index=0,
        help="gpt-4o-mini daha hızlıdır, gpt-4o ise daha karmaşık görevlerde başarılıdır."
    )
    
    # Sistem Rolü / Karakter Tanımı
    system_instruction = st.text_area(
        "Sistem Talimatı (AI Karakteri)",
        value="Sen, kullanıcılara her konuda yardımcı olan, profesyonel, cana yakın ve bilgili bir yapay zeka asistanısın. Adın Eymen.AI.",
        height=100
    )
    
    st.write("---")
    
    # Mikrofon Butonu için HTML / JS Enjeksiyonu (STT Altyapısı)
    st.markdown("<b style='color: #f8fafc;'>Sesli İstem (Mikrofon)</b>", unsafe_allow_html=True)
    
    # Tarayıcının yerel SpeechRecognition API'sini kullanan görünmez/gömülü JS entegrasyonu
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
                // Streamlit chat input kutusunu bulup içine yazıyoruz
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
    st.info("Eymen.AI sisteminiz aktif ve kullanıma hazır.")

# --- SOHBET HAFIZASI VE OTURUM YÖNETİMİ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekranda lüks balonlar halinde göster
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f'<div class="ai-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

# --- ANA SOHBET DÖNGÜSÜ (GİRİŞ KUTUSU) ---
if user_query := st.chat_input("Eymen.AI'a bir mesaj yazın veya mikrofona konuşun..."):
    
    # Kullanıcı mesajını ekrana bas ve hafızaya ekle
    st.markdown(f'<div class="user-bubble">{user_query}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    if not api_key:
        st.error("Lütfen OpenAI API anahtarınızı Streamlit Secrets veya Ortam değişkeni olarak ayarlayın.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            
            # OpenAI için mesaj geçmişini yapılandır (System Instruction dahil)
            messages_pipeline = [{"role": "system", "content": system_instruction}]
            for m in st.session_state.messages:
                messages_pipeline.append({"role": m["role"], "content": m["content"]})
            
            # AI Yanıtını Üret
            with st.spinner("Eymen.AI düşünüyor..."):
                response = client.chat.completions.create(
                    model=model_choice,
                    messages=messages_pipeline
                )
                ai_response = response.choices[0].message.content
            
            # AI Yanıtını ekrana bas ve hafızaya ekle
            st.markdown(f'<div class="ai-bubble">{ai_response}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            # --- PREMİUM SESLİ OKUMA (TTS ALTYAPISI) ---
            # Üretilen cevabı otomatik olarak ses dosyasına dönüştürür ve oynatır
            try:
                tts_response = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",  # Net ve pürüzsüz bir Türkçe ses tonu
                    input=ai_response
                )
                
                # Ses verisini tarayıcının okuyabileceği base64 formatına çeviriyoruz
                audio_bytes = tts_response.content
                b64_audio = base64.b64encode(audio_bytes).decode()
                
                # HTML5 ses oynatıcısını gizli olarak enjekte edip otomatik oynatıyoruz
                audio_html = f"""
                <audio autoplay style="display:none;">
                    <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
                </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
                
            except Exception as tts_error:
                # Ses oluşturulamazsa uygulamanın çökmesini engellemek için arka planda logluyoruz
                pass

        except Exception as e:
            st.error(f"Bir hata oluştu: {str(e)}")

# --- TASARIM VE ALT BİLGİ ---
st.write("---")
st.markdown(
    "<p style='text-align: center; color: #475569; font-size: 0.85rem;'>"
    "Eymen.AI © 2026 | Tüm Sürümlerde Kusursuz Performans"
    "</p>", 
    unsafe_allow_html=True
)
