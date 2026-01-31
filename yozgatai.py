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
    SPREADSHEET_ID = "1uhO7562rbctBNe4O-FDWzjUsZKf--FOGVvSg4ETqQWA"
    UYELER_GID = "809867134"    
    SOHBET_GID = "1043430012"   
    UYELER_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={UYELER_GID}"
    SOHBET_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SOHBET_GID}"
    KAYIT_FORM_VIEW = "https://docs.google.com/forms/d/e/1FAIpQLSfmWqswFyM7P7UGxkWnNzPjUZqNTcllt34lvudQZ9vM34LoKA/viewform"
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfzA0QcL_-RvuBf8sMauuawvrjgReFlYme4GlBlgfcLVP_hpw/formResponse"
    ENTRY_CHAT_USER = "entry.2029948747"
    ENTRY_CHAT_MSG  = "entry.1854177336"
    ENTRY_CHAT_ROLE = "entry.698806781"
except Exception as e:
    st.error(f"Ayarlar uçmuş: {e}"); st.stop()

st.set_page_config(page_title="YozgatAI", page_icon="🚀")
genai.configure(api_key=API_KEY)

def verileri_oku(url):
    try:
        taze_url = f"{url}&t={int(time.time())}"
        return pd.read_csv(taze_url, on_bad_lines='skip')
    except: return pd.DataFrame()

# ------------------------------------------------------------------
# 3. GİRİŞ SİSTEMİ
# ------------------------------------------------------------------
if "oturum" not in st.session_state: st.session_state.oturum = None

if st.session_state.oturum is None:
    st.title("🚀 Geleceğin Yapay Zekası: YozgatAI")
    tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])
    with tab1:
        giris_ad = st.text_input("Kullanıcı Adı")
        giris_sifre = st.text_input("Şifre", type="password")
        if st.button("Sisteme Gir"):
            df = verileri_oku(UYELER_CSV)
            if not df.empty:
                g_ad, g_sifre = str(giris_ad).strip().lower(), str(giris_sifre).strip().lower()
                basarili = False
                for _, row in df.iterrows():
                    for i in range(len(row) - 1):
                        if str(row.iloc[i]).strip().lower() == g_ad and str(row.iloc[i+1]).strip().lower() == g_sifre:
                            basarili = True; break
                    if basarili: break
                if basarili:
                    st.session_state.oturum = giris_ad
                    st.success("Giriş Tamam! 🚀"); time.sleep(1); st.rerun()
                else: st.error("Hatalı giriş!")
    with tab2: st.link_button("📝 Kayıt Formu", KAYIT_FORM_VIEW)
    st.stop()

# ------------------------------------------------------------------
# 4. SOHBET ODASI
# ------------------------------------------------------------------
st.title("🚀 Geleceğin Yapay Zekası: YozgatAI")

if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []
    df_sohbet = verileri_oku(SOHBET_CSV)
    if not df_sohbet.empty:
        try:
            c_user, c_msg, c_role = (1, 2, 3) if "zaman" in str(df_sohbet.columns[0]).lower() else (0, 1, 2)
            gecmis = df_sohbet[df_sohbet.iloc[:, c_user].astype(str) == st.session_state.oturum]
            for _, row in gecmis.iterrows():
                st.session_state.mesajlar.append({"role": row.iloc[c_role], "content": row.iloc[1]})
        except: pass

for m in st.session_state.mesajlar:
    with st.chat_message(m["role"], avatar="🌾" if m["role"] == "assistant" else None): st.write(m["content"])

if soru := st.chat_input("Emmiye sor hele..."):
    st.session_state.mesajlar.append({"role": "user", "content": soru})
    with st.chat_message("user"): st.write(soru)
    
    # --- AI CEVAP ÜRETME (EN SAĞLAM VE YENİ YÖNTEM) ---
    try:
        # 1. Modeli doğrudan en güncel isimle çağırıyoruz
        # Not: requirements.txt dosyasında google-generativeai>=0.8.3 olmalı
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 2. Şiveli talimatı doğrudan prompt'a gömüyoruz
        prompt = f"Sen Yozgatlı, bilge ve samimi bir emmisin. Şiveli konuş. Soru: {soru}"
        
        # 3. Cevabı üret
        cevap_obj = model.generate_content(prompt)
        cevap = cevap_obj.text
        
        if cevap:
            st.session_state.mesajlar.append({"role": "assistant", "content": cevap})
            with st.chat_message("assistant", avatar="🌾"):
                st.write(cevap)
            
            # Formlara kaydetme işlemini de buraya ekle...
            try:
                requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: soru, ENTRY_CHAT_ROLE: "user"})
                requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: cevap, ENTRY_CHAT_ROLE: "assistant"})
            except: pass
            
    except Exception as e:
        # Eğer hala hata verirse, teknik detayı buraya yazdırıyoruz
        st.error(f"Gardaşım sistemde bir kertik var: {e}")
        st.info("İpucu: Eğer 'API_KEY_INVALID' diyorsa Secrets'ı, '404' diyorsa requirements.txt'yi kontrol et.")