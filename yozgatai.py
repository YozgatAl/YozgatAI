import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import re

# --- 1. AYARLAR VE ANAHTARLAR ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    SHEET_URL = st.secrets["GSHEET_URL"]
    
    # SOHBET FORMU (Buna dokunmadık, eski yerinde)
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfAANTySmXphVhxNLT76RN-2n7MVjnX7WyNLJrH73qRZxPcrg/formResponse"
    ENTRY_CHAT_USER = "entry.1594572083"
    ENTRY_CHAT_MSG = "entry.1966407140"
    ENTRY_CHAT_ROLE = "entry.1321459799"

    # YENİ KAYIT FORMU (Senin şahsi hesabınla açtığın, 401 vermeyen form)
    REGISTER_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSe_3gXSSc9RY5l6pqvv_SHQ5quV15MYypfFlASu2lzmY3sijQ/formResponse"
    ENTRY_REG_USER = "entry.1141114266"
    ENTRY_REG_PASS = "entry.589284418"

    # GID NUMARALARI
    SOHBET_GID = "0"          # Sohbetler 1. sayfada
    UYELER_GID = "80041286"   # İŞTE YENİ VERDİĞİN NUMARA BURADA!

    # CSV LİNKLERİ
    BASE_URL = SHEET_URL.split('/edit')[0]
    SOHBET_CSV = f"{BASE_URL}/export?format=csv&gid={SOHBET_GID}"
    UYELER_CSV = f"{BASE_URL}/export?format=csv&gid={UYELER_GID}"

except Exception as e:
    st.error(f"Ayarlarda bir kertik var cano: {e}")
    st.stop()

genai.configure(api_key=API_KEY)
st.set_page_config(page_title="YozgatAI", page_icon="🌾")

# --- 2. YARDIMCI FONKSİYONLAR ---
def verileri_oku(url):
    try:
        # on_bad_lines='skip' bozuk satır varsa atlar, hata vermez
        return pd.read_csv(url, on_bad_lines='skip')
    except:
        return pd.DataFrame()

# --- 3. GİRİŞ VE KAYIT EKRANI ---
if "oturum" not in st.session_state:
    st.session_state.oturum = None

if st.session_state.oturum is None:
    st.title("🛡️ YozgatAI: Giriş Kapısı")
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])

    # SEKME 1: GİRİŞ
    with tab1:
        st.subheader("Üye Girişi")
        giris_ad = st.text_input("Kullanıcı Adı", key="giris_ad")
        giris_sifre = st.text_input("Şifre", type="password", key="giris_sifre")
        
        if st.button("Dükkana Gir"):
            df = verileri_oku(UYELER_CSV)
            if not df.empty:
                # Sütun isimlerini küçük harfe çevirip garantiye alalım
                df.columns = [c.lower() for c in df.columns]
                try:
                    # İçinde 'kullanici', 'ad' veya 'entry' geçen sütunu bul
                    k_col = [c for c in df.columns if any(x in c for x in ['kullanici', 'ad', 'entry'])][0]
                    # İçinde 'sifre', 'pass' veya 'entry' geçen sütunu bul (2. sıradaki)
                    # Not: Aynı isimde birden fazla sütun olmaması için basit bir filtre
                    cols_list = list(df.columns)
                    # Genelde formda 2. ve 3. sütunlardır, isimden bulamazsa sırayla deneriz ama isimden bulması daha iyi
                    s_col = [c for c in df.columns if any(x in c for x in ['sifre', 'pass'])][0]

                    # Eşleşme kontrolü
                    kisi = df[(df[k_col].astype(str) == giris_ad) & (df[s_col].astype(str) == giris_sifre)]
                    
                    if not kisi.empty:
                        st.session_state.oturum = giris_ad
                        st.rerun()
                    else:
                        st.error("Adın veya şifren yanlış kurban. Yadırgadım seni.")
                except:
                    st.error("Sistem tabloyu okudu ama sütunları bulamadı. (Tablo başlıklarına bak)")
            else:
                st.error("Üye listesi boş veya okunamadı.")

    # SEKME 2: KAYIT
    with tab2:
        st.subheader("Yeni Kimlik Çıkar")
        yeni_ad = st.text_input("Kullanıcı Adı Seç", key="yeni_ad")
        yeni_sifre = st.text_input("Şifre Seç", type="password", key="yeni_sifre")
        
        if st.button("Kaydı Tamamla"):
            if len(yeni_ad) < 3:
                st.warning("Adın çok kısa, biraz uzat.")
            elif len(yeni_sifre) < 4:
                st.warning("Şifren çok basit, zorlaştır.")
            else:
                try:
                    # İnsan Maskesi (User-Agent) takıyoruz ki Google 'Robot' demesin
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                    veriler = {ENTRY_REG_USER: yeni_ad, ENTRY_REG_PASS: yeni_sifre}
                    
                    r = requests.post(REGISTER_FORM_URL, data=veriler, headers=headers)
                    
                    if r.status_code == 200:
                        st.success(f"Hayırlı olsun {yeni_ad}! Kaydın yapıldı. Giriş Yap sekmesine geçebilirsin.")
                    else:
                        st.warning(f"Google biraz nazlandı (Kod: {r.status_code}) ama kayıt gitmiş olabilir. Yan taraftan giriş yapmayı dene!")
                except Exception as e:
                    st.error(f"Bağlantı koptu: {e}")

    st.stop()

# --- 4. SOHBET EKRANI (İÇERİSİ) ---
kullanici = st.session_state.oturum
st.title(f"🌾 Selamünaleyküm {kullanici}!")

if st.sidebar.button("Çıkış Yap"):
    st.session_state.oturum = None
    st.rerun()

# Mesaj Geçmişini Getir
if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []
    df = verileri_oku(SOHBET_CSV)
    if not df.empty:
        try:
            df.columns = [c.lower() for c in df.columns]
            k_col = [c for c in df.columns if 'kullanici' in c][0]
            m_col = [c for c in df.columns if 'mesaj' in c][0]
            r_col = [c for c in df.columns if 'rol' in c][0]
            # Sadece bu kullanıcının mesajlarını süz
            gecmis = df[df[k_col].astype(str).str.lower() == kullanici.lower()]
            for _, row in gecmis.iterrows():
                st.session_state.mesajlar.append({"role": row[r_col], "content": row[m_col]})
        except: pass

# Mesajları Ekrana Bas
for m in st.session_state.mesajlar:
    with st.chat_message(m["role"]): st.write(m["content"])

# Emmi Zekası
model = genai.GenerativeModel('models/gemini-flash-latest', system_instruction="Sen Yozgatlı samimi bir emmisin. Şiveli konuş.")

if soru := st.chat_input("Nörüyon..."):
    st.session_state.mesajlar.append({"role": "user", "content": soru})
    with st.chat_message("user"): st.write(soru)
    # Sohbeti kaydederken de maske takalım
    headers = {"User-Agent": "Mozilla/5.0"}
    requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: soru, ENTRY_CHAT_ROLE: "user"}, headers=headers)
    
    try:
        cevap = model.generate_content(soru).text
        st.session_state.mesajlar.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant"): st.write(cevap)
        requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: cevap, ENTRY_CHAT_ROLE: "assistant"}, headers=headers)
    except:
        st.error("Emmi şu an meşgul.")