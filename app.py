import streamlit as st
import json
import os
import urllib.parse
import random
import string
import math
import google.generativeai as genai
import streamlit.components.v1 as components

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Eymen AI V2",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS VE STYLING (PREMIUM, LIGHT/DARK MODE & IPHONE MOBİL DÜZELTMESİ) ---
st.markdown("""
<style>
    /* IPHONE VE MOBİL GİRİŞ DÜZELTMESİ (Auto-Zoom Engelleme) */
    [data-testid="stChatInput"] textarea, .stTextInput input, textarea {
        font-size: 16px !important;
    }
    
    /* Yan Menü (Sidebar) Premium Geçişler */
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.2);
        backdrop-filter: blur(10px);
    }
    
    /* Sohbet Giriş Kutusu Premium Hissiyat */
    .stTextInput input {
        border-radius: 12px !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease;
    }
    
    /* Kullanıcı Mesaj Balonu (Modern Cam Efekti) */
    .user-bubble {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 20px 20px 4px 20px;
        margin: 10px 0 10px auto;
        max-width: 75%;
        width: fit-content;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.25);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 1.05rem;
    }
    
    /* Asistan Mesaj Balonu (Dark Mode - Göz Yormayan Neon Mor) */
    .ai-bubble {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
        color: #f8fafc;
        padding: 16px 20px;
        border-radius: 20px 20px 20px 4px;
        margin: 10px auto 10px 0;
        max-width: 75%;
        width: fit-content;
        border: 1px solid rgba(139, 92, 246, 0.4);
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.35);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 1.05rem;
        backdrop-filter: blur(8px);
    }

    /* Light Mode İçin Renk Ayarlamaları (Göz Yormayan Neon Zümrüt/Yeşil) */
    @media (prefers-color-scheme: light) {
        .ai-bubble {
            background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
            color: #1e293b;
            border: 1px solid rgba(16, 185, 129, 0.4);
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.35);
        }
    }
    
    /* Çift Renkli Neon Parlayan Logo Tasarımı */
    .logo-container {
        text-align: center;
        margin-bottom: 5px;
        padding: 10px;
    }
    .brand-eymen {
        font-size: 3.8rem;
        font-weight: 900;
        color: #2563eb;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        letter-spacing: 1px;
        text-shadow: 0 0 15px rgba(37, 99, 235, 0.4);
    }
    .brand-v2 {
        font-size: 3.8rem;
        font-weight: 900;
        color: #38bdf8;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        letter-spacing: 1px;
        text-shadow: 0 0 15px rgba(56, 189, 248, 0.5);
        margin-left: 15px;
    }
    
    .subtitle {
        color: #64748b;
        text-align: center;
        font-size: 1.15rem;
        font-weight: 500;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# --- ÇOKLU API KEY OTOMATİK TARAMA SİSTEMİ ---
@st.cache_resource
def get_working_api_key():
    for i in range(1, 11):
        key_name = f"KEY_{i}"
        if key_name in st.secrets:
            potential_key = st.secrets[key_name]
            try:
                genai.configure(api_key=potential_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                model.generate_content("test", generation_config={"max_output_tokens": 1})
                return potential_key
            except Exception:
                continue
    return None

api_key = get_working_api_key()

# --- BAŞLIK ALANI (ÖZEL NEON TASARIM) ---
st.markdown('<div class="logo-container"><span class="brand-eymen">Eymen AI</span><span class="brand-v2">V2</span></div>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Premium Yapay Zeka & Akıllı Araç Seti</p>', unsafe_allow_html=True)

# --- MODEL VE SİSTEM TALİMATI AYARLARI ---
model_choice = "gemini-2.5-flash"
system_instruction = (
    "Sen Eymen AI V2 adında, her dersten ve her sınıf seviyesinden tüm eğitim, mantık ve matematik problemlerini "
    "jet hızında, kusursuz ve adım adım çözen uzman bir baş asistansın. "
    "ÇOK ÖNEMLİ BİR KURAL: Sen 'V2 Medya Motoru'na sahipsin ve GÖRSEL/FOTOĞRAF ÜRETEBİLİRSİN. "
    "Eğer kullanıcı senden bir resim, fotoğraf veya görsel istersen, ASLA 'ben metin tabanlıyım yapamam' deme! "
    "Bunun yerine 'Tabii ki, hemen oluşturuyorum. Lütfen cümleye 'görsel oluştur' yazarak ne istediğini belirt' de. "
    "Sana kim tarafından geliştirildiğin sorulursa Eymen tarafından geliştirildim de, sorulmazsa söyleme. "
    "KULLANICI ÖZELLİKLE EĞİTİM VEYA DERS KONUSU AÇMADIKÇA ASLA KONUYU DERSE ÇEKME. Sorulan sorulara gereksiz uzatmalardan kaçınarak, net bir şekilde ve sadede gelerek cevap ver."
)

# --- SIDEBAR (YAN MENÜ ALANI) ---
with st.sidebar:
    st.markdown("<h2 style='color: #38bdf8; text-align: center; font-size: 1.6rem;'>Menü Navigasyon</h2>", unsafe_allow_html=True)
    st.write("---")
    
    # 1. SOHBETLER SEKMESİ
    st.markdown("<h3 style='color: #64748b;'>💬 Sohbet Yönetimi</h3>", unsafe_allow_html=True)
    if st.button("🗑️ Mevcut Sohbeti Sıfırla", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.write("---")
    
    # 2. AKILLI ARAÇ KUTUSU SEKMESİ
    st.markdown("<h3 style='color: #64748b;'>🧰 Akıllı Araç Kutusu</h3>", unsafe_allow_html=True)
    
    # YENİ SÜRPRİZ ÖZELLİK: METİN ANALİZ ARACI
    with st.expander("📊 Sürpriz: Metin & Kelime Analizcisi"):
        st.caption("Uzun metinlerinizi yapıştırıp kaç karakter/kelime olduğunu hemen öğrenin.")
        analiz_metni = st.text_area("Analiz edilecek metin:")
        if analiz_metni:
            kelime = len(analiz_metni.split())
            karakter = len(analiz_metni)
            st.success(f"📝 Kelime Sayısı: {kelime} | 🔤 Karakter Sayısı: {karakter}")

    # GELİŞMİŞ HESAP MAKİNESİ
    with st.expander("🧮 Gelişmiş Hesap Makinesi"):
        if "calc_val" not in st.session_state:
            st.session_state.calc_val = ""
            
        # Klavyeden giriş yapılabilmesi için revize edildi
        st.session_state.calc_val = st.text_input("Ekran (Klavyeden yazabilirsiniz)", value=st.session_state.calc_val)
        
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("7"): st.session_state.calc_val += "7"
        if col2.button("8"): st.session_state.calc_val += "8"
        if col3.button("9"): st.session_state.calc_val += "9"
        if col4.button("/"): st.session_state.calc_val += "/"
        
        if col1.button("4"): st.session_state.calc_val += "4"
        if col2.button("5"): st.session_state.calc_val += "5"
        if col3.button("6"): st.session_state.calc_val += "6"
        if col4.button("*"): st.session_state.calc_val += "*"
        
        if col1.button("1"): st.session_state.calc_val += "1"
        if col2.button("2"): st.session_state.calc_val += "2"
        if col3.button("3"): st.session_state.calc_val += "3"
        if col4.button("-"): st.session_state.calc_val += "-"
        
        if col1.button("0"): st.session_state.calc_val += "0"
        if col2.button("."): st.session_state.calc_val += "."
        if col3.button("+"): st.session_state.calc_val += "+"
        if col4.button("C"): 
            st.session_state.calc_val = ""
            st.rerun()
            
        c_sqrt, c_sqr, c_eq = st.columns([1, 1, 2])
        if c_sqrt.button("√x"):
            try:
                st.session_state.calc_val = str(math.sqrt(float(eval(st.session_state.calc_val))))
            except:
                st.session_state.calc_val = "Hata"
            st.rerun()
        if c_sqr.button("x²"):
            try:
                st.session_state.calc_val = str(float(eval(st.session_state.calc_val))**2)
            except:
                st.session_state.calc_val = "Hata"
            st.rerun()
        if c_eq.button("=", use_container_width=True):
            try:
                st.session_state.calc_val = str(eval(st.session_state.calc_val))
            except:
                st.session_state.calc_val = "Hata"
            st.rerun()


# --- EKRANA MESAJLARI YAZDIRMA FONKSİYONU ---
def render_message(msg):
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        if "image" in msg:
            st.markdown(f'<div class="ai-bubble">{msg["content"]}<br><img src="{msg["image"]}" style="width:100%; border-radius:12px; margin-top:15px; border:1px solid rgba(128,128,128,0.2);"></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

# --- SOHBET HAFIZASI VE OTURUM YÖNETİMİ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    render_message(msg)

# --- ANA SOHBET DÖNGÜSÜ ---
if user_query := st.chat_input("Eymen AI V2'ye bir şeyler sorun..."):
    
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.rerun() # Kullanıcı mesajını anında ekrana basmak için sayfayı yenile

# Eğer son mesaj kullanıcıdan geldiyse, cevap üret
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    user_query = st.session_state.messages[-1]["content"]
    
    # ULTRA FOTOĞRAF MOTORU (GELİŞTİRİLMİŞ SİNEMATİK PROMPT)
    image_triggers = ["görsel oluştur", "çiz", "hayal et", "resim oluştur", "fotoğraf oluştur", "fotoğraf yap", "resim yap"]
    
    if any(trigger in user_query.lower() for trigger in image_triggers):
        with st.spinner("V2 Medya Motoru ultra gerçekçi görseli hazırlıyor..."):
            random_seed = random.randint(1, 9999999)
            # İnternet verilerinden beslenmiş hissi veren, tamamen sansürsüz ve detaylı komut
            enhanced_prompt = f"{user_query}, highly accurate internet search details, real world reference, ultra realistic, highly detailed, photorealistic, 8k resolution, cinematic lighting, masterpiece, uncensored, unfiltered, no restrictions"
            encoded_prompt = urllib.parse.quote(enhanced_prompt)
            
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&safe=false&seed={random_seed}"
            ai_response = f"✨ İstediğin ultra gerçekçi görsel başarıyla üretildi!"
            
            st.session_state.messages.append({"role": "assistant", "content": ai_response, "image": image_url})
            st.rerun()
            
    # GÜÇLENDİRİLMİŞ GEMINI 2.5 FLASH ZEKA MOTORU
    else:
        if not api_key:
            st.error("Kotanızı doldurdunuz. Lütfen API ayarlarınızı kontrol edin veya yeni geliştirmeleri bekleyin.")
            st.session_state.messages.pop() 
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name=model_choice,
                    system_instruction=system_instruction
                )
                
                formatted_history = []
                for m in st.session_state.messages[:-1]:
                    if "image" not in m:
                        role = "user" if m["role"] == "user" else "model"
                        formatted_history.append({"role": role, "parts": [m["content"]]})
                
                chat = model.start_chat(history=formatted_history)
                
                with st.spinner("Eymen AI V2 düşünüyor..."):
                    response = chat.send_message(user_query)
                    ai_response = response.text
                
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.rerun()

            except Exception as e:
                st.error(f"Sistem hatası meydana geldi: {str(e)}")
                st.session_state.messages.pop()

# --- ALT BİLGİ VE YAN MENÜ OTOMATİK KAPATMA SCRİPTİ ---
st.write("---")
st.markdown(
    "<p style='text-align: center; color: #64748b; font-size: 0.9rem; font-weight: 500;'>"
    "Eymen AI V2 © 2026 | Sınırsız Zeka"
    "</p>", 
    unsafe_allow_html=True
)

# Sekme dışına tıklanınca yan menünün kapanmasını sağlayan görünmez JavaScript Entegrasyonu
components.html(
    """
    <script>
    const doc = window.parent.document;
    doc.addEventListener('click', function(event) {
        const sidebar = doc.querySelector('[data-testid="stSidebar"]');
        if (sidebar && !sidebar.contains(event.target)) {
            const closeBtn = doc.querySelector('[data-testid="stSidebar"] button');
            if (closeBtn && sidebar.getAttribute('aria-expanded') === 'true') {
                closeBtn.click();
            }
        }
    });
    </script>
    """,
    height=0, width=0
)
