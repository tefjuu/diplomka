import streamlit as st
from datetime import datetime, time

# --- 1. KONFIGURACE VÝZKUMU ---
DATUM_STARTU = datetime(2026, 1, 29) 
CAS_ODEMCENI = time(9, 0)

st.set_page_config(page_title="Výzkum: Dechová cvičení", layout="wide")

# HLAVNÍ NÁZEV
st.title("🧘 Výzkum: Vliv dechových cvičení")

# --- 2. CSS STYLY ---
st.markdown("""
    <style>
    .stButton > button {
        height: 120px;
        font-size: 20px !important;
        font-weight: bold;
        border-radius: 15px;
        transition: all 0.3s ease;
        margin-bottom: 10px;
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
    col1, col2 = st.columns(2) # Tady jsme vytvořili ty dva sloupce
    
    with col1:
        st.subheader("Nová registrace")
        reg_email = st.text_input("Váš e-mail:")
        st.info("""
        **Váš unikátní kód vytvoříte takto:**
        1. První 2 písmena jména (např. Tereza -> **TE**)
        2. Den narození - vždy dvě cifry (např. 2. dne -> **02**)
        3. Poslední 2 čísla mobilu (např. ...89)
        *Příklad kódu: **TE0289***
        """)
        if st.button("Registrovat se"):
            st.success("Registrace (simulovaná) proběhla. Nyní se přihlaste vpravo.")

    with col2:
        st.subheader("Přihlášení")
        st.write("Zadejte kód pro vstup do lekcí.")
        
        email = st.text_input("E-mail:", key="input_email")
        # Přihlašujeme se kódem, který student vytvořil
        kod_login = st.text_input("Váš unikátní kód (např. TE0289):", key="input_kod")
        
        if st.button("Vstoupit do aplikace"):
            if email and kod_login:
                st.session_state.prihlasen = True
                # Uložíme kód do jména, aby fungoval i Admin mód
                st.session_state.input_jmeno = kod_login.upper()
                st.success(f"Přihlášeno: {kod_login.upper()}")
            else:
                st.error("Prosím vyplňte e-mail i kód.")

# --- SEKCE LEKCE ---
with tab_lekce:
    if not st.session_state.get("prihlasen", False):
        st.warning("⚠️ Pro přístup k lekcím se prosím nejdříve přihlaste v záložce 'Přihlášení / Registrace'.")
    else:
        if 'vybrana_oblast' not in st.session_state:
            st.header("Vyberte si své zaměření")
            st.info("Vyberte oblast, na které chcete pracovat. Toto rozhodnutí je konečné.")
            
            if st.button("🚀 Zvládání stresu a zkoušková úzkost", use_container_width=True):
                st.session_state.vybrana_oblast = "Stres"
                st.rerun()
            if st.button("⏰ Time-management a prokrastinace", use_container_width=True):
                st.session_state.vybrana_oblast = "Time-management"
                st.rerun()
            if st.button("😴 Problémy se spánkem a regenerací", use_container_width=True):
                st.session_state.vybrana_oblast = "Spánek"
                st.rerun()
        
        else:
            oblast = st.session_state.vybrana_oblast
            st.subheader(f"Vaše cesta: {oblast}")
            
            max_dostupna = ziskej_dostupnou_lekci()
            # Pokud se přihlásíš jako ADMIN, uvidíš všechno
            if st.session_state.get("input_jmeno") == "ADMIN":
                max_dostupna = 7

            cols = st.columns(7)
            for i in range(1, 8):
                je_odemceno = i <= max_dostupna
                with cols[i-1]:
                    if st.button(f"{i}", key=f"btn_l{i}", use_container_width=True, disabled=not je_odemceno):
                        st.session_state.vybrana_lekce = i

            st.divider()

            vyber = st.session_state.get("vybrana_lekce", 1)
            st.subheader(f"Den {vyber}: Instrukce")

            if oblast == "Stres":
                st.write("Dnes se zaměříme na techniku 4-7-8 pro okamžité uklidnění...")
            elif oblast == "Time-management":
                st.write("Dnes využijeme dech k zostření pozornosti před studiem...")
            elif oblast == "Spánek":
                st.write("Před spaním vyzkoušejte toto uvolňující cvičení...")
