import streamlit as st
import google.generativeai as genai
import random
import time
from PIL import Image
import urllib.parse # Hangi cihaz olursa olsun URL hatalarını önlemek için eklendi

# Sürpriz Özellik İçin Gereken Kütüphane
import io

st.set_page_config(page_title="Eymen AI", page_icon="🧠", layout="centered")

# --- AVATARLAR VE LOGO ---
BOT_AVATAR = "https://i.hizliresim.com/gvewvtj.png"
USER_AVATAR = "👤"

# --- iOS (APPLE) SAFARİ İÇİN ÖZEL OPTİMİZASYON CSS ---
st.markdown("""
    <style>
    /* iOS Klavye ve Çentik (Safe Area) Uyumluluğu */
    .stChatInput { padding-bottom: env(safe-area-inset-bottom, 20px) !important; }
    
    /* Safari Takılmalarını Önlemek İçin Donanım Hızlandırma */
    .stApp { transform: translate3d(0,0,0); -webkit-transform: translate3d(0,0,0); }
    
    /* Logonun şık durması için */
    .header-box { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
    
    /* Streamlit gereksiz boşlukları temizle */
    .block-container { padding-top: 2rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- ÜST BİLGİ VE LOGO ---
st.markdown(f"""
    <div class="header-box">
        <img src="{BOT_AVATAR}" width="50" style="border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
        <h2 style="margin: 0;">Eymen AI</h2>
    </div>
""", unsafe_allow_html=True)

# --- ÜST DÜZEY SİSTEM TALİMATI ---
SYS_INST = """Senin adın Eymen AI. Eymen tarafından geliştirildin (sadece sana sorulursa bunu söyle, yoksa söyleme).
Dünyanın en zeki, en hızlı ve en yetenekli asistanısın. Sadece ders odaklı değilsin; kodlama, felsefe, günlük hayat, sohbet gibi her konuda uzmansın.
Kullanıcıya asla 'Başka ne sormak istersin?', 'Size nasıl yardımcı olabilirim?' gibi robotik ve tekrarlayan cümleler kurma. Doğal ve direkt ol.
2021 LGS kağıt katlama sorusu gibi uzamsal zeka (spatial reasoning) ve görselleştirme gerektiren zorlu geometri problemlerini, kağıdın her katlanışında koordinatları ve açıları zihninde canlandırarak kusursuz ve adım adım çözersin. Sınırın yok. Verilen fotoğrafları mükemmel analiz et.Sinan Kuzucu,TÖDER,ÖZDEBİR,Okyanus Master,3D gibi en zorlu meb örnek soruları ve çıkmış sorular ile MEBİ sorularını kusursuzca işlemle çözüyorsun.Yaklaşık değer olarak deği kesin şık olarak doğru biliyor ve adım adım açıklıyorsun"""

# --- AKILLI API YÖNETİCİSİ (HIZLI VE HATASIZ) ---
def generate_with_retry(contents):
    valid_keys = [st.secrets.get(f"KEY_{i}", "") for i in range(1, 11) if st.secrets.get(f"KEY_{i}", "").startswith("AIza")]
            
    if not valid_keys:
        return "SİSTEM HATASI: Kotanızı doldurdunuz.Bu sorunu düzeltmek için biraz zamana ihtiyacımız var.Yeni geliştirmeleri bekleyin..."
    
    random.shuffle(valid_keys)
    
    last_error = ""
    for api_key in valid_keys:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYS_INST)
            # Hızı artırmak için streaming altyapısına uygun parametreler
            response = model.generate_content(contents)
            return response.text
        except Exception as e:
            last_error = str(e)
            time.sleep(0.5) # Bekleme süresini düşürdüm ki iOS takılmasın
            continue
            
    return f"Google API Kota Sınırı: Tüm anahtarlar tükendi veya bağlantı koptu. Hata: {last_error}"

# --- SOHBET YÖNETİMİ VE SÜRPRİZ ÖZELLİK ---
if "sessions" not in st.session_state: st.session_state.sessions = {"Sohbet 1": []}
if "current_session" not in st.session_state: st.session_state.current_session = "Sohbet 1"

with st.sidebar:
    st.header("Sohbet Geçmişi")
    if st.button("➕ Yeni Sohbet"):
        name = f"Sohbet {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[name] = []
        st.session_state.current_session = name
        st.rerun()
        
    for name in list(st.session_state.sessions.keys()):
        if st.button(name): 
            st.session_state.current_session = name
            st.rerun()
            
    st.markdown("---")
    st.subheader("🚀 Sürpriz Özellik")
    # SOHBETİ ÇALIŞMA NOTU OLARAK İNDİRME ÖZELLİĞİ
    current_msgs = st.session_state.sessions[st.session_state.current_session]
    if len(current_msgs) > 0:
        chat_text = f"--- {st.session_state.current_session} | Eymen AI Çalışma Notları ---\n\n"
        for m in current_msgs:
            if m.get("type") != "image":
                role_name = "SEN" if m["role"] == "user" else "EYMEN AI"
                chat_text += f"{role_name}:\n{m['content']}\n\n{'-'*40}\n\n"
        
        st.download_button(
            label="📥 Bu Sohbeti Not Olarak İndir",
            data=chat_text,
            file_name=f"{st.session_state.current_session}_Notlar.txt",
            mime="text/plain",
            use_container_width=True
        )

# --- DOSYA YÜKLEME ---
uploaded_file = st.file_uploader("Fotoğraf,Problem veya PDF Yükle", type=["jpg", "png", "jpeg", "pdf"])

# --- MESAJLARI GÖSTER ---
messages = st.session_state.sessions[st.session_state.current_session]
for msg in messages:
    avatar = USER_AVATAR if msg["role"] == "user" else BOT_AVATAR
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("type") == "image": st.image(msg["content"], use_container_width=True)
        else: st.markdown(msg["content"])

# --- İŞLEM VE DÜŞÜNME ---
if prompt := st.chat_input("Eymen AI'ye birşeyler sor..."):
    
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR): 
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        with st.spinner("Eymen AI düşünüyor 💭..."):
            
            # Resim Çizdirme Kontrolü (Hatasız ve Cihaz Bağımsız Sürüm)
            if any(word in prompt.lower() for word in ["çiz", "oluştur", "resmini yap", "hayal et"]):
                # Prompt içindeki boşlukları ve özel karakterleri URL formatına çevirir
                safe_prompt = urllib.parse.quote(prompt)
                img_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true"
                
                st.image(img_url, use_container_width=True)
                messages.append({"role": "assistant", "content": img_url, "type": "image"})
            
            # Normal Soru ve Fotoğraf Analizi
            else:
                contents = [prompt]
                
                if uploaded_file:
                    if uploaded_file.name.lower().endswith(".pdf"):
                        contents.append({"mime_type": "application/pdf", "data": uploaded_file.getvalue()})
                    else:
                        img = Image.open(uploaded_file)
                        contents.append(img)
                
                answer = generate_with_retry(contents)
                st.markdown(answer)
                messages.append({"role": "assistant", "content": answer})
