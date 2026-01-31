import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import re

# --- 1. AYARLAR VE ANAHTARLAR ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    SHEET_URL = st.secrets["GSHEET_URL"]
    
    # SOHBET FORMU (Eski Form)
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfAANTySmXphVhxNLT76RN-2n7MVjnX7WyNLJrH73qRZxPcrg/formResponse"
    ENTRY_CHAT_USER = "entry.1594572083"
    ENTRY_CHAT_MSG = "entry.1966407140"
    ENTRY_CHAT_ROLE = "entry.1321459799"

    # KAYIT FORMU (Yeni Form)
    REGISTER_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdvXHwAP5Z8g1ganu6R0G1goJmsJSN8_XXCtGKpLeKdsUwenw/formResponse"
    ENTRY_REG_USER = "entry.1673314803"
    ENTRY_REG_PASS = "entry.133228326"

    # GID NUMARALARI
    SOHBET_GID = "0"
    UYELER_GID = "1016867892"

    BASE_URL = SHEET_URL.split('/edit')[0]
    SOHBET_CSV = f"{BASE_URL}/export?format=csv&gid={SOHBET_GID}"
    UYELER_CSV = f"{BASE_URL}/export?format=csv&gid={UYELER_GID}"

except Exception as e:
    st.error(f"Ayarlarda hata var cano: {e}")
    st.stop()

genai.configure(api_key=API_KEY)
st.set_page_config(page_title="YozgatAI", page_icon="🌾")

# --- 2. FONKSİYONLAR ---
def verileri_oku(url):
    try:
        return pd.read_csv(url, on_bad_lines='skip')
    except:
        return pd.DataFrame()

def kullanici_kontrol(isim):
    if len(isim) < 4: return False, "İsim en az 4 harf olsun."
    if not re.match("^[a-zA-Z0-9]+$", isim): return False, "Sadece İngilizce harf ve sayı kullan."
    return True, ""

def sifre_kontrol(sifre):
    if len(sifre) < 6: return False, "Şifre en az 6 hane olsun."
    if not re.search("[0-9]", sifre): return False, "Şifreye en az bir rakam koy."
    return True, ""

# --- 3. GİRİŞ VE KAYIT EKRANI ---
if "oturum" not in st.session_state:
    st.title("🛡️ YozgatAI: Giriş Kapısı")
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])

    with tab1:
        g_ad = st.text