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

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Eymen AI V2 - Premium",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SOHBET VE MOTOR HAFIZASI ---
if "chats" not in st.session_state:
    st.session_state.chats = {"Sohbet 1": []}
    st.session_state.current_chat = "Sohbet 1"

if "image_seed" not in st.session_state:
    st.session_state.image_seed = random.randint(1, 99999999)

if "aktif_motor" not in st.session_state:
    st.session_state.aktif_motor = "flux"

st.session_state.messages = st.session_state.chats[st.session_state.current_chat]

# --- CSS VE STYLING (IOS OPTİMİZASYONLU PREMIUM UI) ---
st.markdown("""
<style>
    [data-testid="stChatInput"] textarea, .stTextInput input, textarea { font-size: 16px !important; -webkit-text-size-adjust: 100%; }
    [data-testid="stSidebar"] { border-right: 1px solid rgba(128, 128, 128, 0.15); background-color: #0f172a !important; }
    .user-bubble { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; padding: 14px 18px; border-radius: 20px 20px 4px 20px; margin: 10px 0 10px auto; max-width: 75%; width: fit-content; box-shadow: 0 6px 15px rgba(37, 99, 235, 0.2); font-family: 'Segoe UI', system-ui, sans-serif; font-size: 1.02rem; }
    .ai-bubble { background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%); color: #f8fafc; padding: 14px 18px; border-radius: 20px 20px 20px 4px; margin: 10px auto 10px 0; max-width: 75%; width: fit-content; border: 1px solid rgba(139, 92, 246, 0.3); box-shadow: 0 4px 12px rgba(139, 92, 246, 0.15); font-family: 'Segoe UI', system-ui, sans-serif; font-size: 1.02rem; -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px); }
    .logo-container { text-align: center; margin-bottom: 2px; padding: 5px; }
    .brand-eymen { font-size: 3.5rem; font-weight: 900; color: #2563eb; text-shadow: 0 0 15px rgba(37, 99, 235, 0.3); }
    .brand-v2 { font-size: 3.5rem; font-weight: 900; color: #38bdf8; text-shadow: 0 0 15px rgba(56, 189, 248, 0.4); margin-left: 10px; }
    .subtitle { color: #64748b; text-align: center; font-size: 1.1rem; font-weight: 500; margin-bottom: 25px; }
    .typing-dots { display: inline-flex; align-items: center; margin-left: 8px; }
    .dot { width: 7px; height: 7px; background-color: white; border-radius: 50%; margin: 0 2px; animation: bounce 1.4s infinite ease-in-out both; }
    .dot:nth-child(1) { animation-delay: -0.32s; }
    .dot:nth-child(2) { animation-delay: -0.16s; }
    @keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.4; } 40% { transform: scale(1); opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ALANI ---
st.markdown('<div class="logo-container"><span class="brand-eymen">Eymen AI</span><span class="brand-v2">V2</span></div>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Premium Yapay Zeka & Akıllı Sentez Motoru</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📁 Dosya veya Fotoğraf Yükle", help="Sadece analiz içindir.")

# --- DİNAMİK GEMINI ÇAĞIRICI ---
def calistir_gemini(sorgu, sistem_talimati, geçmiş=None, görsel_parçası=None):
    son_hata = "Lütfen Streamlit ayarlarında (secrets) API key eklediğinden emin ol."
    anahtar_bulundu = False
    
    for i in range(1, 11):
        key_adı = f"KEY_{i}"
        if key_adı in st.secrets:
            anahtar_bulundu = True
            aktif_key = st.secrets[key_adı]
            try:
                genai.configure(api_key=aktif_key)
                model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=sistem_talimati)
                
                if geçmiş is not None:
                    chat = model.start_chat(history=geçmiş)
                    yanit = chat.send_message([görsel_parçası, sorgu]) if görsel_parçası else chat.send_message(sorgu)
                else:
                    yanit = model.generate_content([görsel_parçası, sorgu]) if görsel_parçası else model.generate_content(sorgu)
                
                try: return yanit.text, True
                except ValueError: return "Sistem uyarısı: Oluşturulan içerik boş döndü.", False
            except Exception as e:
                err_str = str(e)
                son_hata = err_str
                if any(k in err_str for k in ["429", "Quota", "400", "expired", "API_KEY_INVALID"]): 
                    continue 
                else: 
                    return f"Hata: {err_str}", False
                    
    if not anahtar_bulundu:
        return son_hata, False
        
    return f"Bağlantı başarısız. Google'dan gelen son hata mesajı: {son_hata}", False

# --- DİNAMİK GÖRSEL SENTEZ MOTORU (A4 VE TÜRKÇE FONT DESTEĞİ) ---
def tek_gorsel_olustur(diyagram_bytes, soru_metni):
    try:
        # A4 Oranlarında Şablon
        a4_width = 800
        a4_height_min = 1130
        margin = 50

        # Türkçe Karakter Garantisi: İnternetten Font İndir
        font_path = "Roboto-Regular.ttf"
        if not os.path.exists(font_path):
            try:
                urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf", font_path)
            except:
                pass

        font_size = 24 # Okunabilir büyük punto
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            # Yedek fontlar
            font_paths = ["Arial.ttf", "arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
            font = ImageFont.load_default()
            for path in font_paths:
                try:
                    font = ImageFont.truetype(path, font_size)
                    break
                except: continue

        # Görseli optimize et ve boyutlandır
        diagram = Image.open(io.BytesIO(diyagram_bytes))
        # Diyagramı orantılı şekilde küçült ki A4 kağıdında devasa durmasın (max 500x500)
        diagram.thumbnail((500, 500), Image.Resampling.LANCZOS)
        dw, dh = diagram.size

        # Metni hazırlama ve A4 sayfasına göre hizalama
        max_text_width = a4_width - (2 * margin)
        
        def get_text_width(t, f):
            try: return f.getlength(t)
            except:
                try: return f.getbbox(t)[2]
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
        
        # Sayfa yüksekliğini ayarla (Diyagram + Metin sığıyorsa A4, sığmıyorsa uzat)
        total_height = margin + dh + 40 + text_height + margin
        final_height = max(a4_height_min, int(total_height))

        # Beyaz zemin oluştur
        composite = Image.new("RGB", (a4_width, final_height), "white")
        draw = ImageDraw.Draw(composite)

        # Görseli en üste, ortaya hizala
        x_diagram = (a4_width - dw) // 2
        y_cursor = margin
        composite.paste(diagram, (x_diagram, y_cursor))
        
        # Metni görselin altına yaz (Koyu renkli daha şık mürekkep rengi)
        y_cursor += dh + 40
        for line in lines:
            draw.text((margin, y_cursor), line, fill="#0f172a", font=font)
            y_cursor += line_height
            
        out_bytes = io.BytesIO()
        composite.save(out_bytes, format="PNG")
        return out_bytes.getvalue()
    except Exception as e:
        st.error(f"Sentez motoru hatası: {e}")
        return diyagram_bytes

# --- SIDEBAR KONTROL PANELİ ---
with st.sidebar:
    st.markdown("<h2 style='color: #38bdf8; text-align: center; font-size: 1.5rem; margin-top:10px;'>🛠️ MENÜ</h2>", unsafe_allow_html=True)
    st.write("---")
    
    st.markdown("<b style='color: #f8fafc; font-size: 1.05rem;'>💬 Aktif Oturumlar</b>", unsafe_allow_html=True)
    chat_list = list(st.session_state.chats.keys())
    selected_chat = st.selectbox("Geçiş Yap:", chat_list, index=chat_list.index(st.session_state.current_chat), label_visibility="collapsed")
    if selected_chat != st.session_state.current_chat:
        st.session_state.current_chat = selected_chat
        st.rerun()

    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("➕ Yeni Soru", use_container_width=True):
        new_name = f"Sohbet {len(st.session_state.chats) + 1}"
        st.session_state.chats[new_name] = []
        st.session_state.current_chat = new_name
        st.session_state.image_seed = random.randint(1, 99999999)
        st.rerun()
    if col_btn2.button("🗑️ Temizle", use_container_width=True):
        st.session_state.chats[st.session_state.current_chat] = []
        st.rerun()
        
    st.write("---")
    
    # --- AKILLI ARAÇ KUTUSU ---
    st.markdown("<h3 style='color: #38bdf8; font-size: 1.2rem; margin-top:10px;'>🧰 Akıllı Araç Kutusu</h3>", unsafe_allow_html=True)
    
    motor_secimi = st.selectbox(
        "🎨 Görsel Çizim Motoru",
        options=["flux", "turbo", "midjourney", "dall-e"],
        index=["flux", "turbo", "midjourney", "dall-e"].index(st.session_state.aktif_motor)
    )
    if motor_secimi != st.session_state.aktif_motor:
        st.session_state.aktif_motor = motor_secimi
        st.rerun()
        
    if st.button("🎲 Seed Yenile (Yeni Tarz)", use_container_width=True):
        st.session_state.image_seed = random.randint(1, 99999999)
        st.success("Seed yenilendi! Yeni görseller farklı olacak.")
        
    st.write("") 
    
    with st.expander("🔗 QR Kod Oluşturucu"):
        qr_metin = st.text_input("Link veya Metin girin:")
        if st.button("Kodu Üret", use_container_width=True):
            if qr_metin:
                encoded_url = urllib.parse.quote(qr_metin)
                api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={encoded_url}"
                st.image(api_url, caption="QR Kodunuz Hazır!")
            else:
                st.warning("Lütfen bir metin girin.")

    with st.expander("📝 Hızlı Soru Hazırlayıcı"):
        hizli_sinav = st.selectbox("Sınav Seç", ["LGS", "YKS-TYT", "YKS-AYT", "Yazılı Sınav"])
        hizli_ders = st.selectbox("Ders Seç", ["Matematik", "Fen Bilimleri", "Türkçe", "Tarih/İnkılap"])
        hizli_konu = st.text_input("Soru Konusu (Örn: Kareköklü Sayılar)")
        hizli_zorluk = st.selectbox("Zorluk Seviyesi", ["Kolay", "Orta", "Zor", "Ultra Zor (Yeni Nesil)"])
        if st.button("Soruyu Üret", use_container_width=True):
            if hizli_konu:
                oto_istek = f"{hizli_sinav} sınavı {hizli_ders} dersi {hizli_konu} konusu için {hizli_zorluk} seviyesinde görsel diyagram içeren yeni nesil mükemmel bir soru oluştur."
                st.session_state.messages.append({"role": "user", "content": oto_istek})
                st.rerun()
            else:
                st.warning("Lütfen bir konu yazın.")

    with st.expander("🔑 Şifre Oluşturucu"):
        hane_sayisi = st.slider("Şifre Uzunluğu (Hane)", min_value=4, max_value=32, value=12)
        if st.button("Güvenli Şifre Üret", use_container_width=True):
            karakterler = string.ascii_letters + string.digits + "!@#$%^&*"
            uretilen_sifre = ''.join(random.choice(karakterler) for _ in range(hane_sayisi))
            st.success(f"**{uretilen_sifre}**")
            
    st.write("---")
    st.info("🚀 COMPOSITE SYNTHESIS MOTOR ACTIVE")

# --- MESAJLARI GÖSTERME (TEK GÖRSEL ENTEGRASYONU) ---
for msg in st.session_state.messages:
    if msg["role"] == "user": 
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        if msg.get("is_composite") and "image_bytes" in msg:
            st.image(msg["image_bytes"], use_container_width=True, caption="Eymen AI V2 - Soru Bankası Çıktısı")
            st.download_button(
                label="📥 Soruyu Tek Görsel Olarak İndir (PNG)",
                data=msg["image_bytes"],
                file_name="eymen_ai_v2_soru.png",
                mime="image/png",
                use_container_width=True
            )
            if msg.get("content"):
                with st.expander("🔑 Detaylı Çözüm ve Cevap Anahtarı (Panele Özel)"):
                    st.write(msg["content"])
        else:
            if "image_bytes" in msg:
                st.image(msg["image_bytes"], use_container_width=True)
            if msg.get("content"):
                st.markdown(f'<div class="ai-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

# --- ANA ETKİLEŞİM INPUTU ---
if user_query := st.chat_input("Eymen AI'a birşeyler sor..."):
    st.session_state.messages.append({"role": "user", "content": user_query})

# --- YANIT MOTORU ---
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    user_query = st.session_state.messages[-1]["content"]
    
    formatted_history = []
    for m in st.session_state.messages[:-1]:
        formatted_history.append({"role": "user" if m["role"] == "user" else "model", "parts": [m.get("content", "Görsel isteği.")]})
            
    image_triggers = ["görsel", "resim", "oluştur", "çiz", "hayal et", "fotoğraf", "yap", "diyagram"]
    is_image_intent = any(trigger in user_query.lower() for trigger in image_triggers)

    if is_image_intent:
        st.markdown("""
        <div class="user-bubble" style="margin: 10px auto 10px 0; border-radius: 20px 20px 20px 4px; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; box-shadow: 0 6px 15px rgba(37, 99, 235, 0.2);">
            ⏳ V2 Medya Motoru Analiz Ediyor...
            <div class="typing-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.spinner("⏳ V2 Dijital Sentez Motoru Çalışıyor... Görsel ve Metin LGS Formatında Birleştiriliyor..."):
            
            prompt_instruction = (
                "Sen uzman bir AI Prompt mühendisisin. Görevin kullanıcının isteğini analiz edip JSON döndürmek.\n"
                "KURALLAR:\n"
                "1. Görsel motorunun içine metin veya şık yazmasını KESİNLİKLE YASAKLA. Prompt'a mutlaka şu ifadeleri ekle: 'pure mathematical vector diagram ONLY, strictly NO text, NO words, NO numbers, NO letters, minimalist educational style, isolated on white background'.\n"
                "2. ÇIKTI SADECE VE SADECE GEÇERLİ BİR JSON OLMALIDIR. ÖRNEK: {\"is_new_subject\": true, \"prompt\": \"A clean pure mathematical diagram of a prism...\"}"
            )
            ai_json_response, success = calistir_gemini(user_query, prompt_instruction, geçmiş=formatted_history)
            
            metin_talimati = (
                "Sen uzman bir soru yazarı ve LGS öğretmenisin. Kullanıcının istediği konuya göre KESİNLİKLE HATASIZ (%100 doğru çözümlü), mükemmel Türkçe metne sahip bir soru metni ve detaylı çözümünü oluştur.\n\n"
                "ŞIK DÜZENİ KURALLARI:\n"
                "- Eğer şıklar yorum içeriyorsa veya uzun cümlelerse, şıkları MUTLAKA alt alta ve aralarında birer boş satır olacak şekilde yaz.\n"
                "- Eğer şıklar matematikteki gibi sadece KISA SAYILAR veya harflerden oluşuyorsa, hepsini aynı satıra (yan yana), aralarında belirgin geniş boşluklar bırakarak yaz.\n\n"
                "Çıktı Formatı:\n"
                "1. Soru Hikayesi/Metni\n"
                "2. Şıklar (yukarıdaki akıllı düzene göre)\n"
                "3. Detaylı Çözüm ve Cevap. E şıkkını asla kullanma."
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
            
            st.session_state.image_seed = random.randint(1, 99999999)
            encoded_prompt = urllib.parse.quote(enhanced_prompt)
            final_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={st.session_state.image_seed}&nofeed=true&model={st.session_state.aktif_motor}"
            
            try:
                media_response = requests.get(final_image_url, timeout=40)
                if media_response.status_code == 200:
                    raw_image_bytes = media_response.content
                    
                    composite_image_bytes = tek_gorsel_olustur(raw_image_bytes, soru_metni)
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": soru_metni, 
                        "image_bytes": composite_image_bytes,
                        "is_composite": True
                    })
                else:
                    st.error("Görsel motoru yanıt vermedi.")
                    st.session_state.messages.pop()
            except Exception as e:
                st.error(f"Bağlantı zaman aşımı: {e}")
                st.session_state.messages.pop()

            st.rerun() 
            
    else:
        with st.spinner("Eymen AI V2 düşünüyor..."):
            system_instruction = (
                "Sen Eymen AI V2 adında, her dersten tüm problemleri jet hızında çözen uzman bir asistansın. Eymen tarafından geliştirildin."
            )
            görsel_parçası = None
            if uploaded_file and uploaded_file.type.startswith("image/"):
                görsel_parçası = {"mime_type": uploaded_file.type, "data": uploaded_file.read()}
                uploaded_file.seek(0)
            
            ai_response, cevap_alindi = calistir_gemini(user_query, system_instruction, geçmiş=formatted_history, görsel_parçası=görsel_parçası)
            if not cevap_alindi:
                st.error(ai_response)
                st.session_state.messages.pop()
            else:
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.rerun() 

# --- ALT BİLGİ ---
st.write("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9rem; font-weight: 500;'>Eymen AI V2 © 2026 | </p>", unsafe_allow_html=True)
