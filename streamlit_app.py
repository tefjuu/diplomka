import streamlit as st
import requests
import pandas as pd
import streamlit.components.v1 as components
from datetime import datetime, time
from streamlit_gsheets import GSheetsConnection

yumo_html = """
<script src="https://sf-cdn.coze.com/obj/unpkg-va/flow-platform/chat-app-sdk/1.2.0-beta.6/libs/oversea/index.js"></script>
<script>
  new CozeWebSDK.WebChatClient({
    config: {
      bot_id: '7610756366369554485',
    },
    componentProps: {
      title: 'Yumo',
    },
    auth: {
      type: 'token',
      token: 'pat_B4am7o2JSYpoKfjqN5cchUan3vkrryaa2Qq92g13mfU6KYqgk96rMIIu5qzRhso6',
      onRefreshToken: function () {
        return 'pat_B4am7o2JSYpoKfjqN5cchUan3vkrryaa2Qq92g13mfU6KYqgk96rMIIu5qzRhso6'
      }
    }
  });
</script>
"""
components.html(yumo_html, height=0)

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
            <div style="font-family: sans-serif; max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px; border-radius: 10px;">
                <h2 style="color: #333;">Dobrý den,</h2>
                <p style="font-size: 16px; color: #555;">děkujeme za zapojení do výzkumu k diplomové práci. Tvůj unikátní kód pro přihlášení je:</p>
                <div style="background-color: #f9f9f9; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0;">
                    <span style="font-size: 24px; font-weight: bold; color: #4CAF50; letter-spacing: 2px;">{kod}</span>
                </div>
                <p style="font-size: 16px; color: #555;">Do aplikace s lekcemi se můžeš kdykoliv vrátit kliknutím na odkaz níže:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://vyzkum-diplomka.streamlit.app/" 
                       style="background-color: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; font-weight: bold; border-radius: 5px; font-size: 18px;">
                       VSTOUPIT DO APLIKACE
                    </a>
                </div>
                <p style="font-size: 14px; color: #888; border-top: 1px solid #eee; pt-10px; margin-top: 30px;">
                    Doporučujeme si tento e-mail uložit.
                </p>
            </div>
            """
        }
        response = requests.post(url, json=data, headers=headers)
        
        # Ponecháme diagnostiku, kdyby se zase vyčerpal limit, ať víme
        if response.status_code not in [200, 202]:
            st.error(f"❌ MailerSend Error: {response.status_code} - {response.text}")
            
        return response.status_code
    except Exception as e:
        st.error(f"🔥 Kritická chyba v kódu odesílání: {e}")
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
                df_aktualni = conn.read(worksheet="List 1") # <--- TADY JE TEN ŘÁDEK!
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
        # --- SEKCE PŘIHLÁŠENÍ ---
        st.subheader("Přihlášení do výzkumu")
        
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            login_email = st.text_input("E-mail:", key="login_email_field").strip()
        with col_l2:
            login_pass = st.text_input("Heslo:", type="password", key="login_pass_field").strip()
        
        if st.button("Vstoupit do aplikace", key="login_btn", use_container_width=True):
            if not login_email or not login_pass:
                st.warning("Vyplňte prosím e-mail a heslo.")
            else:
                try:
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    df_login = conn.read(worksheet="List 1", ttl=0)

                    # Pomocná funkce musí být definována správně odsazená uvnitř try
                    def vycisti_heslo(heslo):
                        h = str(heslo).strip()
                        if h.endswith('.0'):
                            return h[:-2]  # Uřízne .0
                        return h

                    # Vyčištění dat
                    df_login["Password"] = df_login["Password"].apply(vycisti_heslo)
                    vstup_email = str(login_email).lower().strip()
                    vstup_heslo = str(login_pass).strip()

                    # Maska pro hledání
                    maska = (
                        (df_login["Email"].astype(str).str.lower().str.strip() == vstup_email) & 
                        (df_login["Password"] == vstup_heslo)
                    )
                    
                    uzivatel = df_login[maska]

                    if not uzivatel.empty:
                        st.session_state.prihlasen = True
                        st.session_state.muj_email = vstup_email
                        st.session_state.moje_id = str(uzivatel.iloc[0]["Code"]).strip()
                        st.session_state.vybrana_oblast = str(uzivatel.iloc[0]["Topic"]).strip()
                        
                        st.success("🎉 Přihlášení úspěšné!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Nesprávný e-mail nebo heslo.")
                        
                except Exception as e:
                    st.error(f"Chyba při komunikaci s tabulkou: {e}")
# Tady končí tab_dotaznik a začíná tab_lekce (mimo předchozí bloky)
with tab_lekce:
    if not st.session_state.get("prihlasen"):
        st.warning("Pro zobrazení lekcí se nejprve přihlaste v záložce Přihlášení/Registrace.")
    else:
        # 1. Získání oblasti (buď z přihlášení, nebo výchozí)
        oblast = st.session_state.get('vybrana_oblast', 'Diplomka_Vyzkum')
        st.subheader(f"Vaše cesta: {oblast}")
        
        # 2. Výpočet, kolikátý je den
        dostupna_lekce = ziskej_dostupnou_lekci()
        
        # 3. Definice obsahu lekcí
        # (Zde si doplň své skutečné názvy a URL z YouTube)
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
            ],
            "Diplomka_Vyzkum": [
                {"titel": "1. den: Úvodní video", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
                {"titel": "2. den: Technika dechu", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
            ]
        }

        # Načtení konkrétních lekcí pro danou oblast
        lekce_pro_vysledek = lekce_data.get(oblast, [])

        # 4. Zobrazení lekcí v expanderech
        for i, lekce in enumerate(lekce_pro_vysledek):
            cislo_lekce = i + 1
            stav_ikona = '✅' if dostupna_lekce >= cislo_lekce else '🔒'
            
            with st.expander(f"{stav_ikona} {lekce['titel']}"):
                if dostupna_lekce >= cislo_lekce:
                    st.write(f"Vítejte u {cislo_lekce}. lekce!")
                    st.video(lekce['url'])
                    if st.button(f"Označit lekci {cislo_lekce} za hotovou", key=f"done_{cislo_lekce}"):
                        st.success("Skvělá práce! Pokrok byl zaznamenán.")
                else:
                    st.info(f"Tato lekce se odemkne až {cislo_lekce}. den výzkumu.")

        # Tlačítko pro odhlášení (volitelné)
        if st.button("Odhlásit se", key="logout_btn"):
            st.session_state.prihlasen = False
            st.rerun()

<script>
  new CozeWebSDK.WebChatClient({
    config: {
      bot_id: '7610756366369554485',
    },
    componentProps: {
      title: 'Yumo',
    },
    auth: {
      type: 'token',
      token: 'pat_B4am7o2JSYpoKfjqN5cchUan3vkrryaa2Qq92g13mfU6KYqgk96rMIIu5qzRhso6
',
      onRefreshToken: function () {
        return 'pat_B4am7o2JSYpoKfjqN5cchUan3vkrryaa2Qq92g13mfU6KYqgk96rMIIu5qzRhso6
'
      }
    }
  });
</script>
"""
components.html(yumo_html, height=0)
