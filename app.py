import streamlit as st
import google.generativeai as genai
import random
import time
from PIL import Image

st.set_page_config(page_title="Eymen AI", page_icon="🧠", layout="centered")

# --- AVATARLAR VE LOGO ---
BOT_AVATAR = "https://i.hizliresim.com/gvewvtj.png"
USER_AVATAR = "👤"

# --- MOBİL İÇİN TEMİZ CSS ---
st.markdown("""
    <style>
    .stChatInput { padding-bottom: 20px; }
    .header-box { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- ÜST BİLGİ VE LOGO ---
st.markdown(f"""
    <div class="header-box">
        <img src="{BOT_AVATAR}" width="50" style="border-radius: 10px;">
        <h2 style="margin: 0;">Eymen AI</h2>
    </div>
""", unsafe_allow_html=True)

# --- SİSTEM TALİMATI ---
SYS_INST = """Sen Eymen AI'sin. Dünyanın en zeki asistanısın. 
LGS (Matematik, Fen, Türkçe, İnkılap, Din, İngilizce) ve lise dahil tüm sınıf seviyelerinde bir dahisin. 
Sinan Kuzucu, Okyanus Master gibi en zorlu ve yeni nesil mantık-muhakeme sorularını şak diye anlar, 
hatasız, adım adım ve harika bir dille çözersin. Özel üçgenleri, eğimi, cebirsel ifadeleri kusursuz yaparsınGeometrik cisimler dik prizmalar hepsinin alan hac,m yüzey alanı yanal alanının nasıl bulunduğu konusunda dahisin hata yapmıyorsun ayrıca sana hangi sınıftan hangi dersten soru sorulursa sorulsun hatasız çözüm ile açıklayarak yapıyorsun sıfır hata ile.
Kullanıcı belge veya fotoğraf atarsa onu satır satır inceler, detaylı analiz edersin. 
Asla yavaşlama, her sorunu çöz."""

# --- AKILLI API YÖNETİCİSİ (HATA ÇÖZÜCÜ) ---
def generate_with_retry(contents):
    # Sadece "AIza" ile başlayan GERÇEK anahtarları listeye al
    valid_keys = []
    for i in range(1, 11):
        key = st.secrets.get(f"KEY_{i}", "")
        if key.startswith("AIza"):
            valid_keys.append(key)
            
    if not valid_keys:
        return "SİSTEM HATASI: Streamlit Secrets kısmında geçerli bir API anahtarı bulunamadı! Lütfen kontrol et."
    
    # Anahtarları rastgele karıştır
    random.shuffle(valid_keys)
    
    last_error = ""
    # Anahtarları sırayla dene
    for api_key in valid_keys:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYS_INST)
            response = model.generate_content(contents)
            return response.text
        except Exception as e:
            last_error = str(e)
            time.sleep(1) # Hata verirse 0.5 saniye bekle, diğer anahtarı dene
            continue
            
    return f"SİSTEM HATASI: Tüm anahtarlar denendi ama cevap alınamadı. Hata detayı: {last_error}"

# --- SOHBET YÖNETİMİ ---
if "sessions" not in st.session_state: st.session_state.sessions = {"Sohbet 1": []}
if "current_session" not in st.session_state: st.session_state.current_session = "Sohbet 1"

with st.sidebar:
    st.header("Sohbet Geçmişi")
    if st.button("➕ Yeni Sohbet"):
        name = f"Sohbet {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[name] = []
        st.session_state.current_session = name
    for name in list(st.session_state.sessions.keys()):
        if st.button(name): st.session_state.current_session = name

# --- DOSYA YÜKLEME ---
uploaded_file = st.file_uploader("Fotoğraf,problem veya PDF Yükle", type=["jpg", "png", "jpeg", "pdf"])

# --- MESAJLARI GÖSTER ---
messages = st.session_state.sessions[st.session_state.current_session]
for msg in messages:
    avatar = USER_AVATAR if msg["role"] == "user" else BOT_AVATAR
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("type") == "image": st.image(msg["content"], use_container_width=True)
        else: st.markdown(msg["content"])

# --- İŞLEM VE DÜŞÜNME ANİMASYONU ---
if prompt := st.chat_input("Eymen AI'ye birşeyler sor"):
    
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR): 
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        with st.spinner("Eymen AI düşünüyor 💭..."):
            
            # Resim Çizdirme Kontrolü
            if any(word in prompt.lower() for word in ["çiz", "oluştur", "resmini yap", "hayal et"]):
                img_url = f"https://pollinations.ai/p/{prompt}?width=512&height=512&nologo=true"
                st.image(img_url, use_container_width=True)
                messages.append({"role": "assistant", "content": img_url, "type": "image"})
            
            # Soru, PDF ve Matematik Çözümleri
            else:
                contents = [prompt]
                
                if uploaded_file:
                    if uploaded_file.name.lower().endswith(".pdf"):
                        contents.append({"mime_type": "application/pdf", "data": uploaded_file.getvalue()})
                    else:
                        img = Image.open(uploaded_file)
                        contents.append(img)
                
                # Akıllı API yöneticisine gönder
                answer = generate_with_retry(contents)
                st.markdown(answer)
                messages.append({"role": "assistant", "content": answer})
