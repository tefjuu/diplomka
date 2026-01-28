import streamlit as st
from datetime import datetime, time

# --- KONFIGURACE VÝZKUMU ---
# Tady nastav datum, kdy tvůj výzkum OFICIÁLNĚ ZAČÍNÁ (rok, měsíc, den)
DATUM_STARTU = datetime(2026, 1, 29) 
CAS_ODEMCENI = time(9, 0) # Lekce se otevře vždy v 9:00 ráno

# 1. Nastavení stránky
st.set_page_config(page_title="Výzkum: Dechová cvičení", layout="wide")

st.title("🧘 Výzkum: Vliv dechových cvičení")

# 2. Hlavní horní menu
tab_uvod, tab_souhlas, tab_dotaznik, tab_lekce = st.tabs([
    "🏠 Úvodní informace", 
    "📝 Informovaný souhlas", 
    "📊 Vstupní dotazník", 
    "📅 Lekce"
])

# Pomocná funkce pro výpočet aktuálně dostupné lekce
def ziskej_dostupnou_lekci():
    ted = datetime.now()
    rozdil = ted - DATUM_STARTU
    pocet_dni = rozdil.days + 1 # Den 1 začíná v den startu
    
    # Pokud je dnes před 9:00 ráno, poslední lekce ještě není dostupná
    if ted.time() < CAS_ODEMCENI:
        pocet_dni -= 1
        
    return max(0, pocet_dni)

# --- SEKCE 1-3 (Zůstávají stejné) ---
with tab_uvod:
    st.header("Vítejte")
    st.write("Informace o diplomové práci...")

with tab_souhlas:
    st.header("Souhlas")
    st.checkbox("Souhlasím se zpracováním údajů")

with tab_dotaznik:
    st.header("Vstupní dotazník")
    st.text_input("Jméno:")

# --- SEKCE 4: LEKCE (Tvůj nový systém) ---
with tab_lekce:
    st.header("Denní program")
    
    max_dostupna = ziskej_dostupnou_lekci()
    
    # Vytvoření 7 sloupců pro tlačítka lekcí
    cols = st.columns(7)
    
    # Inicializace paměti pro vybranou lekci (pokud ještě nebyla vybrána)
    if 'vybrana_lekce' not in st.session_state:
        st.session_state.vybrana_lekce = 1 if max_dostupna > 0 else 0

    # Vykreslení tlačítek 1-7
    for i in range(1, 8):
        je_odemceno = i <= max_dostupna
        with cols[i-1]:
            # Tlačítko je šedé (disabled), pokud ještě není čas
            if st.button(f"Lekce {i}", use_container_width=True, disabled=not je_odemceno):
                st.session_state.vybrana_lekce = i

    st.divider()

    # Zobrazení obsahu vybrané lekce
    vyber = st.session_state.vybrana_lekce

    if vyber == 0:
        st.info(f"První lekce se odemkne {DATUM_STARTU.strftime('%d.%m.')} v {CAS_ODEMCENI.strftime('%H:%M')}.")
    elif vyber == 1:
        st.subheader("Lekce 1: První kroky")
        st.success("Tato lekce je nyní AKTIVNÍ")
        st.write("Tady začíná tvé dýchací cvičení...")
    elif vyber == 2:
        st.subheader("Lekce 2: Prohloubený dech")
        st.write("Obsah pro druhý den...")
    # ... doplníš si další dny podle potřeby
