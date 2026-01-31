import streamlit as st
import google.generativeai as genai

# --- GÜVENLİK AYARI ---
# Anahtarı direkt buraya yazmıyoruz, Streamlit'in gizli kasasından çekiyoruz
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Aman kurban, gizli anahtar (Secrets) bulunamadı!")
    st.stop()

genai.configure(api_key=API_KEY)

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="YozgatAI", page_icon="🌾")
st.title("🚀 YozgatAI: Bozkırın Dehası")

sistem_komutu = "Sen Yozgatlı samimi bir emmisin. Nörüyon, gubür gibi kelimeleri kullan."

# Senin listedeki en garanti model
model = genai.GenerativeModel('models/gemini-flash-latest', system_instruction=sistem_komutu)

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

for message in st.session_state.chat.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.write(message.parts[0].text)

if soru := st.chat_input("Nörüyon kurban, bir yumuş buyur..."):
    with st.chat_message("user"):
        st.write(soru)
    try:
        cevap = st.session_state.chat.send_message(soru)
        with st.chat_message("assistant"):
            st.write(cevap.text)
    except Exception as e:
        st.error(f"Bir kertik çıktı kurban: {e}")