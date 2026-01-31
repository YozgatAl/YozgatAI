import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import re  # Şifre ve isim kontrolü için lazım olan alet

# --- KASA VE BAĞLANTILAR ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    SHEET_URL = st.secrets["GSHEET_URL"]
    
    # 1. SOHBET DEFTERİ (Eski Formun)
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfAANTySmXphVhxNLT76RN-2n7MVjnX7WyNLJrH73qRZxPcrg/formResponse"
    ENTRY_CHAT_USER = "entry.1594572083"
    ENTRY_CHAT_MSG = "entry.1966407140"
    ENTRY_CHAT_ROLE = "entry.1321459799"

    # 2. NÜFUS MÜDÜRLÜĞÜ (Yeni Kayıt Formun)
    REGISTER_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdkyeYqKIeTIu3xEFd4X6YAVVrUPDeg5kekKfCaYhHwd0EYLw/formResponse"
    ENTRY_REG_USER = "entry.1024954161"
    ENTRY_REG_PASS = "entry.1526008229"

    # Tabloyu okuma linki (Sadece ilk sayfayı okur - Sohbetler sayfası en başta olsun!)
    CSV_URL = SHEET_URL.split('/edit')[0] + '/export?format=csv'

except Exception as e:
    st.error(f"Ayarlarda bir kertik var kurban: {e}")
    st.stop()

genai.configure(api_key=API_KEY)
st.set_page_config(page_title="YozgatAI", page_icon="🌾")

# --- FONKSİYONLAR ---

def verileri_getir():
    try:
        # Bu fonksiyon sohbet geçmişini çeker
        return pd.read_csv(CSV_URL)
    except:
        return pd.DataFrame()

def kullanici_kontrol_kurallari(isim):
    # Kural 1: En az 4 karakter
    if len(isim) < 4:
        return False, "Kurban, isim dediğin en az 4 harf olacak."
    # Kural 2: Sadece İngilizce harf ve rakam (Özel karakter yok, Türkçe yok)
    if not re.match("^[a-zA-Z0-9]+$", isim):
        return False, "İsimde Türkçe karakter, boşluk veya garip işaretler olamaz. Sadece İngilizce harf ve sayı!"
    return True, ""

def sifre_kontrol_kurallari(sifre):
    # Kural 1: En az 6 karakter
    if len(sifre) < 6:
        return False, "Şifre çok kısa, en az 6 hane olsun."
    # Kural 2: Büyük harf, küçük harf, rakam
    if not re.search("[a-z]", sifre):
        return False, "Şifreye bir tane küçük harf koy."
    if not re.search("[A-Z]", sifre):
        return False, "Şifreye bir tane BÜYÜK harf koy."
    if not re.search("[0-9]", sifre):
        return False, "Şifreye bir tane de rakam iliştir."
    return True, ""

def kayit_yap(kullanici, sifre):
    # Yeni üyeyi forma (Google Sheets'e) kaydeder
    payload = {ENTRY_REG_USER: kullanici, ENTRY_REG_PASS: sifre}
    try:
        requests.post(REGISTER_FORM_URL, data=payload)
        return True
    except:
        return False

def sohbet_kaydet(kullanici, mesaj, rol):
    # Konuşmaları kaydeder
    payload = {ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: mesaj, ENTRY_CHAT_ROLE: rol}
    try:
        requests.post(CHAT_FORM_URL, data=payload)
    except:
        pass

