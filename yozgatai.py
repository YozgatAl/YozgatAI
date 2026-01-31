import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests

# --- 1. AYARLAR ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    
    # 🚨 BURAYA YENİ GOOGLE E-TABLO ID'SİNİ YAPIŞTIR!
    SPREADSHEET_ID = "1hjLh1OqVfzuv5sM3o_NDlGc67mt5Anu3Bd_tPOZDhDg" 
    
    # 🚨 SOHBET KAYIT FORMU BİLGİLERİ (İkinci açtığın form)
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/YENI_SOHBET_FORM_ID/formResponse"
    ENTRY_CHAT_USER = "entry.XXXXX" # Kullanıcı kutusu
    ENTRY_CHAT_MSG = "entry.YYYYY"  # Mesaj (Paragraf) kutusu
    ENTRY_CHAT_ROLE = "entry.ZZZZZ" # Rol kutusu

    # 🚨 KAYIT FORMU LİNKİ (Birinci açtığın form - Giriş için)
    KAYIT_FORM_VIEW = "https://docs.google.com/forms/d/e/YENI_KAYIT_FORM_ID/viewform"

    # GID NUMARALARI (Senin verdiklerin)
    UYELER_GID = "809867134"   # Üye Listesi Sekmesi
    SOHBET_GID = "1043430012"  # Sohbet Geçmişi Sekmesi

    # CSV LİNKLERİ
    UYELER_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={UYELER_GID}"
    SOHBET_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SOHBET_GID}"

except Exception as e:
    st.error(f"Ayarlarda bir kertik var gardaşım: {e}")
    st.stop()

genai.configure(api_key=API_KEY)
st.set_page_config(page_title="YozgatAI", page_icon="🌾")

# --- 2. YARDIMCI İŞLER ---
def verileri_oku(url):
    try:
        # Dosya > Paylaş > Web'de Yayınla dediysen tıkır tıkır okur
        return pd.read_csv(url, on_bad_lines='skip')
    except:
        return pd.DataFrame()

# --- 3. GİRİŞ KAPISI ---
if "oturum" not in st.session_state:
    st.session_state.oturum = None

if st.session_state.oturum is None:
    st.title("🛡️ YozgatAI: Giriş Kapısı")
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])

    with tab1:
        st.subheader("Üye Girişi")
        giris_ad = st.text_input("Kullanıcı Adı", key="giris_ad")
        giris_sifre = st.text_input("Şifre", type="password", key="giris_sifre")
        
        if st.button("Dükkana Gir"):
            df = verileri_oku(UYELER_CSV)
            if not df.empty:
                df.columns = [c.lower() for c in df.columns]
                try:
                    k_col = [c for c in df.columns if any(x in c for x in ['kullanici', 'ad', 'entry'])][0]
                    s_col = [c for c in df.columns if any(x in c for x in ['sifre', 'pass'])][0]
                    kisi = df[(df[k_col].astype(str) == giris_ad) & (df[s_col].astype(str) == giris_sifre)]
                    
                    if not kisi.empty:
                        st.session_state.oturum = giris_ad
                        st.rerun()
                    else:
                        st.error("Adın veya şifren yanlış kurban.")
                except:
                    st.error("Sütunlar bulunamadı. Tablo başlıklarını kontrol et.")
            else:
                st.error("Üye listesi okunamadı. 'Web'de Yayınla' açık mı?")

    with tab2:
        st.info("Kayıt olmak için aşağıdaki butona tıkla, formu doldur ve buraya gel.")
        st.link_button("📝 Şimdi Kayıt Ol", KAYIT_FORM_VIEW)

    st.stop()

# --- 4. SOHBET EKRANI (İçerisi) ---
kullanici = st.session_state.oturum
st.title(f"🌾 Selamünaleyküm {kullanici}!")

if st.sidebar.button("Çıkış Yap"):
    st.session_state.oturum = None
    st.rerun()

# GEÇMİŞİ OKU
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

# EKRANA BAS
for m in st.session_state.mesajlar:
    with st.chat_message(m["role"]): st.write(m["content"])

model = genai.GenerativeModel('models/gemini-flash-latest', system_instruction="Sen Yozgatlı samimi bir emmisin. Şiveli konuş.")

if soru := st.chat_input("Nörüyon..."):
    st.session_state.mesajlar.append({"role": "user", "content": soru})
    with st.chat_message("user"): st.write(soru)
    
    # FORMA GÖNDER (Kullanıcı Mesajı)
    try:
        requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: soru, ENTRY_CHAT_ROLE: "user"})
    except: pass
    
    try:
        cevap = model.generate_content(soru).text
        st.session_state.mesajlar.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant"): st.write(cevap)
        
        # FORMA GÖNDER (Bot Cevabı)
        requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: cevap, ENTRY_CHAT_ROLE: "assistant"})
    except:
        st.error("Emmi cevap veremedi.")