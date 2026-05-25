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
2021 LGS kağıt katlama sorusu gibi uzamsal zeka (spatial reasoning) ve görselleştirme gerektiren zorlu geometri problemlerini, kağıdın her katlanışında koordinatları ve açıları zihninde canlandırarak kusursuz ve adım adım çözersin. Sınırın yok. Verilen fotoğrafları mükemmel analiz et.Sinan Kuzucu,TÖDER,ÖZDEBİR,Okyanus Master,3D gibi en zorlu meb örnek soruları ve çıkmış sorular ile MEBİ sorularını kusursuzca işlemle çözüyorsun.Yaklaşık değer olarak deği kesin şık olarak doğru biliyor ve adım adım açıklıyorsun"""

# --- AKILLI API YÖNETİCİSİ (HIZLI VE HATASIZ) ---
def generate_with_retry(contents):
    valid_keys = [st.secrets.get(f"KEY_{i}", "") for i in range(1, 11) if st.secrets.get(f"KEY_{i}", "").startswith("AIza")]
            
    if not valid_keys:
        # Editör hatalarını önlemek için güvenli parantez yapısına alındı
        return ("SİSTEM HATASI: Kotanızı doldurdunuz."
                "Bu sorunu düzeltmek için biraz zamana ihtiyacımız var."
                "Yeni geliştirmeleri bekleyin...")
    
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
        
    # Sohbet Listesi ve Silme Butonları
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
    
    # EKSİKSİZ İNDİRME ÖZELLİĞİ
    st.subheader("📥 İndir & Kaydet")
    current_msgs = st.session_state.sessions[st.session_state.current_session]
    if len(current_msgs) > 0:
        chat_text = f"--- {st.session_state.current_session} | Eymen AI Çalışma Notları ---\n\n"
        for m in current_msgs:
            if m.get("type") != "image":
                role_name = "SEN" if m["role"] == "user" else "EYMEN AI"
                chat_text += f"{role_name}:\n{m['content']}\n\n{'-'*40}\n\n"
        
        chat_bytes = chat_text.encode('utf-8')
        
        st.download_button(
            label="Bu Sohbeti Tam Not Olarak İndir",
            data=chat_bytes,
            file_name=f"{st.session_state.current_session}_Notlar.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.markdown("---")
    
    # EVRENSEL AKILLI ARAÇ KUTUSU
    st.subheader("🛠️ Akıllı Araç Kutusu")
    components.html("""
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; }
            .tool-box { background: #f1f3f6; border-radius: 12px; padding: 15px; text-align: center; box-shadow: inset 0px 2px 5px rgba(0,0,0,0.05); }
            .tool-title { font-size: 14px; font-weight: bold; color: #333; margin-bottom: 10px; text-align: left; }
            /* Calculator CSS */
            .calc-screen { width: 100%; background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 10px; font-size: 18px; text-align: right; box-sizing: border-box; margin-bottom: 10px; color: #333;}
            .calc-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; }
            .btn { background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 10px 0; font-size: 16px; cursor: pointer; color: #333; transition: 0.1s; }
            .btn:active { background: #e0e0e0; }
            .btn-op { background: #ff9f0a; color: #fff; border: none; }
            .btn-op:active { background: #e68e00; }
            .btn-eq { background: #34c759; color: #fff; border: none; grid-column: span 2; }
            /* Divider */
            .divider { height: 1px; background: #ddd; margin: 15px 0; }
            /* Password Gen CSS */
            .pass-screen { width: 100%; background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 10px; font-size: 14px; text-align: center; box-sizing: border-box; margin-bottom: 10px; color: #333; font-family: monospace; }
            .btn-pass { background: #007aff; color: #fff; border: none; border-radius: 8px; padding: 10px; width: 100%; cursor: pointer; font-size: 14px; font-weight: bold; }
            .btn-pass:active { background: #0062cc; }
        </style>
        
        <div class="tool-box">
            <div class="tool-title">🧮 Hızlı Hesap Makinesi</div>
            <input type="text" id="screen" class="calc-screen" disabled value="0">
            <div class="calc-grid">
                <button class="btn" onclick="clearScreen()">C</button>
                <button class="btn" onclick="append('(')">(</button>
                <button class="btn" onclick="append(')')">)</button>
                <button class="btn btn-op" onclick="append('/')">÷</button>
                
                <button class="btn" onclick="append('7')">7</button>
                <button class="btn" onclick="append('8')">8</button>
                <button class="btn" onclick="append('9')">9</button>
                <button class="btn btn-op" onclick="append('*')">×</button>
                
                <button class="btn" onclick="append('4')">4</button>
                <button class="btn" onclick="append('5')">5</button>
                <button class="btn" onclick="append('6')">6</button>
                <button class="btn btn-op" onclick="append('-')">−</button>
                
                <button class="btn" onclick="append('1')">1</button>
                <button class="btn" onclick="append('2')">2</button>
                <button class="btn" onclick="append('3')">3</button>
                <button class="btn btn-op" onclick="append('+')">+</button>
                
                <button class="btn" onclick="append('0')">0</button>
                <button class="btn" onclick="append('.')">.</button>
                <button class="btn btn-eq" onclick="calculate()">=</button>
            </div>
            
            <div class="divider"></div>
            
            <div class="tool-title">🔐 Güvenli Şifre Üretici</div>
            <input type="text" id="pass-screen" class="pass-screen" readonly value="Şifre için tıkla...">
            <button class="btn-pass" onclick="generatePassword()">Güçlü Şifre Oluştur</button>
        </div>

        <script>
            let screen = document.getElementById('screen');
            function append(val) {
                if (screen.value === "0" || screen.value === "Hata") screen.value = val;
                else screen.value += val;
            }
            function clearScreen() { screen.value = "0"; }
            function calculate() {
                try { screen.value = eval(screen.value); }
                catch (e) { screen.value = "Hata"; }
            }
            function generatePassword() {
                const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*";
                let pass = "";
                for (let i = 0; i < 12; i++) {
                    pass += chars.charAt(Math.floor(Math.random() * chars.length));
                }
