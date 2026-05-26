# ==============================================================================
# PROJE ADI: EYMEN AI (PREMIUM ENTERPRISE EDITION V6)
# ÖZELLİKLER: Zıplayan Nokta Animasyonları, Gemini Enhanced 1080p Medya Motoru,
#            Gelişmiş iOS Uyumluluğu, Bağlamsal Akıllı Görsel Hafızası
# ==============================================================================

import streamlit as st
import google.generativeai as genai
import random
import time
from PIL import Image
import urllib.parse 
import streamlit.components.v1 as components 
import json

# --- SİSTEM GENELİ CODESPACE VE GÖRSEL AYARLARI ---
st.set_page_config(
    page_title="Eymen AI", 
    page_icon="🧠", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- SOHBET VE OTURUM DURUMU YÖNETİCİSİ ---
if "sessions" not in st.session_state: st.session_state.sessions = {"Sohbet 1": []}
if "current_session" not in st.session_state: st.session_state.current_session = "Sohbet 1"

BOT_AVATAR = "https://i.hizliresim.com/gvewvtj.png"
USER_AVATAR = "👤"

# ==============================================================================
# 1. KISIM: CSS (iOS UYUMLULUĞU, ZIPLAYAN NOKTALAR VE TASARIM)
# ==============================================================================
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <style>
    .stChatInput { padding-bottom: max(15px, env(safe-area-inset-bottom)) !important; position: fixed !important; bottom: 0 !important; left: 0 !important; right: 0 !important; z-index: 999999 !important; }
    .stApp { transform: translate3d(0,0,0); -webkit-transform: translate3d(0,0,0); -webkit-overflow-scrolling: touch !important; height: 100vh !important; overflow-y: auto !important; }
    .header-box { display: flex; align-items: center; gap: 15px; margin-bottom: 10px; padding: 10px; border-radius: 12px; background: transparent; }
    .block-container { padding-top: 2.5rem !important; padding-bottom: 6rem !important; }
    
    /* Sesli Okuma Butonu */
    .tts-layer-wrapper { display: flex; justify-content: flex-end; align-items: center; margin-top: -8px; margin-bottom: 12px; padding-right: 5px; }
    .tts-trigger-btn { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 2px 6px rgba(0,0,0,0.06); transition: all 0.2s ease; font-size: 16px; }
    .tts-trigger-btn:hover { background: #f8fafc; transform: scale(1.08); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    
    /* --- ZIPLAYAN NOKTA ANİMASYONU --- */
    .loading-container { display: flex; align-items: center; gap: 10px; font-family: sans-serif; font-weight: 600; color: #3b82f6; padding: 10px; border-radius: 8px; background: rgba(59, 130, 246, 0.1); margin-bottom: 15px; border-left: 4px solid #3b82f6; width: fit-content; }
    .dots-wrapper { display: flex; gap: 4px; align-items: center; margin-top: 5px; }
    .dot { width: 6px; height: 6px; background-color: #3b82f6; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; }
    .dot:nth-child(1) { animation-delay: -0.32s; }
    .dot:nth-child(2) { animation-delay: -0.16s; }
    @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="header-box">
        <img src="{BOT_AVATAR}" width="52" style="border-radius: 12px; box-shadow: 0px 4px 12px rgba(0,0,0,0.12); object-fit: cover;">
        <h2 style="margin: 0; font-weight: 700; color: #1e293b;">Eymen AI</h2>
    </div>
""", unsafe_allow_html=True)

# --- DOSYA YÜKLEYİCİ ARTIK TAM AYNI UZUNLUKTA VE EYMEN AI YAZISININ ALTINDA ---
uploaded_file = st.file_uploader("Fotoğrafı, Problem veya PDF Yükle", type=["jpg", "png", "jpeg", "pdf"])

SYS_INST = """Senin adın Eymen AI. Eymen tarafından geliştirildin.
Kullanıcıya asla 'Başka ne sormak istersin?' gibi robotik cümleler kurma. Doğal ve direkt ol.
2021 LGS kağıt katlama sorusu gibi zorlu problemleri kusursuz çözersin. MEB ve yayıncı sorularını hata yapmadan, kesin şık vererek adım adım açıklarsın.
Nano Banana 2 özelliklerin var. Eğer kullanıcı senden görsel isterse bunu yeteneklerinle gerçekleştirirsin."""

# ==============================================================================
# 2. KISIM: YÜK DENGELİ API YÖNETİCİSİ VE ANİMASYON FONKSİYONLARI
# ==============================================================================
def get_loading_html(text):
    return f"""
    <div class="loading-container">
        <span>{text}</span>
        <div class="dots-wrapper">
            <div class="dot"></div><div class="dot"></div><div class="dot"></div>
        </div>
    </div>
    """

def generate_with_retry(contents):
    valid_keys = [st.secrets.get(f"KEY_{i}", "") for i in range(1, 11) if st.secrets.get(f"KEY_{i}", "").startswith("AIza")]
    if not valid_keys: return "SİSTEM HATASI: Kotanızı doldurdunuz."
    
    random.shuffle(valid_keys)
    last_error = ""
    for api_key in valid_keys:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=SYS_INST)
            return model.generate_content(contents).text
        except Exception as e:
            last_error = str(e)
            time.sleep(0.4) 
            continue
    return f"Hata: {last_error}"

# ==============================================================================
# 3. KISIM: 1080P SÜREKLİ GÖRSEL HAFIZA MOTORU (BAĞLAM DUYARLI)
# ==============================================================================
def generate_1080p_image_url(user_prompt, history_pipeline):
    # Geçmiş konuşmalardan metin bazlı olanları toplayıp zeka motoruna hafıza olarak veriyoruz
    context_memory = ""
    for m in history_pipeline[-6:]:
        if m.get("type") != "image":
            role_label = "Kullanıcı" if m["role"] == "user" else "Eymen AI"
            context_memory += f"{role_label}: {m['content']}\n"
            
    enhancement_prompt = f"""Aşağıda kullanıcının seninle olan son konuşma geçmişi ve en son isteği yer almaktadır.
Konuşma geçmişini derinlemesine analiz ederek (özellikle 'bunu mavi yap', 'arkasına şunu ekle', 'bir tane daha' gibi ardışık ifadeler varsa neyi kastettiğini kusursuzca anlamak için), kullanıcının en son isteğini yapay zekanın çizebilmesi için ultra detaylı, 1080p, fotogerçekçi ve sinematik İngilizce bir Stable Diffusion promptuna çevir. 
Sadece İngilizce promptu yaz, başka hiçbir açıklama veya yorum ekleme.

Konuşma Geçmişi:
{context_memory}

Kullanıcının En Son İsteği: {user_prompt}"""
    
    enhanced_english_prompt = generate_with_retry([enhancement_prompt])
    
    safe_prompt = urllib.parse.quote(enhanced_english_prompt.strip())
    unique_seed = time.time_ns() % 1000000
    
    return f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1920&height=1080&nologo=true&seed={unique_seed}&enhance=true"

def get_tts_html(response_text):
    clean_text = response_text.replace('*', '').replace('#', '').replace('`', '"')
    json_safe_text = json.dumps(clean_text)
    return f"""
    <div class="tts-layer-wrapper">
        <button class="tts-trigger-btn" onclick='if("speechSynthesis" in window){{ window.speechSynthesis.cancel(); let speechNode = new SpeechSynthesisUtterance({json_safe_text}); speechNode.lang="tr-TR"; window.speechSynthesis.speak(speechNode); }} else {{ alert("Desteklenmiyor."); }}'>🔊</button>
    </div>
    """

# ==============================================================================
# 4. KISIM: SİDEBAR - SOHBET GEÇMİŞİ VE AKILLI ARAÇ KUTUSU
# ==============================================================================
with st.sidebar:
    st.header("Sohbet Geçmişi")
    if st.button("➕ Yeni Sohbet", use_container_width=True):
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
    
    st.subheader("📥 İndir & Kaydet")
    current_msgs = st.session_state.sessions[st.session_state.current_session]
    if len(current_msgs) > 0:
        chat_text = f"--- {st.session_state.current_session} | Eymen AI Çalışma Notları ---\n\n"
        for m in current_msgs:
            if m.get("type") != "image":
                role_name = "SEN" if m["role"] == "user" else "EYMEN AI"
                chat_text += f"{role_name}:\n{m['content']}\n\n{'-'*40}\n\n"
        st.download_button(label="Not Olarak İndir", data=chat_text.encode('utf-8'), file_name=f"{st.session_state.current_session}_Notlar.txt", mime="text/plain", use_container_width=True)

    st.markdown("---")
    
    st.subheader("🛠️ Akıllı Araç Kutusu")
    components.html("""
        <style>
            body { font-family: -apple-system, sans-serif; margin: 0; padding: 0; background: transparent; }
            .tool-box { background: #f1f3f6; border-radius: 12px; padding: 15px; box-sizing: border-box; }
            .calc-screen { width: 100%; padding: 12px; margin-bottom: 10px; border-radius: 8px; border: 1px solid #ddd; text-align: right; font-size: 18px; background: #fff; }
            .calc-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
            .btn { background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 12px 0; cursor: pointer; font-size: 15px; font-weight: 600; }
            .btn:active { background: #e2e8f0; }
            .input-field { width: 100%; padding: 10px; box-sizing: border-box; border-radius: 8px; border: 1px solid #ddd; margin-top: 5px; }
            .action-btn { width: 100%; margin-top: 8px; background: #007aff; color: white; border: none; font-weight: bold; padding: 12px; border-radius: 8px; cursor: pointer; }
        </style>
        <div class="tool-box">
            <input type="text" id="screen" class="calc-screen" value="0" readonly>
            <div class="calc-grid">
                <button class="btn" onclick="append('7')">7</button><button class="btn" onclick="append('8')">8</button><button class="btn" onclick="append('9')">9</button><button class="btn" onclick="append('/')">/</button>
                <button class="btn" onclick="append('4')">4</button><button class="btn" onclick="append('5')">5</button><button class="btn" onclick="append('6')">6</button><button class="btn" onclick="append('*')">x</button>
                <button class="btn" onclick="append('1')">1</button><button class="btn" onclick="append('2')">2</button><button class="btn" onclick="append('3')">3</button><button class="btn" onclick="append('-')">-</button>
                <button class="btn" onclick="wipe()">C</button><button class="btn" onclick="append('0')">0</button><button class="btn" onclick="sqrRoot()">√</button>
                <button class="btn" onclick="compute()" style="background:#34c759; color:white;">=</button>
            </div>
            <hr style="border-top: 1px solid #d1d5db; margin: 15px 0;">
            <label style="font-size: 13px; font-weight: 600; color: #4b5563;">Şifre Uzunluğu (Hane)</label>
            <input type="number" id="len" class="input-field" placeholder="Hane Sayısı (örn: 12)" min="4" value="12">
            <button class="action-btn" onclick="genPass()">Şifre Oluştur</button>
            <input type="text" id="pass" class="input-field" readonly style="margin-top:8px; text-align:center; font-weight:bold;">
        </div>
        <script>
            function append(v){ let s=document.getElementById('screen'); s.value=(s.value=='0')?v:s.value+v; }
            function wipe(){ document.getElementById('screen').value='0'; }
            function sqrRoot(){ let s=document.getElementById('screen'); try{ s.value=Math.sqrt(eval(s.value)); }catch(e){ s.value='Error'; } }
            function compute(){ let s=document.getElementById('screen'); try{ s.value=eval(s.value); }catch(e){ s.value='Error'; } }
            function genPass(){ 
                let len = document.getElementById('len').value || 12;
                let chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*";
                let pass = ""; for(let i=0; i<len; ++i) pass += chars.charAt(Math.floor(Math.random()*chars.length));
                document.getElementById('pass').value = pass;
            }
        </script>
    """, height=420)

components.html("<script>window.parent.document.addEventListener('click', function(e) { const side = window.parent.document.querySelector('[data-testid=\"stSidebar\"]'); const btn = window.parent.document.querySelector('[data-testid=\"collapsedControl\"]'); if (side && !side.contains(e.target) && btn && !btn.contains(e.target)) { if (side.getAttribute('aria-expanded') === 'true') btn.click(); } });</script>", height=0)

# ==============================================================================
# 5. KISIM: EKRAN RENDER VE SOHBET ALTYAPISI
# ==============================================================================
messages_pipeline = st.session_state.sessions[st.session_state.current_session]

for msg in messages_pipeline:
    active_avatar = USER_AVATAR if msg["role"] == "user" else BOT_AVATAR
    with st.chat_message(msg["role"], avatar=active_avatar):
        if msg.get("type") == "image": 
            st.image(msg["content"], use_container_width=True)
        else: 
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                st.markdown(get_tts_html(msg["content"]), unsafe_allow_html=True)

# ==============================================================================
# 6. KISIM: ZEKİ GİRDİ YÖNETİMİ VE ANİMASYONLU İŞLEME
# ==============================================================================
if prompt := st.chat_input("Eymen AI'ye birşeyler sor..."):
    messages_pipeline.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR): 
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        normalized_query = prompt.lower().strip()
        
        # --- GELİŞMİŞ GÖRSEL MODU TESPİT ALTYAPISI (HAFIZA BAĞLANTILI) ---
        is_image_request = any(indicator in normalized_query for indicator in ["resim", "görsel", "çiz", "oluştur", "foto", "fotoğraf"])
        
        # Eğer tetikleyici kelime yoksa ama bir önceki asistan mesajı bir resimse/resimle ilgiliyse devamı niteliğindedir
        if not is_image_request and len(messages_pipeline) > 1:
            last_assistant_msg = None
            for m in reversed(messages_pipeline[:-1]): # Mevcut kullanıcı mesajı hariç son asistan yanıtını bul
                if m["role"] == "assistant":
                    last_assistant_msg = m
                    break
            if last_assistant_msg and (last_assistant_msg.get("type") == "image" or "ürettim" in last_assistant_msg["content"] or "oluşturdum" in last_assistant_msg["content"]):
                # Kullanıcı görsel modundayken kısa modifikasyon veya ardışık emirler veriyorsa resim motorunu açık tut
                if len(normalized_query) < 60 or any(w in normalized_query for w in ["renk", "mavi", "yeşil", "kırmızı", "siyah", "beyaz", "sarı", "arkası", "arka plan", "olsun", "başka", "tane", "daha", "değiştir", "bunu", "şunu"]):
                    is_image_request = True

        # --- FOTOĞRAF OLUŞTURMA İSTEĞİ (Her İstemde Kusursuz Çalışır) ---
        if is_image_request:
            loading_placeholder = st.empty()
            loading_placeholder.markdown(get_loading_html("Fotoğraf oluşturuluyor"), unsafe_allow_html=True)
            
            # Gemini konuşma geçmişini ve yeni emri birleştirip URL üretir
            computed_image_url = generate_1080p_image_url(prompt, messages_pipeline)
            
            loading_placeholder.empty() 
            
            notification_text = "İstediğin konuyu ve konuşma geçmişindeki değişiklikleri analiz ettim, senin için 1080p (1920x1080) çözünürlükte yeni yapay zeka görselini başarıyla ürettim."
            
            st.image(computed_image_url, use_container_width=True)
            st.markdown(notification_text)
            st.markdown(get_tts_html(notification_text), unsafe_allow_html=True)
            
            messages_pipeline.append({"role": "assistant", "content": notification_text})
            messages_pipeline.append({"role": "assistant", "content": computed_image_url, "type": "image"})
            
        # --- NORMAL SOHBET VE PROBLEM ÇÖZÜMÜ ---
        else:
            with st.spinner("Eymen AI düşünüyor 💭..."):
                input_payload = [prompt]
                if uploaded_file:
                    if uploaded_file.name.lower().endswith(".pdf"):
                        input_payload.append({"mime_type": "application/pdf", "data": uploaded_file.getvalue()})
                    else:
                        input_payload.append(Image.open(uploaded_file))
                
                ai_response = generate_with_retry(input_payload)
                st.markdown(ai_response)
                st.markdown(get_tts_html(ai_response), unsafe_allow_html=True)
                messages_pipeline.append({"role": "assistant", "content": ai_response})
