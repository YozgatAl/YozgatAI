import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests

# --- KASA VE FORM AYARLARI ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    SHEET_URL = st.secrets["GSHEET_URL"]
    
    # Senin Form Numaraların (Bunları senin linkinden aldım kurban!)
    FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfAANTySmXphVhxNLT76RN-2n7MVjnX7WyNLJrH73qRZxPcrg/formResponse"
    ENTRY_USER = "entry.1594572083"
    ENTRY_MESSAGE = "entry.1966407140"
    ENTRY_ROLE = "entry.1321459799"

    # Tabloyu okuma linki
    CSV_URL = SHEET_URL.split('/edit')[0] + '/export?format=csv'
except:
    st.error("Kasa ayarlarında bir kertik var kurban!")
    st.stop()

genai.configure(api_key=API_KEY)

# --- VERİ YAZMA VE ÇEKME FONKSİYONLARI ---
def tabloya_yaz(kullanici, mesaj, rol):
    payload = {ENTRY_USER: kullanici, ENTRY_MESSAGE: mesaj, ENTRY_ROLE: rol}
    try:
        requests.post(FORM_URL, data=payload)
    except:
        pass # Yazamazsa da dükkanı kapatmayalım

def gecmisi_getir(kullanici_adi):
    try:
        df = pd.read_csv(CSV_URL)
        # Sütun isimlerini senin tabloya göre kontrol et (Kullanıcı, Mesaj, Rol)
        # Formdan gelen sütun isimleri farklıysa burayı ona göre süzer
        kullanici_gecmisi = df[df.iloc[:, 1].astype(str).str.lower() == kullanici_adi.lower()]
        return kullanici_gecmisi
    except:
        return pd.DataFrame()

# --- GİRİŞ SİSTEMİ ---
if "oturum" not in st.session_state:
    st.title("🛡️ YozgatAI: VIP Oda")
    ad = st.text_input("Adın ne kurban?")
    if st.button("Dükkana Gir"):
        if ad:
            st.session_state.oturum = ad.strip().lower()
            st.rerun()
    st.stop()

# --- SOHBET EKRANI ---
kullanici = st.session_state.oturum
st.title(f"🚀 Hoşgeldin {kullanici.capitalize()}!")

if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []
    gecmis_df = gecmisi_getir(kullanici)
    if not gecmis_df.empty:
        for _, row in gecmis_df.iterrows():
            st.session_state.mesajlar.append({"role": row.iloc[3], "content": row.iloc[2]})

for m in st.session_state.mesajlar:
    with st.chat_message(m["role"]):
        st.write(m["content"])

model = genai.GenerativeModel('models/gemini-flash-latest', 
                              system_instruction="Sen Yozgatlı emmisin. Şiveli konuş.")

if soru := st.chat_input("Nörüyon..."):
    # 1. Kullanıcı mesajını kaydet ve göster
    st.session_state.mesajlar.append({"role": "user", "content": soru})
    with st.chat_message("user"):
        st.write(soru)
    tabloya_yaz(kullanici, soru, "user")
    
    # 2. Emmi cevap versin
    cevap = model.generate_content(soru).text
    st.session_state.mesajlar.append({"role": "assistant", "content": cevap})
    with st.chat_message("assistant"):
        st.write(cevap)
    tabloya_yaz(kullanici, cevap, "assistant")