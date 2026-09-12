import streamlit as st
import json
import urllib.parse
import urllib.request
import os
import random
import string
import requests
import time
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import pytz
import asyncio
import edge_tts

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Eyx AI Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- KALICI HAFIZA & STATE YÖNETİMİ ---
if "chats" not in st.session_state:
    st.session_state.chats = {
        "Genel Sohbet": [],
        "Kodlama Asistanı": [],
        "Yaratıcı Yazar": [],
        "Kişisel Zeka": []
    }

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Genel Sohbet"

if "chat_personalities" not in st.session_state:
    st.session_state.chat_personalities = {
        "Genel Sohbet": "Sen yardımsever ve net bir yapay zeka asistanısın.",
        "Kodlama Asistanı": "Sen kıdemli bir yazılım mühendisisin. Sadece temiz, optimize kodlar yazarsın ve teknik çözümler sunarsın.",
        "Yaratıcı Yazar": "Sen yaratıcı bir edebiyatçısın. Şiirli, akıcı, hikayeleştirici ve etkileyici bir dille konuşursun.",
        "Kişisel Zeka": "Sen kullanıcının özel olarak yapılandırdığı kişisel yapay zekasısın."
    }

if "bg_settings" not in st.session_state:
    st.session_state.bg_settings = {
        "chat_bg": "#14151a",
        "bubble_ai": "linear-gradient(135deg, rgba(30, 31, 38, 0.9) 0%, rgba(20, 21, 26, 0.9) 100%)",
        "text_color": "#e2e8f0"
    }

if "image_seed" not in st.session_state:
    st.session_state.image_seed = random.randint(1, 99999999)

if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None

GUNUN_SOZLERI = [
    "🚀 Kodunu yaz, sınırları zorla, geleceği şekillendir.",
    "💡 En iyi hata, henüz yapmadığın ve öğreneceğin hatadır.",
    "⚡ Küçük adımlar büyük sistemleri inşa eder.",
    "🔥 Vazgeçmediğin sürece yenilmiş sayılmazsın.",
    "🎯 Bugün yazdığın her satır, yarınki gücündür."
]

if "gunun_sozu" not in st.session_state:
    st.session_state.gunun_sozu = random.choice(GUNUN_SOZLERI)

st.session_state.messages = st.session_state.chats[st.session_state.current_chat]

# --- DİNAMİK CSS VE ÖZELLEŞTİRİLEBİLİR STİLLER ---
current_bg = st.session_state.bg_settings["chat_bg"]
current_bubble_ai = st.session_state.bg_settings["bubble_ai"]
current_text_color = st.session_state.bg_settings["text_color"]

