
import streamlit as st
import google.generativeai as genai
import time, random
from PIL import Image

st.set_page_config(page_title="Eymen AI", layout="centered")

# --- CSS: AVATARLARI KÖKTEN SİL VE LOGO YERLEŞTİR ---
st.markdown("""
    <style>
    /* Avatarları ve Streamlit'in kendi ikonlarını SİL */
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"], 
    [data-testid="stChatMessageAvatar"] { display: none !important; }
    
    /* Mesaj genişliğini ayarla */
    .stChatMessage { padding-left: 0px !important; }
    
    /* Logo ve Başlık Hizalama */
    .header-container { display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- MATEMATİKSEL ZEKA VE HIZLI MODEL ---
def get_model_with_retry(prompt, img=None):
    # API Listesi (Secrets'tan gelenler)
    keys = [st.secrets[f"KEY_{i}"] for i in range(1, 11)]
    
    for attempt in range(5):
        try:
            api_key = random.choice(keys)
            genai.configure(api_key=api_key)
            # Matematiksel kesinlik için flash modeli
            model = genai.GenerativeModel('gemini-2.5-flash',
                system_instruction="""Sen bir Matematik ve Geometri dahisisin. 
                3x+8y=24 gibi denklemleri y=mx+n formuna çevirip eğimi (m) anında bulursun. 
                3-4-5, 5-12-13 üçgenlerini ve tüm özel üçgenleri çok iyi bilirsin. 
                Cevaplarını adım adım, formülleri göstererek ve çok hızlı bir şekilde ver. 
                Hata yapma, işlem basamaklarını net yaz.Geometrik Cisimlerin hacim yüzey alanı yanal alanının nasıl hesaplandığı konusunda dahisin hatasız yapıyorsun daire grafiği karekök veri analizi üslü ifadeler sorularında da dahisin hatasız yapıyorsun.""")
            
            if img: return model.generate_content([prompt, img])
            return model.generate_content(prompt)
        except:
            time.sleep(0.3)
            continue
    return None

# --- LOGO VE BAŞLIK ---
st.markdown(f"""
    <div class="header-container">
        <img src="https://i.hizliresim.com/gvewvtj.png" width="40">
        <h2 style="margin:0;">Eymen AI</h2>
    </div>
""", unsafe_allow_html=True)

# --- SOHBET ---
if "sessions" not in st.session_state: st.session_state.sessions = {"Sohbet 1": []}
if "current_session" not in st.session_state: st.session_state.current_session = "Sohbet 1"

# Sohbetleri Sidebar'da yönet
with st.sidebar:
    if st.button("➕ Yeni Sohbet"):
        name = f"Sohbet {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[name] = []
        st.session_state.current_session = name
    for name in list(st.session_state.sessions.keys()):
        if st.button(name): st.session_state.current_session = name

uploaded_file = st.file_uploader("Dosya", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
messages = st.session_state.sessions[st.session_state.current_session]

for msg in messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image": st.image(msg["content"], use_container_width=True)
        else: st.markdown(msg["content"])

if prompt := st.chat_input(""):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        img = Image.open(uploaded_file) if uploaded_file else None
        
        # Resim oluşturma (Analitik değilse)
        if "çiz,oluştur,resmi vb." in prompt.lower() or "oluştur" in prompt.lower():
            img_url = f"https://pollinations.ai/p/{prompt}?width=512&height=512&nologo=true"
            st.image(img_url, use_container_width=True)
            messages.append({"role": "assistant", "content": img_url, "type": "image"})
        else:
            response = get_model_with_retry(prompt, img)
            if response:
                st.markdown(response.text)
                messages.append({"role": "assistant", "content": response.text})
            else:
                st.error("Kotayı doldurdunuz.Bu sorunu düzeltmek için biraz zamana ihtiyacımız var.Lütfen şimdilik yeni güncellemeleri ve geliştirmeleri bekleyin")
    st.rerun()
