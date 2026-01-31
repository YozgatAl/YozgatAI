import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import re

# --- 1. KASA VE BAĞLANTILAR (AYARLAR) ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    SHEET_URL = st.secrets["GSHEET_URL"]
    
    # SOHBET FORMU (Eski Form)
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfAANTySmXphVhxNLT76RN-2n7MVjnX7WyNLJrH73qRZxPcrg/formResponse"
    ENTRY_CHAT_USER = "entry.1594572083"
    ENTRY_CHAT_MSG = "entry.1966407140"
    ENTRY_CHAT_ROLE = "entry.1321459799"

    # KAYIT FORMU (Yeni Nüfus Formu)
    REGISTER_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdkyeYqKIeTIu3xEFd4X6YAVVrUPDeg5kekKfCaYhHwd0EYLw/formResponse"
    ENTRY_REG_USER = "entry.1024954161"
    ENTRY_REG_PASS = "entry.1526008229"

    # CSV Okuma Linkleri (Senin verdiğin GID numaralarıyla)
    # Sohbetler (Genelde ilk sayfa GID=0 olur)
    SOHBET_GID = "0"
    # Üyeler (Senin verdiğin numara)
    UYELER_GID = "1016867892"

    BASE_URL = SHEET_URL.split('/edit')[0]
    SOHBET_CSV = f"{BASE_URL}/export?format=csv&gid={SOHBET_GID}"
    UYELER_CSV = f"{BASE_URL}/export?format=csv&gid={UYELER_GID}"

except Exception as e:
    st.error(f"Kasa ayarlarında bir kertik var kurban: {e}")
    st.stop()

# --- 2. AYARLAR ---
genai.configure(api_key=API_KEY)
st.set_page_config(page_title="YozgatAI", page_icon="🌾")

# --- 3. FONKSİYONLAR (İŞÇİLER) ---

def verileri_oku(url):
    # Tabloyu internetten çekip okuyan fonksiyon
    try:
        return pd.read_csv(url, on_bad_lines='skip')
    except:
        return pd.DataFrame()

def kullanici_kontrol(isim):
    # İsim kuralları
    if len(isim) < 4:
        return False, "İsim en az 4 harf olacak kurban."
    if not re.match("^[a-zA-Z0-9]+$", isim):
        return False, "İsimde Türkçe harf, boşluk yok! Sadece İngilizce harf ve sayı."
    return True, ""

def sifre_kontrol(sifre):
    # Şifre kuralları
    if len(sifre) < 6:
        return False, "Şifre çok kısa, en az 6 hane olsun."
    if not re.search("[a-z]", sifre) or not re.search("[A-Z]", sifre) or not re.search("[0-9]", sifre):
        return False, "Şifrede en az bir BÜYÜK harf, bir küçük harf ve bir rakam olsun."
    return True, ""

