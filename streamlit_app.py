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

# --- SEKCE 4: LEKCE ---
with tab_lekce:
    # 1. Styly pro "Vilgain" karty (obrázky/tlačítka pod sebou)
    st.markdown("""
        <style>
        div.stButton > button {
            height: 150px;
            font-size: 24px !important;
            font-weight: bold;
            border-radius: 15px;
            border: 2px solid #e0e0e0;
            transition: all 0.3s ease;
            margin-bottom: 10px;
        }
        div.stButton > button:hover {
            transform: scale(1.02);
            border-color: #4CAF50;
            color: #4CAF50;
            background-color: #f0f9f0;
        }
        </style>
    """, unsafe_allow_html=True)

    # 2. Logika výběru oblasti (zobrazí se jen poprvé)
    if 'vybrana_oblast' not in st.session_state:
        st.header("Na co se chceš v programu zaměřit?")
        st.write("Vyber si jednu oblast, která tě nejvíce pálí:")

        # Tři velká tlačítka pod sebou
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
        # --- ZOBRAZENÍ LEKCÍ PO VÝBĚRU ---
        st.info(f"Tvé zaměření: **{st.session_state.vybrana_oblast}**")
        if st.button("🔄 Změnit zaměření"):
            del st.session_state.vybrana_oblast
            st.rerun()

        st.divider()

        # Tady zůstává tvá logika s odemykáním lekcí
        max_dostupna = ziskej_dostupnou_lekci()
        
        # Admin přístup
        if st.session_state.get("uzivatel_jmeno") == "Admin":
            max_dostupna = 7
        
        cols = st.columns(7)
        if 'vybrana_lekce' not in st.session_state:
            st.session_state.vybrana_lekce = 1 if max_dostupna > 0 else 0

        for i in range(1, 8):
            je_odemceno = i <= max_dostupna
            with cols[i-1]:
                if st.button(f"{i}", key=f"btn_lekce_{i}", use_container_width=True, disabled=not je_odemceno):
                    st.session_state.vybrana_lekce = i

        st.divider()

        # OBSAH LEKCÍ PODLE OBLASTI
        vyber = st.session_state.vybrana_lekce
        oblast = st.session_state.vybrana_oblast

        if vyber == 1:
            st.subheader(f"Lekce 1: První kroky ({oblast})")
            
            if oblast == "Stres":
                st.write("Dnes se zaměříme na uvolnění napětí v ramenou...")
            elif oblast == "Time-management":
                st.write("Dnes začneme krátkým cvičením na soustředění...")
            elif oblast == "Spánek":
                st.write("Dnes se naučíme, jak zklidnit mysl před spaním...")
