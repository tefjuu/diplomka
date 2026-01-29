import streamlit as st
import requests  # PŘIDÁNO: Nutné pro MailerSend
from datetime import datetime, time

# --- 1. FUNKCE PRO ODESÍLÁNÍ EMAILU (NOVÉ) ---
def odeslat_email(prijemce, kod):
    try:
        url = "https://api.mailersend.com/v1/email"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.secrets['MAILERSEND_API_KEY']}"
        }
        data = {
            "from": {
                "email": st.secrets["MAILERSEND_SENDER"], 
                "name": "Výzkum: Diplomová práce"
            },
            "to": [{"email": prijemce}],
            "subject": "Tvůj unikátní kód pro výzkum",
            "text": (
                f"Dobrý den,\n\n"
                f"děkujeme za zapojení do výzkumu k diplomové práci. Tvůj unikátní kód pro přihlášení je: {kod}\n\n"
                f"Do aplikace s lekcemi se můžeš kdykoliv vrátit kliknutím na tento odkaz:\n"
                f"https://vyzkum-diplomka.streamlit.app/\n\n"
                f"Doporučujeme si tento e-mail uložit pro budoucí přihlášení."
            ),
            "html": (
                f"<div style='font-family: sans-serif; line-height: 1.5; color: #333;'>"
                f"<p>Dobrý den,</p>"
                f"<p>děkujeme za zapojení do výzkumu k diplomové práci. Tvůj unikátní kód pro přihlášení je: "
                f"<span style='font-size: 1.2em; font-weight: bold; color: #4CAF50;'>{kod}</span></p>"
                f"<p>Do aplikace s lekcemi se můžeš kdykoliv vrátit kliknutím na odkaz níže:</p>"
                f"<p><a href='https://vyzkum-diplomka.streamlit.app/' "
                f"style='display: inline-block; padding: 10px 20px; background-color: #4CAF50
        response = requests.post(url, json=data, headers=headers)
        }
        return response.status_code
    except:
        return "Chyba"

# --- 2. KONFIGURACE VÝZKUMU ---
DATUM_STARTU = datetime(2026, 1, 29) 
CAS_ODEMCENI = time(9, 0)

st.set_page_config(page_title="Výzkum: Dechová cvičení", layout="wide")
st.title("🧘 Výzkum: Vliv dechových cvičení")

# --- 3. CSS STYLY ---
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

# --- 4. POMOCNÉ FUNKCE ---
def ziskej_dostupnou_lekci():
    ted = datetime.now()
    rozdil = ted - DATUM_STARTU
    pocet_dni = rozdil.days + 1
    if ted.time() < CAS_ODEMCENI:
        pocet_dni -= 1
    return max(0, pocet_dni)

# --- 5. HLAVNÍ STRUKTURA (MENU) ---
tab_uvod, tab_dotaznik, tab_lekce = st.tabs([
    "🏠 Úvodní informace", 
    "📊 Přihlášení / Registrace", 
    "📅 Vaše lekce"
])

with tab_uvod:
    st.header("Vítejte v programu")
    st.write("Tato aplikace je součástí výzkumu k diplomové práci.")

with tab_dotaznik:
    st.header("Vstup do programu")
    rezim = st.radio("Jste zde poprvé?", ["Chci se zaregistrovat", "Už mám svůj kód (Přihlášení)"], horizontal=True)
    st.divider()

    if rezim == "Chci se zaregistrovat":
        st.subheader("Nová registrace")
        reg_email = st.text_input("Zadejte svůj e-mail (pro zaslání kódu):")
        
        st.info("""
        **Váš unikátní kód si vytvořte takto:**
        1. První 2 písmena jména (Tereza -> **TE**)
        2. Den narození (vždy 2 cifry, 2. den -> **02**)
        3. Poslední 2 čísla mobilu (...89 -> **89**)
        """)
        
        novy_kod = st.text_input("Vytvořte si svůj kód (např. TE0289):", key="reg_kod").upper()
        
        if st.button("Dokončit registraci"):
            if reg_email and novy_kod:
                # --- OPRAVENÉ PROPOJENÍ NA MAIL ---
                status = odeslat_email(reg_email, novy_kod)
                if status in [200, 202]:
                    st.success(f"Registrace úspěšná! Na e-mail {reg_email} byl odeslán váš kód: {novy_kod}")
                    st.balloons()
                else:
                    st.error(f"E-mail se nepodařilo odeslat. (Chyba {status}). Máte správně Secrets?")
            else:
                st.error("Vyplňte prosím e-mail i kód!")

    else:
        st.subheader("Přihlášení")
        login_kod = st.text_input("Zadejte svůj unikátní kód:", key="login_kod").upper()
        if st.button("Vstoupit k lekcím"):
            if login_kod:
                st.session_state.prihlasen = True
                st.session_state.moje_id = login_kod
                st.success(f"Přihlášeno! Vítejte zpět.")
            else:
                st.error("Zadejte prosím kód.")

with tab_lekce:
    if not st.session_state.get("prihlasen", False):
        st.warning("⚠️ Pro přístup k lekcím se prosím nejdříve přihlaste.")
    else:
        if 'vybrana_oblast' not in st.session_state:
            st.header("Vyberte si své zaměření")
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
            if st.session_state.get("moje_id") == "ADMIN": max_dostupna = 7

            cols = st.columns(7)
            for i in range(1, 8):
                with cols[i-1]:
                    if st.button(f"{i}", key=f"btn_l{i}", use_container_width=True, disabled=not (i <= max_dostupna)):
                        st.session_state.vybrana_lekce = i

            st.divider()
            vyber = st.session_state.get("vybrana_lekce", 1)
            st.subheader(f"Den {vyber}: Instrukce")
            if oblast == "Stres": st.write("Technika 4-7-8...")
            elif oblast == "Time-management": st.write("Soustředění...")
            elif oblast == "Spánek": st.write("Uvolnění...")
