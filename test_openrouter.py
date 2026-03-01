import re
import json
import time
import streamlit as st
from openai import OpenAI

# =========================================================
# CONFIG
# =========================================================
MODEL = "arcee-ai/trinity-large-preview:free"

st.set_page_config(page_title="Yumo – empatický sprievodca", layout="centered")

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
)

st.title("Yumo – empatický sprievodca")

st.caption(
    "⚠️ Demo prototyp. Nenahrádza odbornú psychologickú pomoc. "
    "Ak si v akútnej kríze alebo sa cítiš v ohrození, vyhľadaj odbornú pomoc."
)

# Reset button (useful for supervisor demo)
if st.button("🔄 Reset rozhovoru"):
    st.session_state.clear()
    st.rerun()

# =========================================================
# HELPERS
# =========================================================
def detect_gender(history_text: str) -> str:
    """Heuristic gender detection. No slashes; default female if unsure."""
    male_markers = [
        r"\bbol som\b", r"\bcítil som\b", r"\bmal som\b", r"\bchcel som\b",
        r"\bpovedal som\b", r"\burobil som\b", r"\bprišiel som\b",
        r"\bbol som v\b", r"\burobil by som\b",
    ]
    female_markers = [
        r"\bbola som\b", r"\bcítila som\b", r"\bmala som\b", r"\bchcela som\b",
        r"\bpovedala som\b", r"\burobila som\b", r"\bprišla som\b",
        r"\bbola som v\b", r"\burobila by som\b",
    ]
    t = history_text.lower()
    if any(re.search(p, t) for p in male_markers):
        return "M"
    if any(re.search(p, t) for p in female_markers):
        return "F"
    return "F"

def is_number_0_10(text: str):
    text = text.strip()
    if not re.fullmatch(r"\d+(\.\d+)?", text):
        return None
    val = float(text)
    if 0 <= val <= 10:
        return int(val) if val.is_integer() else val
    return None

def llm_text(system: str, user: str, temperature: float = 0.6) -> str:
    """Free-form therapeutic text slot."""
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content.strip()

def llm_json(system: str, user: str):
    if not user:
        return {"complete": False, "followup": ""}

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            temperature=0.2,
            messages=[
                {
                    "role": "user",
                    "content": system + "\n\n" + user
                }
            ],
        )
    except Exception as e:
        st.error(f"LLM JSON ERROR: {e}")
        return {"complete": True, "followup": ""}

    raw = resp.choices[0].message.content.strip()

    try:
        return json.loads(raw)
    except:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except:
                pass

    return {"complete": True, "followup": ""}

def say(text: str):
    with st.chat_message("assistant"):
        placeholder = st.empty()

        displayed = ""
        for char in text:
            displayed += char
            placeholder.markdown(displayed)
            time.sleep(0.012)

    st.session_state.messages.append({
        "role": "assistant",
        "content": text
    })

