import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests

# ------------------------------------------------------------------
# 1. AYARLAR VE SABİTLER (Dükkanın Tapusu)
# ------------------------------------------------------------------
try:
    # Gemini Anahtarı (Secrets dosyasından gelir)
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    
    # 📌 SENİN VERDİĞİN SAĞLAM E-TABLO ID'Sİ
    SPREADSHEET_ID = "1uhO7562rbctBNe4O-FDWzjUsZKf--FOGVvSg4ETqQWA"
    
    # 📌 TABLO SEKME NUMARALARI (Senin verdiklerin)
    UYELER_GID = "809867134"    # Üye Listesi
    SOHBET_GID = "1043430012"   # Sohbet Geçmişi

    # 📌 LİNKLER (Google'dan veriyi çeken sihirli yollar)
    # Not: Tablonun "Bağlantıya sahip olan herkes: Görüntüleyen" olması şarttır!
    UYELER_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={UYELER_GID}"
    SOHBET_CSV = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SOHBET_GID}"

    # ------------------------------------------------------------------
    # 🚨 DİKKAT: AŞAĞIDAKİLERİ KENDİ FORMUNA GÖRE DOLDUR GARDAŞIM!
    # ------------------------------------------------------------------
    
    # 1. KAYIT FORMU (Kullanıcının üye olduğu form)
    # Linkin sonu 'viewform' ile bitmeli.
    KAYIT_FORM_VIEW = "https://docs.google.com/forms/d/e/SENIN_KAYIT_FORM_ID_BURAYA/viewform"
    
    # 2. SOHBET FORMU (Konuşmaların kaydedildiği form)
    # Linkin sonu 'formResponse' ile bitmeli.
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/SENIN_SOHBET_FORM_ID_BURAYA/formResponse"
    
    # Sohbet Formundaki Kutucuk Numaraları (Sağ tık > İncele ile buldukların)
    ENTRY_CHAT_USER = "entry.XXXXX"   # Kullanıcı Adı kutusu
    ENTRY_CHAT_MSG  = "entry.YYYYY"   # Mesaj (Paragraf) kutusu
    ENTRY_CHAT_ROLE = "entry.ZZZZZ"   # Rol (User/Assistant) kutusu

except Exception as e:
    st.error(f"Ayarlarda bir kertik var kurban olduğum: {e}")
    st.stop()

# Gemini ve Sayfa Ayarları
genai.configure(api_key=API_KEY)
st.set_page_config(page_title="YozgatAI", page_icon="🌾")

# ------------------------------------------------------------------
# 2. YARDIMCI FONKSİYONLAR (Çıraklar)
# ------------------------------------------------------------------
def verileri_oku(url):
    """Google E-Tablo'dan CSV okur, hata verirse boş döner."""
    try:
        df = pd.read_csv(url, on_bad_lines='skip')
        # Sütun isimlerini küçük harfe çevirip boşlukları temizleyelim
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except Exception as e:
        return pd.DataFrame()

# ------------------------------------------------------------------
# 3. GİRİŞ EKRANI (Dükkan Kapısı)
# ------------------------------------------------------------------
if "oturum" not in st.session_state:
    st.session_state.oturum = None

