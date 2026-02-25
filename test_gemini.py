import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Gemini test", layout="centered")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("models/gemini-1.5-flash")

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

    response = model.generate_content(prompt)

    reply = response.text

    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.history.append({"role": "assistant", "content": reply})
