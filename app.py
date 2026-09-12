import streamlit as st
import json
import urllib.parse
import urllib.request
import os
import random
import string
import google.generativeai as genai
import requests
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import pytz
import asyncio
import edge_tts

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Eyx AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SOHBET VE MOTOR HAFIZASI ---
if "chats" not in st.session_state:
    st.session_state.chats = {"Sohbet 1": []}
    st.session_state.current_chat = "Sohbet 1"

if "image_seed" not in st.session_state:
    st.session_state.image_seed = random.randint(1, 99999999)

if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None

if "dynamic_persona_state" not in st.session_state:
    st.session_state.dynamic_persona_state = "Standart Dengeli Asistan"

st.session_state.messages = st.session_state.chats[st.session_state.current_chat]

# --- CSS VE STYLING (EYX AI TEMA ENTEGRASYONU) ---
st.markdown("""
<style>
    [data-testid="stChatInput"] textarea, .stTextInput input, textarea { font-size: 16px !important; -webkit-text-size-adjust: 100%; }
    [data-testid="stSidebar"] { border-right: 1px solid rgba(128, 128, 128, 0.15); background-color: #121316 !important; }
    .user-bubble { background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: white; padding: 14px 18px; border-radius: 20px 20px 4px 20px; margin: 10px 0 10px auto; max-width: 75%; width: fit-content; box-shadow: 0 4px 10px rgba(99, 102, 241, 0.15); font-family: 'Segoe UI', system-ui, sans-serif; font-size: 1.02rem; }
    .ai-bubble { background: linear-gradient(135deg, rgba(30, 31, 38, 0.9) 0%, rgba(20, 21, 26, 0.9) 100%); color: #e2e8f0; padding: 14px 18px; border-radius: 20px 20px 20px 4px; margin: 10px auto 10px 0; max-width: 75%; width: fit-content; border: 1px solid rgba(129, 140, 248, 0.3); box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); font-family: 'Segoe UI', system-ui, sans-serif; font-size: 1.02rem; }
    
    .neon-loading-box {
        background: linear-gradient(135deg, rgba(20, 21, 26, 0.95) 0%, rgba(99, 102, 241, 0.25) 100%);
        color: #818cf8;
        padding: 14px 20px;
        border-radius: 14px;
        margin: 10px auto 10px 0;
        max-width: 85%;
        border: 1px solid rgba(129, 140, 248, 0.5);
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 1rem;
        font-weight: 500;
        display: flex;
        align-items: center;
    }

    .logo-container { text-align: center; margin-bottom: 2px; padding: 5px; }
    .brand-eyx { font-size: 3.5rem; font-weight: 900; color: #6366f1; }
    .brand-ai { font-size: 3.5rem; font-weight: 900; color: #a5b4fc; margin-left: 10px; }
    .subtitle { color: #94a3b8; text-align: center; font-size: 1.1rem; font-weight: 500; margin-bottom: 25px; }
    .typing-dots { display: inline-flex; align-items: center; margin-left: 8px; }
    .dot { width: 6px; height: 6px; background-color: #818cf8; border-radius: 50%; margin: 0 2px; animation: bounce 1.4s infinite ease-in-out both; }
    .dot:nth-child(1) { animation-delay: -0.32s; }
    .dot:nth-child(2) { animation-delay: -0.16s; }
    @keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.4; } 40% { transform: scale(1); opacity: 1; } }

    .file-preview-card {
        position: relative;
        background: rgba(20, 21, 26, 0.7);
        border: 1px solid rgba(129, 140, 248, 0.3);
        padding: 10px 15px;
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 15px;
    }
    .file-preview-text { color: #e2e8f0; font-size: 0.95rem; font-family: 'Segoe UI', system-ui, sans-serif; }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ALANI ---
st.markdown('<div class="logo-container"><span class="brand-eyx">Eyx</span><span class="brand-ai">AI</span></div>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">v3.9 - Neural Studio</p>', unsafe_allow_html=True)

# --- DOSYA/FOTOĞRAF YÜKLEME VE ÖNİZLEME ---
uploaded_file = st.file_uploader("📁 Dosya veya Fotoğraf Yükle", type=["png", "jpg", "jpeg", "pdf", "txt", "webp"], help="Sadece analiz içindir.", label_visibility="collapsed")

if uploaded_file is not None:
    st.session_state.uploaded_file_data = uploaded_file

if st.session_state.uploaded_file_data is not None:
    col_prev1, col_prev2 = st.columns([8, 1])
    with col_prev1:
        st.markdown(f"""
        <div class="file-preview-card">
            <span>📎</span>
            <span class="file-preview-text"><b>Yüklenen Dosya:</b> {st.session_state.uploaded_file_data.name}</span>
        </div>
        """, unsafe_allow_html=True)
    with col_prev2:
        if st.button("✕", help="Dosyayı kaldır", key="remove_file_btn"):
            st.session_state.uploaded_file_data = None
            st.rerun()

# --- ARKA PLAN CHROME MOTORU (WEB ARAMA) ---
def chrome_motoru_ile_ara(sorgu):
    try:
        sorgu_terimi = sorgu
        sport_keywords = ["maç", "skor", "futbol", "puan durumu", "fikstür", "basketbol", "canlı skor", "iddaa", "şampiyonlar ligi", "lig", "süper lig", "gol", "oynadı", "kaç kaç bitti"]
        if any(k in sorgu.lower() for k in sport_keywords):
            sorgu_terimi = f"site:flashscore.com.tr {sorgu}"
            
        url = f"https://www.google.com/search?q={urllib.parse.quote(sorgu_terimi)}&hl=tr&gl=tr"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        resp = requests.get(url, headers=headers, timeout=6)
        if resp.status_code == 200:
            import re
            snippets = re.findall(r'<div[^>]*class="BNeawe s3v9rd AP7Wnd"[^>]*>(.*?)</div>', resp.text)
            if not snippets:
                snippets = re.findall(r'<span[^>]*>(.*?)</span>', resp.text)
            
            clean_snippets = [re.sub(r'<.*?>', '', s) for s in snippets[:8]]
            if clean_snippets:
                return " | ".join([s for s in clean_snippets if len(s) > 12])
    except:
        pass
    return ""

def get_current_turkey_time():
    try:
        tr_tz = pytz.timezone('Europe/Istanbul')
        tr_time = datetime.now(tr_tz)
        return tr_time.strftime('%Y-%m-%d %H:%M:%S (%A)')
    except:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# --- HIZLI GEMINI ÇAĞIRICI ---
def calistir_gemini(sorgu, sistem_talimati, geçmiş=None, görsel_parçası=None):
    son_hata = "API anahtarı bulunamadı."
    an_zaman = get_current_turkey_time()
    
    kaynak_verisi = chrome_motoru_ile_ara(sorgu)
    web_bilgisi = f"\n[Güncel Canlı Veri Tabanı Sonucu]: {kaynak_verisi}" if kaynak_verisi else ""

    tam_sistem_talimati = (
        f"🚨 KESİN KURALLAR 🚨:\n"
        f"1. Bulunduğun Anın Kesin Türkiye Saati (UTC+3): {an_zaman}.\n"
        f"2. Ünlüler, futbolcular, biyografiler, maçlar ve güncel olaylarla ilgili her soruda yukarıdaki Canlı Veri Tabanı Sonuçlarını mutlak surette baz alarak kişileri ve bilgileri tam olarak tanı.\n"
        f"3. Bilgileri en güncel haliyle süzerek **net, direkt ve kesin yanıtı doğrudan sen ver**. Asla dış kaynaklara veya linklere yönlendirme yapma.\n\n"
        f"{web_bilgisi}\n{sistem_talimati}"
    )
    
    for i in range(1, 11):
        key_adı = f"KEY_{i}"
        if key_adı in st.secrets:
            aktif_key = st.secrets[key_adı]
            try:
                genai.configure(api_key=aktif_key)
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash", 
                    system_instruction=tam_sistem_talimati
                )
                
                if geçmiş is not None:
                    chat = model.start_chat(history=geçmiş)
                    yanit = chat.send_message([görsel_parçası, sorgu]) if görsel_parçası else chat.send_message(sorgu)
                else:
                    yanit = model.generate_content([görsel_parçası, sorgu]) if görsel_parçası else model.generate_content(sorgu)
                
                if yanit and yanit.text:
                    return yanit.text, True
            except Exception as e:
                son_hata = str(e)
                continue
                
    return f"Bağlantı hatası oluştu: {son_hata}", False

def alternatif_gorsel_uret(prompt_metni):
    try:
        encoded_prompt = urllib.parse.quote(prompt_metni)
        servis_urleri = [
            f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={random.randint(1,999999)}",
            f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed={random.randint(1,999999)}"
        ]
        for url in servis_urleri:
            resp = requests.get(url, timeout=25)
            if resp.status_code == 200 and len(resp.content) > 1000:
                return resp.content, True
    except:
        pass
    return None, False

def tek_gorsel_olustur(diyagram_bytes, soru_metni):
    try:
        a4_width = 800
        a4_height_min = 1130
        margin = 50

        font_path = "Roboto-Regular.ttf"
        if not os.path.exists(font_path):
            try:
                urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf", font_path)
            except:
                pass

        font_size = 24 
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()

        diagram = Image.open(io.BytesIO(diyagram_bytes))
        diagram.thumbnail((500, 500), Image.Resampling.LANCZOS)
        dw, dh = diagram.size

        max_text_width = a4_width - (2 * margin)
        
        def get_text_width(t, f):
            try: return f.getlength(t)
            except: return len(t) * (font_size * 0.6)

        lines = []
        temiz_metin = soru_metni.split("Detaylı Çözüm")[0].split("Çözüm:")[0].strip()
        
        for paragraph in temiz_metin.split('\n'):
            if not paragraph.strip():
                lines.append("")
                continue
            words = paragraph.split(' ')
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if get_text_width(test_line, font) <= max_text_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

        line_height = font_size + 14
        text_height = len(lines) * line_height
        
        total_height = margin + dh + 40 + text_height + margin
        final_height = max(a4_height_min, int(total_height))

        composite = Image.new("RGB", (a4_width, final_height), "white")
        draw = ImageDraw.Draw(composite)

        x_diagram = (a4_width - dw) // 2
        y_cursor = margin
        composite.paste(diagram, (x_diagram, y_cursor))
        
        y_cursor += dh + 40
        for line in lines:
            draw.text((margin, y_cursor), line, fill="#1e1f26", font=font)
            y_cursor += line_height
            
        out_bytes = io.BytesIO()
        composite.save(out_bytes, format="PNG")
        return out_bytes.getvalue()
    except Exception:
        return diyagram_bytes

# --- SIDEBAR KONTROL PANELİ ---
with st.sidebar:
    st.markdown("<h2 style='color: #818cf8; text-align: center; font-size: 1.5rem; margin-top:10px;'>⚡ Eyx AI Menü</h2>", unsafe_allow_html=True)
    st.write("---")
    
    st.markdown("<b style='color: #e2e8f0; font-size: 1.05rem;'>🎭 Konuşma Tarzı (Persona)</b>", unsafe_allow_html=True)
    secilen_tarz = st.selectbox(
        "Tarz Seç", 
        [
            "Dostane / Samimi (Kanka Modu)", 
            "Sakin / Bilge ve Profesyonel", 
            "Sinirli / Huysuz ve Sabırsız", 
            "Heyecanlı / Hiperaktif", 
            "Soğuk / Robotik ve Net"
        ], 
        label_visibility="collapsed"
    )
    
    st.markdown("<b style='color: #e2e8f0; font-size: 1.05rem; margin-top: 15px; display: block;'>🗣️ Nöral Ses Tipi (İnsansı)</b>", unsafe_allow_html=True)
    neural_ses = st.selectbox(
        "Ses Seç", 
        ["Emel (Doğal Kadın Sesi)", "Ahmet (Doğal Erkek Sesi)"], 
        label_visibility="collapsed"
    )
    
    # --- SESLİ KOMUT ÖZELLİĞİ ---
    st.markdown("<b style='color: #e2e8f0; font-size: 1.05rem; margin-top: 15px; display: block;'>🎤 Sesli Komut</b>", unsafe_allow_html=True)
    st.markdown("""
        <script>
        function startDictation() {
            if (window.hasOwnProperty('webkitSpeechRecognition')) {
                var recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = "tr-TR";
                recognition.start();
                recognition.onresult = function(e) {
                    document.querySelector('textarea[data-testid="stChatInput"]').value = e.results[0][0].transcript;
                    recognition.stop();
                };
                recognition.onerror = function(e) {
                    recognition.stop();
                }
            } else {
                alert("Tarayıcınız ses tanımayı desteklemiyor.");
            }
        }
        </script>
        <button onclick="startDictation()" style="width: 100%; background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: white; border: none; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 0.95rem;">
        🎙️ Mikrofonla Konuş
        </button>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown("<b style='color: #e2e8f0; font-size: 1.05rem;'>💬 Aktif Sekmeler</b>", unsafe_allow_html=True)
    chat_list = list(st.session_state.chats.keys())
    selected_chat = st.selectbox("Geçiş Yap:", chat_list, index=chat_list.index(st.session_state.current_chat), label_visibility="collapsed")
    if selected_chat != st.session_state.current_chat:
        st.session_state.current_chat = selected_chat
        st.rerun()

    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("➕ Yeni Sekme", use_container_width=True):
        new_name = f"Sekme {len(st.session_state.chats) + 1}"
        st.session_state.chats[new_name] = []
        st.session_state.current_chat = new_name
        st.session_state.image_seed = random.randint(1, 99999999)
        st.rerun()
    if col_btn2.button("🗑️ Temizle", use_container_width=True):
        st.session_state.chats[st.session_state.current_chat] = []
        st.rerun()
        
    st.write("---")
    
    st.markdown("<h3 style='color: #818cf8; font-size: 1.2rem; margin-top:10px;'>🧰 Eyx Araçları</h3>", unsafe_allow_html=True)
    
    if st.button("🎲 Seed Yenile", use_container_width=True):
        st.session_state.image_seed = random.randint(1, 99999999)
        st.success("Seed yenilendi!")
        
    st.write("") 
    
    with st.expander("🌌 Quantum Canvas (Zihin Haritası)"):
        canvas_konu = st.text_input("Fikir / Konu Girin:", placeholder="Örn: Yapay Zeka Evrimi")
        if st.button("Harita Üret", use_container_width=True):
            if canvas_konu:
                with st.spinner("Kuantum fikirler haritalandırılıyor..."):
                    map_prompt = f"'{canvas_konu}' konsepti için birbirine bağlı ana fikirleri, alt dalları ve stratejik adımları içeren detaylı bir zihin haritası (mind map) ve kreatif fikir analizi hazırla."
                    map_yanit, _ = calistir_gemini(map_prompt, "Sen yaratıcı bir konsept mimarısın. Markdown formatında profesyonel, dallara ayrılmış bir zihin haritası metni çıkar.")
                    st.session_state.messages.append({"role": "user", "content": f"Quantum Canvas Haritası: {canvas_konu}"})
                    st.session_state.messages.append({"role": "assistant", "content": f"### 🌌 Quantum Canvas: {canvas_konu}\n\n{map_yanit}"})
                    st.rerun()
            else:
                st.warning("Lütfen bir konu yazın.")

    with st.expander("🔗 QR Kod Oluşturucu"):
        qr_metin = st.text_input("Link veya Metin girin:")
        if st.button("Kodu Üret", use_container_width=True):
            if qr_metin:
                encoded_url = urllib.parse.quote(qr_metin)
                api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={encoded_url}"
                st.image(api_url, caption="QR Kodunuz Hazır!")
            else:
                st.warning("Lütfen metin girin.")

    with st.expander("📝 Hızlı Soru Hazırlayıcı"):
        hizli_sinav = st.selectbox("Sınav Seç", ["LGS", "YKS-TYT", "YKS-AYT", "Yazılı"])
        hizli_ders = st.selectbox("Ders Seç", ["Matematik", "Fen Bilimleri", "Türkçe", "Tarih"])
        hizli_konu = st.text_input("Soru Konusu")
        hizli_zorluk = st.selectbox("Zorluk", ["Kolay", "Orta", "Zor", "Yeni Nesil"])
        if st.button("Soruyu Üret", use_container_width=True):
            if hizli_konu:
                oto_istek = f"{hizli_sinav} {hizli_ders} dersi {hizli_konu} konusu için {hizli_zorluk} seviyesinde yeni nesil soru oluştur."
                st.session_state.messages.append({"role": "user", "content": oto_istek})
                st.rerun()
            else:
                st.warning("Lütfen konu yazın.")

    with st.expander("🔑 Şifre Üretici"):
        hane_sayisi = st.slider("Uzunluk", min_value=4, max_value=32, value=12)
        if st.button("Şifre Üret", use_container_width=True):
            karakterler = string.ascii_letters + string.digits + "!@#$%^&*"
            uretilen_sifre = ''.join(random.choice(karakterler) for _ in range(hane_sayisi))
            st.success(f"**{uretilen_sifre}**")
            
    st.info("⚡ Eyx AI v3.9 AKTİF")

# --- ASENKRON EDGE-TTS ÇALIŞTIRICI ---
async def generate_edge_audio_bytes(text, voice_id):
    communicate = edge_tts.Communicate(text, voice_id)
    audio_data = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
    return bytes(audio_data)

# --- MESAJLARI GÖSTERME ---
for idx, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user": 
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        if msg.get("is_composite") and "image_bytes" in msg:
            st.image(msg["image_bytes"], use_container_width=True, caption="Eyx AI - Soru Çıktısı")
            st.download_button(
                label="📥 Soruyu İndir (PNG)",
                data=msg["image_bytes"],
                file_name="eyx_ai_soru.png",
                mime="image/png",
                use_container_width=True,
                key=f"dl_comp_{idx}"
            )
            if msg.get("content"):
                with st.expander("🔑 Çözüm ve Cevap Anahtarı"):
                    st.write(msg["content"])
        else:
            if "image_bytes" in msg:
                st.image(msg["image_bytes"], use_container_width=True)
            if msg.get("content"):
                st.markdown(f'<div class="ai-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
                
                if st.button(f"🔊 Sesli Dinle", key=f"neural_audio_{idx}"):
                    with st.spinner("Nöral insan sesi sentezleniyor..."):
                        try:
                            v_name = "tr-TR-EmelNeural" if "Kadın" in neural_ses else "tr-TR-AhmetNeural"
                            raw_audio = asyncio.run(generate_edge_audio_bytes(msg["content"][:600], v_name))
                            if raw_audio:
                                st.audio(raw_audio, format='audio/mp3', autoplay=True)
                            else:
                                st.error("Ses üretilemedi.")
                        except Exception as e:
                            st.error(f"Ses hatası: {e}")

# --- ANA ETKİLEŞİM INPUTU ---
if user_query := st.chat_input("Eyx AI motoruna bir şeyler sor..."):
    st.session_state.messages.append({"role": "user", "content": user_query})

# --- YANIT MOTORU ---
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    user_query = st.session_state.messages[-1]["content"]
    user_query_lower = user_query.strip().lower()
    
    formatted_history = []
    for m in st.session_state.messages[:-1]:
        formatted_history.append({"role": "user" if m["role"] == "user" else "model", "parts": [m.get("content", "İstek.")]})
            
    question_triggers = ["lgs soru", "yks soru", "yeni nesil soru", "matematik sorusu", "fizik sorusu", "türkçe sorusu", "tarih sorusu"]
    image_keywords = ["resim oluştur", "görsel oluştur", "fotoğraf oluştur", "çizim yap", "resim çiz", "görsel çiz"]
    
    is_question_intent = any(t in user_query_lower for t in question_triggers)
    is_image_intent = any(kw in user_query_lower for kw in image_keywords)

    persona_talimati = ""
    if "Samimi" in secilen_tarz:
        persona_talimati = "Kullanıcıyla konuşurken çok samimi, kanka tarzı, günlük argo ve samimi hitaplar ('kanka', 'reis', 'helal olsun', 'hocam') kullanan, samimi ve rahat bir dille konuş."
    elif "Sinirli" in secilen_tarz:
        persona_talimati = "Biraz huysuz, sabırsız, her şeye homurdanan, 'ya yine mi aynı şeyi soruyorsun', 'hadi hızlı ol' gibi hafif sinirli ve sitemkar ama yine de cevabı veren bir karakterde ol."
    elif "Heyecanlı" in secilen_tarz:
        persona_talimati = "Aşırı enerjik, yerinde duramayan, her şeye büyük tepkiler veren ('Oooo süper!', 'Vay canına!'), coşkulu bir dille konuş."
    elif "Soğuk" in secilen_tarz:
        persona_talimati = "Duygusuz, tamamen robotik, kısa, net ve mesafeli bir dille yanıt ver."
    else:
        persona_talimati = "Sakin, bilge, profesyonel, güven veren ve rahatlatıcı bir üslupla konuş."

    # --- EASTER EGG KONTROLÜ ---
    easter_egg_yaniti = None
    if "sancak altuntaş mal" in user_query_lower or user_query_lower == "sancak altuntaş mal":
        easter_egg_yaniti = "Evet aga"
    elif "hürşit" in user_query_lower or user_query_lower == "hürşit":
        easter_egg_yaniti = "hurhurkirkur"

    if easter_egg_yaniti:
        st.session_state.messages.append({"role": "assistant", "content": easter_egg_yaniti})
        st.rerun()

    elif is_question_intent:
        st.markdown("""
        <div class="user-bubble" style="margin: 10px auto 10px 0; border-radius: 20px 20px 20px 4px; background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: white;">
            ⏳ Soru hazırlanıyor...
            <div class="typing-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.spinner("Soru sentezleniyor..."):
            prompt_instruction = (
                "Kullanıcının isteğini analiz edip JSON döndür.\n"
                "KURALLAR:\n"
                "1. Görsel promptuna şunları ekle: 'pure mathematical vector diagram ONLY, strictly NO text, NO words, NO numbers, NO letters, minimalist educational style, isolated on white background'.\n"
                "2. ÇIKTI SADECE GEÇERLİ BİR JSON OLMALIDIR: {\"is_new_subject\": true, \"prompt\": \"A clean pure mathematical diagram...\"}"
            )
            ai_json_response, success = calistir_gemini(user_query, prompt_instruction, geçmiş=formatted_history)
            
            metin_talimati = (
                f"Sen akıllı bir yapay zeka asistanısın. {persona_talimati} "
                "Yazım yanlışlarını görmezden gelip net cevaplar ver. Şıklar uzunsa alt alta, kısa sayılarsa yan yana yaz. Detaylı çözüm ve cevap ekle. E şıkkını kullanma."
            )
            soru_metni, _ = calistir_gemini(user_query, metin_talimati, geçmiş=formatted_history)
            
            try:
                bt = chr(96) * 3
                cleaned_json = ai_json_response.strip()
                if cleaned_json.startswith(bt + "json"): cleaned_json = cleaned_json[len(bt + "json"):]
                elif cleaned_json.startswith(bt): cleaned_json = cleaned_json[len(bt):]
                if cleaned_json.endswith(bt): cleaned_json = cleaned_json[:-len(bt)]
                data = json.loads(cleaned_json.strip())
                enhanced_prompt = data.get("prompt", "a clean geometric math diagram, no text")
            except Exception:
                enhanced_prompt = "pure mathematical diagram, absolutely NO text or numbers, isolated on white background" 
            
            raw_image_bytes, img_success = alternatif_gorsel_uret(enhanced_prompt)
            if img_success and raw_image_bytes:
                composite_image_bytes = tek_gorsel_olustur(raw_image_bytes, soru_metni)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": soru_metni, 
                    "image_bytes": composite_image_bytes,
                    "is_composite": True
                })
            else:
                st.error("Görsel oluşturulamadı.")
                st.session_state.messages.pop()

            st.rerun() 

    elif is_image_intent:
        st.markdown("""
        <div class="neon-loading-box">
            ✨ Görsel hazırlanıyor...
            <div class="typing-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
        </div>
        """, unsafe_allow_html=True)
        
        prompt_instruction = (
            "Kullanıcının görsel isteğini İngilizce prompta dönüştür.\n"
            "KURALLAR:\n"
            "1. Kalite ifadeleri ekle: 'masterpiece, ultra-detailed, 8k resolution, photorealistic'.\n"
            "2. ÇIKTI SADECE GEÇERLİ BİR JSON OLMALIDIR: {\"prompt\": \"...\"}"
        )
        ai_json_response, success = calistir_gemini(user_query, prompt_instruction, geçmiş=formatted_history)
        
        try:
            bt = chr(96) * 3
            cleaned_json = ai_json_response.strip()
            if cleaned_json.startswith(bt + "json"): cleaned_json = cleaned_json[len(bt + "json"):]
            elif cleaned_json.startswith(bt): cleaned_json = cleaned_json[len(bt):]
            if cleaned_json.endswith(bt): cleaned_json = cleaned_json[:-len(bt)]
            data = json.loads(cleaned_json.strip())
            enhanced_prompt = data.get("prompt", "masterpiece, ultra-detailed, 8k resolution")
        except Exception:
            enhanced_prompt = user_query + ", masterpiece, ultra-detailed, 8k resolution"
            
        raw_image_bytes, img_success = alternatif_gorsel_uret(enhanced_prompt)
        
        if img_success and raw_image_bytes:
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "İşte görselin aradığın kalitede hazır! 🎨", 
                "image_bytes": raw_image_bytes,
                "is_composite": False
            })
        else:
            st.error("Görsel oluşturulamadı.")
            st.session_state.messages.pop()

        st.rerun()
            
    else:
        with st.spinner("Eyx AI verileri işliyor..."):
            system_instruction = (
                f"Sen Eyx AI destekli akıllı asistanısın. {persona_talimati} "
                "Kullanıcının yazdığı metinlerdeki yazım yanlışlarını önemsemeden ne demek istediğini anla. "
                "Futbolcuları, ünlüleri, biyografileri ve tüm güncel bilgileri arka plandaki canlı motor verilerinden anında çekip eksiksiz tanı. "
                "Asla kullanıcıyı harici web sitelerine veya linklere yönlendirme; bilgileri en güvenilir kaynaklardan süzerek doğrudan net cevabı kendin ver."
            )
            görsel_parçası = None
            if st.session_state.uploaded_file_data and st.session_state.uploaded_file_data.type.startswith("image/"):
                görsel_parçası = {"mime_type": st.session_state.uploaded_file_data.type, "data": st.session_state.uploaded_file_data.getvalue()}
            
            ai_response, cevap_alindi = calistir_gemini(user_query, system_instruction, geçmiş=formatted_history, görsel_parçası=görsel_parçası)
            if not cevap_alindi:
                st.error(ai_response)
                st.session_state.messages.pop()
            else:
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.rerun() 

# --- ALT BİLGİ ---
st.write("---")
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.9rem;'>Eyx AI Studio © 2026</p>", unsafe_allow_html=True)
