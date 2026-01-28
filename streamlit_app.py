import streamlit as st

# 1. Nastavení stránky (layout="wide" zajistí, že menu bude hezky vedle sebe)
st.set_page_config(page_title="Výzkum: Dechová cvičení", layout="wide")

# 2. Hlavní nadpis aplikace
st.title("🧘 Výzkum: Vliv dechových cvičení")

# 3. Vytvoření horního menu pomocí Tabs (Záložek)
tab_uvod, tab_souhlas, tab_dotaznik, tab_lekce = st.tabs([
    "🏠 Úvodní informace", 
    "📝 Informovaný souhlas", 
    "📊 Vstupní dotazník", 
    "📅 Denní lekce (1-7)"
])

# --- SEKCE 1: ÚVOD ---
with tab_uvod:
    st.header("Vítejte ve výzkumném programu")
    st.write("""
    Tato aplikace slouží k realizaci praktické části mé diplomové práce. 
    V následujících 14 dnech vás provedu krátkými dechovými technikami.
    """)
    st.info("💡 Tip: Pro začátek si přečtěte informovaný souhlas v další záložce.")

# --- SEKCE 2: SOUHLAS ---
with tab_souhlas:
    st.header("Informovaný souhlas")
    st.write("Prosím, potvrďte, že souhlasíte s účastí ve výzkumu.")
    
    souhlas = st.checkbox("Souhlasím se zpracováním údajů pro účely diplomové práce.")
    
    if souhlas:
        st.success("Děkuji za váš souhlas! Nyní můžete přejít k vyplnění dotazníku.")
    else:
        st.warning("Před zahájením výzkumu je nutné potvrdit souhlas.")

# --- SEKCE 3: DOTAZNÍK ---
with tab_dotaznik:
    st.header("Vstupní údaje")
    st.write("Tyto údaje slouží pouze pro spárování vašich výsledků.")
    
    jmeno = st.text_input("Jméno / Přezdívka:")
    email = st.text_input("E-mail:")
    vek = st.number_input("Váš věk:", min_value=15, max_value=100, value=25)
    
    if st.button("Odeslat a uložit"):
        if jmeno and email:
            st.balloons()
            st.success(f"Děkuji, {jmeno}! Vaše údaje byly zaregistrovány.")
        else:
            st.error("Prosím, vyplňte jméno i e-mail.")

# --- SEKCE 4: LEKCE ---
with tab_lekce:
    st.header("Program dechových cvičení")
    
    # Výběr dne (rozbalovací seznam)
    den = st.selectbox("Vyberte"
