import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time
from streamlit_gsheets import GSheetsConnection

# --- 1. FUNKCE PRO ODESÍLÁNÍ EMAILU ---
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
            "html": f"""
                <div style="font-family: sans-serif; line-height: 1.5; color: #333;">
                    <p>Dobrý den,</p>
                    <p>děkujeme za zapojení do výzkumu k diplomové práci. Tvůj unikátní kód pro přihlášení je: 
                    <b style="color: #4CAF50; font-size: 1.2em;">{kod}</b></p>
                    <p>Do aplikace s lekcemi se můžeš kdykoliv vrátit kliknutím na odkaz níže:</p>
                    <p><a href="https://vyzkum-diplomka.streamlit.app/" 
                    style="display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    VSTOUPIT DO APLIKACE</a></p>
                    <p>Doporučujeme si tento e-mail uložit.</p>
                </div>
            """
        }
        response = requests.post(url, json=data, headers=headers)
        return response.status_code
    except:
        return "Chyba"

# --- 2. KONFIGURACE VÝZKUMU ---
DATUM_STARTU = datetime(2026, 1, 29) 
CAS_ODEMCENI = time(9, 0)

# OPRAVA: Uzavřená závorka zde
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
        
        # CSS úprava pro zelené orámování políček (místo červeného)
        st.markdown("""
            <style>
            .stTextInput div[data-baseweb="input"]:focus-within {
                border-color: #4CAF50 !important;
                box-shadow: 0 0 0 1px #4CAF50 !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        conn = st.connection("gsheets", type=GSheetsConnection)
        try:
            df = conn.read()
        except:
            df = pd.DataFrame(columns=["Email", "Kod"])

        col1, col2 = st.columns(2)
        with col1:
            reg_email = st.text_input("Zadejte svůj e-mail:", key="email_1", placeholder="napr. t.novakova@email.cz")
        with col2:
            reg_email_potvrzeni = st.text_input("Zadejte e-mail znovu:", key="email_2")

        if reg_email and reg_email_potvrzeni:
            if reg_email == reg_email_potvrzeni:
                st.success("✅ E-maily se shodují")
            else:
                st.error("❌ E-maily se neshodují")

        # --- TVŮJ PŘESNÝ NÁVOD NA KÓD ---
        st.markdown("""
        <div style="background-color: #f0f7f0; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50;">
            <b>Váš unikátní kód si vytvořte takto:</b><br>
            1. První 2 písmena jména (Tereza -> <b>TE</b>)<br>
            2. Den narození (vždy 2 cifry, 2. den -> <b>02</b>)<br>
            3. Poslední 2 čísla mobilu (...89 -> <b>89</b>)<br>
            <i>Výsledek: <b>TE0289</b></i>
        </div>
        """, unsafe_allow_html=True)
        
        novy_kod = st.text_input("Vytvořte si svůj kód podle návodu výše:", key="reg_kod").upper()

        # Kontrola duplicity
        stop_registrace = False
        if novy_kod and not df.empty:
            if novy_kod in df["Kod"].values:
                st.error("❌ Tento kód je již použit – zkuste jej poupravit nebo kontaktujte vedoucího.")
                stop_registrace = True
            elif reg_email in df["Email"].values:
                st.error("❌ Tento e-mail je již zaregistrován.")
                stop_registrace = True

        if st.button("Dokončit registraci", key="btn_finalni_registrace"):
            if not reg_email or not reg_email_potvrzeni or not novy_kod:
                st.error("Vyplňte prosím všechna pole!")
            elif reg_email != reg_email_potvrzeni:
                st.error("Zadané e-maily se neshodují!")
            elif stop_registrace:
                st.error("Registrace není možná. Zkontrolujte prosím kód nebo e-mail.")
            else:
                status = odeslat_email(reg_email, novy_kod)
                if status in [200, 202]:
                    novy_radek = pd.DataFrame([{"Email": reg_email, "Kod": novy_kod}])
                    aktualizovana_data = pd.concat([df, novy_radek], ignore_index=True)
                    conn.update(data=aktualizovana_data)
                    st.success(f"Registrace úspěšná! Kód byl odeslán na {reg_email}.")
                    st.balloons()
                else:
                    st.error(f"E-mail se nepodařilo odeslat (Chyba {status}).")

        # Tlačítko pro registraci (OPRAVA ODSZENÍ A DUPLICITY)
        if st.button("Dokončit registraci", key="btn_finalni_registrace"):
            if not reg_email or not reg_email_potvrzeni or not novy_kod:
                st.error("Vyplňte prosím všechna pole!")
            elif reg_email != reg_email_potvrzeni:
                st.error("Zadané e-maily se neshodují!")
            elif stop_registrace:
                st.error("Registrace není možná. Tento kód nebo e-mail už v databázi existuje.")
            else:
                status = odeslat_email(reg_email, novy_kod)
                if status in [200, 202]:
                    # ZÁPIS DO TABULKY
                    novy_radek = pd.DataFrame([{"Email": reg_email, "Kod": novy_kod}])
                    aktualizovana_data = pd.concat([df, novy_radek], ignore_index=True)
                    conn.update(data=aktualizovana_data)
                    
                    st.success(f"Registrace úspěšná! Kód byl odeslán na {reg_email}.")
                    st.balloons()
                else:
                    st.error(f"E-mail se nepodařilo odeslat (Chyba {status}).")

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
            if st.button("🚀 Zvládání stresu a zkoušková úzkost", key="btn_stres", use_container_width=True):
                st.session_state.vybrana_oblast = "Stres"
                st.rerun()
            if st.button("⏰ Time-management a prokrastinace", key="btn_time", use_container_width=True):
                st.session_state.vybrana_oblast = "Time-management"
                st.rerun()
            if st.button("😴 Problémy se spánkem a regenerací", key="btn_spanek", use_container_width=True):
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
            vy
