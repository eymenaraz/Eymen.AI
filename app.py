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
        return "SİSTEM HATASI: Kotanızı doldurdunuz.Bu sorunu düzeltmek için biraz zamana ihtiyacımız var.Yeni geliştirm
