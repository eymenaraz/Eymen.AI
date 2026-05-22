import streamlit as st
import google.generativeai as genai
import time

st.set_page_config(page_title="Eymen AI", layout="centered")

def get_response(prompt):
    # Yeni oluşturduğun temiz anahtarların isimleri
    keys = [st.secrets["KEY_1"], st.secrets["KEY_2"], st.secrets["KEY_3"]]
    
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            # Yanıt almadan önce küçük bir bekleme (hız limitine takılmamak için)
            time.sleep(1)
            return model.generate_content(prompt).text
        except Exception as e:
            if "ResourceExhausted" in str(e):
                continue # Diğer anahtara geç
            else:
                return "Bağlantı hatası: " + str(e)
    return "Tüm anahtarların kotası dolu. Lütfen yarın tekrar dene."

st.title("⚡ Eymen AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Eymen AI'ye sor..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        response_text = get_response(prompt)
        st.write(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
