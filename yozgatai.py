import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import re

# --- 1. AYARLAR VE ANAHTARLAR ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    SHEET_URL = st.secrets["GSHEET_URL"]
    
    # SOHBET DEFTERİ (Eski Form)
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfAANTySmXphVhxNLT76RN-2n7MVjnX7WyNLJrH73qRZxPcrg/formResponse"
    ENTRY_CHAT_USER = "entry.1594572083"
    ENTRY_CHAT_MSG = "entry.1966407140"
    ENTRY_CHAT_ROLE = "entry.1321459799"

    # YENİ KAYIT FORMU (Senin Son Verdiğin Linkin Düzeltilmiş Hali)
    # Not: viewform yerine formResponse yaptık ki 401 hatası vermesin.
    REGISTER_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdvXHwAP5Z8g1ganu6R0G1goJmsJSN8_XXCtGKpLeKdsUwenw/formResponse"
    ENTRY_REG_USER = "entry.1673314803"
    ENTRY_REG_PASS = "entry.133228326"

    # GID NUMARALARI
    SOHBET_GID = "0"          # Sohbetler genelde ilk sayfadadır
    UYELER_GID = "1016867892" # Senin verdiğin Üyeler sayfası numarası

    # CSV OKUMA LİNKLERİ
    BASE_URL = SHEET_URL.split('/edit')[0]
    SOHBET_CSV = f"{BASE_URL}/export?format=csv&gid={SOHBET_GID}"
    UYELER_CSV = f"{BASE_URL}/export?format=csv&gid={UYELER_GID}"

except Exception as e:
    st.error(f"Kodun ayarlarında bir kertik var cano: {e}")
    st.stop()

# --- 2. SAYFA AYARI ---
genai.configure(api_key=API_KEY)
st.set_page_config(page_title="YozgatAI", page_icon="🌾")

# --- 3. FONKSİYONLAR ---

def verileri_oku(url):
    try:
        # Hata vermeden okumaya çalış
        return pd.read_csv(url, on_bad_lines='skip')
    except:
        return pd.DataFrame()

def kullanici_kontrol(isim):
    if len(isim) < 4:
        return False, "İsim en az 4 harf olsun."
    if not re.match("^[a-zA-Z0-9]+$", isim):
        return False, "İsimde sadece İngilizce harf ve sayı kullan."
    return True, ""

def sifre_kontrol(sifre):
    if len(sifre) < 6:
        return False, "Şifre en az 6 hane olsun."
    if not re.search("[0-9]", sifre): # Basit kontrol: En az bir rakam
        return False, "Şifreye en az bir rakam koy."
    # İstersen büyük/küçük harf kontrolünü buraya eklersin
    return True, ""

# --- 4. GİRİŞ VE KAYIT EKRANI ---
if "oturum" not in st.session_state:
    st.title("🛡️ YozgatAI: Giriş Kapısı")
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])

    # SEKME 1: GİRİŞ
    with tab1:
        g_ad = st.text_input("Kullanıcı Adı", key="g_ad").strip()
        g_sifre = st.text_input("Şifre", type="password", key="g_sifre").strip()
        
        if st.button("Dükkana Gir"):
            # Üyeler tablosunu indir
            df = verileri_oku(UYELER_CSV)
            if not df.empty:
                # Sütun adlarını küçük harfe çevir ki hata olmasın
                df.columns = [c.lower() for c in df.columns]
                try:
                    # Sütunları bul (ad ve sifre geçenleri)
                    # Formdan 'Kullanıcı Adı' diye gelir, biz 'kullanici' veya 'ad' ararız
                    k_col = [c for c in df.columns if 'kullanici' in c or 'ad' in c][0]
                    s_col = [c for c in df.columns if 'sifre' in c or 'pass' in c][0]
                    
                    # Kontrol
                    kisi = df[(df[k_col].astype(str) == g_ad) & (df[s_col].astype(str) == g_sifre)]
                    
                    if not kisi.empty:
                        st.success("Giriş yapılıyor...")
                        st.session_state.oturum = g_ad
                        st.rerun()
                    else:
                        st.error("Adın veya şifren yanlış cano. Yadırgadım seni.")
                except:
                    st.error("Tablo sütunları bulunamadı. Form başlıklarını kontrol et.")
            else:
                st.error("Üye listesi okunamadı veya boş.")

    # SEKME 2: KAYIT
    with tab2:
        y_ad = st.text_input("Yeni Kullanıcı Adı", key="y_ad").strip()
        y_sifre = st.text_input("Yeni Şifre", type="password", key="y_sifre").strip()
        
        if st.button("Kaydı Tamamla"):
            # 1. Kuralları Kontrol Et
            k_ok, k_msg = kullanici_kontrol(y_ad)
            s_ok, s_msg = sifre_kontrol(y_sifre)
            
            if not k_ok: st.error(k_msg)
            elif not s_ok: st.error(s_msg)
            else:
                # 2. İsim alınmış mı bak
                df = verileri_oku(UYELER_CSV)
                # Basit kontrol: Tüm tablo metninde bu isim geçiyor mu?
                if not df.empty and y_ad in df.to_string():
                    st.error("Bu isim kapılmış, başka bul.")
                else:
                    # 3. Kaydı Gönder
                    try:
                        veriler = {ENTRY_REG_USER: y_ad, ENTRY_REG_PASS: y_sifre}
                        # request atarken headers ekleyelim, belki Google robot sanıyordur
                        cevap = requests.post(REGISTER