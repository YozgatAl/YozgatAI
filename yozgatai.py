import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import time

# ------------------------------------------------------------------
# 1. AYARLAR (Dükkanın Tapusu ve Form Anahtarları)
# ------------------------------------------------------------------
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    
    # SENİN VERDİĞİN SAĞLAM E-TABLO ID'Sİ
    SPREADSHEET_ID = "1uhO7562rbctBNe4O-FDWzjUsZKf--FOGVvSg4ETqQWA"
    
    # GID NUMARALARI
    UYELER_GID = "809867134"    
    SOHBET_GID = "1043430012"   

    # 🚀 GOOGLE'IN EN SAĞLAM VERİ ÇEKME YOLU (CSV EXPORT)
    UYELER_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={UYELER_GID}"
    SOHBET_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SOHBET_GID}"

    # FORM LİNKLERİ (Senin verdiğin linkler)
    KAYIT_FORM_VIEW = "https://docs.google.com/forms/d/e/1FAIpQLSfmWqswFyM7P7UGxkWnNzPjUZqNTcllt34lvudQZ9vM34LoKA/viewform"
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfzA0QcL_-RvuBf8sMauuawvrjgReFlYme4GlBlgfcLVP_hpw/formResponse"
    
    # AYIKLADIĞIM ENTRY NUMARALARI
    ENTRY_CHAT_USER = "entry.2029948747"
    ENTRY_CHAT_MSG  = "entry.1854177336"
    ENTRY_CHAT_ROLE = "entry.698806781"

except Exception as e:
    st.error(f"Ayarlarda bir hata var: {e}")
    st.stop()

# Gemini Ayarları
genai.configure(api_key=API_KEY)
st.set_page_config(page_title="YozgatAI", page_icon="🌾")

# ------------------------------------------------------------------
# 2. VERİ OKUMA ÇIRAĞI (Taze Veri Garantili)
# ------------------------------------------------------------------
def verileri_oku(url):
    try:
        # Google'ın eski veriyi (cache) vermemesi için sonuna zaman damgası ekliyoruz
        taze_url = f"{url}&t={int(time.time())}"
        df = pd.read_csv(taze_url, on_bad_lines='skip')
        return df
    except Exception as e:
        st.error(f"Tablo okuma hatası: {e}")
        return pd.DataFrame()

# ------------------------------------------------------------------
# 3. GİRİŞ VE KAYIT EKRANI
# ------------------------------------------------------------------
if "oturum" not in st.session_state:
    st.session_state.oturum = None

if st.session_state.oturum is None:
    st.title("🛡️ YozgatAI: Giriş Kapısı")
    tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])

    with tab1:
        st.subheader("Üye Girişi")
        giris_ad = st.text_input("Kullanıcı Adı", placeholder="Adını yaz...")
        giris_sifre = st.text_input("Şifre", type="password", placeholder="Şifreni yaz...")
        
        if st.button("Dükkana Gir"):
            with st.spinner("Deftere bakılıyor, bekle hele..."):
                df = verileri_oku(UYELER_CSV)
            
            if not df.empty:
                # Giriş bilgilerini temizleyelim
                deneme_ad = str(giris_ad).strip().lower()
                deneme_sifre = str(giris_sifre).strip().lower()
                
                # 🕵️‍♂️ AKILLI KONTROL: Tüm satırlara tek tek bak, büyük-küçük harf takılma
                basarili = False
                for index, row in df.iterrows():
                    # Zaman damgası yüzünden sütunlar kayabilir, o yüzden ilk 3 sütunu tara
                    for i in range(len(row) - 1):
                        tablo_ad = str(row.iloc[i]).strip().lower()
                        tablo_sifre = str(row.iloc[i+1]).strip().lower()
                        
                        if tablo_ad == deneme_ad and tablo_sifre == deneme_sifre:
                            basarili = True
                            break
                    if basarili: break
                
                if basarili:
                    st.session_state.oturum = giris_ad
                    st.success("Hah, şimdi oldu! Çaylar demlendi...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Adın veya şifren yanlış gardaşım. (Sistem '{deneme_ad}' aradı ama bulamadı)")
                    st.info(f"Defterde şu an {len(df)} kayıt var. Adını doğru yazdığından emin ol.")
            else:
                st.error("Üye defteri boş veya Google izin vermiyor. 'Paylaş: Herkes' yaptığından emin ol!")

    with tab2:
        st.info("⚠️ Önce buradan kayıt ol, sonra yan taraftan giriş yap.")
        st.link_button("📝 Kayıt Formuna Git", KAYIT_FORM_VIEW)

    st.stop()

# ------------------------------------------------------------------
# 4. SOHBET EKRANI (İçerisi)
# ------------------------------------------------------------------
kullanici = st.session_state.oturum

with st.sidebar:
    st.title(f"👤 {kullanici}")
    if st.button("Kapıyı Kapat (Çıkış)"):
        st.session_state.oturum = None
        st.rerun()

st.title("🌾 YozgatAI Sohbet Odası")

# GEÇMİŞİ YÜKLE
if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []
    df_sohbet = verileri_oku(SOHBET_CSV)
    if not df_sohbet.empty:
        try:
            # Kullanıcıya göre filtrele (Sütun: 0=Kullanıcı, 1=Mesaj, 2=Rol)
            gecmis = df_sohbet[df_sohbet.iloc[:, 0].astype(str) == kullanici]
            for _, row in gecmis.iterrows():
                st.session_state.mesajlar.append({"role": row.iloc[2], "content": row.iloc[1]})
        except: pass

# EKRANA BAS
for m in st.session_state.mesajlar:
    with st.chat_message(m["role"]): st.write(m["content"])

# YENİ MESAJ SİSTEMİ
model = genai.GenerativeModel('models/gemini-1.5-flash', 
                              system_instruction="Sen Yozgatlı samimi bir emmisin. Şiveli konuş. Nörüyon, kurban olduğum gibi laflar kullan.")

if soru := st.chat_input("Bir şey de hele..."):
    st.session_state.mesajlar.append({"role": "user", "content": soru})
    with st.chat_message("user"): st.write(soru)
    
    # Google Form'a Kaydet (Arka Plan)
    try:
        requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: soru, ENTRY_CHAT_ROLE: "user"})
    except: pass

    # Emmi Cevap Versin
    try:
        cevap = model.generate_content(soru).text
        st.session_state.mesajlar.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant"): st.write(cevap)
        
        # Cevabı Kaydet
        requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: cevap, ENTRY_CHAT_ROLE: "assistant"})
    except:
        st.error("Emmi dalmış gitmiş, cevap veremedi.")