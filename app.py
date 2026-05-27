# ==============================================================================
# PROJE ADI: EYMEN AI V2 (ULTIMATE PREMIUM EDITION)
# ÖZELLİKLER: Görsel Zeka Motoru, Kusursuz Arayüz, Akıllı Araçlar, Bağlamsal Hafıza
# GELİŞTİRME: Kişi/Nesne Tanıma, Sürekli Görsel Döngüsü, Kesin TTS Kararlılığı
# ==============================================================================

import streamlit as st
import google.generativeai as genai
import random
import time
from PIL import Image
import urllib.parse 
import streamlit.components.v1 as components 
import json

# ==============================================================================
# 1. KISIM: SİSTEM GENELİ CODESPACE VE OTURUM YÖNETİMİ
# ==============================================================================
st.set_page_config(
    page_title="Eymen AI V2", 
    page_icon="🧠", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# Sohbet oturumları ve hafıza başlatma
if "sessions" not in st.session_state: 
    st.session_state.sessions = {"Sohbet 1": []}
if "current_session" not in st.session_state: 
    st.session_state.current_session = "Sohbet 1"

BOT_AVATAR = "https://i.hizliresim.com/gvewvtj.png"
USER_AVATAR = "👤"

# ==============================================================================
# 2. KISIM: CSS MOTORU VE TASARIM (EKRANA SIZMAYAN KUSURSUZ VE PREMIUM YAPI)
# ==============================================================================
# Fontlar, gölgelendirmeler, giriş kutusu tasarımı ve premium görünüm detaylandırıldı
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, Roboto, sans-serif !important;
    background-color: #090d16 !important;
    color: #f1f5f9 !important;
}

.stChatInput { 
    padding-bottom: max(20px, env(safe-area-inset-bottom)) !important; 
    position: fixed !important; 
    bottom: 0 !important; 
    left: 0 !important; 
    right: 0 !important; 
    z-index: 999999 !important; 
    background-color: transparent !important;
}

.stChatInput textarea {
    background-color: #131c2e !important;
    color: #ffffff !important;
    border: 1px solid rgba(59, 130, 246, 0.3) !important;
    border-radius: 14px !important;
    font-size: 15px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stChatInput textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 15px rgba(59, 130, 246, 0.6) !important;
}

.stApp { 
    transform: translate3d(0,0,0); 
    -webkit-transform: translate3d(0,0,0); 
    -webkit-overflow-scrolling: touch !important; 
    height: 100vh !important; 
    overflow-y: auto !important; 
}

.header-box { 
    display: flex; 
    align-items: center; 
    gap: 18px; 
    margin-bottom: 20px; 
    padding: 15px; 
    border-radius: 16px; 
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.8) 100%); 
    border: 1px solid rgba(255,255,255,0.05);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.block-container { 
    padding-top: 2.5rem !important; 
    padding-bottom: 8.5rem !important; 
}

.tts-layer-wrapper { 
    display: flex; 
    justify-content: flex-end; 
    align-items: center; 
    margin-top: -5px; 
    margin-bottom: 20px; 
    padding-right: 8px; 
}

.tts-trigger-btn { 
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
    border: 1px solid rgba(59, 130, 246, 0.4); 
    border-radius: 50%; 
    width: 40px; 
    height: 40px; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    cursor: pointer; 
    box-shadow: 0 4px 12px rgba(0,0,0,0.3); 
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); 
    font-size: 18px; 
}

.tts-trigger-btn:hover { 
    background: #3b82f6; 
    transform: scale(1.12) rotate(5deg); 
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5); 
}

.loading-container { 
    display: flex; 
    align-items: center; 
    gap: 12px; 
    font-family: 'SF Pro Display', sans-serif; 
    font-weight: 600; 
    color: #3b82f6; 
    padding: 14px 20px; 
    border-radius: 12px; 
    background: rgba(59, 130, 246, 0.12); 
    margin-bottom: 20px; 
    border-left: 5px solid #3b82f6; 
    width: fit-content; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.2); 
    animation: fadeIn 0.3s ease-out;
}

.premium-img-frame {
    width: 100%;
    border-radius: 16px;
    border: 2px solid rgba(59, 130, 246, 0.4);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
    margin-top: 10px;
    margin-bottom: 15px;
    transition: transform 0.4s ease;
}

