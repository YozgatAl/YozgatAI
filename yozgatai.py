import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import re

# --- 1. AYARLAR ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    SHEET_URL = st.secrets["GSHEET_URL"]
    
    # LİNKLER
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfAANTySmXphVhxNLT76RN-2n7MVjnX7WyNLJrH73qRZxPcrg/formResponse"
    ENTRY_CHAT_USER = "entry.1594572083"
    ENTRY_CHAT_MSG = "entry.1966407140"
    ENTRY_CHAT_ROLE = "entry.1321459799"

    REGISTER_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdvXHwAP5Z8g1ganu6R0G1goJmsJSN8_XXCtGKpLeKdsUwenw/formResponse"
    ENTRY_REG_USER = "entry.1673314803"
    ENTRY_REG_PASS = "entry.133228326"

    SOHBET_GID = "0"
    UYELER_GID = "1016867892"

    BASE_URL = SHEET_URL.split('/edit')[0]
    SOHBET_CSV = f"{BASE_URL}/export?format=csv&gid={SOHBET_GID}"
    UYELER_CSV = f"{BASE_URL}/export?format=csv&gid={UYELER_GID}"

except Exception as e:
    st.error(f"Ayar hatası: {e}")
    st.stop()

genai.configure(api_key=API_KEY)
st.set_page_config(page_title="YozgatAI", page_icon="🌾")

# --- 2. YARDIMCI İŞLER ---
def verileri_oku(url):
    try:
        return pd.read_csv(url, on_bad_lines='skip')
    except:
        return pd.DataFrame()

# --- 3. OTURUM KONTROLÜ ---
if "oturum" not in st.session_state:
    st.session_state.oturum = None

if st.session_state.oturum is None:
    st.title("🛡️ YozgatAI: Giriş Kapısı")
    
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])

    # SEKME 1: GİRİŞ YAP
    with tab1:
        st.subheader("Üye Girişi")
        giris_ad = st.text_input("Kullanıcı Adı", key="giris_ad_input")
        giris_sifre = st.text_input("Şifre", type="password", key="giris_sifre_input")
        
        if st.button("Giriş Yap", key="btn_giris"):
            if not giris_ad or not giris_sifre:
                st.warning("Adını şifreni yazmadan nereye?")
            else:
                df = verileri_oku(UYELER_CSV)
                if not df.empty:
                    df.columns = [c.lower() for c in df.columns]
                    try:
                        k_col = [c for c in df.columns if 'kullanici' in c or 'ad' in c][0]
                        s_col = [c for c in df.columns if 'sifre' in c or 'pass' in c][0]
                        kisi = df[(df[k_col].astype(str) == giris_ad) & (df[s_col].astype(str) == giris_sifre)]
                        if not kisi.empty:
                            st.session_state.oturum = giris_ad
                            st.rerun()
                        else:
                            st.error("Yanlış bilgi girdin cano.")
                    except:
                        st.error("Sistem hatası: Tablo sütunları bulunamadı.")
                else:
                    st.error("Üye listesine ulaşılamıyor.")

    # SEKME 2: KAYIT OL
    with tab2:
        st.subheader("Yeni Kayıt")
        yeni_ad = st.text_input("Yeni Kullanıcı Adı", key="yeni_ad_input")
        yeni_sifre = st.text_input("Yeni Şifre", type="password", key="yeni_sifre_input")
        
        if st.button("Kayıt Ol", key="btn_kayit"):
            if len(yeni_ad) < 4:
                st.error("İsim en az 4 harf olsun.")
            elif len(yeni_sifre) < 6:
                st.error("Şifre en az 6 hane olsun.")
            else:
                df = verileri_oku(UYELER_CSV)
                if not df.empty and yeni_ad in df.to_string():
                    st.error("Bu isim alınmış.")
                else:
                    try:
                        veriler = {ENTRY_REG_USER: yeni_ad, ENTRY_REG_PASS: yeni_sifre}
                        r = requests.post(REGISTER_FORM_URL, data=veriler)
                        
                        # --- HATA DETAYI GÖSTEREN KISIM ---
                        if r.status_code == 200:
                            st.success(f"Kaydın oldu {yeni_ad}! Yan taraftan giriş yap.")
                        else:
                            st.error(f"Kayıt Başarısız! HATA KODU: {r.status_code}")
                            st.write("Google Form diyor ki:", r.text) # Hatanın detayını yazar
                    except Exception as e:
                        st.error(f"İnternet hatası: {e}")

    st.stop() 

# --- 4. SOHBET EKRANI ---
kullanici = st.session_state.oturum
st.title(f"🌾 Hoşgeldin {kullanici}")

if st.sidebar.button("Çıkış Yap"):
    st.session_state.oturum = None
    st.rerun()

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
    requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: soru, ENTRY_CHAT_ROLE: "user"})
    
    try:
        cevap = model.generate_content(soru).text
        st.session_state.mesajlar.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant"): st.write(cevap)
        requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: cevap, ENTRY_CHAT_ROLE: "assistant"})
    except:
        st.error("Emmi cevap veremedi.")