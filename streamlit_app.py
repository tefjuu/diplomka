import streamlit as st

# 1. Nastavení stránky
st.set_page_config(page_title="Výzkum: Dechová cvičení", layout="wide")

# 2. Hlavní nadpis aplikace
st.title("🧘 Výzkum: Vliv dechových cvičení")

# 3. Vytvoření horního menu pomocí Tabs
tab_uvod, tab_souhlas, tab_dotaznik, tab_lekce = st.tabs([
    "🏠 Úvodní informace", 
    "📝 Informovaný souhlas", 
    "📊 Vstupní dotazník", 
    "📅 Denní lekce (1-7)"
])

# --- SEKCE 1: ÚVOD ---
with tab_uvod:
    st.header("Vítejte ve výzkumném programu")
    st.write("Tato aplikace slouží k realizaci praktické části mé diplomové práce.")

# --- SEKCE 2: SOUHLAS ---
with tab_souhlas:
    st.header("Informovaný souhlas")
    souhlas = st.checkbox("Souhlasím se zpracováním údajů.")
    if souhlas:
        st.success("Děkuji za váš souhlas!")

# --- SEKCE 3: DOTAZNÍK ---
with tab_dotaznik:
    st.header("Vstupní údaje")
    jmeno = st.text_input("Jméno / Přezdívka:")
    if st.button("Odeslat a uložit"):
        st.balloons()
        st.success(f"Děkuji, {jmeno}!")

# --- SEKCE 4: LEKCE ---
with tab_lekce:
    st.header("Program dechových cvičení")
    # Tady byla ta chyba - teď je to opravené:
    den = st.selectbox("Vyberte aktuální den:", [f"Den {i}" for i in range(1, 8)])
    
    st.divider()
    
    if den == "Den 1":
        st.subheader("Lekce 1: První kroky")
        st.write("Tady začíná tvé dýchací cvičení...")
    else:
        st.write(f"Obsah pro {den} připravujeme...")
