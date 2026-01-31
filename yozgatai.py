import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests

# ------------------------------------------------------------------
# 1. AYARLAR (Dükkanın Tapusu)
# ------------------------------------------------------------------
try:
    # Gemini Anahtarı (Secrets dosyasından gelir)
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    
    # 📌 SENİN VERDİĞİN YENİ E-TABLO ID'Sİ
    SPREADSHEET_ID = "1uhO7562rbctBNe4O-FDWzjUsZKf--FOGVvSg4ETqQWA"
    
    # 📌 SENİN VERDİĞİN GID NUMARALARI
    UYELER_GID = "809867134"    # Üye Listesi (Kullanıcı Giriş)
    SOHBET_GID = "1043430012"   # Sohbet Geçmişi

    # 📌 LİNKLER (Google'dan veriyi çeken sihirli yollar)
    # Not: Tablonun "Paylaş: Herkes" olması şarttır!
    UYELER_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={UYELER_GID}"
    SOHBET_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SOHBET_GID}"

    # ------------------------------------------------------------------
    # 🚨 DİKKAT: FORMLARIN LİNKLERİNİ BURAYA YAZMAN LAZIM GARDAŞIM!
    # ------------------------------------------------------------------
    
    # 1. KAYIT FORMU (Viewform linki)
    KAYIT_FORM_VIEW = "https://docs.google.com/forms/d/e/SENIN_KAYIT_FORM_ID_BURAYA/viewform"
    
    # 2. SOHBET FORMU (FormResponse linki)
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/SENIN_SOHBET_FORM_ID_BURAYA/formResponse"
    
    # Sohbet Formundaki Kutucuk Numaraları (Sağ tık > İncele ile buldukların)
    # Bunları doldurmazsan sohbet kaydolmaz ama site çalışır.
    ENTRY_CHAT_USER = "entry.XXXXX"   
    ENTRY_CHAT_MSG  = "entry.YYYYY"   
    ENTRY_CHAT_ROLE = "entry.ZZZZZ"   

except Exception as e:
    st.error(f"Ayarlarda bir kertik var kurban olduğum: {e}")
    st.stop()

# Gemini ve Sayfa Ayarları
genai.configure(api_key=API_KEY)
st.set_page_config(page_title="YozgatAI", page_icon="🌾")

# ------------------------------------------------------------------
# 2. YARDIMCI FONKSİYONLAR (Çıraklar)
# ------------------------------------------------------------------
def verileri_oku(url):
    """Google E-Tablo'dan CSV okur."""
    try:
        df = pd.read_csv(url, on_bad_lines='skip')
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# ------------------------------------------------------------------
# 3. GİRİŞ EKRANI
# ------------------------------------------------------------------
if "oturum" not in st.session_state:
    st.session_state.oturum = None

if st.session_state.oturum is None:
    st.title("🛡️ YozgatAI: Giriş Kapısı")
    
    tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])

    # --- GİRİŞ YAP ---
    with tab1:
        giris_ad = st.text_input("Kullanıcı Adı", key="giris_ad")
        giris_sifre = st.text_input("Şifre", type="password", key="giris_sifre")
        
        if st.button("Dükkana Gir"):
            df = verileri_oku(UYELER_CSV)
            
            if not df.empty:
                try:
                    # Sütunları bulmaya çalışıyoruz
                    col_user = [c for c in df.columns if "kullanıcı" in c or "user" in c or "ad" in c][0]
                    col_pass = [c for c in df.columns if "şifre" in c or "sifre" in c or "pass" in c][0]
                    
                    kisi = df[(df[col_user].astype(str) == giris_ad) & (df[col_pass].astype(str) == giris_sifre)]
                    
                    if not kisi.empty:
                        st.success("Giriş Başarılı! Çaylar söyleniyor...")
                        st.session_state.oturum = giris_ad
                        st.rerun()
                    else:
                        st.error("Adın veya şifren yanlış gardaşım.")
                except:
                    st.error("Tabloda 'Kullanıcı' ve 'Şifre' sütunlarını bulamadım. Başlıkları yazdın mı?")
            else:
                st.error("Liste okunamadı. Tabloyu 'Paylaş: Herkes' yaptığından emin misin?")

    # --- KAYIT OL ---
    with tab2:
        st.info("Kayıt olmak için aşağıdaki butona bas, formu doldur gel.")
        st.link_button("👉 Kayıt Formunu Aç", KAYIT_FORM_VIEW)

    st.stop()

# ------------------------------------------------------------------
# 4. SOHBET EKRANI
# ------------------------------------------------------------------
kullanici = st.session_state.oturum

with st.sidebar:
    st.title(f"👤 {kullanici}")
    if st.button("Çıkış Yap"):
        st.session_state.oturum = None
        st.rerun()

st.title("🌾 YozgatAI Sohbet Odası")

# GEÇMİŞİ YÜKLE
if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []
    df_sohbet = verileri_oku(SOHBET_CSV)
    if not df_sohbet.empty:
        try:
            c_user = [c for c in df_sohbet.columns if "kullanıcı" in c or "user" in c][0]
            c_msg  = [c for c in df_sohbet.columns if "mesaj" in c][0]
            c_role = [c for c in df_sohbet.columns if "rol" in c][0]
            
            gecmis = df_sohbet[df_sohbet[c_user].astype(str) == kullanici]
            for _, row in gecmis.iterrows():
                st.session_state.mesajlar.append({"role": row[c_role], "content": row[c_msg]})
        except: pass

# MESAJLARI GÖSTER
for m in st.session_state.mesajlar:
    with st.chat_message(m["role"]): st.write(m["content"])

# YENİ MESAJ
model = genai.GenerativeModel('models/gemini-1.5-flash', system_instruction="Sen Yozgatlı samimi bir emmisin. Şiveli konuş.")

if soru := st.chat_input("Nörüyon..."):
    st.session_state.mesajlar.append({"role": "user", "content": soru})
    with st.chat_message("user"): st.write(soru)
    
    # Forma kaydet (Hata verirse site durmaz)
    try:
        requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: soru, ENTRY_CHAT_ROLE: "user"})
    except: pass

    try:
        cevap = model.generate_content(soru).text
        st.session_state.mesajlar.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant"): st.write(cevap)
        
        requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: cevap, ENTRY_CHAT_ROLE: "assistant"})
    except:
        st.error("Emmi cevap veremedi.")