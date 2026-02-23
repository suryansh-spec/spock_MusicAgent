# agent_llm.py
import json
from llm import call_llm

SYSTEM_PROMPT = """
You are a music agent.

You receive:
- user request
- current player state
- optional candidate tracks

Decide ONE action using this tool schema:

play_youtube_music(
  intent: play | queue | stop | adjust_volume | query_status,
  music_query?: string,
  volume_change?: integer,
  candidate_index?: integer
)

Rules:
- If candidates are provided, prefer selecting one using candidate_index.
- Do NOT hallucinate URLs.
- If music already matches request, do nothing.
- Output JSON only.
"""

def decide_action(user_text, state, candidates=None):
    payload = {
        "user": user_text,
        "state": state,
        "candidates": candidates or []
    }

    prompt = f"""
{SYSTEM_PROMPT}

INPUT:
{json.dumps(payload, indent=2)}
"""

    return call_llm(prompt)
