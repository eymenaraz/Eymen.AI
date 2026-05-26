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
Dünyanın en zeki, en hızlı ve en yetenekli asistanısın.Sana söylenen her şarkı sözü ve ismini bilirsin. Sadece ders odaklı değilsin; kodlama, felsefe, günlük hayat, sohbet gibi her konuda uzmansın.
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
    if len(current_msgs)