.premium-img-frame:hover {
    transform: scale(1.015);
    border-color: #3b82f6;
}

.dots-wrapper { 
    display: flex; 
    gap: 6px; 
    align-items: center; 
    margin-top: 2px; 
}

.dot { 
    width: 8px; 
    height: 8px; 
    background-color: #3b82f6; 
    border-radius: 50%; 
    animation: bounce 1.4s infinite ease-in-out both; 
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce { 
    0%, 80%, 100% { transform: scale(0); } 
    40% { transform: scale(1); } 
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Sidebar Özelleştirmeleri */
[data-testid="stSidebar"] {
    background-color: #0c1322 !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. KISIM: ANA EKRAN YERLEŞİMİ (BAŞLIK VE DOSYA YÜKLEME)
# ==============================================================================
# Eymen AI V2 Başlığı - En Üstte
st.markdown(f"""
<div class="header-box">
    <img src="{BOT_AVATAR}" width="58" style="border-radius: 15px; box-shadow: 0px 5px 20px rgba(0,0,0,0.4); object-fit: cover;">
    <h1 style="margin: 0; font-weight: 800; color: #ffffff; font-size: 2.3rem; letter-spacing: -0.5px;">Eymen AI <span style="color: #3b82f6; text-shadow: 0 0 15px rgba(59,130,246,0.4);">V2</span></h1>
</div>
""", unsafe_allow_html=True)

# Başlığın hemen altına yerleştirilmiş dosya yükleme alanı
uploaded_file = st.file_uploader("Görsel, Problem veya PDF Dokümanı Yükle", type=["jpg", "png", "jpeg", "pdf"])

st.markdown("---")

# ==============================================================================
# 4. KISIM: YAPAY ZEKA KİMLİĞİ VE API YÖNETİMİ
# ==============================================================================
SYS_INST = """Senin adın Eymen AI V2. Eymen tarafından geliştirildin.
Kullanıcıya asla 'Başka ne sormak istersin?' gibi robotik cümleler kurma. Doğal, kendinden emin ve direkt ol.
2021 LGS kağıt katlama sorusu gibi en zorlu problemleri kusursuz çözersin. MEB ve nitelikli yayıncı sorularını hata yapmadan, kesin şık vererek adım adım açıklarsın.
Gelişmiş Nano Banana 2 mimarisine ve V2 Medya Zekasına sahipsin.Bu yüzden üstüste gelen görsel oluşturma istemlerini gerçekleştir. Kullanıcı görsel isterse bunu üst düzey kaliteyle sağlarsın."""

def get_loading_html(text):
    return f"""
    <div class="loading-container">
        <span style="font-size: 15px;">{text}</span>
        <div class="dots-wrapper">
            <div class="dot"></div><div class="dot"></div><div class="dot"></div>
        </div>
    </div>
    """

def generate_with_retry(contents):
    valid_keys = [st.secrets.get(f"KEY_{i}", "") for i in range(1, 11) if st.secrets.get(f"KEY_{i}", "").startswith("AIza")]
    if not valid_keys: 
        return "🚨 SİSTEM HATASI: API Anahtarları tükenmiş veya hatalı yapılandırılmış."
    
    random.shuffle(valid_keys)
    last_error = ""
    for api_key in valid_keys:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=SYS_INST)
            return model.generate_content(contents).text
        except Exception as e:
            last_error = str(e)
            time.sleep(0.5) 
            continue
    return f"Sistem Geçici Olarak Yanıt Veremiyor. Hata Detayı: {last_error}"

# ==============================================================================
# 5. KISIM: 1080P SÜREKLİ GÖRSEL HAFIZA VE PHOTOSHOP ANALİZ MOTORU
# ==============================================================================
def generate_1080p_image_url(user_prompt, history_pipeline):
    context_memory = ""
    for m in history_pipeline[-12:]: # Analiz derinliği 12 adıma çıkartılarak kılı kırk yarma sağlandı
        if m.get("type") != "image":
            role_label = "Kullanıcı" if m["role"] == "user" else "Eymen AI V2"
            context_memory += f"{role_label}: {m['content']}\n"
            
    # Gelişmiş Kişi, Ünlü, Nesne Tanıma ve Photoshop Kurgu Katmanı
    enhancement_prompt = f"""Aşağıda kullanıcının seninle olan son konuşma geçmişi ve en son isteği yer almaktadır.
Eğer istekte internette veya dünyada bilinen ünlü bir kişi (örn: futbolcu, aktör, tarihi figür) ya da özel bir nesne/kavram geçiyorsa, onun karakteristik fiziksel özelliklerini, yüz yapısını, renk paletini içsel bilgi birikiminle derinlemesine analiz et.
Ardından kullanıcının ardışık photoshop komutlarını (renk değiştirme, nesne ekleme/çıkarma, arka plan manipülasyonu, sahne birleştirme) süzgeçten geçir.
Tüm bu verileri harmanlayarak, Pollinations yapay zeka motorunun sıfır hata ile çizebileceği, 1080p çözünürlükte, ultra detaylı, fotogerçekçi, stüdyo ışıklandırmalı, sinematik ve başyapıt niteliğinde bir İNGİLİZCE Stable Diffusion promptu oluştur.

YALNIZCA nihai İngilizce promptu yaz. Başka hiçbir açıklama, kelime, tırnak işareti veya sembol kullanma.

Geçmiş Bağlam:
{context_memory}

Yeni İstek: {user_prompt}"""
    
    enhanced_english_prompt = generate_with_retry([enhancement_prompt])
    
    # Boş kalma veya çökme durumuna karşı güvenlik koruması
    final_prompt_raw = enhanced_english_prompt.strip() if enhanced_english_prompt else user_prompt
    safe_prompt = urllib.parse.quote(final_prompt_raw)
    
    # Her seferinde benzersiz ve taze görsel tetiklemek için gelişmiş yüksek çözünürlüklü zaman damgası
    unique_seed = random.randint(1000000, 9999999) + int(time.time_ns() % 100000)
    
    # Kesin çalışan 1080p adresi
    return f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1920&height=1080&nologo=true&seed={unique_seed}&enhance=true"

# Sesli Okuma (TTS) Motoru - Yüksek Kararlılık Sürümü
def get_tts_html(response_text):
    clean_text = response_text.replace('*', '').replace('#', '').replace('`', '"').replace('\n', ' ')
    json_safe_text = json.dumps(clean_text)
    return f"""
    <div class="tts-layer-wrapper">
        <button class="tts-trigger-btn" title="Sesli Dinle" onclick='if("speechSynthesis" in window){{ window.speechSynthesis.cancel(); let speechNode = new SpeechSynthesisUtterance({json_safe_text}); speechNode.lang="tr-TR"; speechNode.rate=1.05; window.speechSynthesis.speak(speechNode); }} else {{ alert("Tarayıcınız sesli okumayı desteklemiyor."); }}'>🔊</button>
    </div>
    """

# ==============================================================================
# 6. KISIM: SİDEBAR - PROFESYONEL ARAÇ KUTUSU VE GEÇMİŞ YÖNETİMİ
# ==============================================================================
with st.sidebar:
    st.markdown("### 🗂️ Sohbet Yöneticisi")
    if st.button("➕ Yeni V2 Oturumu", use_container_width=True):
        name = f"Sohbet {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[name] = []
        st.session_state.current_session = name
        st.rerun()
        
    for name in list(st.session_state.sessions.keys()):
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(name, key=f"nav_{name}", use_container_width=True): 
                st.session_state.current_session = name
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"kill_{name}"):
                del st.session_state.sessions[name]
                if st.session_state.current_session == name:
                    st.session_state.current_session = list(st.session_state.sessions.keys())[0] if st.session_state.sessions else "Sohbet 1"
                    if not st.session_state.sessions: st.session_state.sessions = {"Sohbet 1": []}
                st.rerun()
            
    st.markdown("---")
    
    st.markdown("### 📥 Veri Aktarımı")
    current_msgs = st.session_state.sessions[st.session_state.current_session]
    if len(current_msgs) > 0:
        chat_text = f"--- EYMEN AI V2 | SİSTEM RAPORU: {st.session_state.current_session} ---\n\n"
        for m in current_msgs:
            if m.get("type") != "image":
                role_name = "KULLANICI" if m["role"] == "user" else "EYMEN AI V2"
                chat_text += f"{role_name}:\n{m['content']}\n\n{'-'*50}\n\n"
        st.download_button(label="📄 Konuşmayı TXT Olarak İndir", data=chat_text.encode('utf-8'), file_name=f"EymenAI_V2_{st.session_state.current_session}.txt", mime="text/plain", use_container_width=True)

    st.markdown("---")
    
    st.markdown("### 🛠️ Akıllı Araç Kutusu")
    components.html("""
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: transparent; }
            .tool-box { background: #ffffff; border-radius: 12px; padding: 18px; box-sizing: border-box; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
            .calc-screen { width: 100%; padding: 14px; margin-bottom: 12px; border-radius: 8px; border: 1px solid #cbd5e1; text-align: right; font-size: 20px; background: #f8fafc; color: #0f172a; font-weight: 600; outline: none; }
            .calc-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
            .btn { background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 0; cursor: pointer; font-size: 16px; font-weight: 700; color: #334155; transition: all 0.15s ease; }
            .btn:hover { background: #e2e8f0; }
            .btn:active { transform: scale(0.96); }
            .btn-op { background: #e0f2fe; color: #0284c7; border-color: #bae6fd; }
            .btn-eq { background: #10b981; color: white; border-color: #059669; }
            .btn-eq:hover { background: #059669; }
            .input-field { width: 100%; padding: 12px; box-sizing: border-box; border-radius: 8px; border: 1px solid #cbd5e1; margin-top: 6px; font-size: 14px; outline: none; }
            .input-field:focus { border-color: #3b82f6; }
            .action-btn { width: 100%; margin-top: 10px; background: #3b82f6; color: white; border: none; font-weight: bold; padding: 14px; border-radius: 8px; cursor: pointer; transition: background 0.2s; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }
            .action-btn:hover { background: #2563eb; }
        </style>
        <div class="tool-box">
            <input type="text" id="screen" class="calc-screen" value="0" readonly>
            <div class="calc-grid">
                <button class="btn" onclick="append('7')">7</button><button class="btn" onclick="append('8')">8</button><button class="btn" onclick="append('9')">9</button><button class="btn btn-op" onclick="append('/')">÷</button>
                <button class="btn" onclick="append('4')">4</button><button class="btn" onclick="append('5')">5</button><button class="btn" onclick="append('6')">6</button><button class="btn btn-op" onclick="append('*')">×</button>
                <button class="btn" onclick="append('1')">1</button><button class="btn" onclick="append('2')">2</button><button class="btn" onclick="append('3')">3</button><button class="btn btn-op" onclick="append('-')">-</button>
                <button class="btn" onclick="wipe()" style="color:#ef4444;">C</button><button class="btn" onclick="append('0')">0</button><button class="btn btn-op" onclick="append('+')">+</button><button class="btn btn-eq" onclick="compute()">=</button>
            </div>
            <div style="margin-top: 25px; border-top: 1px solid #e2e8f0; padding-top: 15px;">
                <label style="font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase;">Güvenli Şifre Üretici</label>
                <input type="number" id="len" class="input-field" placeholder="Uzunluk (Örn: 16)" min="6" value="16">
                <button class="action-btn" onclick="genPass()">ÜRET</button>
                <input type="text" id="pass" class="input-field" readonly style="margin-top:10px; text-align:center; font-weight:800; color:#0f172a; background:#f8fafc;">
            </div>
        </div>
        <script>
            function append(v){ let s=document.getElementById('screen'); s.value=(s.value=='0')?v:s.value+v; }
            function wipe(){ document.getElementById('screen').value='0'; }
            function compute(){ let s=document.getElementById('screen'); try{ s.value=eval(s.value); }catch(e){ s.value='HATA'; } }
            function genPass(){ 
                let len = document.getElementById('len').value || 16;
                let chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+~|<>?";
                let pass = ""; for(let i=0; i<len; ++i) pass += chars.charAt(Math.floor(Math.random()*chars.length));
                document.getElementById('pass').value = pass;
            }
        </script>
    """, height=520)

# ==============================================================================
# 7. KISIM: SOHBET EKRANI RENDER MOTORU (KUSURSUZ GÖRSEL ENJEKSİYONLU)
# ==============================================================================
messages_pipeline = st.session_state.sessions[st.session_state.current_session]

for msg in messages_pipeline:
    active_avatar = USER_AVATAR if msg["role"] == "user" else BOT_AVATAR
    with st.chat_message(msg["role"], avatar=active_avatar):
        if msg.get("type") == "image": 
            # Streamlit'in önbellekte takılmasını engelleyen ve resmi doğrudan tarayıcı DOM'una zorlayan premium HTML5 yapısı
            st.markdown(f'<img src="{msg["content"]}" class="premium-img-frame" alt="Eymen AI V2 Realtime Render">', unsafe_allow_html=True)
        else: 
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                st.markdown(get_tts_html(msg["content"]), unsafe_allow_html=True)

# ==============================================================================
# 8. KISIM: V2 KARAR MEKANİZMASI VE GİRDİ İŞLEME (PREMIUM YENİLENEN SÜRÜM)
# ==============================================================================
if prompt := st.chat_input("Eymen AI V2'ye bir şeyler sor..."):
    # Kullanıcı mesajını ekle ve göster
    messages_pipeline.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR): 
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        normalized_query = prompt.lower().strip()
        
        # Akıllı Görsel Modu Tespiti
        is_image_request = any(indicator in normalized_query for indicator in ["resim", "görsel", "çiz", "oluştur", "foto", "fotoğraf"])
        
        # Görsel hafıza zinciri kontrolü (Arka arkaya resim modifiye etme kararlılığı arttırıldı)
        if not is_image_request and len(messages_pipeline) > 1:
            last_assistant_msg = next((m for m in reversed(messages_pipeline[:-1]) if m["role"] == "assistant"), None)
            if last_assistant_msg and (last_assistant_msg.get("type") == "image" or "ürettim" in last_assistant_msg["content"] or "oluşturdum" in last_assistant_msg["content"]):
                if len(normalized_query) < 120 or any(w in normalized_query for w in ["renk", "yap", "ekle", "kaldır", "arkası", "arka plan", "olsun", "başka", "tane", "daha", "değiştir", "bunu", "şunu", "giydir", "çıkart"]):
                    is_image_request = True

        # V2 Görsel Üretim Modu
        if is_image_request:
            loading_placeholder = st.empty()
            loading_placeholder.markdown(get_loading_html("V2 Medya Motoru & Photoshop Katmanı veriyi işliyor"), unsafe_allow_html=True)
            
            # API ve bağlam motoru ile 1080p resmi oluştur
            computed_image_url = generate_1080p_image_url(prompt, messages_pipeline)
            
            loading_placeholder.empty() 
            
            notification_text = "V2 Medya Motoru ve Photoshop Zekası komutunu başarıyla analiz etti. Talebine uygun 1080p (1920x1080) çözünürlüğündeki yeni nesil görselin aşağıda başarıyla render edildi."
            
            # Resmi HTML Enjeksiyonu ile ekrana çökme riski olmadan basıyoruz
            st.markdown(f'<img src="{computed_image_url}" class="premium-img-frame" alt="Eymen AI V2 Realtime Render">', unsafe_allow_html=True)
            st.markdown(notification_text)
            st.markdown(get_tts_html(notification_text), unsafe_allow_html=True)
            
            # Verileri hafızaya kaydet (Her iki element de sırayla pipeline'a eklenerek geçmiş güvenceye alınır)
            messages_pipeline.append({"role": "assistant", "content": notification_text})
            messages_pipeline.append({"role": "assistant", "content": computed_image_url, "type": "image"})
            
        # V2 Gelişmiş Sohbet ve Doküman Çözümleme Modu
        else:
            with st.spinner("Eymen AI V2 analiz ediyor..."):
                input_payload = [prompt]
                
                # Dosya okuma ve analiz bloğu
                if uploaded_file:
                    if uploaded_file.name.lower().endswith(".pdf"):
                        input_payload.append({"mime_type": "application/pdf", "data": uploaded_file.getvalue()})
                    else:
                        input_payload.append(Image.open(uploaded_file))
                
                ai_response = generate_with_retry(input_payload)
                st.markdown(ai_response)
                st.markdown(get_tts_html(ai_response), unsafe_allow_html=True)
                messages_pipeline.append({"role": "assistant", "content": ai_response})
