import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import re

# --- KASA VE BAĞLANTILAR ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    SHEET_URL = st.secrets["GSHEET_URL"]
    
    # 1. SOHBET DEFTERİ (Eski Form)
    CHAT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfAANTySmXphVhxNLT76RN-2n7MVjnX7WyNLJrH73qRZxPcrg/formResponse"
    ENTRY_CHAT_USER = "entry.1594572083"
    ENTRY_CHAT_MSG = "entry.1966407140"
    ENTRY_CHAT_ROLE = "entry.1321459799"

    # 2. NÜFUS MÜDÜRLÜĞÜ (Yeni Kayıt Formu)
    REGISTER_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdkyeYqKIeTIu3xEFd4X6YAVVrUPDeg5kekKfCaYhHwd0EYLw/formResponse"
    ENTRY_REG_USER = "entry.1024954161"
    ENTRY_REG_PASS = "entry.1526008229"

    # CSV Linkleri (Hem Sohbetler hem Uyeler sayfasını okumak için)
    # GID denilen sayfa numaralarını bulmak zordur, o yüzden biraz hile yapıp
    # Pandas ile tüm tabloyu okumaya çalışacağız.
    CSV_URL = SHEET_URL.split('/edit')[0] + '/export?format=csv'

except Exception as e:
    st.error(f"Ayarlarda bir kertik var kurban: {e}")
    st.stop()

genai.configure(api_key=API_KEY)
st.set_page_config(page_title="YozgatAI", page_icon="🌾")

# --- FONKSİYONLAR ---

# --- ÖNEMLİ: Google Sheets'ten "Uyeler" sayfasını bulmak için GID lazım ---
# Ama GID bulmak zorsa, kullanıcıdan basit bir işlem isteyeceğiz:
# Google Sheet linkinde 'gid=12345' diye yazar. 
# Eğer bulamazsan, buradaki mantığı 'Sadece Kayıt Yapan Girebilir' şeklinde değiştireceğiz.

def uyeleri_getir():
    # Bu kısım biraz 'deneme-yanılma' ile çalışır çünkü 2. sayfayı CSV olarak çekmek zordur.
    # EN GARANTİ YOL: Kayıt olurken şifreyi hafızada tutmak değil,
    # Kullanıcıdan "gid" (Sayfa ID'si) istemektir.
    # AMA ŞİMDİLİK: Basitlik için sadece ilk sayfayı (Sohbetleri) çekebiliyoruz.
    # Çözüm: "st-gsheets-connection" kütüphanesini kullanmak gerekirdi ama requirements'tan sildik.
    # O yüzden manuel bir çözüm: Kayıt olanın şifresini kontrol edemiyoruz çünkü Pandas sadece 1. sayfayı okur.
    
    # --- ÇÖZÜM: HACK ---
    # Madem Pandas ile 2. sayfayı okuyamıyoruz, o zaman 'Uyeler' sayfasını EN BAŞA (1. Sıraya) alırsan
    # Üyeleri okuruz ama bu sefer sohbetleri okuyamayız.
    
    # DOĞRU YOL:
    # Google Sheets linkinin sonuna '&gid={SAYFA_ID}' eklersek o sayfayı indirir.
    # Senin 'Uyeler' sayfanın GID numarasını bulman lazım.
    # Tabloda 'Uyeler' sekmesine tıkla, tarayıcıdaki linkte 'gid=...' yazar.
    # O numarayı bulamazsan, bu kod yine çalışmaz kurban.
    pass

# --- ALTERNATİF ÇÖZÜM: ST.SECRETS İLE GID GİRME ---
# Kurban, 2. sayfayı okumak için bana o sayfanın 'gid' numarasını vermen lazım.
# Tabloyu aç, 'Uyeler' sekmesine tıkla. Yukarıdaki link şöyle olacak:
# .../edit#gid=987654321
# İşte o '987654321' numarasını bana verirsen, şifre kontrolünü şak diye yaparım.

# ŞİMDİLİK GEÇİCİ ÇÖZÜM:
# Eğer bu GID işi zor gelirse, sana 'Login' işlemini simüle eden (yalandan yapan) kod değil,
# Gerçekten kontrol eden kodu yazmak için o GID numarasına muhtacım.

# --- SENİN İÇİN BASİTLEŞTİRİLMİŞ ÇÖZÜM (GID İSTEMEDEN) ---
# Tek sayfa kullanalım!
# Formu şöyle değiştirelim: Herkes 'Sohbetler' sayfasına kaydolur.
# Ama bu sefer tablo çok karışır.

# Gel en iyisi sana GID numarasını nasıl bulacağını göstereyim, kodu ona göre yazalım.
# Yoksa "Rastgele giren girer" sorununu çözemeyiz.

st.error("Kurban, 'Uyeler' sayfasındaki şifreleri okuyabilmem için o sayfanın kimlik numarası (GID) lazım.")
st.info("1. Google Tablo'nu aç.\n2. Alttan 'Uyeler' sekmesine tıkla.\n3. Tarayıcının adres çubuğundaki linke bak.\n4. Linkin sonunda `#gid=123456` gibi bir sayı göreceksin.\n5. O sayıyı kopyalayıp koddaki 'UYELER_GID' kısmına yapıştır.")