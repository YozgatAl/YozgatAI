import streamlit as st
import google.generativeai as genai
import pandas as pd

# --- GÜVENLİK VE BAĞLANTI ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    SHEET_URL = st.secrets["GSHEET_URL"]
    
    if "/edit" in SHEET_URL:
        CSV_URL = SHEET_URL.split('/edit')[0] + '/export?format=csv'
    else:
        CSV_URL = SHEET_URL
except Exception as e:
    st.error("Aman kurban, Secrets ayarlarında bir kertik var!")
    st.stop()

genai.configure(api_key=API_KEY)

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="YozgatAI VIP", page_icon="🌾")

# --- VERİTABANINDAN GEÇMİŞİ ÇEKME ---
def gecmisi_getir(kullanici_adi):
    try:
        df = pd.read_csv(CSV_URL)
        kullanici_gecmisi = df[df['kullanici'].str.lower() == kullanici_adi.lower()]
        return kullanici_gecmisi
    except:
        return pd.DataFrame(columns=['kullanici', 'mesaj', 'rol', 'zaman'])

# --- GİRİŞ SİSTEMİ ---
if "kullanici" not in st.session_state:
    st.title("🛡️ YozgatAI: Giriş Kapısı")
    st.write("Dükkana girmek için ibdil (öncelikle) bir isim de hele kurban.")
    
    ad = st.text_input("Adın ne?")
    
    if st.button("Dükkana Gir"):
        if ad:
            st.session_state.kullanici = ad.strip()
            st.rerun()
        else:
            st.warning("Adını demezsen seni yadırgarım!")
    st.stop()

# --- SOHBET EKRANI ---
st.title(f"🚀 Selamünaleyküm {st.session_state.kullanici}!")
st.sidebar.header("Dükkan Menüsü")
st.sidebar.write(f"👤 Kullanıcı: {st.session_state.kullanici}")

if st.sidebar.button("Çıkış Yap"):
    st.session_state.clear()
    st.rerun()

sistem_komutu = "Sen Yozgatlı samimi bir emmisin. Şiveli konuş."
model = genai.GenerativeModel('models/gemini-flash-latest', system_instruction=sistem_komutu)

if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []
    gecmis_df = gecmisi_getir(st.session_state.kullanici)
    if not gecmis_df.empty:
        for _, row in gecmis_df.iterrows():
            st.session_state.mesajlar.append({"role": row['rol'], "content": row['mesaj']})

for m in st.session_state.mesajlar:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if soru := st.chat_input(f"Nörüyon {st.session_state.kullanici}, bir yumuş buyur..."):
    st.session_state.mesajlar.append({"role": "user", "content": soru})
    with st.chat_message("user"):
        st.write(soru)
    
    try:
        cevap_obj = model.generate_content(soru)
        cevap = cevap_obj.text
        st.session_state.mesajlar.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant"):
            st.write(cevap)
    except Exception as e:
        st.error(f"Bir kertik çıktı kurban: {e}")