import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import time

# ------------------------------------------------------------------
# 1. AYARLAR VE ANAHTARLAR
# ------------------------------------------------------------------
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    
    # SENİN TABLO VE FORM BİLGİLERİN
    SPREADSHEET_ID = "1uhO7562rbctBNe4O-FDWzjUsZKf--FOGVvSg4ETqQWA"
    UYELER_GID = "809867134"    
    SOHBET_GID = "1043430012"   

    # LİNKLER
    UYELER_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={UYELER_GID}"
    SOHBET_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SOHBET_GID}"

    # FORMLAR
    KAYIT_FORM_VIEW = "https://docs.google.com/forms/d/e/1FAIpQLSfmWqswFyM7P7UGxkWnNzPjUZqNTcllt34lvudQZ9vM34LoKA/viewform"
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfzA0QcL_-RvuBf8sMauuawvrjgReFlYme4GlBlgfcLVP_hpw/formResponse"
    
    # ENTRY NUMARALARI
    ENTRY_CHAT_USER = "entry.2029948747"
    ENTRY_CHAT_MSG  = "entry.1854177336"
    ENTRY_CHAT_ROLE = "entry.698806781"

except Exception as e:
    st.error(f"Ayarlarda sıkıntı var kanki: {e}")
    st.stop()

# ------------------------------------------------------------------
# 2. SAYFA VE AI AYARLARI
# ------------------------------------------------------------------
st.set_page_config(page_title="YozgatAI", page_icon="🚀", layout="centered")
genai.configure(api_key=API_KEY)

# Verileri her zaman taze çeken fonksiyon
def verileri_oku(url):
    try:
        taze_url = f"{url}&t={int(time.time())}"
        return pd.read_csv(taze_url, on_bad_lines='skip')
    except:
        return pd.DataFrame()

# ------------------------------------------------------------------
# 3. GİRİŞ KAPISI (AKILLI TARAMA)
# ------------------------------------------------------------------
if "oturum" not in st.session_state:
    st.session_state.oturum = None

if st.session_state.oturum is None:
    st.title("🚀 Geleceğin Yapay Zekası: YozgatAI")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])

    with tab1:
        giris_ad = st.text_input("Kullanıcı Adı", placeholder="Adını yaz...")
        giris_sifre = st.text_input("Şifre", type="password", placeholder="Şifreni yaz...")
        
        if st.button("Sisteme Gir"):
            with st.spinner("Yozgat veritabanına bağlanılıyor..."):
                df = verileri_oku(UYELER_CSV)
            
            if not df.empty:
                g_ad = str(giris_ad).strip().lower()
                g_sifre = str(giris_sifre).strip().lower()
                basarili = False
                
                # Sütun kaymasına karşı akıllı tarama
                for index, row in df.iterrows():
                    for i in range(len(row) - 1):
                        try:
                            # Yan yana duran iki hücreyi kontrol et
                            h1 = str(row.iloc[i]).strip().lower()
                            h2 = str(row.iloc[i+1]).strip().lower()
                            if h1 == g_ad and h2 == g_sifre:
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
                    st.error("Kanki adın veya şifren yanlış. Kayıt oldun mu?")
            else:
                st.error("Veri çekilemedi. Bağlantıyı kontrol et.")

    with tab2:
        st.info("Aramıza katılmak için formu doldur.")
        st.link_button("📝 Kayıt Formuna Git", KAYIT