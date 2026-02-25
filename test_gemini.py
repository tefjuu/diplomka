import streamlit as st
from google import genai

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

st.title("Debug – dostupné modely")

try:
    models = list(client.models.list())
    for m in models:
        st.write(m.name)
except Exception as e:
    st.error(e)
