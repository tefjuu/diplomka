import streamlit as st
from google import genai

st.set_page_config(page_title="Gemini test", layout="centered")

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"],
    http_options={'api_version': 'v1'} # Přidání této verze vynutí správnou cestu
)

st.title("Test Gemini napojenia")

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Napíš niečo..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        reply = response.text
        
        with st.chat_message("assistant"):
            st.markdown(reply)
        st.session_state.history.append({"role": "assistant", "content": reply})

    except Exception as e:
        # Tady to vypíše tu skutečnou chybu, kterou Google posílá
        st.error(f"Aha, nastala chyba: {e}")
        # Pro debugování v logách Streamlitu
        print(f"DEBUG: {type(e)} - {e}")

    with st.chat_message("user"):
        st.markdown(prompt)

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
    )

    reply = response.text

    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.history.append({"role": "assistant", "content": reply})