# --- 4. GİRİŞ VE KAYIT EKRANI ---
if "oturum" not in st.session_state:
    st.title("🛡️ YozgatAI: Güvenlik Kapısı")
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])

    # --- SEKME 1: GİRİŞ ---
    with tab1:
        st.write("Hesabın varsa gir hele:")
        g_ad = st.text_input("Kullanıcı Adı", key="g_ad").strip()
        g_sifre = st.text_input("Şifre", type="password", key="g_sifre").strip()
        
        if st.button("Dükkana Gir"):
            if not g_ad or not g_sifre:
                st.warning("Adını şifreni yazmadan nereye?")
            else:
                # Üyeler tablosunu çek
                df = verileri_oku(UYELER_CSV)
                if not df.empty:
                    # Sütun isimlerini düzelt (küçük harf yap)
                    df.columns = [c.lower() for c in df.columns]
                    
                    # Kullanıcı ve Şifre sütunlarını bul
                    try:
                        k_col = [c for c in df.columns if 'kullanici' in c][0]
                        s_col = [c for c in df.columns if 'sifre' in c][0]
                        
                        # Kontrol Et
                        kisi = df[(df[k_col].astype(str) == g_ad) & (df[s_col].astype(str) == g_sifre)]
                        
                        if not kisi.empty:
                            st.success("Giriş başarılı! Yönlendiriliyorsun...")
                            st.session_state.oturum = g_ad
                            st.rerun()
                        else:
                            st.error("Adın ya da şifren yanlış kurban. Yadırgadım seni.")
                    except:
                        st.error("Tabloda sütun isimleri uyuşmuyor! (kullanici, sifre)")
                else:
                    st.error("Üye listesi boş veya okunamadı.")

    # --- SEKME 2: KAYIT ---
    with tab2:
        st.write("Yeni kimlik çıkartalım:")
        y_ad = st.text_input("İstediğin Kullanıcı Adı", key="y_ad").strip()
        y_sifre = st.text_input("Belirlediğin Şifre", type="password", key="y_sifre").strip()
        
        if st.button("Kaydı Tamamla"):
            # 1. Önce kurallara uyuyor mu?
            k_uygun, k_msg = kullanici_kontrol(y_ad)
            s_uygun, s_msg = sifre_kontrol(y_sifre)
            
            if not k_uygun:
                st.error(k_msg)
            elif not s_uygun:
                st.error(s_msg)
            else:
                # 2. İsim daha önce alınmış mı?
                df = verileri_oku(UYELER_CSV)
                alinmis = False
                if not df.empty:
                    # Basit kontrol (Tüm tabloyu metin olarak tara)
                    if y_ad in df.to_string():
                        alinmis = True
                
                if alinmis:
                    st.error("Bu isim kapılmış kurban, başka bul.")
                else:
                    # 3. Kaydı Form'a Gönder
                    try:
                        veriler = {ENTRY_REG_USER: y_ad, ENTRY_REG_PASS: y_sifre}
                        cevap = requests.post(REGISTER_FORM_URL, data=veriler)
                        
                        if cevap.status_code == 200:
                            st.success(f"Hayırlı olsun {y_ad}! Kaydın yapıldı. Şimdi 'Giriş Yap' sekmesinden girebilirsin.")
                        else:
                            st.error(f"Form kabul etmedi! Hata Kodu: {cevap.status_code}. Google Form ayarlarını kontrol et!")
                    except Exception as e:
                        st.error(f"İnternet koptu sanki: {e}")

    st.stop() # Giriş yapılmadıysa aşağıya geçme

# --- 5. SOHBET EKRANI (İÇERİSİ) ---
kullanici = st.session_state.oturum
st.title(f"🌾 Selamünaleyküm {kullanici}!")

# Yan Menü
with st.sidebar:
    st.write(f"👤 Ağa: **{kullanici}**")
    if st.button("Çıkış Yap"):
        st.session_state.oturum = None
        st.rerun()

# Geçmişi Getir ve Göster
if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []
    df = verileri_oku(SOHBET_CSV)
    
    if not df.empty:
        try:
            df.columns = [c.lower() for c in df.columns]
            k_col = [c for c in df.columns if 'kullanici' in c][0]
            m_col = [c for c in df.columns if 'mesaj' in c][0]
            r_col = [c for c in df.columns if 'rol' in c][0]
            
            # Sadece bu kullanıcının mesajlarını süz
            gecmis = df[df[k_col].astype(str).str.contains(kullanici, case=False, na=False)]
            
            for _, row in gecmis.iterrows():
                st.session_state.mesajlar.append({"role": row[r_col], "content": row[m_col]})
        except:
            pass

# Mesajları Ekrana Diz
for m in st.session_state.mesajlar:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# Emmi Cevap Veriyor
model = genai.GenerativeModel('models/gemini-flash-latest', system_instruction="Sen Yozgatlı samimi bir emmisin. Şiveli konuş.")

if soru := st.chat_input("Nörüyon..."):
    # 1. Senin mesajın
    st.session_state.mesajlar.append({"role": "user", "content": soru})
    with st.chat_message("user"):
        st.write(soru)
    # Forma kaydet
    requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: soru, ENTRY_CHAT_ROLE: "user"})
    
    # 2. Emminin cevabı
    try:
        cevap = model.generate_content(soru).text
        st.session_state.mesajlar.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant"):
            st.write(cevap)
        # Forma kaydet
        requests.post(CHAT_FORM_URL, data={ENTRY_CHAT_USER: kullanici, ENTRY_CHAT_MSG: cevap, ENTRY_CHAT_ROLE: "assistant"})
    except:
        st.error("Emmiye nazar değdi, cevap veremedi.")