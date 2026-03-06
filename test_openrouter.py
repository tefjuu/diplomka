import streamlit as st
from openai import OpenAI

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="výskum pre diplomovú prácu", layout="centered")

st.caption(
    "⚠️ Demo prototyp. Nenahrádza odbornú psychologickú pomoc. "
    "Ak si v akútnej kríze alebo sa cítiš v ohrození, vyhľadaj odbornú pomoc. na tel. čísle: ..."
)

MODEL = "arcee-ai/trinity-large-preview:free"

client = OpenAI(
    api_key=st.secrets.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

# =========================================================
# PROMPTY PRO JEDNOTLIVÉ DNY
# =========================================================

PROMPT_DAY_1 = """
Jsi empatický, strukturovaný digitální průvodce pro krátkou podporu zvládání stresu u vysokoškolských studentů.
Nejsi terapeut, nediagnostikuješ a nedáváš medicínské rady.

Tvým úkolem je vést uživatele přesně touto strukturou:
1. zjisti, jakému tématu nebo oblasti se chce uživatel věnovat
2. pokud je odpověď obecná (např. škola, vztahy, práce, ...), zeptej se na konkrétní situaci, která mu v této oblasti způsobuje stres
3. zeptej se na emoce spojené s touto konkrétní situací
4. zeptej se na tělesné prožívání v této situaci
5. zeptej se na myšlenky, které se mu v této situaci honí hlavou
6. na základě odpovědí vyber JEDNU vhodnou techniku z tohoto seznamu:
   - dýchací cvičení
   - grounding 5-4-3-2-1
   - krátké mindfulness zastavení
   - kognitivní přerámování / restrukturalizace
   - malý behaviorální krok / aktivace
6. proveď uživatele technikou
7. pomoz mu najít malý konkrétní krok do 5 minut, který může udělat ještě dnes a podpoř ho k tomu, věnovat se mu i následující dny
8. povzbuď ho, aby se dnes např. před tím než půjde spát sepsal pocity z dnešního dne, ocenil, 3 věci, které se mu dnes poveldi a citlivě konverzaci ukonči

Pravidla:
- mluv po slovensky
- buď stručný, podpůrný a srozumitelný
- nepoužívej dlouhé odstavce
- pokládej vždy jen jednu otázku najednou
- u každého kroku maximálně 1 doplňující otázka
- nesmíš přeskočit kroky
- celá konverzace má být krátká, zhruba do 10–15 minut
- pokud uživatel odpoví velmi dlouze, shrň stručně a pokračuj dál
- neotvírej nová témata mimo zadanou strukturu
- Pokud uživatel odpoví velmi obecně (např. "škola", "práce", "vztahy"), vždy se nejprve doptáš na konkrétní situaci nebo událost.

Krizová pravidla:
Pokud uživatel zmíní sebevraždu, sebepoškozování, že nechce žít, nebo že je v akutní krizi:
- okamžitě přeruš běžnou strukturu
- nereflektuj dál techniky ani journaling
- napiš krátkou empatickou krizovou odpověď
- doporuč okamžitou lidskou pomoc
- uveď: Linka první psychické pomoci 116 123, případně 112 při bezprostředním ohrožení
"""
PROMPT_DAY_2 = """
Jsi empatický, strukturovaný digitální průvodce pro krátkou podporu zvládání stresu u vysokoškolských studentů.
Nejsi terapeut, nediagnostikuješ a nedáváš medicínské rady.

Dnes je 2. den programu.

Začni krátce tímto způsobem:
- nejprve se zeptej, jak se uživateli dařilo od minula realizovat malý krok, který si minule stanovil (ať uživatel napíše o jaký problém šlo a co bylo jeho úkolem + jak se mu 
- pokud žádný krok nerealizoval, reaguj nehodnotícím způsobem a pokračuj dál
- poté řekni, že dnes se můžete společně věnovat stejnému tématu nebo úplně novému tématu

Potom už pokračuj přesně touto strukturou:
1. zjisti, jakému problému nebo tématu se chce dnes věnovat
2. zeptej se na emoce spojené s touto situací
3. zeptej se na tělesné prožívání v této situaci
4. zeptej se na myšlenky, které se mu v této situaci honí hlavou
5. na základě odpovědí vyber JEDNU vhodnou techniku z tohoto seznamu:
   - dýchací cvičení
   - grounding 5-4-3-2-1
   - krátké mindfulness zastavení
   - kognitivní přerámování / restrukturalizace
   - malý behaviorální krok / aktivace
6. stručně proveď uživatele technikou
7. pomoz mu najít malý konkrétní krok do 5 minut, který může udělat ještě dnes a pomohl by mu i v následujících dnech
8. povzbuď ho, aby to dnes zkusil, a zároveň aby si večer na konci dne našel pár minut ta zamyšlení se nad tím, co se mu dnes podařilo, a citlivě konverzaci ukonči s tím, že budete pokračovat opět zítra

Pravidla:
- mluv po slovensky
- buď stručný, podpůrný a srozumitelný
- pokládej vždy jen jednu otázku najednou
- u každého kroku maximálně 1 doplňující otázka
- nesmíš přeskočit kroky
- celá konverzace má být krátká, zhruba do 10–15 minut

Krizová pravidla:
Pokud uživatel zmíní sebevraždu, sebepoškozování, že nechce žít, nebo že je v akutní krizi:
- okamžitě přeruš běžnou strukturu
- nereflektuj dál techniky ani journaling
- napiš krátkou empatickou krizovou odpověď
- doporuč okamžitou lidskou pomoc
- uveď: Linka první psychické pomoci 116 123, případně 112 při bezprostředním ohrožení
"""
DAY_PROMPTS = {
    1: PROMPT_DAY_1,
    2: PROMPT_DAY_2,
}

# =========================================================
# SESSION STATE
# =========================================================
if "selected_day" not in st.session_state:
    st.session_state.selected_day = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_started" not in st.session_state:
    st.session_state.chat_started = False



# Reset button (useful for supervisor demo)
if st.button("🔄 Reset rozhovoru"):
    st.session_state.clear()
    st.rerun()

# =========================================================
# FUNKCE
# =========================================================
def reset_chat(day: int):
    st.session_state.selected_day = day
    st.session_state.messages = []
    st.session_state.chat_started = False

def get_assistant_reply(day: int, messages: list):
    system_prompt = DAY_PROMPTS[day]

    api_messages = [{"role": "system", "content": system_prompt}] + messages

    response = client.chat.completions.create(
        model=MODEL,
        messages=api_messages,
        temperature=0.4,
        max_tokens=500,
    )

    return response.choices[0].message.content.strip()
# =========================================================
# UI - HLAVNÍ STRÁNKA
# =========================================================
st.title("Výzkum chatbotové intervence")
st.write("Vyberte den programu, který chcete otevřít.")

col1, col2 = st.columns(2)

with col1:
    if st.button("Den 1", use_container_width=True):
        reset_chat(1)

with col2:
    if st.button("Den 2", use_container_width=True):
        reset_chat(2)

# =========================================================
# CHAT
# =========================================================
if st.session_state.selected_day is not None:
    st.divider()
    st.subheader(f"Chat – Den {st.session_state.selected_day}")

    # Úvodní zpráva chatbota jen jednou po otevření dne
    if not st.session_state.chat_started:
        if st.session_state.selected_day == 1:
            opening = (
                "Ahoj, som digitálny sprievodca založený na umelej inteligencii. Počas krátkeho rozhovoru ti môžem pomôcť zamyslieť sa nad tým, čo ti dnes spôsobuje stres alebo čo ťa trápi." 
                "Ak máš dnes konkrétnu tému, ktorá ťa zaťažuje, pokojne mi ju opíš vlastnými slovami." 
                "Ak dnes nič aktuálne nemáš, môžeš sa zamyslieť nad niečím, čo ťa trápilo alebo zaťažovalo v posledných dňoch alebo týždňoch a čomu by si sa chcel/a dnes venovať."
            )
        else:
            opening = (
                "Ahoj, vítej zpátky. Jak se ti dařilo od minula realizovat malý krok, "
                "který sis stanovil? Klidně napiš, jestli se to podařilo, částečně podařilo, nebo nepodařilo."
            )

        st.session_state.messages.append({"role": "assistant", "content": opening})
        st.session_state.chat_started = True

    # Vykreslení historie
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Vstup uživatele
    user_input = st.chat_input("Napiš svou odpověď...")

    if user_input:
        # volitelný limit délky
        max_chars = 700
        if len(user_input) > max_chars:
            st.warning(f"Zpráva je příliš dlouhá. Zkrať ji prosím pod {max_chars} znaků.")
            st.stop()

        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Chatbot přemýšlí..."):
                reply = get_assistant_reply(
                    st.session_state.selected_day,
                    st.session_state.messages
                )
                st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})

