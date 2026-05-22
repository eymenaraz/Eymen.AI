import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Eymen AI", page_icon="🤖")

st.markdown("<h1 style='color: #40E0D0; text-align: center;'>✨ Eymen AI</h1>", unsafe_allow_html=True)

# Buraya API anahtarını yaz
API_KEY = "AIzaSyCY_ZsASlHUCQ6h7NA9ETnfHz2QcslNL6E"

try:
    genai.configure(api_key=API_KEY)
    # Model ismi yerine 'gemini-1.5-flash' kullanmak yerine,
    # doğrudan varsayılanı kullanmak için model adını boş bırakıyoruz 
    # veya doğrudan "gemini-pro" deniyoruz.
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"Sistem Hatası: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Eymen AI'ye bir şey sor..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Buradaki ismi de güncelledik
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("Bağlantı hatası.")
            st.write(f"Hata detayı: {e}")
