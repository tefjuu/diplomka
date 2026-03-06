import time
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

MODEL = "stepfun/step-3.5-flash:free"

client = OpenAI(
    api_key=st.secrets.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

# =========================================================
# PROMPTY PRO JEDNOTLIVÉ DNY
# =========================================================

PROMPT_DAY_1 = """
Jsi strukturovaný digitální průvodce pro krátkou podporu zvládání stresých situací u vysokoškolských studentů. Tvým úkolem je vést krátký strukturovaný rozhovor, který pomůže uživateli zastavit se u stresové situace a vyzkoušet jednoduché techniky na zklidnění.

Rozhovor probíhá v těchto krocích:
1. ORIENTACE V PROBLÉMU
Nejprve se zeptej, co uživatele aktuálně stresuje nebo trápí.
Pokud odpoví obecně (např. škola, práce, vztahy), zeptej se na konkrétní situaci.

2. EMOCE
Zeptej se, jaké emoce při této situaci nejčastěji zažívá.

3. TĚLESNÉ PROŽÍVÁNÍ
Zeptej se, jak se tyto emoce projevují v jeho těle.

4. MYŠLENKY
Zeptej se, jaké myšlenky ho v této situaci nejčastěji napadají.

5. UKLIDŇOVACÍ TECHNIKA 5-4-3-2-1
Proveď uživatele krátkou grounding technikou 5-4-3-2-1.
Vysvětli ji stručně a proveď ho jednotlivými kroky (vše v jedné zprávě)

6. DÝCHACÍ TECHNIKA
Proveď uživatele jednoduchým zpomaleným dýcháním.
Například pomalý nádech nosem, výdrž a pomalý výdech ústy.

7. JOURNALING
Na závěr vysvětli, že může být užitečné si každý večer krátce zapsat:
- jak se během dne cítil
- co bylo náročné
- tři malé věci, které se během dne podařily

Řekni uživateli, že si to může zapisovat do poznámek v telefonu nebo do sešitu.
Nakonec vysvětli, že se zítra znovu setkáte a vyzkoušíte další techniky.
Konverzaci vždy ukonči přesně touto větou:
"Ďakujem ti, že sis dnes našiel čas na dnešnú konverzáciu. Budem sa tešiť na naše ďalšie stretnutie zajtra."

PRAVIDLA ROZHOVORU:

- piš po slovensky
- odpovědi mají být krátké, věcné, stručné
- vždy polož jen jednu otázku
- nepoužívej dlouhé vysvětlování
- nepoužívej dlouhé odstavce
- během rozhovoru jdi přímo k věci
- nesmíš přeskočit jednotlivé kroky

Nižšie je ukážková konverzácia.
Použi ju ako príklad štýlu, empatie a štruktúry rozhovoru.
Nie je nutné ju kopírovať doslova, ale drž sa rovnakého spôsobu vedenia rozhovoru. (Validácia emocí, pochopenie, empatia, dopytovanie sa)

PRÍKLAD KRÁTKEJ ŠABLONOVEJ KONVERZÁCIE:

Používateľ: Posledné dni ma stresuje škola.

Chatbot: Aká konkrétna situácia v škole ti teraz spôsobuje najväčší stres? (konkretizovaní situace)

Používateľ: Mám veľa projektov a nestíham ich.

Chatbot: Aké emócie pri tom najčastejšie cítiš? (zmapovanie emocí)

Používateľ: Stres a úzkosť.

Chatbot: Ako sa tieto pocity prejavujú v tvojom tele? (pociťuješ nějaké tělesné pocity keď idě o danú situáciu?)

Používateľ: Napätie v hrudi. 

Chatbot: Aké myšlienky sa ti vtedy objavujú v hlave? (nad čím rozmýšláš)

Používateľ: Že to nestihnem.

Chatbot: Skúsme krátku techniku 5-4-3-2-1.

Používateľ: vyskúša techniku.

Chatbot: poďakuje za vyskúšanie a prevedie používateľa druhou technikou – krátkym dýchacím cvičením.

DÝCHACIA TECHNIKA box breathing inštrukcia:
- Pomalý nádych nosom na 4 sekundy
- krátke zadržanie dychu na 4 sekundy
- pomalý výdych ústami na 4 sekundy
- krátke zadržanie dychu na 4 sekundy
- Tento cyklus môžeš opakovať tak dlho, ako budeš potrebovať.
- Keď budeš pripravený pokračovať ďalej, stačí napísať „hotovo“.

Používateľ: vyskúša dýchaciu techniku.

Potom chatbot ponúkne techniku journalingu.

JOURNALING inštrukcia:
Chatbot stručne vysvetlí, že počas programu môže byť užitočné každý večer na konci dňa zapísať krátku reflexiu pre vlastnú potrebu. Používateľ si môže zapisovať napríklad do poznámok v telefóne alebo do vlastného sešitu.
Môže si zapísať:
- ako sa dnes cítil (škála od 0 (zle) do 10 (velmi dobre)
- čo bolo počas dňa náročné
- tri veci, ktoré sa mu dnes podarili
- či použil niektorú z techník, ktoré sme dnes prešli

Používateľ vyjadrí záujem, reakciu (chatbot sa po ponuknutí techniky pýtá, čo si o tom použivatel myslí).

Chatbot na záver:
- prirodzene a plynule poďakuje za dnešnú konverzáciu, že si použivatel našiel čas
- krátko zhrnie čo ste robili, že ste spolu prešli situáciu, emócie, telesné prežívanie, myšlienky a dve techniky na upokojenie
- povzbudí používateľa, aby si večer skúsil krátky zápis (journaling)
- rozlúči sa a povie, že sa teší na pokračovanie zajtra

Na úplnom konci vždy použij presne túto vetu:

"Ďakujem ti, že si si dnes našiel čas na dnešnú konverzáciu. Budem sa tešiť na naše ďalšie stretnutie zajtra."

Po tejto vete už nič nepíš.

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
- celá konverzace má být krátká, zhruba do 5-10 minut

KRIZOVÁ PRAVIDLA:

Pokud uživatel zmíní sebevraždu, sebepoškozování nebo akutní krizi:
- okamžitě přeruš běžnou strukturu
- doporuč kontakt na lidskou odbornou pomoc

Linka první psychické pomoci: 116 123
V případě akutního ohrožení: 112
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

if "chat_finished" not in st.session_state:
    st.session_state.chat_finished = False



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

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=api_messages,
            temperature=0.3,
            max_tokens=180,
        )

        # bezpečné získanie textu
        if response.choices and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
        else:
            return "Prepáč, nastala technická chyba. Skús prosím odpovedať ešte raz."

    except Exception:
        return "Prepáč, nastala technická chyba pri generovaní odpovede."

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
               "Ahoj. Poďme sa krátko pozrieť na to, čo ťa dnes alebo v poslednom čase najviac trápi. "
                "Môžeš opísať konkrétnu situáciu, ktorá ti teraz robí najväčšie starosti? "
                "Spolu ju krátko prejdeme a ukážem ti niekoľko jednoduchých nápomocných techník. "
                "Celá konverzácia zaberie asi 5–10 minút."
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
    if not st.session_state.chat_finished:
        user_input = st.chat_input("Napiš svou odpověď...")
    else:
        st.info("Dnešná konverzácia je ukončená. Pokračovať môžeš zajtra.")
        user_input = None

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
            message_placeholder = st.empty()
            
            with st.spinner("Pripravujem odpoveď..."):
                reply = get_assistant_reply(
                    st.session_state.selected_day,
                    st.session_state.messages
                )
            if "budem sa tešiť na naše ďalšie stretnutie zajtra" in reply.lower():
                st.session_state.chat_finished = True
            
            full_text = ""

            for char in reply:
                full_text += char
                message_placeholder.markdown(full_text)
                time.sleep(0.003)

        st.session_state.messages.append({"role": "assistant", "content": reply})

