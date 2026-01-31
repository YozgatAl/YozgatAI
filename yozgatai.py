try:
        # 🕵️‍♂️ MODEL ÇAĞIRMA OPERASYONU
        # Önce en yeni motoru (1.5-flash) deniyoruz
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Sen Yozgatlı, bilge ve şiveli konuşan bir emmisin. Adın YozgatAI. Şu soruya Yozgat şivesiyle cevap ver: {soru}"
            cevap_obj = model.generate_content(prompt)
            cevap = cevap_obj.text
        except:
            # Eğer Flash hata verirse, her devrin adamı olan Pro modeline geçiyoruz
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"Sen Yozgatlı, bilge ve şiveli konuşan bir emmisin. Adın YozgatAI. Şu soruya Yozgat şivesiyle cevap ver: {soru}"
            cevap_obj = model.generate_content(prompt)
            cevap = cevap_obj.text
        
        # Ekran ve Form Kaydı
        st.session_state.mesajlar.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant", avatar="🌾"):
            st.write(cevap)
            
        requests.post(CHAT_FORM_URL, data={
            ENTRY_CHAT_USER: st.session_state.oturum, 
            ENTRY_CHAT_MSG: cevap, 
            ENTRY_CHAT_ROLE: "assistant"
        })
        
    except Exception as e:
        # Eğer buraya düşerse API Key'de veya bağlantıda bir kertik var demektir
        st.error("⚠️ Emmi'nin dili tutuldu, teknik bir arıza var.")
        st.info(f"Hata detayı: {e}")