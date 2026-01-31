import streamlit as st
import google.generativeai as genai
import pandas as pd

# --- GÜVENLİK VE BAĞLANTI ---
# Bu bilgiler Streamlit'teki "Secrets" kutusundan geliyor
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    SHEET_URL = st.secrets["GSHEET_URL"]
    
    # Google Sheet linkini sistemin okuyabileceği CSV formatına çeviriyoruz
    if "/edit" in SHEET_URL:
        CSV_URL = SHEET_URL.split('/edit')[0] + '/export?format=csv'
    else:
        CSV_URL = SHEET_URL
except Exception as e:
    st.error("Aman kurban, Secrets ayarlarında bir kertik var! Anahtarları kontrol et.")
    st.stop()

# Yapay zekayı ateşliyoruz
genai.configure(api_key=API_KEY)

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="YozgatAI VIP", page_icon="🌾")

# --- VERİTABANINDAN GEÇMİŞİ ÇEKME ---
def gecmisi_getir(kullanici_adi):
    try:
        # Tabloyu internetten oku
        df = pd.read_csv(CSV_URL)
        # Sadece bu kullanıcıya ait olanları ayır (küçük harfe çevirerek bakıyoruz)
        kullanici_gecmisi = df[df['kullanici'].str.lower() == kullanici_adi.lower()]
        return kullanici_gecmisi
    except:
        # Tablo boşsa veya hata verirse boş bir liste dön
        return pd.DataFrame(columns=['kullanici', 'mesaj', 'rol', 'zaman'])

# --- GİRİŞ SİSTEMİ (HESAP AÇMA) ---
if "kullanici" not in st.session_state:
    st.title("🛡️ YozgatAI: Giriş Kapısı")
    st.write("Dükkana girmek için ibdil (öncelikle) bir isim de hele kurban.")
    
    ad = st.text_input("Adın ne?")
    
    if st.button("Dükkana Gir"):
        if ad:
            st.session_state.kullanici = ad.strip()
            st.rerun()
        else:
            st.warning("Adını demezsen seni yadırgarım, içeri almam!")
    st.stop()

# --- SOHBET EKRANI (GİRİŞ YAPILINCA BURASI ÇALIŞIR) ---
st.title(f"🚀 Selamünaleyküm {st.session_state.kullanici}!")
st.sidebar.header("Dükkan Menüsü")
st.sidebar.write(f"👤 Kullanıcı: {st.session_state.kullanici}")

if