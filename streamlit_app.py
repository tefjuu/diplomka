import streamlit as st

st.title("Výzkum: Dechová cvičení")

jmeno = st.text_input("Napište své jméno:")
if jmeno:
    st.write(f"Ahoj {jmeno}, vítej v dnešní lekci!")

if st.button("Lekce 1"):
    st.write("Tady začíná tvé dýchací cvičení...")
