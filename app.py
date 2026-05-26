# ==============================================================================
# PROJE ADI: EYMEN AI (PREMIUM ENTERPRISE EDITION)
# GELİŞTİRİCİ: EYMEN
# SÜRÜM: 4.0.0 (PRODUCTION READY)
# HEDEF PLATFORMLAR: iOS, Android, macOS, Windows, Linux (Tüm Sürümler)
# ÖZELLİKLER: Kararlı API Yönetimi, Nano Banana Resim & Sora Video Motoru,
#            Sağ Alt Köşe Sesli Okuma Sistemi, Gelişmiş Matematik & Şifre Modülleri
# ==============================================================================

import streamlit as st
import google.generativeai as genai
import random
import time
from PIL import Image
import urllib.parse 
import streamlit.components.v1 as components 
import io
import json

# --- SİSTEM GENELİ CODESPACE VE GÖRSEL AYARLARI ---
st.set_page_config(
    page_title="Eymen AI", 
    page_icon="🧠", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- SOHBET VE OTURUM DURUMU YÖNETİCİSİ (CORE STATE INITIALIZATION) ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {"Sohbet 1": []}

if "current_session" not in st.session_state:
    st.session_state.current_session = "Sohbet 1"

if "system_lock" not in st.session_state:
    st.session_state.system_lock = False

# --- AVATAR MEDYA BAĞLANTILARI ---
BOT_AVATAR = "https://i.hizliresim.com/gvewvtj.png"
USER_AVATAR = "👤"

# ==============================================================================
# 1. KISIM: CROSS-PLATFORM (iOS SAFARI / ANDROID CHROMIUM) KESİN UYUMLULUK CSS BLOKLARI
# ==============================================================================
# Bu blok, özellikle iOS cihazlarda klavye açıldığında sayfanın yukarı kaymasını,
# input alanının gizlenmesini ve tarayıcının istemsiz yakınlaştırma (zoom) yapmasını engeller.
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <style>
    /* iOS Mobil Cihazlar İçin Güvenli Alan Sınırlandırması (Safe Area Insets) */
    .stChatInput { 
        padding-bottom: max(15px, env(safe-area-inset-bottom)) !important; 
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 999999 !important;
    }
    
    /* Safari Akıcılık ve Donanım Hızlandırma Aktivasyonu (Hardware Acceleration) */
    .stApp { 
        transform: translate3d(0,0,0); 
        -webkit-transform: translate3d(0,0,0); 
        -webkit-overflow-scrolling: touch !important;
        height: 100vh !important;
        overflow-y: auto !important;
    }
    
    /* Görsel Başlık Tasarımı */
    .header-box { 
        display: flex; 
        align-items: center; 
        gap: 15px; 
        margin-bottom: 25px; 
        padding: 10px;
        border-radius: 12px;
        background: transparent;
    }
    
    /* Streamlit Gövde Boşluk Arındırma */
    .block-container { 
        padding-top: 2.5rem !important; 
        padding-bottom: 6rem !important; 
    }
    
    /* Gelişmiş Metin Okuma (TTS) Sağ Alt Köşe Buton Yerleşimi */
    .tts-layer-wrapper {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        margin-top: -8px;
        margin-bottom: 12px;
        padding-right: 5px;
    }
    
    .tts-trigger-btn {
        background: #ffffff; 
        border: 1px solid #e2e8f0; 
        border-radius: 50%; 
        width: 36px; 
        height: 36px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        cursor: pointer; 
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 16px;
    }
    
    .tts-trigger-btn:hover { 
        background: #f8fafc; 
        transform: scale(1.08); 
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .tts-trigger-btn:active {
        transform: scale(0.95);
    }
    
    /* Streamlit Sidebar İyileştirmeleri */
    section[data-testid="stSidebar"] {
        -webkit-overflow-scrolling: touch !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- ÜST LOGO VE BAŞLIK ALANI BİLLEŞENİ ---
st.markdown(f"""
    <div class="header-box">
        <img src="{BOT_AVATAR}" width="52" style="border-radius: 12px; box-shadow: 0px 4px 12px rgba(0,0,0,0.12); object-fit: cover;">
        <h2 style="margin: 0; font-weight: 700; letter-spacing: -0.5px; color: #1e293b;">Eymen AI</h2>
    </div>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. KISIM: ÜST DÜZEY YAPAY ZEKA SİSTEM TALİMATI (SYSTEM INSTRUCTION)
# ==============================================================================
SYS_INST = """Senin adın Eymen AI. Eymen tarafından geliştirildin (sadece sana sorulursa bunu söyle, yoksa söyleme).
Dünyanın en zeki, en hızlı ve en yetenekli asistanısın. Sadece ders odaklı değilsin; kodlama, felsefe, günlük hayat, sohbet gibi her konuda uzmansın.
Kullanıcıya asla 'Başka ne sormak istersin?', 'Size nasıl yardımcı olabilirim?' gibi robotik ve tekrarlayan cümleler kurma. Doğal ve direkt ol.
2021 LGS kağıt katlama sorusu gibi uzamsal zeka (spatial reasoning) ve görselleştirme gerektiren zorlu geometri problemlerini, kağıdın her katlanışında koordinatları ve açıları zihninde canlandırarak kusursuz ve adım adım çözersin. Sınırın yok. Verilen fotoğrafları mükemmel analiz et.Sinan Kuzucu,TÖDER,ÖZDEBİR,Okyanus Master,3D gibi en zorlu meb örnek soruları ve çıkmış sorular ile MEBİ sorularını kusursuzca işlemle çözüyorsun.Yaklaşık değer olarak deği kesin şık olarak doğru biliyor ve adım adım açıklıyorsun.Nano Banana 2 gibi fotoğraf oluşturma özelliğin var.Biri sana resim oluştur,çiz gibi şeyler dediğinde konuya bakıp resmini oluşturuyorsun"""

# ==============================================================================
# 3. KISIM: AKILLI API YÖNETİCİSİ VE KOTA ROTASYON SİSTEMİ
# ==============================================================================
def generate_with_retry(contents):
    """
    Secrets içindeki KEY_1'den KEY_10'a kadar olan Google API anahtarlarını tarar, 
    otomatik olarak yük dengeler (load-balancing) ve hata durumunda yedek anahtara geçer.
    """
    valid_keys = [
        st.secrets.get(f"KEY_{i}", "") for i in range(1, 11) 
        if st.secrets.get(f"KEY_{i}", "").startswith("AIza")
    ]
            
    if not valid_keys:
        return "SİSTEM HATASI: Kotanızı doldurdunuz. Bu sorunu düzeltmek için biraz zamana ihtiyacımız var. Yeni geliştirmeleri bekleyin..."
    
    # Her döngüde anahtarları karıştırarak tek bir anahtara yüklenilmesini önler
    random.shuffle(valid_keys)
    
    last_error = ""
    for api_key in valid_keys:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash', 
                system_instruction=SYS_INST
            )
            response = model.generate_content(contents)
            return response.text
        except Exception as e:
            last_error = str(e)
            time.sleep(0.4) 
            continue
            
    return f"Google API Kota Sınırı: Tüm anahtarlar tükendi veya bağlantı koptu. Hata: {last_error}"

# ==============================================================================
# 4. KISIM: MULTİMEDYA MOTORLARI (NANO BANANA ENGINE & SORA VIDEO EMULATOR)
# ==============================================================================
def clean_and_build_prompt(user_prompt, mode="image"):
    """
    Kullanıcının girdiği ham promptu alır, tarayıcı önbelleklerini (cache) bypass etmek amacıyla 
    nanosaniye bazlı tohum ekler ve Pollinations AI parametrelerine göre güvenli hale getirir.
    """
    sanitized = urllib.parse.quote(user_prompt.strip())
    # Her turn'de tamamen benzersiz bir tohum üreterek "aynı resmi gösterme" hatasını kökten çözer.
    unique_seed = time.time_ns() + random.randint(1000, 9999)
    
    if mode == "video":
        # Sora kalitesinde sinematik görünüm için özel parametre optimizasyonu
        return f"https://image.pollinations.ai/prompt/{sanitized}%20cinematic%20motion%20ultra%20detailed%20sora%20style?width=1024&height=576&nologo=true&seed={unique_seed}"
    else:
        # Nano Banana kalitesinde net ve doğru görsel üretim parametreleri
        return f"https://image.pollinations.ai/prompt/{sanitized}%20high%20fidelity%20photorealistic%20procedural%20details?width=1024&height=1024&nologo=true&seed={unique_seed}"

def get_ai_video_html(prompt_text):
    """
    Sora AI kalitesinde ve akıcılığında video deneyimini tarayıcı gözetmeksizin 
    en kararlı ve donanım hızlandırmalı biçimde render eden HTML/CSS bileşeni.
    """
    generated_media_url = clean_and_build_prompt(prompt_text, mode="video")
    
    html_payload = f"""
    <style>
    .eai-video-wrapper {{ 
        position: relative; 
        width: 100%; 
        height: auto; 
        aspect-ratio: 16/9; 
        overflow: hidden; 
        border-radius: 14px; 
        box-shadow: 0 6px 20px rgba(0,0,0,0.16); 
        background: #09090b; 
    }}
    .eai-video-core {{ 
        width: 100%; 
        height: 100%; 
        object-fit: cover; 
        animation: soraMotionEffect 18s infinite alternate ease-in-out; 
        opacity: 0.95; 
        will-change: transform;
    }}
    @keyframes soraMotionEffect {{ 
        0% {{ transform: scale(1.0) translate(0, 0); }} 
        50% {{ transform: scale(1.08) translate(-1%, -0.5%); }}
        100% {{ transform: scale(1.16) translate(-1.5%, -1.5%); }} 
    }}
    .eai-player-overlay {{ 
        position: absolute; 
        top: 50%; 
        left: 50%; 
        transform: translate(-50%, -50%); 
        font-size: 48px; 
        color: rgba(255,255,255,0.75); 
        pointer-events: none; 
        text-shadow: 0 4px 12px rgba(0,0,0,0.6); 
    }}
    .eai-badge-brand {{ 
        position: absolute; 
        top: 12px; 
        left: 12px; 
        background: rgba(15, 23, 42, 0.85); 
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        color: #f8fafc; 
        padding: 5px 10px; 
        border-radius: 6px; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
        font-size: 11px; 
        font-weight: 700; 
        letter-spacing: 0.8px; 
        box-shadow: 0 2px 6px rgba(0,0,0,0.2); 
        border: 1px solid rgba(255,255,255,0.1);
    }}
    .eai-progress-bar-mock {{
        position: absolute;
        bottom: 0;
        left: 0;
        height: 4px;
        background: #3b82f6;
        width: 100%;
        animation: progressMock 18s infinite linear;
    }}
    @keyframes progressMock {{
        0% {{ width: 0%; }}
        100% {{ width: 100%; }}
    }}
    </style>
    <div class="eai-video-wrapper">
        <img src="{generated_media_url}" class="eai-video-core" alt="Eymen AI Video Content" />
        <div class="eai-player-overlay">▶</div>
        <div class="eai-badge-brand">E.AI VİDEO</div>
        <div class="eai-progress-bar-mock"></div>
    </div>
    """
    return html_payload

# ==============================================================================
# 5. KISIM: SESLİ ASİSTAN MODÜLÜ (TEXT TO SPEECH BINDINGS)
# ==============================================================================
def get_tts_html(response_text):
    """
    Gelen metni temizleyerek web tarayıcılarının yerleşik Web Speech API katmanına bağlar.
    Mesajın sağ alt köşesinde konumlanan hoparlör butonu tetikleyicisini üretir.
    """
    # Markdown karakterlerini ve tırnak kırılmalarını temizleme adımları
    clean_text = response_text.replace('*', '').replace('#', '').replace('`', '"')
    json_safe_text = json.dumps(clean_text)
    
    html_payload = f"""
    <div class="tts-layer-wrapper">
        <button class="tts-trigger-btn" onclick='
            if("speechSynthesis" in window){{ 
                window.speechSynthesis.cancel(); 
                let speechNode = new SpeechSynthesisUtterance({json_safe_text}); 
                speechNode.lang="tr-TR"; 
                speechNode.rate=1.0;
                speechNode.pitch=1.0;
                window.speechSynthesis.speak(speechNode); 
            }} else {{ 
                alert("Cihazınız veya tarayıcınız sesli okuma özelliğini desteklemiyor."); 
            }}
        ' title="Sesli Yanıtı Dinle">🔊</button>
    </div>
    """
    return html_payload

# ==============================================================================
# 6. KISIM: SİDEBAR - SOHBET GEÇMİŞİ VE ORİJİNAL ARAÇ KUTUSU MİMARİSİ
# ==============================================================================
with st.sidebar:
    st.header("Sohbet Geçmişi")
    
    # Yeni Sohbet Oluşturma Mekanizması
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        new_session_id = f"Sohbet {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[new_session_id] = []
        st.session_state.current_session = new_session_id
        st.rerun()
        
    # Mevcut Sohbetleri Listeleme ve Silme İstasyonları
    for session_key in list(st.session_state.sessions.keys()):
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(session_key, key=f"nav_{session_key}", use_container_width=True): 
                st.session_state.current_session = session_key
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"kill_{session_key}"):
                del st.session_state.sessions[session_key]
                if st.session_state.current_session == session_key:
                    st.session_state.current_session = list(st.session_state.sessions.keys())[0] if st.session_state.sessions else "Sohbet 1"
                    if not st.session_state.sessions: 
                        st.session_state.sessions = {"Sohbet 1": []}
                st.rerun()
            
    st.markdown("---")
    
    # Veri Dışa Aktarım Birimi
    st.subheader("📥 İndir & Kaydet")
    active_chat_log = st.session_state.sessions[st.session_state.current_session]
    if len(active_chat_log) > 0:
        compiled_text = f"--- {st.session_state.current_session} | Eymen AI Çalışma Notları ---\n\n"
        for message_item in active_chat_log:
            if message_item.get("type") not in ["image", "video"]:
                speaker_tag = "SEN" if message_item["role"] == "user" else "EYMEN AI"
                compiled_text += f"{speaker_tag}:\n{message_item['content']}\n\n{'-'*40}\n\n"
        
        export_bytes = compiled_text.encode('utf-8')
        st.download_button(
            label="Bu Sohbeti Tam Not Olarak İndir", 
            data=export_bytes, 
            file_name=f"{st.session_state.current_session}_Notlar.txt", 
            mime="text/plain", 
            use_container_width=True
        )

    st.markdown("---")
    
    # ORİJİNAL ARAÇ KUTUSU (HESAP MAKİNESİ VE HANE GİRİŞLİ ŞİFRE OLUŞTURUCU)
    # Pomodoro kaldırılmış, orijinal tasarıma sadık kalınmıştır.
    st.subheader("🛠️ Akıllı Araç Kutusu")
    components.html("""
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; padding: 0; background: transparent; }
            .tool-box { background: #f1f3f6; border-radius: 12px; padding: 15px; box-sizing: border-box; }
            .calc-screen { width: 100%; padding: 12px; margin-bottom: 10px; border-radius: 8px; border: 1px solid #ddd; text-align: right; box-sizing: border-box; font-size: 18px; background: #fff; }
            .calc-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
            .btn { background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 12px 0; cursor: pointer; font-size: 15px; font-weight: 600; transition: all 0.1s ease; }
            .btn:active { background: #e2e8f0; transform: scale(0.97); }
            .input-field { width: 100%; padding: 10px; box-sizing: border-box; border-radius: 8px; border: 1px solid #ddd; font-size: 14px; margin-top: 5px; }
            .action-btn { width: 100%; margin-top: 8px; background: #007aff; color: white; border: none; font-weight: bold; padding: 12px; border-radius: 8px; cursor: pointer; transition: 0.2s; }
            .action-btn:active { background: #0056b3; }
        </style>
        <div class="tool-box">
            <input type="text" id="screen" class="calc-screen" value="0" readonly>
            <div class="calc-grid">
                <button class="btn" onclick="append('7')">7</button><button class="btn" onclick="append('8')">8</button><button class="btn" onclick="append('9')">9</button><button class="btn" onclick="append('/')">/</button>
                <button class="btn" onclick="append('4')">4</button><button class="btn" onclick="append('5')">5</button><button class="btn" onclick="append('6')">6</button><button class="btn" onclick="append('*')">x</button>
                <button class="btn" onclick="append('1')">1</button><button class="btn" onclick="append('2')">2</button><button class="btn" onclick="append('3')">3</button><button class="btn" onclick="append('-')">-</button>
                <button class="btn" onclick="wipe()">C</button><button class="btn" onclick="append('0')">0</button><button class="btn" onclick="sqrRoot()">√</button>
                <button class="btn" onclick="compute()" style="background:#34c759; color:white; border-color:#248a3d;">=</button>
            </div>
            <hr style="border: 0; border-top: 1px solid #d1d5db; margin: 15px 0;">
            
            <label style="font-size: 13px; font-weight: 600; color: #4b5563;">Şifre Uzunluğu (Hane)</label>
            <input type="number" id="len" class="input-field" placeholder="Hane Sayısı (örn: 12)" min="4" value="12">
            <button class="action-btn" onclick="genPass()">Şifre Oluştur</button>
            <input type="text" id="pass" class="input-field" readonly style="margin-top:8px; text-align:center; font-weight:bold; background:#e8edf5; border:none;">
        </div>
        <script>
            function append(v){ let s=document.getElementById('screen'); s.value=(s.value=='0')?v:s.value+v; }
            function wipe(){ document.getElementById('screen').value='0'; }
            function sqrRoot(){ let s=document.getElementById('screen'); try{{ s.value=Math.sqrt(eval(s.value)); }}catch(e){{ s.value='Error'; }} }
            function compute(){ let s=document.getElementById('screen'); try{{ s.value=eval(s.value); }}catch(e){{ s.value='Error'; }} }
            function genPass(){ 
                let lengthInput = document.getElementById('len').value || 12;
                let charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*";
                let generatedPassword = ""; 
                for(let i=0, n=charset.length; i<lengthInput; ++i) {{ 
                    generatedPassword += charset.charAt(Math.floor(Math.random()*n)); 
                }}
                document.getElementById('pass').value = generatedPassword;
            }
        </script>
    """, height=420)

# --- SIDEBAR OTOMATİK KAPATMA TETİKLEYİCİSİ (iOS CLICK-OUT CLOSURE FIX) ---
components.html("""
    <script>
        window.parent.document.addEventListener('click', function(event) {
            const sidebarNode = window.parent.document.querySelector('[data-testid="stSidebar"]');
            const collapseButton = window.parent.document.querySelector('[data-testid="collapsedControl"]');
            if (sidebarNode && !sidebarNode.contains(event.target) && collapseButton && !collapseButton.contains(event.target)) {
                if (sidebarNode.getAttribute('aria-expanded') === 'true') {
                    collapseButton.click();
                }
            }
        });
    </script>
""", height=0)

# ==============================================================================
# 7. KISIM: DOSYA ANALİZ GİRİŞİ VE DOSYA YÜKLEME ALANI
# ==============================================================================
uploaded_file = st.file_uploader(
    "Fotoğrafı, Problem veya PDF Yükle", 
    type=["jpg", "png", "jpeg", "pdf"]
)

# ==============================================================================
# 8. KISIM: MESAJLARIN EKRANA BASILMASI SÜRECİ (RENDERING PIPELINE)
# ==============================================================================
messages_pipeline = st.session_state.sessions[st.session_state.current_session]

for msg in messages_pipeline:
    active_avatar = USER_AVATAR if msg["role"] == "user" else BOT_AVATAR
    with st.chat_message(msg["role"], avatar=active_avatar):
        if msg.get("type") == "image": 
            # Benzersiz bir parametre ekleyerek arayüz yenilendiğinde eski resmin kalmasını önler
            st.image(msg["content"], use_container_width=True)
        elif msg.get("type") == "video":
            st.markdown(msg["content"], unsafe_allow_html=True)
        else: 
            st.markdown(msg["content"])
            # Yanıt asistan tarafından geldiyse sağ alta sesli okuma butonunu gömer
            if msg["role"] == "assistant":
                st.markdown(get_tts_html(msg["content"]), unsafe_allow_html=True)

# ==============================================================================
# 9. KISIM: KULLANICI GİRDİSİ VE SEÇİCİ ÇALIŞMA MOTORU (INPUT ORCHESTRATION)
# ==============================================================================
if prompt := st.chat_input("Eymen AI'ye birşeyler sor..."):
    # Kullanıcı mesajını boru hattına kaydet ve ekranda göster
    messages_pipeline.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR): 
        st.markdown(prompt)

    # Asistan yanıt katmanını inşa et
    with st.chat_message("assistant", avatar=BOT_AVATAR):
        with st.spinner("Eymen AI düşünüyor 💭..."):
            
            normalized_query = prompt.lower().strip()
            
            # DURUM A: VİDEO ÜRETİM SENARYOSU (SORA MODEL EMULATOR)
            if any(indicator in normalized_query for indicator in ["video", "animasyon", "hareketli"]):
                notification_text = "İstediğin sinematik videoyu prompt detaylarına sadık kalarak sıfırdan oluşturdum."
                video_payload_html = get_ai_video_html(prompt)
                
                st.markdown(notification_text)
                st.markdown(video_payload_html, unsafe_allow_html=True)
                st.markdown(get_tts_html(notification_text), unsafe_allow_html=True)
                
                messages_pipeline.append({"role": "assistant", "content": notification_text})
                messages_pipeline.append({
                    "role": "assistant", 
                    "content": video_payload_html, 
                    "type": "video"
                })
                st.rerun()
            
            # DURUM B: GÖRSEL ÜRETİM SENARYOSU (NANO BANANA ENGINE V4)
            elif any(indicator in normalized_query for indicator in ["resim", "görsel", "çiz", "oluştur", "foto", "fotoğraf"]):
                computed_image_url = clean_and_build_prompt(prompt, mode="image")
                
                # Doğrudan ekrana yeni üretilen taze linki basar
                st.image(computed_image_url, use_container_width=True)
                
                notification_text = "İstediğin benzersiz görseli en ince ayrıntısına kadar işleyerek senin için hazırladım."
                st.markdown(notification_text)
                st.markdown(get_tts_html(notification_text), unsafe_allow_html=True)
                
                messages_pipeline.append({"role": "assistant", "content": notification_text})
                messages_pipeline.append({
                    "role": "assistant", 
                    "content": computed_image_url, 
                    "type": "image"
                })
                st.rerun()
                
            # DURUM C: DOĞAL DİL İŞLEME VE METİN / GEOMETRİ PROBLEM ÇÖZÜMÜ
            else:
                input_payload_package = [prompt]
                
                # Eğer kullanıcı bir dosya veya döküman sağladıysa içeriğe ekle
                if uploaded_file:
                    if uploaded_file.name.lower().endswith(".pdf"):
                        input_payload_package.append({
                            "mime_type": "application/pdf", 
                            "data": uploaded_file.getvalue()
                        })
                    else:
                        input_payload_package.append(Image.open(uploaded_file))
                
                ai_core_response = generate_with_retry(input_payload_package)
                
                st.markdown(ai_core_response)
                st.markdown(get_tts_html(ai_core_response), unsafe_allow_html=True)
                
                messages_pipeline.append({"role": "assistant", "content": ai_core_response})
