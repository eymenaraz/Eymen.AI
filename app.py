import streamlit as st
import google.generativeai as genai

st.title("🛠️ Model Tanılama Aracı")

API_KEY = "AIzaSyCY_ZsASlHUCQ6h7NA9ETnfHz2QcslNL6E" # Lütfen güncel anahtarını buraya yaz

try:
    genai.configure(api_key=API_KEY)
    
    st.write("### Kullanılabilir Modeller:")
    # Bu kısım anahtarının desteklediği modelleri listeleyecek
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    st.write(models)
    
except Exception as e:
    st.error(f"Bağlantı Hatası: {e}")
