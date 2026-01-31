import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import time

# ------------------------------------------------------------------
# 1. AYARLAR
# ------------------------------------------------------------------
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    
    # TABLO BİLGİLERİ
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
    st.error(f"Ayar hatası: {e}")
    st.stop()

st.set_page_config(page_title="YozgatAI", page_icon="🚀", layout="centered")
genai.configure(api_key=API_KEY)

# ------------------------------------------------------------------
# 2. VERİ OKUMA VE GİRİŞ MANTIĞI
# ------------------------------------------------------------------
def verileri_oku(url):
    try:
        taze_url = f"{url}&t={int(time.time())}"
        df = pd.read_csv(taze_url, on_bad_lines='skip')
        return df
    except:
        return pd.DataFrame()

# ------------------------------------------------------------------
# 3. GİRİŞ KAPISI
# ------------------------------------------------------------------
if "oturum" not in st.session_state:
    st.session_state.oturum = None

if st.session_state.oturum is None:
    st.title("🚀 Geleceğin Yapay Zekası: YozgatAI")
    
    tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])

    with tab1:
        st.info("Kullanıcı adını ve şifreni küçük-büyük harf fark etmeksizin yazabilirsin.")
        giris_ad = st.text_input("Kullanıcı Adı")
        giris_sifre = st.text_input("Şifre", type="password")
        
        if st.button("Sisteme Gir"):
            df = verileri_oku(UYELER_CSV)
            
            if not df.empty:
                # Girdileri temizle
                g_ad = str(giris_ad).strip().lower()
                g_sifre = str(giris_sifre).strip().lower()
                
                basarili = False
                
                # 🕵️‍♂️ AKILLI TARAMA SİSTEMİ
                # Sütun sırası kaymış olsa bile (Zaman damgası yüzünden),
                # yan yana duran (Ad + Şifre) ikilisini bulur.
                for index, row in df.iterrows():
                    # Satırdaki tüm hücreleri gez
                    for i in range(len(row) - 1):
                        try:
                            # Yan yana iki hücreyi al
                            hucre1 = str(row.iloc[i]).strip().lower()
                            hucre2 = str(row.iloc[i+1]).strip().lower()
                            
                            # Eğer bu ikili bizim girişle eşleşiyorsa tamamdır!
                            if hucre1 == g_ad and hucre2 == g_sifre:
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
                    # Hata ayıklama için ipucu (Kullanıcıya tablo başlıklarını göster)
                    st.error("Gardaşım eşleşme olmadı.")
                    st.warning(f"Sistem şu sütunları okudu: {list(df.columns)}")
                    st.caption("Eğer burada 'Zaman Damgası' görüyorsan sorun yok, ben onu hallettim. Adını/Şifreni kontrol et.")
            else:
                st.error("Liste boş veya okunamadı.")

    with tab2:
        st.link_button("📝 Kayıt Formuna Git", KAYIT_FORM_VIEW)

    st.stop()

# ------------------------------------------------------------------
# 4. SOHBET ODASI
# ------------------------------------------------------------------
kullanici = st.session_state.oturum

with st.sidebar:
    st.title(f"👤 {kullanici}")
    if st.button("Çıkış Yap"):
        st.session_state.oturum = None
        st.rerun()

st.title("🚀 Geleceğin Yapay Zekası: YozgatAI")

if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []
    df_sohbet = verileri_oku(SOHBET_CSV)
    if not df_sohbet.empty:
        try:
            # Sohbet tablosunda da zaman damgası olabilir, o yüzden
            # Kullanıcı adını ararken sütunları tarayalım
            c_user = -1
            c_msg = -1
            c_role = -1
            
            # Sütun isimlerinden yerlerini bulmaya çalış
            cols = [c.lower() for c in df_sohbet.columns]
            for i, col in enumerate(cols):
                if "kullanıcı" in col or "user" in col: c_user = i
                elif "mesaj" in col or "message" in col: c_msg = i
                elif "rol" in col or "role" in col: c_role = i
            
            # Bulamazsa varsayılan (Zaman damgası varsa kaydır)
            if c_user == -1: 
                # Zaman damgası varsa (1, 2, 3), yoksa (0, 1, 2)
                if "zaman" in cols[0] or "time" in cols[0]:
                    c_user, c_msg, c_role = 1, 2, 3
                else:
                    c_user, c_msg, c_role = 0, 1, 2

            gecmis = df_sohbet[df_sohbet.iloc[:, c_user].astype(str) == kullanici]
            for _, row in gecmis.iterrows():
                st.session_state.mesajlar.append({"role": row.iloc[c_role], "content": row.iloc[c_msg]})
        except: pass

for m in st.session_state.mesajlar:
    avatar = "🌾" if m["role"] == "assistant" else None
    with st.chat_message(m["role"], avatar=avatar):
        st.write(m["content"])

if soru := st.chat_input("Emmi burda, sor hele..."):
    st.session_state.mesajlar.append({"role": "user", "content": soru})
    with st.chat_message("user"): st.write(soru)
    
    try:
        requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: soru, ENTRY_CHAT_ROLE: "user"})
    except: pass

    try:
        # Sen 2. yolu seçtin (requirements güncelledin), o yüzden Flash motoru çalışır!
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Sen Yozgatlı, samimi, bilge ve şiveli konuşan bir emmisin. Adın YozgatAI. Kullanıcının şu sorusuna Yozgat şivesiyle cevap ver: {soru}"
        
        cevap_obj = model.generate_content(prompt)
        cevap = cevap_obj.text
        
        st.session_state.mesajlar.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant", avatar="🌾"):
            st.write(cevap)
            
        requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: cevap, ENTRY_CHAT_ROLE: "assistant"})
        
    except Exception as e:
        st.error("⚠️ Bir hata oluştu gardaşım.")
        st.write(e)