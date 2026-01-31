import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import time

# ------------------------------------------------------------------
# 1. AYARLAR VE TANIMLAMALAR
# ------------------------------------------------------------------
try:
    # Google API Anahtarı (Secrets'tan çekilir)
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    
    # E-Tablo ve Form Bilgileri
    SPREADSHEET_ID = "1uhO7562rbctBNe4O-FDWzjUsZKf--FOGVvSg4ETqQWA"
    UYELER_GID = "809867134"    
    SOHBET_GID = "1043430012"   

    # Veri Okuma Linkleri (CSV Formatında)
    UYELER_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={UYELER_GID}"
    SOHBET_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SOHBET_GID}"

    # Google Form Linkleri (Veri Kaydetmek İçin)
    KAYIT_FORM_VIEW = "https://docs.google.com/forms/d/e/1FAIpQLSfmWqswFyM7P7UGxkWnNzPjUZqNTcllt34lvudQZ9vM34LoKA/viewform"
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfzA0QcL_-RvuBf8sMauuawvrjgReFlYme4GlBlgfcLVP_hpw/formResponse"
    
    # Form Entry Numaraları (Soru ve Cevapları Eşleştirmek İçin)
    ENTRY_CHAT_USER = "entry.2029948747"
    ENTRY_CHAT_MSG  = "entry.1854177336"
    ENTRY_CHAT_ROLE = "entry.698806781"

except Exception as e:
    st.error(f"Ayarlarda sıkıntı var gardaşım: {e}")
    st.stop()

# ------------------------------------------------------------------
# 2. SAYFA YAPILANDIRMASI
# ------------------------------------------------------------------
st.set_page_config(page_title="YozgatAI", page_icon="🚀", layout="centered")
genai.configure(api_key=API_KEY)

# Verileri önbelleğe takılmadan taze çeken fonksiyon
def verileri_oku(url):
    try:
        taze_url = f"{url}&t={int(time.time())}"
        return pd.read_csv(taze_url, on_bad_lines='skip')
    except:
        return pd.DataFrame()

# ------------------------------------------------------------------
# 3. GİRİŞ EKRANI (Login)
# ------------------------------------------------------------------
if "oturum" not in st.session_state:
    st.session_state.oturum = None

if st.session_state.oturum is None:
    st.title("🚀 Geleceğin Yapay Zekası: YozgatAI")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])

    with tab1:
        st.info("Gardaşım hoş geldin, bilgilerini gir hele.")
        giris_ad = st.text_input("Kullanıcı Adı")
        giris_sifre = st.text_input("Şifre", type="password")
        
        if st.button("Sisteme Gir"):
            with st.spinner("Defter kontrol ediliyor..."):
                df = verileri_oku(UYELER_CSV)
            
            if not df.empty:
                g_ad = str(giris_ad).strip().lower()
                g_sifre = str(giris_sifre).strip().lower()
                basarili = False
                
                # Tabloda isim ve şifre eşleşmesi arıyoruz
                for index, row in df.iterrows():
                    for i in range(len(row) - 1):
                        try:
                            # Yan yana hücreleri kontrol et
                            k_ad = str(row.iloc[i]).strip().lower()
                            k_sifre = str(row.iloc[i+1]).strip().lower()
                            if k_ad == g_ad and k_sifre == g_sifre:
                                basarili = True
                                break
                        except: continue
                    if basarili: break
                
                if basarili:
                    st.session_state.oturum = giris_ad
                    st.success("Giriş Başarılı! Roket kalkıyor... 🚀")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Gardaşım,