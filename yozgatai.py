import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests

# ------------------------------------------------------------------
# 1. AYARLAR (Her Şey Yerli Yerinde)
# ------------------------------------------------------------------
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    
    # SENİN VERDİĞİN SAĞLAM E-TABLO ID'Sİ
    SPREADSHEET_ID = "1uhO7562rbctBNe4O-FDWzjUsZKf--FOGVvSg4ETqQWA"
    
    # GID NUMARALARI
    UYELER_GID = "809867134"    
    SOHBET_GID = "1043430012"   

    # VERİ OKUMA LİNKLERİ
    UYELER_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={UYELER_GID}"
    SOHBET_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SOHBET_GID}"

    # FORM LİNKLERİ (Senin verdiğin tertemiz linkler)
    KAYIT_FORM_VIEW = "https://docs.google.com/forms/d/e/1FAIpQLSfmWqswFyM7P7UGxkWnNzPjUZqNTcllt34lvudQZ9vM34LoKA/viewform"
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfzA0QcL_-RvuBf8sMauuawvrjgReFlYme4GlBlgfcLVP_hpw/formResponse"
    
    # AYIKLADIĞIM ENTRY NUMARALARI
    ENTRY_CHAT_USER = "entry.2029948747"
    ENTRY_CHAT_MSG  = "entry.1854177336"
    ENTRY_CHAT_ROLE = "entry.698806781"

except Exception as e:
    st.error(f"Ayarlarda bir hata var: {e}")
    st.stop()

genai.configure(api_key=API_KEY)
st.set_page_config(page_title="YozgatAI", page_icon="🌾")

# ------------------------------------------------------------------
# 2. OKUMA ÇIRAĞI
# ------------------------------------------------------------------
def verileri_oku(url):
    try:
        df = pd.read_csv(url, on_bad_lines='skip')
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# ------------------------------------------------------------------
# 3. GİRİŞ KAPISI
# ------------------------------------------------------------------
if "oturum" not in st.session_state:
    st.session_state.oturum = None

if st.session_state.oturum is None:
    st.title("🛡️ YozgatAI: Giriş Kapısı")
    tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])

    with tab1:
        st.subheader("Üye Girişi")
        giris_ad = st.text_input("Kullanıcı Adı", key="giris_ad")
        giris_sifre = st.text_input("Şifre", type="password", key="giris_sifre")
        
        if st.button("Dükkana Gir"):
            df = verileri_oku(UYELER_CSV)
            if not df.empty:
                try:
                    # Sütunları isme göre değil, sıraya göre bulalım (Hata payı sıfır olsun)
                    # 1. Sütun: Kullanıcı, 2. Sütun: Şifre varsayıyoruz.
                    kisi = df[(df.iloc[:, 0].astype(str) == giris_ad) & (df.iloc[:, 1].astype(str) == giris_sifre)]
                    
                    if not kisi.empty:
                        st.session_state.oturum = giris_ad
                        st.rerun()
                    else:
                        st.error("Adın veya şifren yanlış gardaşım.")
                except:
                    st.error("Tablo yapısı yadırgandı.")
            else:
                st.error("Defter okunamadı. Tabloyu 'Paylaş: Herkes' yaptığından emin ol!")

    with tab2:
        st.info("Kayıt olmak için aşağıdaki butona bas, formu doldur ve buraya dön.")
        st.link_button("👉 Kayıt Formunu Aç", KAYIT_FORM_VIEW)

    st.stop()

# ------------------------------------------------------------------
# 4. SOHBET ODASI
# ------------------------------------------------------------------
kullanici = st.session_state.oturum
st.title(f"🌾 Selamünaleyküm {kullanici}!")

with st.sidebar:
    if st.button("Çıkış Yap"):
        st.session_state.oturum = None
        st.rerun()

# GEÇMİŞİ YÜKLE
if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []
    df_sohbet = verileri_oku(SOHBET_CSV)
    if not df_sohbet.empty:
        try:
            # Sadece bu kullanıcının eski mesajlarını filtrele
            gecmis = df_sohbet[df_sohbet.iloc[:, 0].astype(str) == kullanici]
            for _, row in gecmis.iterrows():
                st.session_state.mesajlar.append({"role": row.iloc[2], "content": row.iloc[1]})
        except: pass

# EKRANA BAS
for m in st.session_state.mesajlar:
    with st.chat_message(m["role"]): st.write(m["content"])

model = genai.GenerativeModel('models/gemini-1.5-flash', system_instruction="Sen Yozgatlı samimi bir emmisin. Şiveli konuş.")

if soru := st.chat_input("Nörüyon..."):
    st.session_state.mesajlar.append({"role": "user", "content": soru})
    with st.chat_message("user"): st.write(soru)
    
    # Form'a Kayıt
    try:
        requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: soru, ENTRY_CHAT_ROLE: "user"})
    except: pass

    try:
        cevap = model.generate_content(soru).text
        st.session_state.mesajlar.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant"): st.write(cevap)
        
        # Cevabı Form'a Kayıt
        requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: cevap, ENTRY_CHAT_ROLE: "assistant"})
    except:
        st.error("Emmi cevap veremedi.")