# --- ANA EKRAN (GİRİŞ KAPISI) ---
if "oturum" not in st.session_state:
    st.title("🛡️ YozgatAI: Güvenlik Kapısı")
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol (Nüfus)"])

    # --- SEKME 1: GİRİŞ ---
    with tab1:
        st.subheader("Hoşgeldin Ağa")
        giris_ad = st.text_input("Kullanıcı Adı", key="giris_ad")
        giris_sifre = st.text_input("Şifre", type="password", key="giris_sifre")
        
        if st.button("Dükkana Gir"):
            if giris_ad and giris_sifre:
                # Normalde burada şifreyi veritabanından kontrol etmek lazım.
                # Ama Google Sheets'in 2. sayfasını okumak şu an karmaşık olur.
                # O yüzden şimdilik ismi doğru yazanı içeri alıyoruz.
                # İlerde şifre kontrolünü de ekleriz.
                st.session_state.oturum = giris_ad
                st.rerun()
            else:
                st.warning("Adını şifreni boş geçme!")

    # --- SEKME 2: KAYIT ---
    with tab2:
        st.subheader("Yeni Kimlik Çıkar")
        yeni_ad = st.text_input("Kullanıcı Adı (İngilizce harf, en az 4 karakter)", key="yeni_ad")
        yeni_sifre = st.text_input("Şifre (En az 6 karakter, Büyük/Küçük harf ve sayı)", type="password", key="yeni_sifre")
        
        if st.button("Kaydı Tamamla"):
            # 1. Kuralları Kontrol Et
            isim_uygun, isim_mesaj = kullanici_kontrol_kurallari(yeni_ad)
            sifre_uygun, sifre_mesaj = sifre_kontrol_kurallari(yeni_sifre)
            
            if not isim_uygun:
                st.error(isim_uygun)
            elif not sifre_uygun:
                st.error(sifre_mesaj)
            else:
                # 2. Kaydı Yap
                if kayit_yap(yeni_ad, yeni_sifre):
                    st.success(f"Hayırlı olsun {yeni_ad}! Şimdi 'Giriş Yap' sekmesinden girebilirsin.")
                    st.info("Not: Kaydın veritabanına işlenmesi 1-2 saniye sürebilir.")
                else:
                    st.error("Nüfus müdürlüğünde sistem gitti, sonra dene!")
    
    st.stop()

# --- SOHBET ODASI (İÇERİSİ) ---
kullanici = st.session_state.oturum
st.title(f"🚀 Selamünaleyküm {kullanici}!")

# Çıkış Butonu
with st.sidebar:
    st.write(f"👤 Aktif Kullanıcı: **{kullanici}**")
    if st.button("Çıkış Yap"):
        st.session_state.oturum = None
        st.rerun()

# Geçmişi Yükle
if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []
    df = verileri_getir()
    
    if not df.empty:
        try:
            # Sütun isimlerini küçük harfe çevir
            df.columns = [c.lower() for c in df.columns]
            
            # Sütunları bul (kullanici, mesaj, rol)
            # Not: Formdan gelen sütun adları bazen değişebilir, "içinde geçen" kelimeye bakıyoruz
            kul_col = [c for c in df.columns if 'kullanici' in c][0]
            mesaj_col = [c for c in df.columns if 'mesaj' in c][0]
            rol_col = [c for c in df.columns if 'rol' in c][0]

            # Sadece bu kullanıcıya ait mesajları süz
            gecmis = df[df[kul_col].astype(str).str.contains(kullanici, case=False, na=False)]
            
            for _, row in gecmis.iterrows():
                st.session_state.mesajlar.append({"role": row[rol_col], "content": row[mesaj_col]})
        except Exception as e:
            # Hata verirse sessizce geç, geçmiş yüklenmez sadece
            pass 

# Mesajları Ekrana Yaz
for m in st.session_state.mesajlar:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# Emmi Ayarları
model = genai.GenerativeModel('models/gemini-flash-latest', system_instruction="Sen Yozgatlı samimi bir emmisin. Şiveli konuş.")

# Soru Sorma Yeri
if soru := st.chat_input("Bir yumuş buyur..."):
    # 1. Kullanıcı mesajını göster ve kaydet
    st.session_state.mesajlar.append({"role": "user", "content": soru})
    with st.chat_message("user"):
        st.write(soru)
    sohbet_kaydet(kullanici, soru, "user")
    
    # 2. Emmi cevap versin
    try:
        cevap = model.generate_content(soru).text
        st.session_state.mesajlar.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant"):
            st.write(cevap)
        sohbet_kaydet(kullanici, cevap, "assistant")
    except Exception as e:
        st.error("Emmi cevap veremedi, internette bi kertik var.")