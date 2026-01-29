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
            "html": f"Dobrý den, tvůj kód je: <b>{kod}</b>"
        }
        response = requests.post(url, json=data, headers=headers)
        
        # Pokud status není OK, vypiš chybu přímo na obrazovku
        if response.status_code not in [200, 202]:
            st.error(f"❌ MailerSend Error: {response.status_code} - {response.text}")
            
        return response.status_code
    except Exception as e:
        # Pokud spadne samotný Python (např. chybí knihovna requests)
        st.error(f"🔥 Kritická chyba v kódu: {e}")
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
        # 1. KONTROLA STAVU (Zabrání opakovanému odesílání)
        if st.session_state.get("registrace_dokoncena", False):
            st.success("### 🎉 Registrace proběhla úspěšně!")
            st.info("Na Váš e-mail jsme poslali potvrzení. Nyní se prosím přepněte nahoře na **'Už mám svůj kód'** a přihlaste se.")
            st.balloons()
        
        else:
            st.subheader("Nová registrace")
            
            # Načtení dat (ošetřené proti chybám připojení)
            try:
                conn = st.connection("gsheets", type=GSheetsConnection)
                df_aktualni = conn.read(worksheet="List 1")
            except Exception:
                df_aktualni = pd.DataFrame(columns=["Email", "Code", "Registration_Date", "Topic", "Last_Lesson"])

            col1, col2 = st.columns(2)
            with col1:
                reg_email = st.text_input("E-mail:", key="reg_email_field", placeholder="t.novakova@email.cz").strip()
            with col2:
                reg_email_potvrzeni = st.text_input("E-mail znovu:", key="reg_email_confirm").strip()
            
            if reg_email and reg_email_potvrzeni:
                if reg_email == reg_email_potvrzeni:
                    st.success("✅ E-maily se shodují")
                else:
                    st.error("❌ E-maily se neshodují")
            
            # --- KOLONKY PRO HESLO (Vylepšená verze) ---
            col3, col4 = st.columns(2)
            with col3:
                reg_heslo = st.text_input("Vaše heslo:", type="password", key="reg_pass_field", placeholder="Minimálně 8 znaků").strip()
            with col4:
                reg_heslo_potvrzeni = st.text_input("Zopakujte heslo:", type="password", key="reg_pass_confirm").strip()
            
            # 1. Kontrola délky (reaguje hned na první políčko)
            if reg_heslo:
                if len(reg_heslo) < 8:
                    st.warning(f"⚠️ Heslo je příliš krátké (zatím {len(reg_heslo)}/8 znaků).")
                
                # 2. Kontrola shody (spustí se, až když je něco i v druhém políčku)
                if reg_heslo_potvrzeni:
                    if reg_heslo == reg_heslo_potvrzeni:
                        st.success("✅ Hesla se shodují")
                    else:
                        st.error("❌ Hesla se neshodují")
                else:
                    st.error("❌ Hesla se neshodují")
            # -------------------------------
            st.markdown("""
            <div style="background-color: #f0f7f0; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50; margin: 10px 0;">
                <b>Váš unikátní kód si vytvořte takto:</b><br>
                1. První 2 písmena Vašeho křestního jména (např. Tereza -> <b>TE</b>)<br>
                2. Den Vašeho narození (napiště dvouciferné číslo, např. 2. ledna -> <b>02</b>)<br> 
                3. Poslední 2 cifry Vašeho tel. čísla (např. 0911 546 741 -> <b>41</b>)<br>
                4. První 2 písmena jména Vaší matky (např. Julie -> <b>JU</b>)<br><br>
                <i>Vzorový kód: <b>TE0241JU</b></i>
            </div>
            """, unsafe_allow_html=True)
            
            novy_kod = st.text_input("Vytvořte si svůj unikátní kód:", key="reg_kod_field", max_chars=8).upper().strip()

            if novy_kod:
                pismena_zacatek = novy_kod[0:2]  # 1. a 2. znak
                cisla_stred = novy_kod[2:6]      # 3. až 6. znak
                pismena_konec = novy_kod[6:8]    # 7. a 8. znak
                
            if len(novy_kod) < 8:
                st.warning(f"⚠️ Kód je zatím krátký ({len(novy_kod)}/8 znaků).")
            elif not (pismena_zacatek.isalpha() and cisla_stred.isdigit() and pismena_konec.isalpha()):
                st.error("❌ Chybný formát kódu. Kód by musí obsahovat: 2 písmena, 4 čísla a 2 písmena (např. TE0241JU).")
            elif not df_aktualni.empty and novy_kod in df_aktualni["Code"].values:
                st.error("❌ Tento kód už někdo používá. V tomto případě změňte některý ze znaků, aby se kódy neshodovaly.")
            else:
                st.success("✅ Tento kód je v pořádku a ve správném formátu.")

            # TLAČÍTKO PRO REGISTRACI (Pouze jedno)
            if st.button("Dokončit registraci", key="final_reg_btn"):
                vse_ok = True
                
                if not reg_email or not novy_kod:
                    st.error("Vyplňte prosím všechna pole.")
                    vse_ok = False
                elif reg_email != reg_email_potvrzeni:
                    st.error("E-maily se neshodují.")
                    vse_ok = False
                elif not df_aktualni.empty:
                    if reg_email in df_aktualni["Email"].values:
                        st.error("❌ Tento e-mail už je zaregistrován.")
                        vse_ok = False
                    elif novy_kod in df_aktualni["Code"].values:
                        st.error("⚠️ Tento kód už někdo používá.")
                        vse_ok = False

                if vse_ok:
                    try:
                        import datetime
                        reg_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                        novy_radek = pd.DataFrame([{
                            "Email": reg_email, 
                            "Code": novy_kod,
                            "Password": reg_heslo,
                            "Registration_Date": reg_time,
                            "Topic": "Diplomka_Vyzkum",
                            "Last_Lesson": "N/A"
                        }])
                        
                        # Zápis do Google Sheets (List 1)
                        nova_data = pd.concat([df_aktualni, novy_radek], ignore_index=True)
                        conn.update(worksheet="List 1", data=nova_data)
                        
                        # Odeslání e-mailu
                        status = odeslat_email(reg_email, novy_kod)
                        
                        if status in [200, 202]:
                            st.session_state.registrace_dokoncena = True
                            st.rerun() 
                        else:
                            st.warning("Data uložena, ale e-mail se nepodařilo odeslat.")
                    except Exception as e:
                        st.error(f"Chyba při ukládání: {e}")

    else:
        # SEKCE PŘIHLÁŠENÍ (Už mám svůj kód)
        st.subheader("Přihlášení")
        login_kod = st.text_input("Zadejte kód:", key="login_field").upper().strip()
        
        if st.button("Vstoupit", key="login_btn"):
            try:
                conn = st.connection("gsheets", type=GSheetsConnection)
                df_login = conn.read(worksheet="List 1")
                
                if login_kod in df_login["Code"].values:
                    st.session_state.prihlasen = True
                    st.session_state.moje_id = login_kod
                    st.success("Vítejte! Nyní můžete přejít na záložku Lekce.")
                else:
                    st.error("Tento kód neexistuje. Zaregistrujte se prosím.")
            except:
                st.error("Chyba při ověřování kódu.")

