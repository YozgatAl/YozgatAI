import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests

# --- 1. AYARLAR ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    
    # SENİN VERDİĞİN TABLO BİLGİLERİ (Burası mühim!)
    SPREADSHEET_ID = "1hjLh1OqVfzuv5sM3o_NDlGc67mt5Anu3Bd_tPOZDhDg"
    UYELER_GID = "609965995" # Üyeler sayfası
    SOHBET_GID = "0"         # Sohbet sayfası

    # LİNKLERİ OLUŞTURUYORUZ
    UYELER_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={UYELER_GID}"
    SOHBET_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SOHBET_GID}"
    
    # FORM LİNKLERİ
    # Kayıt Formunun Orijinal Linki (Kullanıcıyı buraya göndereceğiz)
    KAYIT_LINKI = "https://docs.google.com/forms/d/e/1FAIpQLSe_3gXSSc9RY5l6pqvv_SHQ5quV15MYypfFlASu2lzmY3sijQ/viewform"
    
    # Sohbet Formu (Botun konuşması için)
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfAANTySmXphVhxNLT76RN-2n7MVjnX7WyNLJrH73qRZxPcrg/formResponse"
    ENTRY_CHAT_USER = "entry.1594572083"
    ENTRY_CHAT_MSG = "entry.1966407140"
    ENTRY_CHAT_ROLE = "entry.1321459799"

except Exception as e:
    st.error(f"Ayarlarda hata var gardaşım: {e}")
    st.stop()

genai.configure(api_key=API_KEY)
st.set_page_config(page_title="YozgatAI", page_icon="🌾")

# --- 2. YARDIMCI İŞLER ---
def verileri_oku(url):
    try:
        return pd.read_csv(url, on_bad_lines='skip')
    except:
        return pd.DataFrame()

# --- 3. GİRİŞ KAPISI ---
if "oturum" not in st.session_state:
    st.session_state.oturum = None

if st.session_state.oturum is None:
    st.title("🛡️ YozgatAI: Giriş Kapısı")
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])

    # SEKME 1: GİRİŞ YAP
    with tab1:
        st.info("Kayıt olduysan bilgilerini gir gardaşım.")
        giris_ad = st.text_input("Kullanıcı Adı", key="giris_ad")
        giris_sifre = st.text_input("Şifre", type="password", key="giris_sifre")
        
        if st.button("Dükkana Gir"):
            df = verileri_oku(UYELER_CSV)
            if not df.empty:
                df.columns = [c.lower() for c in df.columns]
                try:
                    # Tabloda isim ve şifre sütunlarını bul
                    k_col = [c for c in df.columns if any(x in c for x in ['kullanici', 'ad', 'entry'])][0]
                    s_col = [c for c in df.columns if any(x in c for x in ['sifre', 'pass'])][0]
                    
                    # Kontrol et
                    kisi = df[(df[k_col].astype(str) == giris_ad) & (df[s_col].astype(str) == giris_sifre)]
                    
                    if not kisi.empty:
                        st.success("Giriş Başarılı! Yönlendiriliyorsun...")
                        st.session_state.oturum = giris_ad
                        st.rerun()
                    else:
                        st.error("Adın veya şifren yanlış. Kayıt oldun mu?")
                except:
                    st.error("Sistem tabloyu okuyamadı. Tablo boş olabilir mi?")
            else:
                st.error("Üye defteri boş veya okunamıyor. (Tabloyu 'Herkes'e açtın mı?)")

    # SEKME 2: KAYIT OL (KESİN ÇÖZÜM)
    with tab2:
        st.warning("⚠️ Google robotlara izin vermiyor. O yüzden aşağıdaki butona bas, açılan sayfada kaydını yap gel.")
        
        # Direkt form sayfasına gönderiyoruz
        st.link_button("📝 Kayıt Formunu Aç (Tıkla)", KAYIT_LINKI)
        
        st.write("---")
        st.write("Kaydını yaptıktan sonra **Giriş Yap** sekmesine dönüp girebilirsin.")

    st.stop()

# --- 4. SOHBET EKRANI ---
kullanici = st.session_state.oturum
st.title(f"🌾 Selamünaleyküm {kullanici}!")

if st.sidebar.button("Çıkış Yap"):
    st.session_state.oturum = None
    st.rerun()

# Geçmiş
if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []
    df = verileri_oku(SOHBET_CSV)
    if not df.empty:
        try:
            df.columns = [c.lower() for c in df.columns]
            k_col = [c for c in df.columns if 'kullanici' in c][0]
            m_col = [c for c in df.columns if 'mesaj' in c][0]
            r_col = [c for c in df.columns if 'rol' in c][0]
            
            gecmis = df[df[k_col].astype(str).str.lower() == kullanici.lower()]
            for _, row in gecmis.iterrows():
                st.session_state.mesajlar.append({"role": row[r_col], "content": row[m_col]})
        except: pass

for m in st.session_state.mesajlar:
    with st.chat_message(m["role"]): st.write(m["content"])

model = genai.GenerativeModel('models/gemini-flash-latest', system_instruction="Sen Yozgatlı samimi bir emmisin. Şiveli konuş.")

if soru := st.chat_input("Nörüyon..."):
    st.session_state.mesajlar.append({"role": "user", "content": soru})
    with st.chat_message("user"): st.write(soru)
    # Sohbeti kaydet (Sohbet formunda genelde 401 vermez ama verirse burayı da try-except yaparız)
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