# =========================================================
# VALIDATORS (Variant B orchestration layer)
# Each validator checks if current step is complete.
# =========================================================
def validate_step(phase: str, user_input: str):
    """
    Returns dict: {complete: bool, followup: str}
    The followup must be Slovak and natural.
    """
    # Define objectives per phase (you can extend later)
    objectives = {
        "STEP1": "Používateľ má opísať, čo ho trápi (stresor).",
        "STEP1_FOLLOWUP": "Používateľ má pridať aspoň 1–2 detaily (kedy je to najsilnejšie / čo je najťažšie).",
        "STEP2": "Používateľ má pomenovať emócie a uviesť, kde ich cíti v tele.",
        "STEP3": "Používateľ má napísať konkrétnu automatickú myšlienku v podobe vety.",
        "STEP3_5": "Používateľ má uviesť číslo 0–10 (úroveň napätia).",
        "STEP4A": "Používateľ má potvrdiť pripravenosť slovom OK.",
        "STEP4B": "Používateľ má uviesť veci, ktoré vidí (ideálne 3–5).",
        "STEP4C": "Používateľ má uviesť veci, ktoré cíti na tele (ideálne 3–4).",
        "STEP4D": "Používateľ má uviesť zvuky (ideálne 2–3).",
        "STEP4E": "Používateľ má uviesť vône (1–2).",
        "STEP4F": "Používateľ má uviesť chuť (1).",
        "STEP4G": "Používateľ má uviesť nové napätie 0–10 a/alebo stručne čo sa zmenilo.",
        "STEP5": "Používateľ má rozhodnúť: dychová technika áno/nie.",
        "STEP6_BREATH": "Používateľ má potvrdiť dokončenie dychovej techniky (napr. 'hotovo').",
        "STEP7_TINY": "Používateľ má navrhnúť maličký krok (tiny habit) alebo povedať, že nevie.",
        "STEP7_NEED": "Používateľ má pomenovať, čo teraz potrebuje (pokoj/pohyb/odškrtnúť povinnosť/…)",
        "STEP7_CONFIRM": "Používateľ má potvrdiť, že tiny habit je OK.",
    }

    goal = objectives.get(phase, "Vyhodnoť, či odpoveď spĺňa cieľ aktuálnej fázy.")

    system = f"""
Si klinický supervízor štruktúrovaného CBT/Mindfulness/SFBT protokolu. Vždy píš po slovensky.

Aktuálna fáza: {phase}
Cieľ fázy: {goal}

Vyhodnoť odpoveď používateľa.
- Ak je odpoveď NEÚPLNÁ alebo mimo, nastav "complete": false a napíš jednu prirodzenú doplňujúcu otázku do "followup".
- Ak je odpoveď dostačujúca, nastav "complete": true a "followup" nechaj prázdne.

Odpovedz striktne ako JSON:
{{
  "complete": true/false,
  "followup": "..."
}}
    """.strip()

    return llm_json(system, user_input)