if st.session_state.oturum is None:
    st.title("🛡️ YozgatAI: Giriş Kapısı")
    st.markdown("*Hoş geldin gardaşım. İçeri girmek için kimliğini göster.*")
    
    tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])

    # --- SEKME 1: GİRİŞ ---
    with tab1:
        giris_ad = st.text_input("Kullanıcı Adı", key="giris_ad")
        giris_sifre = st.text_input("Şifre", type="password", key="giris_sifre")
        
        if st.button("Dükkana Gir"):
            with st.spinner("Deftere bakılıyor..."):
                df = verileri_oku(UYELER_CSV)
                
            if not df.empty:
                try:
                    # Sütunları akıllıca bul (İsimler biraz farklı olsa bile anlar)
                    col_user = [c for c in df.columns if "kullanıcı" in c or "user" in c or "ad" in c][0]
                    col_pass = [c for c in df.columns if "şifre" in c or "sifre" in c or "pass" in c][0]
                    
                    # Kontrol et
                    kisi = df[
                        (df[col_user].astype(str) == giris_ad) & 
                        (df[col_pass].astype(str) == giris_sifre)
                    ]
                    
                    if not kisi.empty:
                        st.success("Giriş Başarılı! Çaylar söyleniyor...")
                        st.session_state.oturum = giris_ad
                        st.rerun()
                    else:
                        st.error("Gardaşım adın veya şifren yanlış. Malamat olma, doğru yaz.")
                except IndexError:
                    st.error("Tablo başlıkları yadırgandı. Tabloda 'Kullanıcı' ve 'Şifre' yazdığından emin ol.")
            else:
                st.error("Üye defteri okunamadı. Tabloyu 'Paylaş: Herkes' yaptın mı?")

    # --- SEKME 2: KAYIT (Yönlendirme ile %100 Çözüm) ---
    with tab2:
        st.info("⚠️ Google robotlara gıcıklık yapıyor. O yüzden kaydı yan dükkanda yapıp geliyoruz.")
        st.link_button("👉 Kayıt Formunu Aç (Tıkla)", KAYIT_FORM_VIEW)
        st.caption("Kaydını yaptıktan sonra 'Giriş Yap' sekmesine dönüp girebilirsin.")

    st.stop()

# ------------------------------------------------------------------
# 4. SOHBET EKRANI (Dükkanın İçi)
# ------------------------------------------------------------------
kullanici = st.session_state.oturum

# Yan menü (Çıkış butonu)
with st.sidebar:
    st.title(f"👤 {kullanici}")
    st.write("Hoş geldin emmi oğlu.")
    if st.button("Çıkış Yap"):
        st.session_state.oturum = None
        st.rerun()

st.title("🌾 YozgatAI Sohbet Odası")

# --- GEÇMİŞİ YÜKLE ---
if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []
    with st.spinner("Eski muhabbetler yükleniyor..."):
        df_sohbet = verileri_oku(SOHBET_CSV)
        if not df_sohbet.empty:
            try:
                # Sütunları bul
                c_user = [c for c in df_sohbet.columns if "kullanıcı" in c or "user" in c][0]
                c_msg  = [c for c in df_sohbet.columns if "mesaj" in c or "message" in c][0]
                c_role = [c for c in df_sohbet.columns if "rol" in c or "role" in c][0]
                
                # Sadece bu kullanıcının mesajlarını al
                gecmis = df_sohbet[df_sohbet[c_user].astype(str) == kullanici]
                
                # Listeye ekle
                for _, row in gecmis.iterrows():
                    st.session_state.mesajlar.append({
                        "role": row[c_role], 
                        "content": row[c_msg]
                    })
            except:
                pass # Hata olursa geçmiş boş gelir, dert değil

# --- MESAJLARI GÖSTER ---
for m in st.session_state.mesajlar:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# --- YENİ MESAJ GÖNDERME ---
model = genai.GenerativeModel(
    'models/gemini-1.5-flash', 
    system_instruction="Sen Yozgatlı samimi, bilge bir emmisin. Şiveli konuş. 'Nörüyon', 'Gardaşım', 'Malamat', 'Sumsuk' gibi kelimeler kullan."
)

if soru := st.chat_input("Bir şey de hele..."):
    # 1. Kullanıcı mesajını ekrana bas
    st.session_state.mesajlar.append({"role": "user", "content": soru})
    with st.chat_message("user"):
        st.write(soru)
    
    # 2. Kullanıcı mesajını forma kaydet (Arka plan)
    try:
        requests.post(CHAT_FORM_URL, data={
            ENTRY_CHAT_USER: kullanici,
            ENTRY_CHAT_MSG: soru,
            ENTRY_CHAT_ROLE: "user"
        })
    except: pass # Kayıt hatası sohbeti bölmesin

    # 3. Gemini Cevap Versin
    try:
        cevap_obj = model.generate_content(soru)
        cevap = cevap_obj.text
        
        # 4. Cevabı ekrana bas
        st.session_state.mesajlar.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant"):
            st.write(cevap)
            
        # 5. Cevabı forma kaydet (Arka plan)
        requests.post(CHAT_FORM_URL, data={
            ENTRY_CHAT_USER: kullanici,
            ENTRY_CHAT_MSG: cevap,
            ENTRY_CHAT_ROLE: "assistant"
        })
        
    except Exception as e:
        st.error("Emmi biraz dalgın, cevap veremedi.")