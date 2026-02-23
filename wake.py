from stt import speech_to_text
import difflib
import re

# Include common mishearings ON PURPOSE
WAKE_WORDS = [
    "spock",
    "spark",
    "spok",
    "spak",
    "fock",
]


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z]", "", text)

    # phonetic smoothing
    text = text.replace("ph", "f")
    text = text.replace("ck", "k")
    text = text.replace("c", "k")
    text = text.replace("x", "ks")

    return text


def is_wake_word(text: str) -> bool:
    text_norm = normalize(text)

    # 🛑 Ignore very short phrases (noise / profanity alone)
    if len(text.split()) <= 1:
        return False

    for wake in WAKE_WORDS:
        wake_norm = normalize(wake)

        # 1️⃣ Fast path: substring
        if wake_norm in text_norm:
            return True

        # 2️⃣ Fuzzy match (short words need low threshold)
        ratio = difflib.SequenceMatcher(None, wake_norm, text_norm).ratio()
        if ratio >= 0.4:
            return True

    return False

def strip_wake_word(text: str) -> str:
    text_norm = normalize(text)

    for wake in WAKE_WORDS:
        wake_norm = normalize(wake)

        if wake_norm in text_norm:
            # remove wake word from original text
            pattern = re.compile(wake, re.IGNORECASE)
            return pattern.sub("", text).strip(" ,")

    return ""


def wait_for_wake_word():
    print("🟢 agent idle. Say the wake word...", flush=True)

    while True:
        text = speech_to_text()

        if not text:
            continue

        print(f"👂 Heard: {text}", flush=True)

        if is_wake_word(text):
            print("🟡 Wake word detected!", flush=True)
            return
