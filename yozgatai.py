import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import time

# ------------------------------------------------------------------
# 1. AYARLAR VE ANAHTARLAR
# ------------------------------------------------------------------
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    
    # SENİN TABLO VE FORM BİLGİLERİN
    SPREADSHEET_ID = "1uhO7562rbctBNe4O-FDWzjUsZKf--FOGVvSg4ETqQWA"
    UYELER_GID = "809867134"    
    SOHBET_GID = "1043430012"   

    # LİNKLER
    UYELER_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={UYELER_GID}"
    SOHBET_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SOHBET_GID}"

    # FORMLAR
    KAYIT_FORM_VIEW = "https://docs.google.com/forms/d/e/1FAIpQLSfmWqswFyM7P7UGxkWnNzPjUZqNTcllt34lvudQZ9vM34LoKA/viewform"
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfzA0QcL_-RvuBf8sMauuawvrjgReFlYme4GlBlgfcLVP_hpw/formResponse"
    
    # ENTRY NUMARALARI
    ENTRY_CHAT_USER = "entry.2029948747"
    ENTRY_CHAT_MSG  = "entry.1854177336"
    ENTRY_CHAT_ROLE = "entry.698806781"

except Exception as e:
    st.error(f"Ayarlarda sıkıntı var kanki: {e}")
    st.stop()

# ------------------------------------------------------------------
# 2. SAYFA VE AI AYARLARI
# ------------------------------------------------------------------
st.set_page_config(page_title="YozgatAI", page_icon="🚀", layout="centered")
genai.configure(api_key=API_KEY)

# Verileri her zaman taze çeken fonksiyon
def verileri_oku(url):
    try:
        taze_url = f"{url}&t={int(time.time())}"
        return pd.read_csv(taze_url, on_bad_lines='skip')
    except:
        return pd.DataFrame()

# ------------------------------------------------------------------
# 3. GİRİŞ KAPISI (AKILLI TARAMA)
# ------------------------------------------------------------------
if "oturum" not in st.session_state:
    st.session_state.oturum = None

if st.session_state.oturum is None:
    st.title("🚀 Geleceğin Yapay Zekası: YozgatAI")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])

    with tab1:
        giris_ad = st.text_input("Kullanıcı Adı", placeholder="Adını yaz...")
        giris_sifre = st.text_input("Şifre", type="password", placeholder="Şifreni yaz...")
        
        if st.button("Sisteme Gir"):
            with st.spinner("Yozgat veritabanına bağlanılıyor..."):
                df = verileri_oku(UYELER_CSV)
            
            if not df.empty:
                g_ad = str(giris_ad).strip().lower()
                g_sifre = str(giris_sifre).strip().lower()
                basarili = False
                
                # Sütun kaymasına karşı akıllı tarama
                for index, row in df.iterrows():
                    for i in range(len(row) - 1):
                        try:
                            # Yan yana duran iki hücreyi kontrol et
                            h1 = str(row.iloc[i]).strip().lower()
                            h2 = str(row.iloc[i+1]).strip().lower()
                            if h1 == g_ad and h2 == g_sifre:
                                basarili = True
                                break
                        except: continue
                    if basarili: break
                
                if basarili:
                    st.session_state.oturum = giris_ad
                    st.success("Giriş Başarılı! Roket kalkıyor... 🚀")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Kanki adın veya şifren yanlış. Kayıt oldun mu?")
            else:
                st.error("Veri çekilemedi. Bağlantıyı kontrol et.")

    with tab2:
        st.info("Aramıza katılmak için formu doldur.")
        st.link_button("📝 Kayıt Formuna Git", KAYIT_FORM_VIEW)

    st.stop()

# ------------------------------------------------------------------
# 4. SOHBET ODASI
# ------------------------------------------------------------------
kullanici = st.session_state.oturum

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_%22G%22_logo.svg/768px-Google_%22G%22_logo.svg.png", width=50)
    st.title("👤 Profil")
    st.write(f"Aktif Pilot: **{kullanici}**")
    if st.button("Çıkış Yap"):
        st.session_state.oturum = None
        st.rerun()

st.title("🚀 Geleceğin Yapay Zekası: YozgatAI")
st.caption("Yozgat Şivesiyle Güçlendirilmiş Yapay Zeka Teknolojisi")

# Geçmiş Mesajları Yükle
if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []
    df_sohbet = verileri_oku(SOHBET_CSV)
    if not df_sohbet.empty:
        try:
            # Sütunları otomatik bul (Zaman damgası varsa kaydır)
            c_user, c_msg, c_role = 0, 1, 2
            cols = [str(c).lower() for c in df_sohbet.columns]
            if len(cols) > 0 and ("zaman" in cols[0] or "timestamp" in cols[0]):
                 c_user, c_msg, c_role = 1, 2, 3
            
            gecmis = df_sohbet[df_sohbet.iloc[:, c_user].astype(str) == kullanici]
            for _, row in gecmis.iterrows():
                st.session_state.mesajlar.append({"role": row.iloc[c_role], "content": row.iloc[c_msg]})
        except: pass

# Mesajları Göster
for m in st.session_state.mesajlar:
    icon = "🌾" if m["role"] == "assistant" else None
    with st.chat_message(m["role"], avatar=icon):
        st.write(m["content"])

# Yeni Mesaj Kutusu
if soru := st.chat_input("Emmiye bir şeyler sor..."):
    # 1. Kullanıcı Mesajını Ekle ve Göster
    st.session_state.mesajlar.append({"role": "user", "content": soru})
    with st.chat_message("user"):
        st.write(soru)
    
    # 2. Arka Planda Form'a Kaydet (User)
    try:
        requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: soru, ENTRY_CHAT_ROLE: "user"})
    except: pass

    # 3. AI Cevabı Üret
    try:
        # Requirements güncellendiği için bu model artık çalışacak!
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"Sen Yozgatlı, samimi, bilge ve şiveli konuşan bir emmisin. Adın YozgatAI. Kullanıcının şu sorusuna Yozgat şivesiyle cevap ver: {soru}"
        
        with st.spinner("Emmi düşünüyor..."):
            cevap_obj = model.generate_content(prompt)
            cevap = cevap_obj.text
        
        # 4. Cevabı Ekle ve Göster
        st.session_state.mesajlar.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant", avatar="🌾"):
            st.write(cevap)
            
        # 5. Arka Planda Form'a Kaydet (AI)
        requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: cevap, ENTRY_CHAT_ROLE: "assistant"})
        
    except Exception as e:
        st.error("⚠️ Bir hata oluştu kanki.")
        st.warning(f"Hata detayı: {e}")
        st.info("Eğer 404 hatası alıyorsan 'requirements.txt' dosyasını güncellememişsin demektir!")