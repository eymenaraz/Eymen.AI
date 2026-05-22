import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Eymen AI", layout="centered")

def get_response(prompt):
    # Secrets'taki anahtarlarını buraya listele
    keys = [st.secrets["KEY_1"], st.secrets["KEY_2"], st.secrets["KEY_3"]]
    
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.5-pro')
            return model.generate_content(prompt).text
        except:
            continue # Hata alırsan durma, diğer anahtarı dene
    return "Tüm kotalar doldu. Lütfen yarın tekrar dene."

st.title("⚡ Eymen AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        response_text = get_response(prompt)
        st.write(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
