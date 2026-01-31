import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import time

# Ayarlar
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except Exception as e:
    st.error("Secrets ayarı bozuk gardaşım."); st.stop()

st.set_page_config(page_title="YozgatAI", page_icon="🚀")
genai.configure(api_key=API_KEY)

st.title("🚀 YozgatAI: Arıza Tespit Ekranı")

# -----------------------------------------------------------
# 🕵️‍♂️ DEDEKTİF MODU: ANAHTARIN NELERİ GÖRÜYOR?
# -----------------------------------------------------------
st.subheader("🔍 Google Depo Kontrolü")
try:
    st.write("Google'a bağlanılıyor... Modeller listeleniyor...")
    
    # Tüm modelleri listeleyelim
    tum_modeller = []
    for m in genai.list_models():
        tum_modeller.append(m.name)
    
    if len(tum_modeller) > 0:
        st.success("✅ Bağlantı Başarılı! Senin anahtarın şu modelleri görüyor:")
        st.code(tum_modeller)
        
        # En uygun modeli seçip deneme yapalım
        secilen = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in tum_modeller else tum_modeller[0]
        st.info(f"Seçilen Model: {secilen} ile deneme yapılıyor...")
        
        model = genai.GenerativeModel(secilen)
        cevap = model.generate_content("Nörüyon? (Deneme Mesajı)").text
        st.write(f"🤖 **Emmi Cevap Verdi:** {cevap}")
        
    else:
        st.error("❌ LİSTE BOŞ! Anahtarın Google'a bağlandı ama HİÇBİR modeli görmüyor.")
        st.warning("Bu ne demek? Anahtarın 'Generative Language API' yetkisi kapalı. Yeni bir proje açman lazım.")

except Exception as e:
    st.error("🚨 HATA VAR GARDAŞIM!")
    st.error(f"Hata Mesajı: {e}")
    st.info("Kütüphane Sürümü: " + genai.__version__)
    st.markdown("""
    **ÇÖZÜM İÇİN ŞUNU YAP:**
    1. [Google AI Studio](https://aistudio.google.com/app/apikey) adresine git.
    2. Mevcut anahtarı sil.
    3. **'Create API key in new project'** butonuna bas.
    4. Yeni anahtarı GitHub Secrets'a yapıştır.
    """)