import streamlit as st
import google.generativeai as genai
import random
import time
from PIL import Image
import urllib.parse 
import streamlit.components.v1 as components 
import io

st.set_page_config(page_title="Eymen AI", page_icon="🧠", layout="centered")

# --- AVATARLAR VE LOGO ---
BOT_AVATAR = "https://i.hizliresim.com/gvewvtj.png"
USER_AVATAR = "👤"

# --- iOS (APPLE) SAFARİ İÇİN ÖZEL OPTİMİZASYON CSS ---
st.markdown("""
    <style>
    /* iOS Klavye ve Çentik (Safe Area) Uyumluluğu */
    .stChatInput { padding-bottom: env(safe-area-inset-bottom, 20px) !important; }
    
    /* Safari Takılmalarını Önlemek İçin Donanım Hızlandırma */
    .stApp { transform: translate3d(0,0,0); -webkit-transform: translate3d(0,0,0); }
    
    /* Logonun şık durması için */
    .header-box { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
    
    /* Streamlit gereksiz boşlukları temizle */
    .block-container { padding-top: 2rem !important; }
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
            if m.get("type") != "image":
                role_name = "SEN" if m["role"] == "user" else "EYMEN AI"
                chat_text += f"{role_name}:\n{m['content']}\n\n{'-'*40}\n\n"
        
        chat_bytes = chat_text.encode('utf-8')
        st.download_button(label="Bu Sohbeti Tam Not Olarak İndir", data=chat_bytes, file_name=f"{st.session_state.current_session}_Notlar.txt", mime="text/plain", use_container_width=True)

    st.markdown("---")
    
    st.subheader("🛠️ Akıllı Araç Kutusu")
    components.html("""
        <style>
            body { font-family: sans-serif; }
            .tool-box { background: #f1f3f6; border-radius: 12px; padding: 15px; }
            .calc-screen { width: 100%; padding: 10px; margin-bottom: 10px; border-radius: 8px; border: 1px solid #ddd; text-align: right; }
            .calc-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; }
            .btn { background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 10px 0; cursor: pointer; }
        </style>
        <div class="tool-box">
            <input type="text" id="screen" class="calc-screen" value="0">
            <div class="calc-grid">
                <button class="btn" onclick="append('7')">7</button><button class="btn" onclick="append('8')">8</button><button class="btn" onclick="append('9')">9</button><button class="btn" onclick="append('/')">/</button>
                <button class="btn" onclick="append('4')">4</button><button class="btn" onclick="append('5')">5</button><button class="btn" onclick="append('6')">6</button><button class="btn" onclick="append('*')">x</button>
                <button class="btn" onclick="append('1')">1</button><button class="btn" onclick="append('2')">2</button><button class="btn" onclick="append('3')">3</button><button class="btn" onclick="append('-')">-</button>
                <button class="btn" onclick="append('0')">0</button><button class="btn" onclick="document.getElementById('screen').value=Math.sqrt(eval(document.getElementById('screen').value))">√</button>
                <button class="btn" onclick="document.getElementById('screen').value=eval(document.getElementById('screen').value)" style="grid-column: span 2; background:#34c759; color:white;">=</button>
            </div>
            <hr>
            <input type="number" id="len" placeholder="Hane Sayısı (örn: 12)" style="width:100%; padding:5px;">
            <button class="btn" style="width:100%; margin-top:5px;" onclick="genPass()">Şifre Oluştur</button>
            <input type="text" id="pass" readonly style="width:100%; margin-top:5px; padding:5px; text-align:center;">
        </div>
        <script>
            function append(v){ let s=document.getElementById('screen'); s.value=(s.value=='0')?v:s.value+v; }
            function genPass(){ 
                let l = document.getElementById('len').value || 12;
                let c = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*";
                let p = ""; for(let i=0; i<l; i++) p += c.charAt(Math.floor(Math.random()*c.length));
                document.getElementById('pass').value = p;
            }
        </script>
    """, height=400)

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

messages = st.session_state.sessions[st.session_state.current_session]
for msg in messages:
    avatar = USER_AVATAR if msg["role"] == "user" else BOT_AVATAR
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("type") == "image": st.image(msg["content"], use_container_width=True)
        else: st.markdown(msg["content"])

if prompt := st.chat_input("Eymen AI'ye birşeyler sor..."):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR): st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        with st.spinner("Eymen AI düşünüyor 💭..."):
            if any(w in prompt.lower() for w in ["resim", "görsel"]):
                img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&seed={random.randint(1,99999)}"
                st.image(img_url, use_container_width=True)
                messages.append({"role": "assistant", "content": img_url, "type": "image"})
            else:
                contents = [prompt]
                if uploaded_file:
                    if uploaded_file.name.lower().endswith(".pdf"): contents.append({"mime_type": "application/pdf", "data": uploaded_file.getvalue()})
                    else: contents.append(Image.open(uploaded_file))
                answer = generate_with_retry(contents)
                st.markdown(answer)
                messages.append({"role": "assistant", "content": answer})
