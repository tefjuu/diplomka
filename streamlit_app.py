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
            "from": {"email": st.secrets["MAILERSEND_SENDER"], "name": "Výzkum: Diplomová práce"},
            "to": [{"email": prijemce}],
            "subject": "Tvůj unikátní kód pro výzkum",
            "html": f"""
                <div style="font-family: sans-serif; line-height: 1.5; color: #333;">
                    <p>Dobrý den,</p>
                    <p>děkujeme za zapojení do výzkumu. Tvůj unikátní kód je: 
                    <b style="color: #4CAF50; font-size: 1.2em;">{kod}</b></p>
                    <p><a href="https://vyzkum-diplomka.streamlit.app/" 
                    style="display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">
                    VSTOUPIT DO APLIKACE</a></p>
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

# OPRAVA CHYBY Z OBRÁZKU: Přidána uzavírací závorka )
st.set_page_config(page_title="Výzkum: Dechová cvičení", layout="wide")
st.title("🧘 Výzkum: Podpůrné intervence na redukci stresu")

# --- 3. CSS STYLY (Zelené orámování a vzhled tlačítek) ---
st.markdown("""
    <style>
    /* Zelené orámování místo červeného při kliknutí */
    .stTextInput div[data-baseweb="input"]:focus-within {
        border-color: #4CAF50 !important;
        box-shadow: 0 0 0 1px #4CAF50 !important;
    }
    .stButton > button {
        height: 80px;
        font-size: 18px !important;
        font-weight: bold;
        border-radius: 15px;
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

# --- 5. TABS ---
tab_uvod, tab_dotaznik, tab_lekce = st.tabs(["🏠 Úvod", "📊 Přihlášení/Registrace", "📅 Lekce"])

with tab_uvod:
    st.header("Vítejte v programu")
    st.write("Tato webová aplikace je součástí výzkumu k diplomové práci.")

with tab_dotaznik:
    rezim = st.radio("Jste zde poprvé?", ["Chci se zaregistrovat", "Už mám svůj kód"], horizontal=True, key="main_rezim")
    st.divider()

    if rezim == "Chci se zaregistrovat":
        st.subheader("Nová registrace")
        
        # Ošetření připojení k tabulce
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = conn.read()
        except:
            df = pd.DataFrame(columns=["Email", "Kod"])

        col1, col2 = st.columns(2)
        with col1:
            reg_email = st.text_input("E-mail:", key="reg_email_field", placeholder="t.novakova@email.cz")
        with col2:
            reg_email_potvrzeni = st.text_input("E-mail znovu:", key="reg_email_confirm")
        # Okamžitá kontrola shody e-mailů
        if reg_email and reg_email_potvrzeni:
            if reg_email == reg_email_potvrzeni:
                st.success("✅ E-maily se shodují")
            else:
                st.error("❌ E-maily se neshodují")

        # TVŮJ NÁVOD NA KÓD
        st.markdown("""
        <div style="background-color: #f0f7f0; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50; margin: 10px 0;">
            <b>Váš unikátní kód si vytvořte takto:</b><br>
            1. První 2 písmena Vašeho křestního jména (např. Tereza -> <b>TE</b>)<br>
            2. Den Vašeho narození (vždy pište 2 cifry, např. datum narození 2. září -> <b>02</b>)<br>
            3. Poslední 2 cifry Vašeho tel. čísla (0911 564 742 -> <b>42</b>)<br>
            4. První 2 písmena jména Vaší matky(např. Julie -> <b>JU</b>)<br>
            <i>Výsledný kód: <b>TE0242JU</b></i>
        </div>
        """, unsafe_allow_html=True)
        
        # Vstup pro kód
        novy_kod = st.text_input("Vytvořte si svůj unikátní kód:", key="reg_kod_field", max_chars=8).upper().strip()

        # --- KONTROLA DÉLKY (8 ZNAKŮ) ---
        kod_je_spravne_dlouhy = False
        if novy_kod:
            delka = len(novy_kod)
            if delka != 8:
                st.error(f"❌ Kód musí mít přesně 8 znaků (aktuálně máte {delka}).")
            else:
                st.success("✅ Délka kódu je v pořádku.")
                kod_je_spravne_dlouhy = True

        # --- KONTROLA DUPLICITY V TABULCE ---
        stop_registrace = False
        if novy_kod and not df.empty:
            if novy_kod in df["Kod"].values:
                st.error("""
                    ⚠️ **Tento kód už je obsazený.** Zkuste jej prosím mírně upravit (např. místo 1. a 2. písmene jména použijte 1. a 3.). 
                    Kód vám po registraci pošleme e-mailem, takže si novou verzi nemusíte složitě pamatovat.
                """)
                stop_registrace = True
            elif reg_email in df["Email"].values:
                st.error("❌ Tento e-mail už je zaregistrován.")
                stop_registrace = True

        # TLAČÍTKO - přidána kontrola délky (kod_je_spravne_dlouhy)
        # TLAČÍTKO - Finální zpracování registrace
        if st.button("Dokončit registraci", key="final_reg_btn"):
            
            # 1. POKUS O NAČTENÍ DAT (Abychom mohli zkontrolovat duplicitu)
            try:
                # Používáme tvůj název List1
                df_aktualni = conn.read(worksheet="List1")
            except Exception as e:
                st.error(f"Chyba: Nepodařilo se načíst tabulku. Zkontrolujte název listu (má být List1). Detaily: {e}")
                df_aktualni = pd.DataFrame() # Nouzový prázdný dataframe

            # 2. PŘÍPRAVA KONTROL
            vse_ok = True
            email_cisty = reg_email.strip()
            kod_cisty = novy_kod.strip()

            # Kontrola prázdných polí
            if not email_cisty or not reg_email_potvrzeni or not kod_cisty:
                st.error("Vyplňte prosím všechna pole.")
                vse_ok = False
            
            # Kontrola shody e-mailů
            elif email_cisty != reg_email_potvrzeni.strip():
                st.error("Zadané e-maily se neshodují.")
                vse_ok = False

            # Kontrola duplicity (jen pokud se tabulka načetla)
            elif not df_aktualni.empty:
                if email_cisty in df_aktualni["Email"].values:
                    st.error("❌ Tento e-mail už je zaregistrován. Přejděte k přihlášení.")
                    vse_ok = False
                elif kod_cisty in df_aktualni["Code"].values:
                    st.error("⚠️ Tento kód už někdo používá. Upravte si jej.")
                    vse_ok = False

            # 3. ZÁPIS A ODESLÁNÍ (Proběhne jen když vse_ok zůstalo True)
            if vse_ok:
                import datetime
                registration_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                
                novy_radek = pd.DataFrame([{
                    "Email": email_cisty, 
                    "Code": kod_cisty,
                    "Registration_Date": registration_time,
                    "Topic": "Diplomka_Vyzkum",
                    "Last_Lesson": "N/A"
                }])
                
                try:
                    # NEJDŘÍV ZAPÍŠEME DO TABULKY (Pokud toto selže, e-mail se nepošle)
                    nova_data = pd.concat([df_aktualni, novy_radek], ignore_index=True)
                    conn.update(worksheet="List1", data=nova_data)
                    
                    # TEPRVE TEĎ ODEŠLEME EMAIL
                    status = odeslat_email(email_cisty, kod_cisty)
                    
                    if status in [200, 202]:
                        st.success("Registrace úspěšná! Kód byl odeslán na Váš e-mail.")
                        st.balloons()
                    else:
                        st.warning(f"Data uložena, ale e-mail se nepodařilo odeslat (kód: {status}). Poznamenejte si svůj kód.")
                
                except Exception as e:
                    st.error(f"Chyba při ukládání do tabulky: {e}. Registrace nebyla dokončena.")
    else:
        st.subheader("Přihlášení")
        login_kod = st.text_input("Zadejte kód:", key="login_field").upper()
        if st.button("Vstoupit", key="login_btn"):
            if login_kod:
                st.session_state.prihlasen = True
                st.session_state.moje_id = login_kod
                st.success("Vítejte!")
            else:
                st.error("Zadejte kód!")

with tab_lekce:
    if not st.session_state.get("prihlasen", False):
        st.warning("Přihlaste se prosím.")
    else:
        if 'vybrana_oblast' not in st.session_state:
            st.header("Vyberte si zaměření")
            if st.button("🚀 Stres a úzkost", key="btn_stres", use_container_width=True):
                st.session_state.vybrana_oblast = "Stres"
                st.rerun()
            if st.button("⏰ Time-management", key="btn_time", use_container_width=True):
                st.session_state.vybrana_oblast = "Time"
                st.rerun()
        else:
            st.subheader(f"Vaše cesta: {st.session_state.vybrana_oblast}")
            # ... zbytek lekcí (stejný jako dříve)
