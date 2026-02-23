# llm.py
import requests
import json


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

SYSTEM_PROMPT = """
You are a music assistant AI agent.

You have ONE tool available:

play_youtube_music(intent, music_query?, volume_change?)

You do NOT execute code.
You only decide the intent and parameters.

Allowed intents:
- play
- queue
- adjust_volume
- query_status

Examples:

User: "play the song from frieren intro"
Output:
{
  "action": "play_youtube_music",
  "parameters": {
    "intent": "play",
    "music_query": "frieren intro"
  }
}

User: "turn it down a bit"
Output:
{
  "action": "play_youtube_music",
  "parameters": {
    "intent": "adjust_volume",
    "volume_change": -10
  }
}

User: "turn it up a bit"
Output:
{
  "action": "play_youtube_music",
  "parameters": {
    "intent": "adjust_volume",
    "volume_change": +15
  }
}

User: "what song is this?"
Output:
{
  "action": "play_youtube_music",
  "parameters": {
    "intent": "query_status"
  }
}

Output ONLY valid JSON.
No extra text.

User: "stop"
Output:
{
  "action": "play_youtube_music",
  "parameters": {
    "intent": "stop"
  }
}


"""


def call_llm(user_input: str) -> dict:
    payload = {
        "model": MODEL,
        "prompt": f"{SYSTEM_PROMPT}\nUser: {user_input}",
        "stream": False,
    }

    resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
    resp.raise_for_status()

    text = resp.json()["response"].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("LLM did not return valid JSON")