with tab_lekce:
    if not st.session_state.get("prihlasen", False):
        st.warning("Přihlaste se prosím v záložce '📊 Přihlášení/Registrace'.")
    else:
        # 1. Výběr oblasti, pokud ještě není vybrána
        if 'vybrana_oblast' not in st.session_state:
            st.header("Vyberte si zaměření")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🚀 Stres a úzkost", key="btn_stres", use_container_width=True):
                    st.session_state.vybrana_oblast = "Stres"
                    st.rerun()
            with col_b:
                if st.button("⏰ Time-management", key="btn_time", use_container_width=True):
                    st.session_state.vybrana_oblast = "Time"
                    st.rerun()
        
        # 2. Zobrazení lekcí po výběru oblasti
        else:
            st.subheader(f"Vaše cesta: {st.session_state.vybrana_oblast}")
            dostupna_lekce = ziskej_dostupnou_lekci()
            
            # Definice obsahu lekcí (příklad pro Stres)
            lekce_data = {
                "Stres": [
                    {"titel": "1. den: Úvod do dýchání", "url": "https://www.youtube.com/watch?v=example1"},
                    {"titel": "2. den: Krabicový dech", "url": "https://www.youtube.com/watch?v=example2"},
                    {"titel": "3. den: Prodloužený výdech", "url": "https://www.youtube.com/watch?v=example3"}
                ],
                "Time": [
                    {"titel": "1. den: Prioritizace", "url": "https://www.youtube.com/watch?v=example4"},
                    {"titel": "2. den: Pomodoro technika", "url": "https://www.youtube.com/watch?v=example5"},
                    {"titel": "3. den: Digitální detox", "url": "https://www.youtube.com/watch?v=example6"}
                ]
            }

            oblast = st.session_state.vybrana_oblast
            lekce_pro_vysledek = lekce_data.get(oblast, [])

            for i, lekce in enumerate(lekce_pro_vysledek):
                cislo_lekce = i + 1
                with st.expander(f"{lekce['titel']} {'✅' if dostupna_lekce >= cislo_lekce else '🔒'}"):
                    if dostupna_lekce >= cislo_lekce:
                        st.write(f"Vítejte u {cislo_lekce}. lekce!")
                        st.video(lekce['url'])
                        if st.button(f"Označit lekci {cislo_lekce} za hotovou", key=f"done_{cislo_lekce}"):
                            st.success("Skvělá práce!")
                    else:
                        st.info(f"Tato lekce se odemkne až {cislo_lekce}. den výzkumu.")

            if st.button("Změnit zaměření (reset)", key="reset_oblast"):
                del st.session_state.vybrana_oblast
                st.rerun()
