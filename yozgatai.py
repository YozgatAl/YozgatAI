import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import re

# --- KASA VE BAĞLANTILAR ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    SHEET_URL = st.secrets["GSHEET_URL"]
    
    # 1. SOHBET FORMU
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfAANTySmXphVhxNLT76RN-2n7MVjnX7WyNLJrH73qRZxPcrg/formResponse"
    ENTRY_CHAT_USER = "entry.1594572083"
    ENTRY_CHAT_MSG = "entry.1966407140"
    ENTRY_CHAT_ROLE = "entry.1321459799"

    # 2. KAYIT FORMU
    REGISTER_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdkyeYqKIeTIu3xEFd4X6YAVVrUPDeg5kekKfCaYhHwd0EYLw/formResponse"
    ENTRY_REG_USER = "entry.1024954161"
    ENTRY_REG_PASS = "entry.1526008229"

    # Sayfa ID'leri (Senin verdiğin GID!)
    SOHBET_GID = "0"  # İlk sayfa genelde 0'dır
    UYELER_GID = "1016867892"

    # CSV Okuma Linkleri
    BASE_URL = SHEET_URL.split('/edit')[0]
    SOHBET_CSV = f"{BASE_URL}/export?format=csv&gid={SOHBET_GID}"
    UYELER_CSV = f"{BASE_URL}/export?format=csv&gid={UYELER_GID}"

except Exception as e:
    st.error(f"Kasa ayarlarında bir kertik var kurban: {e}")
    st.stop()

genai.configure(api_key=API_KEY)
st.set_page_config(page_title="YozgatAI", page_icon="🌾")

# --- FONKSİYONLAR ---

def verileri_oku(url):
    try:
        # Cache'i temizleyerek her seferinde güncel tabloyu çekiyoruz
        return pd.read_csv(url, on_bad_lines='skip')
    except:
        return pd.DataFrame()

def kullanici_kontrol_kurallari(isim):
    if len(isim) < 4:
        return False, "Kurban, isim dediğin en az 4 harf olacak."
    if not re.match("^[a-zA-Z0-9]+$", isim):
        return False, "İsimde sadece İngilizce harf ve sayı olabilir!"
    return True, ""

def sifre_kontrol_kurallari(sifre):
    if len(sifre) < 6:
        return False, "Şifre çok kısa, en az 6 hane olsun."
    if not re.search("[a-z]", sifre) or not re.search("[A-Z]", sifre) or not re.search("[0-9]", sifre):
        return False, "Şifrede en az bir Büyük harf, bir Küçük harf ve bir Rakam olsun!"
    return True, ""

# --- GİRİŞ VE KAYIT EKRANI ---
if "oturum" not in st.session_state:
    st.title("🛡️ YozgatAI: VIP Güvenlik Kapısı")
    tab1, tab2 = st.tabs(["Giriş Yap", "Yeni Kayıt"])

    with tab1:
        st.subheader("Hoşgeldin Ağa")
        g_ad = st.text_input("Kullanıcı Adı", key="g_ad").strip()
        g_sifre = st.text_input("Şifre", type="password", key="g_sifre").strip()
        
        if st.button("Dükkana Gir"):
            uyeler_df = verileri_oku(UYELER_CSV)
            if not uyeler_df.empty:
                # Sütunları küçük harfe çevirip kontrol et
                uyeler_df.columns = [c.lower() for c in uyeler_df.columns]
                # Tablodaki kullanıcı adı ve şifre sütunlarını bul
                k_col = [c for c in uyeler_df.columns if 'kullanici' in c][0]
                s_col = [c for c in uyeler_df.columns if 'sifre' in c][0]
                
                # Kullanıcıyı bul
                kisi = uyeler_df[(uyeler_df[k_col].astype(str) == g_ad) & (uyeler_df[s_col].astype(str) == g_sifre)]
                
                if not kisi.empty:
                    st.session_state.oturum = g_ad
                    st.rerun()
                else:
                    st.error("Adın veya şifren yanlış kurban, yadırgarım bak!")
            else:
                st.error("Üye listesine ulaşılamadı!")

    with tab2:
        st.subheader("Yeni Kimlik Çıkar")
        y_ad = st.text_input("Kullanıcı Adı", key="y_ad").strip()
        y_sifre = st.text_input("Şifre", type="password", key="y_sifre").strip()
        
        if st.button("Kaydı Tamamla"):
            # Önce veritabanında var mı bak
            uyeler_df = verileri_oku(UYELER_CSV)
            if y_ad in uyeler_df.values:
                st.error("Bu isim kapılmış, başka bir tane bul.")
            else:
                i_tam, i_msj = kullanici_kontrol_kurallari(y_ad)
                s_tam, s_msj = sifre_kontrol_kurallari(y_sifre)
                
                if not i_tam: st.error(i_msj)