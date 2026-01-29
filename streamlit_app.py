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

st.set_page_config(page_title
