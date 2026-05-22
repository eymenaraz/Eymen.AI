import streamlit as st
import google.generativeai as genai

# Arayüz ayarları
st.set_page_config(page_title="Eymen AI", layout="centered")

# API Anahtarı
genai.configure(api_key="AIzaSyCY_ZsASlHUCQ6h7NA9ETnfHz2QcslNL6E")

# KİMLİK TANIMI (System Instruction)
# Modelin her zaman Eymen AI olduğunu bilmesini sağlıyoruz
system_instruction = """Sen Eymen AI'sin. 
Kullanıcı sana 'Eymen AI', 'Eymen', 'Eym' veya benzeri isimlerle hitap edebilir. 
Sen Eymen tarafından yaratılmış, hızlı ve modern bir yapay zekasın. 
Kendini her zaman Eymen AI olarak tanıt ve bu kimlikle cevap ver."""

# Modeli kimlik ile tanımla
if "model" not in st.session_state:
    st.session_state.model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction=system_instruction
    )

st.title("⚡ Eymen AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları göster
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Kullanıcı girişi
if prompt := st.chat_input("Eymen AI ile konuş..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        # Model artık kim olduğunu biliyor
        response = st.session_state.model.generate_content(prompt)
        st.write(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
