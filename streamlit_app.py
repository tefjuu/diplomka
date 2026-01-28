import streamlit as st
from datetime import datetime, time

# --- 1. KONFIGURACE VÝZKUMU ---
DATUM_STARTU = datetime(2026, 1, 29) 
CAS_ODEMCENI = time(9, 0)

st.set_page_config(page_title="Výzkum: Dechová cvičení", layout="wide")

# --- 2. CSS STYLY (Pro Vilgain efekt a vzhled) ---
st.markdown("""
    <style>
    /* Styl pro velká výběrová tlačítka oblastí */
    .stButton > button {
        height: 150px;
        font-size: 22px !important;
        font-weight: bold;
        border-radius: 15px;
        transition: all 0.3s ease;
        margin-bottom: 15px;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        border-color: #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. POMOCNÉ FUNKCE ---
def ziskej_dostupnou_lekci():
    ted = datetime.now()
    rozdil = ted - DATUM_STARTU
    pocet_dni = rozdil.days + 1
    if ted.time() < CAS_ODEMCENI:
        pocet_dni -= 1
    return max(0, pocet_dni)

# --- 4. HLAVNÍ STRUKTURA (MENU) ---
tab_uvod, tab_dotaznik, tab_lekce = st.tabs([
    "🏠 Úvodní informace", 
    "📊 Přihlášení / Registrace", 
    "📅 Vaše lekce"
])

# --- SEKCE ÚVOD ---
with tab_uvod:
    st.header("Vítejte v programu")
    st.write("Tato aplikace je součástí výzkumu k diplomové práci.")

# --- SEKCE PŘIHLÁŠENÍ ---
with tab_dotaznik:
    with col1:
    st.subheader("Nová registrace")
    reg_email = st.text_input("Váš e-mail:")
    # Tady je ten vylepšený návod:
    st.info("""
    **Váš unikátní kód vytvoříte takto:**
    1. První 2 písmena jména (např. Tereza -> **TE**)
    2. Den narození - vždy dvě cifry (např. 2. dne -> **02**)
    3. Poslední 2 čísla mobilu (např. ...123489 -> **89**)
    *Váš kód by tedy byl: **TE0289***
    """)
    st.header("Přihlášení")
    st.write("Zadejte údaje, které jste použili při registraci.")
    
    email = st.text_input("E-mail:", key="input_email")
    jmeno = st.text_input("Jméno:", key="input_jmeno")
    
    if st.button("Vstoupit do aplikace"):
        if email and jmeno:
            st.session_state.prihlasen = True
            st.success(f"Přihlášeno: {jmeno}")
        else:
            st.error("Prosím vyplňte e-mail i jméno.")

# --- SEKCE LEKCE ---
with tab_lekce:
    # Kontrola, zda je uživatel přihlášen
    if not st.session_state.get("prihlasen", False):
        st.warning("⚠️ Pro přístup k lekcím se prosím nejdříve přihlaste v záložce 'Přihlášení / Registrace'.")
    else:
        # A. VÝBĚR OBLASTI (zobrazí se jen poprvé)
        if 'vybrana_oblast' not in st.session_state:
            st.header("Vyberte si své zaměření")
            st.info("Vyberte oblast, na které chcete pracovat. Toto rozhodnutí je pro tento výzkum konečné.")
            
            if st.button("🚀 Zvládání stresu a zkoušková úzkost", use_container_width=True):
                st.session_state.vybrana_oblast = "Stres"
                st.rerun()
            if st.button("⏰ Time-management a prokrastinace", use_container_width=True):
                st.session_state.vybrana_oblast = "Time-management"
                st.rerun()
            if st.button("😴 Problémy se spánkem a regenerací", use_container_width=True):
                st.session_state.vybrana_oblast = "Spánek"
                st.rerun()
        
        # B. ZOBRAZENÍ PROGRAMU (po výběru oblasti)
        else:
            oblast = st.session_state.vybrana_oblast
            st.subheader(f"Vaše cesta: {oblast}")
            
            # Výpočet progresu
            max_dostupna = ziskej_dostupnou_lekci()
            if st.session_state.get("input_jmeno") == "Admin":
                max_dostupna = 7

            # Lišta s lekcemi (tlačítka 1-7)
            cols = st.columns(7)
            for i in range(1, 8):
                je_odemceno = i <= max_dostupna
                with cols[i-1]:
                    if st.button(f"Lekce {i}", key=f"btn_l{i}", use_container_width=True, disabled=not je_odemceno):
                        st.session_state.vybrana_lekce = i

            st.divider()

            # Zobrazení konkrétního obsahu
            vyber = st.session_state.get("vybrana_lekce", 1)
            st.subheader(f"Den {vyber}: Instrukce")

            if oblast == "Stres":
                st.write("Dnes se zaměříme na techniku 4-7-8 pro okamžité uklidnění...")
            elif oblast == "Time-management":
                st.write("Dnes využijeme dech k zostření pozornosti před studiem...")
            elif oblast == "Spánek":
                st.write("Před spaním vyzkoušejte toto uvolňující cvičení...")
