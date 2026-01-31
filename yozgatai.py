import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import time

# ------------------------------------------------------------------
# 1. AYARLAR VE ANAHTARLAR (Dükkanın Temeli)
# ------------------------------------------------------------------
try:
    # Gemini Anahtarını Secrets'tan alıyoruz
    # (Secrets dosyasında GOOGLE_API_KEY olduğundan emin ol)
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    
    # 📌 E-TABLO VE SAYFA BİLGİLERİ (Senin verdiğin ID'ler)
    SPREADSHEET_ID = "1uhO7562rbctBNe4O-FDWzjUsZKf--FOGVvSg4ETqQWA"
    UYELER_GID = "809867134"    
    SOHBET_GID = "1043430012"   

    # 📌 VERİ OKUMA LİNKLERİ (CSV Export)
    UYELER_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={UYELER_GID}"
    SOHBET_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SOHBET_GID}"

    # 📌 FORM LİNKLERİ (Kayıt ve Sohbet Kaydı)
    KAYIT_FORM_VIEW = "https://docs.google.com/forms/d/e/1FAIpQLSfmWqswFyM7P7UGxkWnNzPjUZqNTcllt34lvudQZ9vM34LoKA/viewform"
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfzA0QcL_-RvuBf8sMauuawvrjgReFlYme4GlBlgfcLVP_hpw/formResponse"
    
    # 📌 GİZLİ ENTRY NUMARALARI (Sohbeti kaydetmek için)
    ENTRY_CHAT_USER = "entry.2029948747"
    ENTRY_CHAT_MSG  = "entry.1854177336"
    ENTRY_CHAT_ROLE = "entry.698806781"

except Exception as e:
    st.error(f"Ayarlarda bir sıkıntı var gardaşım: {e}")
    st.stop()

# ------------------------------------------------------------------
# 2. SAYFA VE YAPAY ZEKA AYARLARI
# ------------------------------------------------------------------
st.set_page_config(page_title="YozgatAI", page_icon="🚀", layout="centered")
genai.configure(api_key=API_KEY)

# Verileri taze okuyan fonksiyon (Cache Buster)
def verileri_oku(url):
    try:
        # Sonuna zaman ekleyip Google'ı kandırıyoruz, hep taze veri geliyor
        taze_url = f"{url}&t={int(time.time())}"
        df = pd.read_csv(taze_url, on_bad_lines='skip')
        return df
    except Exception as e:
        return pd.DataFrame()

# ------------------------------------------------------------------
# 3. GİRİŞ KAPISI
# ------------------------------------------------------------------
if "oturum" not in st.session_state:
    st.session_state.oturum = None

if st.session_state.oturum is None:
    st.title("🚀 Geleceğin Yapay Zekası: YozgatAI")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])

    with tab1:
        st.subheader("Hoş Geldin Gardaşım")
        giris_ad = st.text_input("Kullanıcı Adı", placeholder="Adını yaz...")
        giris_sifre = st.text_input("Şifre", type="password", placeholder="Şifreni yaz...")
        
        if st.button("Sisteme Gir"):
            with st.spinner("Veriler Yozgat'tan çekiliyor..."):
                df = verileri_oku(UYELER_CSV)
            
            if not df.empty:
                # Temizleme ve Karşılaştırma (Büyük/Küçük harf derdi yok)
                g_ad = str(giris_ad).strip().lower()
                g_sifre = str(giris_sifre).strip().lower()
                
                basarili = False
                # Her satırı tek tek kontrol et
                for index, row in df.iterrows():
                    # İlk sütun ad, ikinci sütun şifre varsayıyoruz
                    try:
                        tablo_ad = str(row.iloc[0]).strip().lower()
                        tablo_sifre = str(row.iloc[1]).strip().lower()
                        
                        if tablo_ad == g_ad and tablo_sifre == g_sifre:
                            basarili = True
                            break
                    except: continue # Hatalı satır varsa atla
                
                if basarili:
                    st.session_state.oturum = giris_ad
                    st.success("Giriş Başarılı! Roket kalkıyor... 🚀")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Gardaşım adın veya şifren uyuşmadı.")
            else:
                st.error("Sunucuya ulaşılamadı. Tablo paylaşım ayarını kontrol et.")

    with tab2:
        st.info("Aşağıdaki butona basarak YozgatAI ailesine katıl.")
        st.link_button("📝 Kayıt Formuna Git", KAYIT_FORM_VIEW)

    st.stop()

# ------------------------------------------------------------------
# 4. SOHBET ODASI (Ana Ekran)
# ------------------------------------------------------------------
kullanici = st.session_state.oturum

# Yan Menü
with st.sidebar:
    st.title("👤 Profil")
    st.write(f"Aktif Kullanıcı: **{kullanici}**")
    if st.button("Çıkış Yap"):
        st.session_state.oturum = None
        st.rerun()

# --- ANA BAŞLIK ---
st.title("🚀 Geleceğin Yapay Zekası: YozgatAI")
st.caption("Yozgat Şivesiyle Güçlendirilmiş Yapay Zeka Teknolojisi")

# GEÇMİŞ MESAJLARI YÜKLE
if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []
    df_sohbet = verileri_oku(SOHBET_CSV)
    if not df_sohbet.empty:
        try:
            # Sadece bu kullanıcının mesajlarını getir
            # Sütun 0: Kullanıcı, Sütun 1: Mesaj, Sütun 2: Rol (Form sırasına göre)
            gecmis = df_sohbet[df_sohbet.iloc[:, 0].astype(str) == kullanici]
            for _, row in gecmis.iterrows():
                st.session_state.mesajlar.append({"role": row.iloc[2], "content": row.iloc[1]})
        except: pass

# MESAJLARI EKRANA BAS
for m in st.session_state.mesajlar:
    role_icon = "user" if m["role"] == "user" else "assistant"
    # Eğer asistan ise özel ikon veya emoji kullanabiliriz
    if m["role"] == "assistant":
        with st.chat_message("assistant", avatar="🌾"):
            st.write(m["content"])
    else:
        with st.chat_message("user"):
            st.write(m["content"])

# YENİ MESAJ GÖNDERME VE YAPAY ZEKA CEVABI
if soru := st.chat_input("Emmiye bir şeyler sor..."):
    # 1. Kullanıcı Mesajını Ekle
    st.session_state.mesajlar.append({"role": "user", "content": soru})
    with st.chat_message("user"):
        st.write(soru)
    
    # 2. Form'a Kaydet (Kullanıcı)
    try:
        requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: soru, ENTRY_CHAT_ROLE: "user"})
    except: pass # Kayıt hatası akışı bozmasın

    # 3. Emmi (AI) Cevap Versin
    try:
        # Modeli her seferinde taze çağıralım ki hata vermesin
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Emmi karakterini doğrudan prompt'un içine gömüyoruz (Daha sağlam)
        prompt = f"Sen Yozgatlı, samimi, bilge ve şiveli konuşan bir emmisin. Adın YozgatAI. Kullanıcının şu sorusuna Yozgat şivesiyle cevap ver: {soru}"
        
        cevap_obj = model.generate_content(prompt)
        cevap = cevap_obj.text
        
        st.session_state.mesajlar.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant", avatar="🌾"):
            st.write(cevap)
            
        # 4. Form'a Kaydet (AI)
        requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: cevap, ENTRY_CHAT_ROLE: "assistant"})
        
    except Exception as e:
        st.error("⚠️ Bir hata oluştu gardaşım.")
        st.error(f"Hata Detayı: {e}") 
        st.info("Eğer 'API Key' hatası görüyorsan, GitHub secrets ayarlarını kontrol et.")