st.markdown(f"""
<style>
    [data-testid="stChatInput"] textarea, .stTextInput input, textarea {{ font-size: 16px !important; -webkit-text-size-adjust: 100%; }}
    [data-testid="stSidebar"] {{ border-right: 1px solid rgba(128, 128, 128, 0.15); background-color: #121316 !important; }}
    
    .stApp {{
        background-color: {current_bg} !important;
    }}

    .user-bubble {{ background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: white; padding: 14px 18px; border-radius: 20px 20px 4px 20px; margin: 10px 0 10px auto; max-width: 75%; width: fit-content; box-shadow: 0 4px 10px rgba(99, 102, 241, 0.15); font-family: 'Segoe UI', system-ui, sans-serif; font-size: 1.02rem; }}
    .ai-bubble {{ background: {current_bubble_ai}; color: {current_text_color}; padding: 14px 18px; border-radius: 20px 20px 20px 4px; margin: 10px auto 10px 0; max-width: 75%; width: fit-content; border: 1px solid rgba(129, 140, 248, 0.3); box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); font-family: 'Segoe UI', system-ui, sans-serif; font-size: 1.02rem; }}
    
    .neon-loading-box {{
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
    }}

    .welcome-banner {{
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(30, 31, 38, 0.8) 100%);
        border: 1px solid rgba(129, 140, 248, 0.4);
        padding: 12px 20px;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.1);
    }}
    .welcome-text {{
        color: #c7d2fe;
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 0.95rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }}

    .logo-container {{ text-align: center; margin-bottom: 2px; padding: 5px; }}
    .brand-eyx {{ font-size: 3.5rem; font-weight: 900; color: #6366f1; }}
    .brand-ai {{ font-size: 3.5rem; font-weight: 900; color: #a5b4fc; margin-left: 10px; }}
    .subtitle {{ color: #94a3b8; text-align: center; font-size: 1.1rem; font-weight: 500; margin-bottom: 15px; }}
    .typing-dots {{ display: inline-flex; align-items: center; margin-left: 8px; }}
    .dot {{ width: 6px; height: 6px; background-color: #818cf8; border-radius: 50%; margin: 0 2px; animation: bounce 1.4s infinite ease-in-out both; }}
    .dot:nth-child(1) {{ animation-delay: -0.32s; }}
    .dot:nth-child(2) {{ animation-delay: -0.16s; }}
    @keyframes bounce {{ 0%, 80%, 100% {{ transform: scale(0); opacity: 0.4; }} 40% {{ transform: scale(1); opacity: 1; }} }}

    .file-preview-card {{
        position: relative;
        background: rgba(20, 21, 26, 0.7);
        border: 1px solid rgba(129, 140, 248, 0.3);
        padding: 10px 15px;
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 15px;
    }}
    .file-preview-text {{ color: #e2e8f0; font-size: 0.95rem; font-family: 'Segoe UI', system-ui, sans-serif; }}
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK VE KARŞILAMA ---
st.markdown('<div class="logo-container"><span class="brand-eyx">Eyx</span><span class="brand-ai">AI</span></div>', unsafe_allow_html=True)
st.markdown(f'<p class="subtitle">Aktif Sekme: <b>{st.session_state.current_chat}</b></p>', unsafe_allow_html=True)

st.markdown(f"""
<div class="welcome-banner">
    <div class="welcome-text">✨ <b>Günün Motivasyonu:</b> {st.session_state.gunun_sozu}</div>
</div>
""", unsafe_allow_html=True)

# --- DOSYA YÜKLEME ---
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

# --- WEB ARAMA VE ZAMAN MOTORU ---
def chrome_motoru_ile_ara(sorgu):
    try:
        sorgu_terimi = sorgu
        sorgu_lower = sorgu.lower()
        sport_keywords = [
            "maç", "skor", "futbol", "puan durumu", "fikstür", "basketbol", 
            "canlı skor", "iddaa", "şampiyonlar ligi", "lig", "süper lig", 
            "gol", "oynadı", "kaç kaç", "bitti", "kazandı", "maçı", "derbi",
            "real madrid", "barcelona", "galatasaray", "fenerbahçe", "beşiktaş", "trabzonspor"
        ]
        if any(k in sorgu_lower for k in sport_keywords):
            sorgu_terimi = f"{sorgu} maç sonucu puan durumu mackolik flashscore"
            
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
            
            clean_snippets = [re.sub(r'<.*?>', '', s) for s in snippets[:10]]
            if clean_snippets:
                return " | ".join([s for s in clean_snippets if len(s) > 5])
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

# --- API ROTASYON MOTORU ---
def calistir_gemini(sorgu, sistem_talimati, geçmiş=None, görsel_parçası=None):
    son_hata = "Sistemde geçerli API anahtarı bulunamadı."
    an_zaman = get_current_turkey_time()
    
    kaynak_verisi = chrome_motoru_ile_ara(sorgu)
    web_bilgisi = f"\n[Canlı Veri Tabanı ve Web Sonucu]: {kaynak_verisi}" if kaynak_verisi else ""

    tam_sistem_talimati = (
        f"🚨 KESİN KURALLAR 🚨:\n"
        f"1. Bulunduğun Anın Kesin Türkiye Saati (UTC+3): {an_zaman}.\n"
        f"2. Kullanıcı sana ne soruyorsa SADECE o konuya odaklan. Tek kelimelik veya kısa mesajlara sadece o kelimenin anlamıyla cevap ver.\n"
        f"3. Bilgileri en güncel haliyle süzerek **net, direkt ve kesin yanıtı doğrudan sen ver**. Asla dış kaynaklara yönlendirme yapma.\n\n"
        f"{web_bilgisi}\n{sistem_talimati}"
    )

    contents = []
    if geçmiş:
        for item in geçmiş:
            role = "user" if item.get("role") == "user" else "model"
            parts = item.get("parts", [])
            text_part = parts[0] if len(parts) > 0 else ""
            contents.append({"role": role, "parts": [{"text": str(text_part)}]})
    
    current_parts = []
    if görsel_parçası:
        current_parts.append({
            "inline_data": {
                "mime_type": görsel_parçası["mime_type"],
                "data": urllib.parse.quote(görsel_parçası["data"])
            }
        })
    current_parts.append({"text": sorgu})
    contents.append({"role": "user", "parts": current_parts})

    payload = {
        "contents": contents,
        "systemInstruction": {
            "parts": [{"text": tam_sistem_talimati}]
        }
    }

    modeller = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]

    for model_adi in modeller:
        for i in range(1, 21):
            key_adi = f"KEY_{i}"
            if key_adi in st.secrets:
                aktif_key = st.secrets[key_adi].strip()
                if not aktif_key:
                    continue
                
                endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_adi}:generateContent?key={aktif_key}"
                
                try:
                    response = requests.post(endpoint, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
                    
                    if response.status_code == 200:
                        res_data = response.json()
                        candidates = res_data.get("candidates", [])
                        if candidates and len(candidates) > 0:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts and len(parts) > 0:
                                return parts[0].get("text", ""), True
                    elif response.status_code == 429:
                        time.sleep(1.5)
                        continue
                    else:
                        son_hata = f"KEY_{i} (Status {response.status_code}): {response.text}"
                except Exception as e:
                    continue

    return "Tüm API anahtarlarının dakikalık istek kotası doldu. Lütfen 30 saniye bekleyip tekrar deneyin.", False

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

# --- SIDEBAR & KİŞİSELLEŞTİRME MENÜSÜ ---
with st.sidebar:
    st.markdown("<h2 style='color: #818cf8; text-align: center; font-size: 1.5rem; margin-top:10px;'>⚡ Eyx AI Menü</h2>", unsafe_allow_html=True)
    st.write("---")
    
    st.markdown("<b style='color: #e2e8f0; font-size: 1.05rem;'>💬 Sohbet Sekmeleri</b>", unsafe_allow_html=True)
    chat_list = list(st.session_state.chats.keys())
    selected_chat = st.selectbox("Sekme Seç:", chat_list, index=chat_list.index(st.session_state.current_chat), label_visibility="collapsed")
    
    if selected_chat != st.session_state.current_chat:
        st.session_state.current_chat = selected_chat
        st.rerun()

    col_b1, col_b2 = st.columns(2)
    if col_b1.button("🗑️ Temizle", use_container_width=True):
        st.session_state.chats[st.session_state.current_chat] = []
        st.rerun()
        
    yeni_sekme_adi = st.text_input("Yeni Sekme Adı", placeholder="Örn: Proje Analizi", label_visibility="collapsed")
    if st.button("➕ Sekme Ekle", use_container_width=True):
        if yeni_sekme_adi and yeni_sekme_adi not in st.session_state.chats:
            st.session_state.chats[yeni_sekme_adi] = []
            st.session_state.chat_personalities[yeni_sekme_adi] = "Sen uzman bir yapay zeka asistanısın."
            st.session_state.current_chat = yeni_sekme_adi
            st.rerun()

    st.write("---")
    st.markdown("<b style='color: #e2e8f0; font-size: 1.05rem;'>🧠 Kişisel Zeka Ayarı</b>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 0.85rem;'>Aşağıya yazarak 'Kişisel Zeka' sekmesindeki AI karakterini dilediğin gibi şekillendir.</p>", unsafe_allow_html=True)
    
    mevcut_kisisel_prompt = st.session_state.chat_personalities.get("Kişisel Zeka", "")
    yeni_kisisel_prompt = st.text_area("Kişisel Zeka Talimatı:", value=mevcut_kisisel_prompt, height=90)
    if st.button("Kaydet & Güncelle", use_container_width=True):
        st.session_state.chat_personalities["Kişisel Zeka"] = yeni_kisisel_prompt
        st.success("Kişisel zeka karakteri güncellendi!")

    st.write("---")
    st.markdown("<b style='color: #e2e8f0; font-size: 1.05rem;'>🎨 Arka Plan ve Tema</b>", unsafe_allow_html=True)
    tema_secimi = st.selectbox("Renk Teması Seç:", ["Koyu Gece (Varsayılan)", "Derin Uzay", "Cyberpunk Neon", "Minimal Beyaz"], label_visibility="collapsed")
    
    if tema_secimi == "Koyu Gece (Varsayılan)":
        st.session_state.bg_settings = {"chat_bg": "#14151a", "bubble_ai": "linear-gradient(135deg, rgba(30, 31, 38, 0.9) 0%, rgba(20, 21, 26, 0.9) 100%)", "text_color": "#e2e8f0"}
    elif tema_secimi == "Derin Uzay":
        st.session_state.bg_settings = {"chat_bg": "#090d16", "bubble_ai": "linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%)", "text_color": "#f8fafc"}
    elif tema_secimi == "Cyberpunk Neon":
        st.session_state.bg_settings = {"chat_bg": "#12081c", "bubble_ai": "linear-gradient(135deg, rgba(45, 10, 60, 0.9) 0%, rgba(20, 5, 30, 0.9) 100%)", "text_color": "#ffc8ff"}
    elif tema_secimi == "Minimal Beyaz":
        st.session_state.bg_settings = {"chat_bg": "#f8fafc", "bubble_ai": "linear-gradient(135deg, rgba(241, 245, 249, 0.95) 0%, rgba(226, 232, 240, 0.95) 100%)", "text_color": "#0f172a"}

    st.write("---")
    st.markdown("<h3 style='color: #818cf8; font-size: 1.2rem; margin-top:10px;'>🧰 Eyx Araçları</h3>", unsafe_allow_html=True)
    
    if st.button("🎲 Seed Yenile", use_container_width=True):
        st.session_state.image_seed = random.randint(1, 99999999)
        st.success("Seed yenilendi!")

    with st.expander("🔗 QR Kod Oluşturucu"):
        qr_metin = st.text_input("Link veya Metin girin:")
        if st.button("Kodu Üret", use_container_width=True):
            if qr_metin:
                encoded_url = urllib.parse.quote(qr_metin)
                api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={encoded_url}"
                st.image(api_url, caption="QR Kodunuz Hazır!")

    with st.expander("🔑 Şifre Üretici"):
        hane_sayisi = st.slider("Uzunluk", min_value=4, max_value=32, value=12)
        if st.button("Şifre Üret", use_container_width=True):
            karakterler = string.ascii_letters + string.digits + "!@#$%^&*"
            uretilen_sifre = ''.join(random.choice(karakterler) for _ in range(hane_sayisi))
            st.success(f"**{uretilen_sifre}**")

# --- ASENKRON SES ÇALIŞTIRICI ---
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
                            raw_audio = asyncio.run(generate_edge_audio_bytes(msg["content"][:600], "tr-TR-EmelNeural"))
                            if raw_audio:
                                st.audio(raw_audio, format='audio/mp3', autoplay=True)
                        except Exception as e:
                            st.error(f"Ses hatası: {e}")

# --- ANA GİRDİ ---
if user_query := st.chat_input("Eyx AI'a bir şeyler sor..."):
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

    # Aktif sekmeye özel karakter talimatı
    aktif_persona = st.session_state.chat_personalities.get(st.session_state.current_chat, "Sen akıllı ve yardımsever bir asistansın.")

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
            ⏳ Eyx AI düşünüyor...
            <div class="typing-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.spinner("Eyx AI düşünüyor..."):
            prompt_instruction = (
                "Kullanıcının isteğini analiz edip JSON döndür.\n"
                "KURALLAR:\n"
                "1. Görsel promptuna şunları ekle: 'pure mathematical vector diagram ONLY, strictly NO text, NO words, NO numbers, NO letters, minimalist educational style, isolated on white background'.\n"
                "2. ÇIKTI SADECE GEÇERLİ BİR JSON OLMALIDIR: {\"is_new_subject\": true, \"prompt\": \"A clean pure mathematical diagram...\"}"
            )
            ai_json_response, success = calistir_gemini(user_query, prompt_instruction, geçmiş=formatted_history)
            
            metin_talimati = (
                f"{aktif_persona} "
                "Yazım yanlışlarını görmezden gelip net cevaplar ver. Detaylı çözüm ve cevap ekle."
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
            ✨ Eyx AI düşünüyor...
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
        # "Eyx AI düşünüyor..." ekran efekti
        st.markdown("""
        <div class="neon-loading-box">
            🧠 Eyx AI düşünüyor...
            <div class="typing-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
        </div>
        """, unsafe_allow_html=True)
        
        system_instruction = (
            f"{aktif_persona} "
            "Kullanıcının yazdığı metinlerdeki yazım yanlışlarını önemsemeden ne demek istediğini anla. "
            "SADECE kullanıcı futbol veya sporla ilgili bir soru sorarsa arka plandaki canlı motor verilerini devreye sok. "
            "Asla kullanıcıyı harici web sitelerine yönlendirme; doğrudan net cevabı kendin ver."
        )
        görsel_parçası = None
        if st.session_state.uploaded_file_data and st.session_state.uploaded_file_data.type.startswith("image/"):
            import base64
            encoded_img = base64.b64encode(st.session_state.uploaded_file_data.getvalue()).decode("utf-8")
            görsel_parçası = {"mime_type": st.session_state.uploaded_file_data.type, "data": encoded_img}
        
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
