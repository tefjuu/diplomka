import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="OpenRouter streaming", layout="centered")

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
)

st.title("OpenRouter – streaming test")

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Napíš niečo…")

if prompt:
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_text = ""

        try:
            stream = client.chat.completions.create(
                model="arcee-ai/trinity-large-preview:free",
                messages=st.session_state.history,
                temperature=0.7,
                stream=True,
            )

            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    full_text += delta.content
                    placeholder.markdown(full_text)

            st.session_state.history.append({"role": "assistant", "content": full_text})

        except Exception as e:
            st.error(f"Chyba: {e}")
