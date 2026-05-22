import streamlit as st
import google.generativeai as genai

# --- AYARLAR ---
st.set_page_config(page_title="Eymen AI", page_icon="🤖", layout="centered")

# API Anahtarını buraya entegre ettim
API_ANAHTARI = "AIzaSyCPQanGNqt9zxU4fvib3EjRkL__J9UDgEE"

genai.configure(api_key=API_ANAHTARI)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- ŞIK TASARIM (CSS) ---
st.markdown("""
    <style>
    /* Arka plan ve genel yazı */
    .stApp { background-color: #FFFFFF; }
    
    /* Başlık stili */
    h1 { color: #40E0D0; text-align: center; font-family: sans-serif; font-weight: 800; }
    
    /* Buton stili */
    div.stButton > button:first-child { 
        background-color: #40E0D0; 
        color: white; 
        border-radius: 20px; 
        border: none;
        padding: 10px 25px;
        width: 100%;
        font-weight: bold;
    }
    
    /* Giriş kutusu stili */
    .stTextInput > div > div > input { 
        border: 2px solid #40E0D0; 
        border-radius: 10px; 
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ARAYÜZ ---
st.title("✨ Eymen AI")
st.markdown("<p style='text-align: center; color: #7f8c8d;'>Modern, hızlı ve kişisel asistanın.</p>", unsafe_allow_html=True)

# Boşluk bırakmak için
st.write("---")

kullanici_mesaji = st.text_input("Sana nasıl yardımcı olabilirim?")

if st.button("Soruyu Gönder"):
    if kullanici_mesaji:
        with st.spinner("Eymen AI analiz ediyor..."):
            try:
                cevap = model.generate_content(kullanici_mesaji)
                st.markdown("### 🤖 Eymen AI")
                st.info(cevap.text)
            except Exception as e:
                st.error("Bir hata oluştu, lütfen internet bağlantını veya API anahtarını kontrol et.")
    else:
        st.warning("Lütfen bir soru yaz!")
