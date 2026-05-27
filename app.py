import streamlit as st
import json
import os
import urllib.parse
import random
import string
import math
import google.generativeai as genai

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Eymen AI V2 - Premium", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

if "chats" not in st.session_state:
    st.session_state.chats = {"Sohbet 1": []}
    st.session_state.current_chat = "Sohbet 1"
st.session_state.messages = st.session_state.chats[st.session_state.current_chat]

# --- CSS ---
st.markdown("""
<style>
    .typing-dots { display: inline-block; margin-left: 5px; }
    .dot { display: inline-block; width: 6px; height: 6px; background-color: #2563eb; border-radius: 50%; animation: pulse 1.4s infinite ease-in-out both; margin: 0 1px; }
    .dot:nth-child(1) { animation-delay: -0.32s; } .dot:nth-child(2) { animation-delay: -0.16s; }
    @keyframes pulse { 0%, 80%, 100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1.0); opacity: 1; } }
    [data-testid="stChatInput"] textarea, .stTextInput input, textarea { font-size: 16px !important; }
    .user-bubble { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; padding: 16px 20px; border-radius: 20px 20px 4px 20px; margin: 10px 0 10px auto; max-width: 75%; width: fit-content; box-shadow: 0 8px 20px rgba(37, 99, 235, 0.25); }
    .ai-bubble { background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%); color: #f8fafc; padding: 16px 20px; border-radius: 20px 20px 20px 4px; margin: 10px auto 10px 0; max-width: 75%; width: fit-content; border: 1px solid rgba(139, 92, 246, 0.4); box-shadow: 0 0 15px rgba(139, 92, 246, 0.35); }
    .brand-eymen { font-size: 3.8rem; font-weight: 900; color: #2563eb; }
    .brand-v2 { font-size: 3.8rem; font-weight: 900; color: #38bdf8; margin-left: 15px; }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
st.markdown('<div style="text-align:center;"><span class="brand-eymen">Eymen AI</span><span class="brand-v2">V2</span></div>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: #38bdf8; text-align: center; font-size: 1.6rem;'>Menü</h2>", unsafe_allow_html=True)
    selected_chat = st.selectbox("Sohbet:", list(st.session_state.chats.keys()), index=list(st.session_state.chats.keys()).index(st.session_state.current_chat))
    if selected_chat != st.session_state.current_chat:
        st.session_state.current_chat = selected_chat
        st.rerun()
    
    st.markdown("<h2 style='color: #38bdf8; text-align: center; font-size: 1.6rem;'>Akıllı Araç Kutusu</h2>", unsafe_allow_html=True)
    with st.expander("📱 QR Oluşturucu"):
        qr_link = st.text_input("Link:")
        if qr_link: st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote(qr_link)}")

# --- MESAJ GÖSTERİM ---
def render_message(msg):
    if msg["role"] == "user": st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        if "image" in msg: st.markdown(f'<div class="ai-bubble">{msg["content"]}<br><img src="{msg["image"]}" style="width:100%; border-radius:12px; margin-top:10px;"></div>', unsafe_allow_html=True)
        else: st.markdown(f'<div class="ai-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

for msg in st.session_state.messages: render_message(msg)

# --- İŞLEMCİ ---
if user_query := st.chat_input("Mesaj..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Görsel Tetikleyici
    image_triggers = ["görsel oluştur", "resmi oluştur", "oluştur", "çiz", "hayal et", "resim oluştur", "fotoğraf oluştur"]
    if any(trigger in user_query.lower() for trigger in image_triggers):
        with st.spinner(""):
            st.markdown('<div style="display: flex; align-items: center; font-weight: bold; color: #64748b;">V2 Medya Motoru Görseli Hazırlıyor... <div class="typing-dots"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div></div>', unsafe_allow_html=True)
            img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(user_query)}?width=1024&height=1024&nologo=true"
            st.session_state.messages.append({"role": "assistant", "content": "✨ Görselin hazır!", "image": img_url})
    else:
        # Metin Cevaplama (Gemini entegrasyonu buraya)
        st.session_state.messages.append({"role": "assistant", "content": "Anlaşıldı."})
    st.rerun()