# =========================================================
# SESSION INIT
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "phase" not in st.session_state:
    st.session_state.phase = "STEP1"
    st.session_state.gender = "F"
    st.session_state.data = {
        "stressor": None,
        "emotions_body": None,
        "thought": None,
        "tension_pre": None,
        "grounding_5": None,
        "grounding_4": None,
        "grounding_3": None,
        "grounding_2": None,
        "grounding_1": None,
        "tension_post": None,
        "wants_breathing": None,
        "tiny_habit": None,
        "need_category": None,
    }
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Ahoj, som Yumo. Čo ťa dnes trápi alebo čo ti spôsobuje stres? Pokojne mi to opíš vlastnými slovami."
    })

        
    # AŽ TEĎ vykresli historii
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_input = st.chat_input("Napíš správu…")

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    # 🔥 OKAMŽITÉ VYKRESLENÍ USER ZPRÁVY
    with st.chat_message("user"):
        st.markdown(user_input)

    phase = st.session_state.phase
    D = st.session_state.data
    gender = st.session_state.gender

    # ---- STEP1 ----
    if phase == "STEP1":
        v = validate_step("STEP1", user_input)
        if not v["complete"]:
            say(v["followup"] or "Môžeš mi prosím povedať, čo ťa trápi?")
        else:
            D["stressor"] = user_input.strip()
            say("Ďakujem, že to zdieľaš. Môžeš pridať ešte pár detailov?")
            st.session_state.phase = "STEP1_FOLLOWUP"

    # ---- STEP1_FOLLOWUP ----
    elif phase == "STEP1_FOLLOWUP":
        v = validate_step("STEP1_FOLLOWUP", user_input)
        if not v["complete"]:
            say(v["followup"] or "Skús prosím pridať aspoň jeden konkrétny detail.")
        else:
            D["stressor"] = (D["stressor"] + "\n" + user_input.strip()).strip()
            st.session_state.phase = "STEP2"
            say("Rozumiem. Poďme to jemne rozkódovať. Aké emócie v tom cítiš—napríklad smútok, hnev, úzkosť, hanbu…? A kde to cítiš v tele?")

    # ---- STEP2 ----
    elif phase == "STEP2":
        v = validate_step("STEP2", user_input)
        if not v["complete"]:
            say(v["followup"] or "Rozumiem. A kde to cítiš v tele?")
        else:
            D["emotions_body"] = user_input.strip()

            system = (
                "Si Yumo, empatický psychologický sprievodca. Vždy píš po slovensky. "
                "Krátko zvaliduj emócie používateľa a plynulo ich zhrň v 2–4 vetách. "
                "Bez psychoedukácie."
            )
            with st.chat_message("assistant"):
                with st.spinner("🟢 Yumo rozmýšľa..."):
                    validation = llm_text(system, D["emotions_body"], temperature=0.6)

            say(validation)

            st.session_state.phase = "STEP3"
            say(
                "Keď si tú situáciu znova predstavíš a vnímaš tie emócie, "
                "aká konkrétna myšlienka ti vtedy prebehne hlavou? Skús ju napísať presne tak, ako ti znie v hlave. "
                "Často je to krátka veta, napríklad „nezvládnem to“ alebo „pokazím to“."
            )

    # ---- STEP3 ----
    elif phase == "STEP3":
        v = validate_step("STEP3", user_input)
        if not v["complete"]:
            say(v["followup"] or "Skús to prosím napísať ako jednu konkrétnu vetu, ktorá ti znie v hlave.")
        else:
            D["thought"] = user_input.strip()

            system = (
                "Si Yumo. Vždy píš po slovensky. "
                "Urob krátku CBT prácu: 1) zhrň jadrovú myšlienku jednou vetou, "
                "2) navrhni vyváženejšiu alternatívu (kognitívny reframing) v 1–2 vetách. "
                "Buď teplý, profesionálny, nehodnotiaci."
            )
            user_block = (
                f"Stresor:\n{D['stressor']}\n\n"
                f"Emócie a telo:\n{D['emotions_body']}\n\n"
                f"Automatická myšlienka:\n{D['thought']}\n"
            )
            with st.chat_message("assistant"):
                with st.spinner("🟢 Yumo rozmýšľa..."):
                reframed = llm_text(system, user_block, temperature=0.6)

            say(reframed)

            st.session_state.phase = "STEP3_5"
            say("Skôr než začneme s technikou na upokojenie, aká je tvoja aktuálna úroveň napätia na škále 0 – 10? (0 = úplný pokoj, 10 = maximum stresu)")

    # ---- STEP3_5 ----
    elif phase == "STEP3_5":
        val = is_number_0_10(user_input)
        if val is None:
            say("Skús prosím napísať len číslo od 0 do 10.")
        else:
            D["tension_pre"] = val
            st.session_state.phase = "STEP4A"
            say(
                "Poďme teraz spraviť krátku techniku na upokojenie nervového systému. "
                "Volá sa 5-4-3-2-1 a trvá približne 1–2 minúty. "
                "Najprv si len všimni dych. Nemusíš ho meniť. "
                "Keď budeš pripravená, napíš mi „OK“ a ideme na to."
            )

    # ---- STEP4A ----
    elif phase == "STEP4A":
        v = validate_step("STEP4A", user_input)
        if not v["complete"]:
            say(v["followup"] or "Kľudne si daj chvíľku. Keď budeš pripravená, napíš „OK“.")
        else:
            st.session_state.phase = "STEP4B"
            say("Zrak (5). Pozri sa okolo seba a pomenuj 5 vecí, ktoré vidíš. Môžu byť úplne bežné. Napíš ich sem.")

    # ---- STEP4B ----
    elif phase == "STEP4B":
        v = validate_step("STEP4B", user_input)
        if not v["complete"]:
            say(v["followup"] or "Stačia aj 3 veci. Môžeš pomaly preskenovať miestnosť zľava doprava.")
        else:
            D["grounding_5"] = user_input.strip()
            st.session_state.phase = "STEP4C"
            say("Dotyk (4). Teraz si všimni 4 veci, ktoré cítiš na tele. Napr. chodidlá na zemi, tričko na ramenách. Napíš ich sem.")

    # ---- STEP4C ----
    elif phase == "STEP4C":
        v = validate_step("STEP4C", user_input)
        if not v["complete"]:
            say(v["followup"] or "Skús napríklad chodidlá na zemi, operadlo stoličky, látku na rukáve…")
        else:
            D["grounding_4"] = user_input.strip()
            st.session_state.phase = "STEP4D"
            say("Sluch (3). Vnímaj 3 zvuky, ktoré práve počuješ. Zapíš ich sem.")

    # ---- STEP4D ----
    elif phase == "STEP4D":
        v = validate_step("STEP4D", user_input)
        if not v["complete"]:
            say(v["followup"] or "Môžeš vnímať aj zvuk dychu alebo jemný zvuk, ktorý spravíš pohybom.")
        else:
            D["grounding_3"] = user_input.strip()
            st.session_state.phase = "STEP4E"
            say("Čuch (2). Všimni si 2 vône (parfum, káva, vzduch). Vypíš ich sem.")

    # ---- STEP4E ----
    elif phase == "STEP4E":
        v = validate_step("STEP4E", user_input)
        if not v["complete"]:
            say(v["followup"] or "Ak je to ťažké, môžeš použiť spomienkovú vôňu (napr. káva).")
        else:
            D["grounding_2"] = user_input.strip()
            st.session_state.phase = "STEP4F"
            say("Chuť (1). A teraz 1 vec, ktorú cítiš na jazyku (voda, neutrálna chuť). Napíš to sem.")

    # ---- STEP4F ----
    elif phase == "STEP4F":
        v = validate_step("STEP4F", user_input)
        if not v["complete"]:
            say(v["followup"] or "Stačí aj neutrálna chuť alebo „nič výrazné“.")
        else:
            D["grounding_1"] = user_input.strip()
            st.session_state.phase = "STEP4G"
            say("Super. Aká je teraz tvoja úroveň napätia na škále 0–10? A čo sa zmenilo v tele alebo v hlave?")

    # ---- STEP4G ----
    elif phase == "STEP4G":
        maybe_num = re.search(r"(\d+(\.\d+)?)", user_input)
        tension = None
        if maybe_num:
            tension = is_number_0_10(maybe_num.group(1))

        D["tension_post"] = tension

        if tension is not None and D["tension_pre"] is not None and tension < D["tension_pre"]:
            say("To je dobrý signál. Aj malý posun znamená, že sa telo vie prepnúť do bezpečnejšieho režimu.")
        else:
            say("Aj to je v poriadku. Niekedy telo potrebuje viac času.")

        st.session_state.phase = "STEP5"
        say("Chceš vyskúšať ešte krátku dychovú techniku, alebo mám pokračovať ďalej? (napíš „áno“ alebo „pokračuj“)")

    # ---- STEP5 ----
    elif phase == "STEP5":
        v = validate_step("STEP5", user_input)
        txt = user_input.strip().lower()

        if not v["complete"]:
            say(v["followup"] or "Chceš dychovú techniku (napíš „áno“) alebo pokračovať ďalej (napíš „pokračuj“)?")
        else:
            wants = None
            if any(k in txt for k in ["áno", "ano", "chcem", "skús", "vyskúšať", "dych"]):
                wants = True
            if any(k in txt for k in ["nie", "nechcem", "pokračuj", "ďalej", "dalej"]):
                wants = False

            if wants is None:
                say("Napíš prosím „áno“ (dych) alebo „pokračuj“ (bez dychu).")

            elif wants:
                D["wants_breathing"] = True
                st.session_state.phase = "STEP6_BREATH"
                say(
                    "Dobre. Skúsme krátke dýchanie:\n\n"
                    "1) Nádych nosom na 4 sekundy.\n"
                    "2) Zadrž dych na 2 sekundy.\n"
                    "3) Pomalý výdych ústami na 6 sekúnd.\n\n"
                    "Urob to 3-krát. Keď skončíš, napíš mi „hotovo“."
                )

            else:
                D["wants_breathing"] = False
                st.session_state.phase = "STEP7_TINY"

                if gender == "M":
                    say(
                        "Skúsme teraz nájsť malý krok. Čo si myslíš, že by si mohol urobiť v nasledujúcej hodine "
                        "alebo počas dňa – niečo úplne malé a krátke – aby si sa cítil o niečo lepšie?"
                    )
                else:
                    say(
                        "Skúsme teraz nájsť malý krok. Čo si myslíš, že by si mohla urobiť v nasledujúcej hodine "
                        "alebo počas dňa – niečo úplne malé a krátke – aby si sa cítila o niečo lepšie?"
                    )

    # ---- STEP6_BREATH ----
    elif phase == "STEP6_BREATH":
        v = validate_step("STEP6_BREATH", user_input)

        if not v["complete"] and "hot" not in user_input.lower():
            say(v["followup"] or "Keď dokončíš 3 cykly, napíš mi „hotovo“.")
        else:
            st.session_state.phase = "STEP7_TINY"

            if gender == "M":
                say("Super. Čo je jeden úplne malý krok, ktorý by si mohol spraviť ešte dnes, aby si sa cítil o kúsok lepšie?")
            else:
                say("Super. Čo je jeden úplne malý krok, ktorý by si mohla spraviť ešte dnes, aby si sa cítila o kúsok lepšie?")

    # ---- STEP7_TINY ----
    elif phase == "STEP7_TINY":
        idea = user_input.strip()

        if len(idea) < 4 or any(k in idea.lower() for k in ["neviem", "netuším"]):
            st.session_state.phase = "STEP7_NEED"
            say(
                "To je úplne v poriadku, že nevieš. Skúsme na to prísť spolu. "
                "Čo by si teraz najviac potrebovala? Bol by to pokoj, pohyb, alebo len odškrtnúť jednu malú povinnosť?"
            )
        else:
            D["tiny_habit"] = idea
            st.session_state.phase = "STEP7_CONFIRM"

            system = (
                "Si Yumo. Vždy píš po slovensky. "
                "Používateľ navrhol malý krok. 1) pochváľ ho, 2) ak je príliš veľký, zmenši ho na verziu do 5 minút, "
                "3) spýtaj sa, či je to takto OK."
            )
            with st.chat_message("assistant"):
                with st.spinner("🟢 Yumo rozmýšľa..."):
                    coach = llm_text(system, idea, temperature=0.6)

            say(coach)

    # ---- STEP7_NEED ----
    elif phase == "STEP7_NEED":
        D["need_category"] = user_input.strip()

        system = (
            "Si Yumo. Navrhni JEDEN ultra-malý krok do 5 minút podľa potreby používateľa."
        )
        with st.chat_message("assistant"):
            with st.spinner("🟢 Yumo rozmýšľa..."):
                suggestion = llm_text(system, user_input, temperature=0.6)

        st.session_state.phase = "STEP7_TINY"
        say(suggestion)

    # ---- STEP7_CONFIRM ----
    elif phase == "STEP7_CONFIRM":
        txt = user_input.lower()

        if any(k in txt for k in ["áno", "ano", "ok", "jasné", "dobre", "platí"]):
            st.session_state.phase = "STEP8"

            tiny = D["tiny_habit"] or "tvoj malý krok"

            say("Teraz máš k dispozícii konkrétny nástroj. Môžeš ho vyskúšať v praxi vždy, keď sa objaví podobná situácia.")
            say(
                "Dnes sme spolu prešli kus cesty. Pozreli sme sa na to, čo ti spôsobuje napätie, "
                "pomenovali sme emócie aj konkrétnu myšlienku a pomocou techniky 5-4-3-2-1 sme upokojili tvoj nervový systém."
            )
            say(
                f"Aj malé kroky, ako ten dnešný: **{tiny}**, sa postupne sčítavajú."
            )
            say("Držím ti palce. Ak budeš potrebovať ďalšiu podporu, ozvi sa.")

        else:
            say("Je to pre teba takto v poriadku? Ak chceš, môžeme to zmenšiť ešte viac (pod 2 minúty).")

    # ---- STEP8 ----
    else:
        say("Ak chceš, môžeš mi napísať, ako sa ti darí s tým malým krokom.")
        
# Update gender guess from user history
all_user_text = "\n".join([m["content"] for m in st.session_state.messages if m["role"] == "user"])
st.session_state.gender = detect_gender(all_user_text)

gender = st.session_state.gender
D = st.session_state.data
phase = st.session_state.phase


