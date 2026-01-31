import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import re

# --- 1. AYARLAR ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    SHEET_URL = st.secrets["GSHEET_URL"]
    
    # LİNKLER
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfAANTySmXphVhxNLT76RN-2n7MVjnX7WyNLJrH73qRZxPcrg/formResponse"
    ENTRY_CHAT_USER = "entry.1594572083"
    ENTRY_CHAT_MSG = "entry.1966407140"
    ENTRY_CHAT_ROLE = "entry.1321459799"

    REGISTER_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdvXHwAP5Z8g1ganu6R0G1goJmsJSN8_XXCtGKpLeKdsUwenw/formResponse"
    ENTRY_REG_USER = "entry.1673314803"
    ENTRY_REG_PASS = "entry.133228326"

    SOHBET_GID = "0"
    UYELER_GID = "1016867892"

    BASE_URL = SHEET_URL.split('/edit')[0]
    SOHBET_CSV = f"{BASE_URL}/export?format=csv&gid={SOHBET_GID}"
    UYELER_CSV = f"{BASE_URL}/export?format=csv&gid={UYELER_GID}"

except Exception as e:
    st.error(f"Ayar hatası: {e}")
    st.stop()

genai.configure(api_key=API_KEY)
st.set_page_config(page_title="YozgatAI", page_icon="🌾")

# --- 2. YARDIMCI İŞLER ---
def verileri_oku(url):
    try:
        return pd.read_csv(url, on_bad_lines='skip')
    except:
        return pd.DataFrame()

# --- 3. OTURUM KONTROLÜ (DÜKKAN KAPISI) ---
# Eğer oturum açılmamışsa bu kısım çalışır
if "oturum" not in st.session_state:
    st.session_state.oturum = None

if st.session_state.oturum is None:
    st.title("🛡️ YozgatAI: Giriş Kapısı")
    
    # Sekmeleri oluşturuyoruz
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])

    # SEKME 1: GİRİŞ YAP
    with tab1:
        st.subheader("Üye Girişi") # Başlık ekledim ki sekme dolu görünsün
        giris_ad = st.text_input("Kullanıcı Adı", key="giris_ad_input")
        giris_sifre = st.text_input("Şifre", type="password", key="giris_sifre_input")
        
        if st.button("Giriş Yap", key="btn_giris"):
            if not giris_ad or not giris_sifre:
                st.warning("Adını şifreni yazmadan nereye?")
            else:
                df = verileri_oku(UYELER_CSV)
                if not df.empty:
                    df.columns = [c.lower() for c in df.columns]
                    try:
                        k_col = [c for c in df.columns if 'kullanici' in c or 'ad' in c][0]
                        s_col = [c for c in df.columns if 'sifre' in c or 'pass' in c][0]
                        # Kontrol
                        kisi = df[(df[k_col].astype(str) == giris_ad) & (df[s_col].astype(str) == giris_sifre)]
                        if not kisi.empty:
                            st.session_state.oturum = giris_ad
                            st.rerun()
                        else:
                            st.error("Yanlış bilgi girdin cano.")
                    except:
                        st.error("Sistem hatası: Tablo sütunları bulunamadı.")
                else:
                    st.error("Üye listesine