import streamlit as st
import google.generativeai as genai

# 1. Arayüz ve Tasarım
st.set_page_config(page_title="Eymen AI", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    h1 { color: #1e1e1e; font-family: 'Arial', sans-serif; text-align: center; margin-bottom: 20px; }
    [data-testid="stChatMessage"] { border-radius: 15px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Eymen AI")

# 2. Bağlantı Ayarları (API Anahtarını Streamlit Secrets kısmına ekle!)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("API Anahtarı bulunamadı! Lütfen Streamlit Settings > Secrets kısmına GOOGLE_API_KEY ekle.")
    st.stop()

# 3. Model Kimliği (System Instruction)
system_prompt = "Sen Eymen AI'sin. Eymen tarafından geliştirildin. Kullanıcı sana 'Eymen AI', 'Eymen', 'Eym' gibi isimlerle seslenebilir. Modern, hızlı, yardımsever ve zekisin."

if "model" not in st.session_state:
    st.session_state.model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction=system_prompt
    )

# 4. Sohbet Geçmişi
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 5. Sohbet Akışı
if prompt := st.chat_input("Eymen AI'ye bir şey sor..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            response = st.session_state.model.generate_content(prompt)
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("Bir hata oluştu, lütfen tekrar dene.")
