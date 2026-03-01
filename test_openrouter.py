import re
import streamlit as st
from openai import OpenAI

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
MODEL = "arcee-ai/trinity-large-preview:free"

st.set_page_config(page_title="Yumo – guided CBT flow", layout="centered")

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
)

st.title("Yumo – empatický sprievodca")

if st.button("🔄 Reset rozhovoru"):
    st.session_state.clear()
    st.rerun()

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def detect_gender(history_text: str) -> str:
    male_markers = [
        r"\bbol som\b", r"\bcítil som\b", r"\bmal som\b", r"\bchcel som\b",
        r"\bpovedal som\b", r"\burobil som\b", r"\bprišiel som\b",
    ]
    female_markers = [
        r"\bbola som\b", r"\bcítila som\b", r"\bmala som\b", r"\bchcela som\b",
        r"\bpovedala som\b", r"\burobila som\b", r"\bprišla som\b",
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

def llm_slot(system: str, user: str) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=0.6,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content.strip()

# -------------------------------------------------
# SESSION INIT
# -------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.phase = "STEP1"
    st.session_state.gender = "F"
    st.session_state.data = {}

    st.session_state.messages.append({
        "role": "assistant",
        "content": "Ahoj, som Yumo. Čo ťa dnes trápi alebo čo ti spôsobuje stres?"
    })

# -------------------------------------------------
# RENDER CHAT
# -------------------------------------------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_input = st.chat_input("Napíš správu…")
if not user_input:
    st.stop()

st.session_state.messages.append({"role": "user", "content": user_input})

all_user_text = "\n".join([m["content"] for m in st.session_state.messages if m["role"] == "user"])
st.session_state.gender = detect_gender(all_user_text)

gender = st.session_state.gender
D = st.session_state.data
phase = st.session_state.phase

def say(text):
    st.session_state.messages.append({"role": "assistant", "content": text})

# -------------------------------------------------
# FLOW
# -------------------------------------------------

if phase == "STEP1":
    D["stressor"] = user_input
    st.session_state.phase = "STEP2"
    say("Môžeš mi o tom povedať viac detailov?")

elif phase == "STEP2":
    D["details"] = user_input
    st.session_state.phase = "STEP3"
    say("Aké emócie v tom cítiš? A kde ich cítiš v tele?")

elif phase == "STEP3":
    D["emotions"] = user_input
    st.session_state.phase = "STEP4"
    say("Aká konkrétna myšlienka ti vtedy prebehne hlavou?")

elif phase == "STEP4":
    D["thought"] = user_input

    reframed = llm_slot(
        "Si empatický CBT sprievodca. Vždy píš po slovensky. "
        "Zhrň myšlienku a navrhni vyváženejší pohľad.",
        user_input
    )

    say(reframed)
    st.session_state.phase = "STEP5"
    say("Aká je tvoja úroveň napätia na škále 0–10?")

elif phase == "STEP5":
    val = is_number_0_10(user_input)
    if val is None:
        say("Napíš len číslo od 0 do 10.")
    else:
        D["tension_pre"] = val
        st.session_state.phase = "GROUNDING"
        say("Poďme na techniku 5-4-3-2-1. Keď budeš pripravená, napíš OK.")

elif phase == "GROUNDING":
    say("Pomenuj 5 vecí, ktoré vidíš.")
    st.session_state.phase = "END"

elif phase == "END":
    say("Dnes sme spolu prešli kus cesty. Ak budeš potrebovať, som tu.")

st.rerun()
