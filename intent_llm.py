def parse_music_intent(call_llm, text: str) -> dict:
    prompt = f"""
You are a music assistant.

User said (noisy STT):
"{text}"

Decide:
- intent: one of [play, stop, adjust_volume, query_status]
- canonical_query: clean music search query (artist + song)
- volume_change: integer (-50 to +50) if volume related

Return JSON only.
"""

    try:
        llm_output = call_llm(prompt)
        return llm_output
    except Exception:
        # 🔑 FAIL SOFT
        return {
            "intent": "unknown"
        }
