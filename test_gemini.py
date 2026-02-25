import streamlit as st
from google import genai

st.set_page_config(page_title="Gemini test", layout="centered")

# 1. OPRAVA: Přidání api_version='v1' do klienta
client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"],
    http_options={'api_version': 'v1'}
)

st.title("Test Gemini napojenia")

if "history" not in st.session_state:
    st.session_state.history = []

# Zobrazení historie chatu
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Vstup od uživatele
if prompt := st.chat_input("Napíš niečo..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. OPRAVA: Sem vložíme ten try-except blok pro odchycení chyb
    try:
        # Volání modelu
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt,
        )
        
        reply = response.text

        # Zobrazení odpovědi asistenta
        with st.chat_message("assistant"):
            st.markdown(reply)
        
        st.session_state.history.append({"role": "assistant", "content": reply})

    except Exception as e:
        # Pokud se něco pokazí, uvidíte to přímo v aplikaci
        st.error(f"Aha, nastala chyba: {e}")
