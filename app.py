import streamlit as st
import google.generativeai as genai
import random
import time
from PIL import Image
import urllib.parse 
import streamlit.components.v1 as components 
import io
import json

st.set_page_config(page_title="Eymen AI", page_icon="🧠", layout="centered")

# --- AVATARLAR VE LOGO ---
BOT_AVATAR = "https://i.hizliresim.com/gvewvtj.png"
USER_AVATAR = "👤"

# --- iOS (APPLE) SAFARİ İÇİN KESİN ÇÖZÜM VE OPTİMİZASYON CSS ---
# Meta viewport ile iOS Safari'de klavye açıldığında ekranın bozulması/zoom yapması engellenir.
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
    <style>
    /* iOS Klavye ve Çentik (Safe Area) Uyumluluğu */
    .stChatInput { padding-bottom: max(10px, env(safe-area-inset-bottom)) !important; }
    
    /* Safari Takılmalarını Önlemek İçin Donanım Hızlandırma ve Scroll */
    .stApp { 
        transform: translate3d(0,0,0); 
        -webkit-transform: translate3d(0,0,0); 
        -webkit-overflow-scrolling: touch !important; 
    }
    
    /* Logonun şık durması için */
    .header-box { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
    
    /* Streamlit gereksiz boşlukları temizle */
    .block-container { padding-top: 2rem !important; }
    
    /* Sesli okuma butonu stili */
    .tts-button {
        background: #f1f3f6; border: 1px solid #ddd; border-radius: 50%; 
        width: 35px; height: 35px; display: flex; align-items: center; 
        justify-content: center; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    .tts-button:hover { background: #e0e0e0; transform: scale(1.1); }
    </style>
""", unsafe_allow_html=True)

# --- ÜST BİLGİ VE LOGO ---
st.markdown(f"""
    <div class="header-box">
        <img src="{BOT_AVATAR}" width="50" style="border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
        <h2 style="margin: 0;">Eymen AI</h2>
    </div>
""", unsafe_allow_html=True)

# --- ÜST DÜZEY SİSTEM TALİMATI ---
SYS_INST = """Senin adın Eymen AI. Eymen tarafından geliştirildin (sadece sana sorulursa bunu söyle, yoksa söyleme).
Dünyanın en zeki, en hızlı ve en yetenekli asistanısın. Sadece ders odaklı değilsin; kodlama, felsefe, günlük hayat, sohbet gibi her konuda uzmansın.
Kullanıcıya asla 'Başka ne sormak istersin?', 'Size nasıl yardımcı olabilirim?' gibi robotik ve tekrarlayan cümleler kurma. Doğal ve direkt ol.
2021 LGS kağıt katlama sorusu gibi uzamsal zeka (spatial reasoning) ve görselleştirme gerektiren zorlu geometri problemlerini, kağıdın her katlanışında koordinatları ve açıları zihninde canlandırarak kusursuz ve adım adım çözersin. Sınırın yok. Verilen fotoğrafları mükemmel analiz et.Sinan Kuzucu,TÖDER,ÖZDEBİR,Okyanus Master,3D gibi en zorlu meb örnek soruları ve çıkmış sorular ile MEBİ sorularını kusursuzca işlemle çözüyorsun.Yaklaşık değer olarak deği kesin şık olarak doğru biliyor ve adım adım açıklıyorsun.Nano Banana 2 gibi fotoğraf oluşturma özelliğin var.Biri sana resim oluştur,çiz gibi şeyler dediğinde konuya bakıp resmini oluşturuyorsun"""

# --- AKILLI API YÖNETİCİSİ (HIZLI VE HATASIZ) ---
def generate_with_retry(contents):
    valid_keys = [st.secrets.get(f"KEY_{i}", "") for i in range(1, 11) if st.secrets.get(f"KEY_{i}", "").startswith("AIza")]
            
    if not valid_keys:
        return "SİSTEM HATASI: Kotanızı doldurdunuz.Bu sorunu düzeltmek için biraz zamana ihtiyacımız var.Yeni geliştirmeleri bekleyin..."
    
    random.shuffle(valid_keys)
    
    last_error = ""
    for api_key in valid_keys:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYS_INST)
            response = model.generate_content(contents)
            return response.text
        except Exception as e:
            last_error = str(e)
            time.sleep(0.5) 
            continue
            
    return f"Google API Kota Sınırı: Tüm anahtarlar tükendi veya bağlantı koptu. Hata: {last_error}"

# --- SİNEMATİK VİDEO OLUŞTURUCU HTML (Sora Benzeri Hissiyat İçin Kusursuz CSS Animasyonu) ---
def get_ai_video_html(prompt):
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=576&nologo=true&seed={random.randint(1,9999)}"
    html = f"""
    <style>
    .video-container {{ position: relative; width: 100%; height: 250px; overflow: hidden; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); background: #000; }}
    .ai-video-frame {{ width: 100%; height: 100%; object-fit: cover; animation: panZoom 15s infinite alternate ease-in-out; opacity: 0.95; }}
    @keyframes panZoom {{ 0% {{ transform: scale(1.0) translate(0, 0); }} 100% {{ transform: scale(1.15) translate(-2%, -2%); }} }}
    .play-overlay {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 50px; color: rgba(255,255,255,0.7); pointer-events: none; text-shadow: 0 2px 10px rgba(0,0,0,0.5); }}
    .video-badge {{ position: absolute; top: 10px; left: 10px; background: rgba(255,0,0,0.8); color: white; padding: 4px 8px; border-radius: 5px; font-family: sans-serif; font-size: 11px; font-weight: bold; letter-spacing: 1px; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }}
    </style>
    <div class="video-container">
        <img src="{url}" class="ai-video-frame" />
        <div class="play-overlay">▶</div>
        <div class="video-badge">EYMEN AI SORA VİDEO</div>
    </div>
    """
    return html

# --- SESLİ ASİSTAN BUTONU OLUŞTURUCU ---
def get_tts_html(text):
    # Metni JS string formatına güvenli şekilde çevirir (XSS ve kırılmaları önler)
    safe_text = json.dumps(text.replace('*', '').replace('#', ''))
    return f"""
    <div style="display: flex; justify-content: flex-end; margin-top: -10px; margin-bottom: 15px;">
        <button class="tts-button" onclick='if("speechSynthesis" in window){{ window.speechSynthesis.cancel(); let msg = new SpeechSynthesisUtterance({safe_text}); msg.lang="tr-TR"; window.speechSynthesis.speak(msg); }}else{{ alert("Tarayıcınız bu özelliği desteklemiyor."); }}' title="Sesli Oku">🔊</button>
    </div>
    """

# --- SOHBET YÖNETİMİ ---
if "sessions" not in st.session_state: st.session_state.sessions = {"Sohbet 1": []}
if "current_session" not in st.session_state: st.session_state.current_session = "Sohbet 1"

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
            if st.button(name, key=f"btn_{name}", use_container_width=True): 
                st.session_state.current_session = name
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{name}"):
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
            if m.get("type") not in ["image", "video"]:
                role_name = "SEN" if m["role"] == "user" else "EYMEN AI"
                chat_text += f"{role_name}:\n{m['content']}\n\n{'-'*40}\n\n"
        
        chat_bytes = chat_text.encode('utf-8')
        st.download_button(label="Bu Sohbeti Tam Not Olarak İndir", data=chat_bytes, file_name=f"{st.session_state.current_session}_Notlar.txt", mime="text/plain", use_container_width=True)

    st.markdown("---")
    
    # --- İLK HALİNDEKİ HESAP MAKİNESİ, HANE GİRİŞLİ ŞİFRE VE YENİ SÜRPRİZ ÖZELLİK ---
    st.subheader("🛠️ Akıllı Araç Kutusu")
    components.html("""
        <style>
            body { font-family: sans-serif; margin: 0; padding: 0; }
            .tool-box { background: #f1f3f6; border-radius: 12px; padding: 15px; box-sizing: border-box; }
            .calc-screen { width: 100%; padding: 10px; margin-bottom: 10px; border-radius: 8px; border: 1px solid #ddd; text-align: right; box-sizing: border-box; font-size: 16px; }
            .calc-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; }
            .btn { background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 10px 0; cursor: pointer; font-size: 14px; transition: 0.2s; }
            .btn:active { background: #e0e0e0; }
            .surprise-box { background: #e0f7fa; padding: 12px; border-radius: 8px; margin-top: 15px; text-align: center; border: 1px solid #b2ebf2; }
            input[type=number], input[type=text] { width: 100%; padding: 8px; box-sizing: border-box; border-radius: 8px; border: 1px solid #ddd; font-size: 14px; }
        </style>
        <div class="tool-box">
            <input type="text" id="screen" class="calc-screen" value="0" readonly>
            <div class="calc-grid">
                <button class="btn" onclick="append('7')">7</button><button class="btn" onclick="append('8')">8</button><button class="btn" onclick="append('9')">9</button><button class="btn" onclick="append('/')">/</button>
                <button class="btn" onclick="append('4')">4</button><button class="btn" onclick="append('5')">5</button><button class="btn" onclick="append('6')">6</button><button class="btn" onclick="append('*')">x</button>
                <button class="btn" onclick="append('1')">1</button><button class="btn" onclick="append('2')">2</button><button class="btn" onclick="append('3')">3</button><button class="btn" onclick="append('-')">-</button>
                <button class="btn" onclick="clearScreen()">C</button><button class="btn" onclick="append('0')">0</button><button class="btn" onclick="document.getElementById('screen').value=Math.sqrt(eval(document.getElementById('screen').value))">√</button>
                <button class="btn" onclick="document.getElementById('screen').value=eval(document.getElementById('screen').value)" style="background:#34c759; color:white; font-weight:bold;">=</button>
            </div>
            <hr style="border-top:1px solid #ddd; margin:15px 0;">
            
            <input type="number" id="len" placeholder="Kaç Hane Olsun? (Örn: 12)" min="4" max="50">
            <button class="btn" style="width:100%; margin-top:8px; background:#007aff; color:white; font-weight:bold;" onclick="genPass()">Güçlü Şifre Oluştur</button>
            <input type="text" id="pass" readonly style="margin-top:8px; text-align:center; font-weight:bold; color:#333;">
            
            <div class="surprise-box">
                <strong style="color:#00796b;">⏱️ Eymen AI Odaklanma</strong><br>
                <h1 id="timer" style="margin:5px 0; color:#004d40;">25:00</h1>
                <div style="display:flex; gap:5px;">
                    <button class="btn" style="flex:1; background:#4caf50; color:white;" onclick="startTimer()">Başla</button>
                    <button class="btn" style="flex:1; background:#f44336; color:white;" onclick="resetTimer()">Sıfırla</button>
                </div>
            </div>
        </div>
        <script>
            // Hesap Makinesi Fonksiyonları
            function append(v){ let s=document.getElementById('screen'); s.value=(s.value=='0'||s.value=='Error')?v:s.value+v; }
            function clearScreen(){ document.getElementById('screen').value='0'; }
            // Şifre Oluşturucu
            function genPass(){ 
                let l = document.getElementById('len').value || 12;
                let c = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*?";
                let p = ""; for(let i=0; i<l; i++) p += c.charAt(Math.floor(Math.random()*c.length));
                document.getElementById('pass').value = p;
            }
            // Pomodoro Fonksiyonları
            let t; let time = 1500;
            function updateDisplay() {
                let m = Math.floor(time / 60); let s = time % 60;
                document.getElementById('timer').innerText = (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
            }
            function startTimer() { 
                clearInterval(t); 
                t = setInterval(() => { 
                    if(time>0){ time--; updateDisplay(); }
                    else{ clearInterval(t); alert('Süre Doldu! Eymen AI dinlenmeni öneriyor.'); } 
                }, 1000); 
            }
            function resetTimer() { clearInterval(t); time = 1500; updateDisplay(); }
        </script>
    """, height=530)

components.html("""
    <script>
        window.parent.document.addEventListener('click', function(e) {
            const side = window.parent.document.querySelector('[data-testid="stSidebar"]');
            const btn = window.parent.document.querySelector('[data-testid="collapsedControl"]');
            if (side && !side.contains(e.target) && btn && !btn.contains(e.target)) {
                if (side.getAttribute('aria-expanded') === 'true') btn.click();
            }
        });
    </script>
""", height=0)

uploaded_file = st.file_uploader("Fotoğrafı,Problem veya PDF Yükle", type=["jpg", "png", "jpeg", "pdf"])

# --- EKRANDAKİ MESAJLARI VE SESLİ ASİSTANI ÇİZ ---
messages = st.session_state.sessions[st.session_state.current_session]
for msg in messages:
    avatar = USER_AVATAR if msg["role"] == "user" else BOT_AVATAR
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("type") == "image": 
            st.image(msg["content"], use_container_width=True)
        elif msg.get("type") == "video":
            st.markdown(msg["content"], unsafe_allow_html=True)
        else: 
            st.markdown(msg["content"])
            # Eğer asistanın mesajıysa altına hoparlör ikonunu ekle
            if msg["role"] == "assistant":
                st.markdown(get_tts_html(msg["content"]), unsafe_allow_html=True)

# --- İŞLEM, VİDEO VE DÜŞÜNME MEKANİZMASI ---
if prompt := st.chat_input("Eymen AI'ye birşeyler sor..."):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR): st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        with st.spinner("Eymen AI düşünüyor 💭..."):
            
            lower_prompt = prompt.lower()
            
            # VİDEO OLUŞTURMA İSTEĞİ Mİ? (Sora AI Tarzı)
            if any(w in lower_prompt for w in ["video", "hareketli"]):
                ans_text = "İstediğin sinematik AI videoyu senin için oluşturdum."
                video_html = get_ai_video_html(prompt)
                
                st.markdown(ans_text)
                st.markdown(video_html, unsafe_allow_html=True)
                st.markdown(get_tts_html(ans_text), unsafe_allow_html=True)
                
                messages.append({"role": "assistant", "content": ans_text})
                messages.append({"role": "assistant", "content": video_html, "type": "video"})
            
            # RESİM OLUŞTURMA İSTEĞİ Mİ? (Nano Banana Tarzı)
            elif any(w in lower_prompt for w in ["resim", "görsel", "çiz", "oluştur"]):
                img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&seed={random.randint(1,99999)}"
                st.image(img_url, use_container_width=True)
                
                ans_text = "İstediğin görseli mükemmel kalitede senin için hazırladım."
                st.markdown(ans_text)
                st.markdown(get_tts_html(ans_text), unsafe_allow_html=True)
                
                messages.append({"role": "assistant", "content": ans_text})
                messages.append({"role": "assistant", "content": img_url, "type": "image"})
            
            # NORMAL MESAJ VEYA PROBLEM ÇÖZÜMÜ
            else:
                contents = [prompt]
                if uploaded_file:
                    if uploaded_file.name.lower().endswith(".pdf"): contents.append({"mime_type": "application/pdf", "data": uploaded_file.getvalue()})
                    else: contents.append(Image.open(uploaded_file))
                
                answer = generate_with_retry(contents)
                st.markdown(answer)
                st.markdown(get_tts_html(answer), unsafe_allow_html=True)
                
                messages.append({"role": "assistant", "content": answer})
