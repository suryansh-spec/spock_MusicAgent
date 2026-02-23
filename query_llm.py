# query_llm.py
from llm import call_llm

def refine_music_query(original_query: str) -> str:
    prompt = f"""
You are a music search optimizer.

User request:
"{original_query}"

Task:
Rewrite this into the MOST LIKELY YouTube Music search query.

Rules:
- If song is well-known, include artist name
- If game/movie/anime OST, normalize to official franchise name
- Remove edition words like remastered, deluxe, edition
- Prefer "Main Theme" or "OST" for games/movies/anime
- Max 30 words
- Return ONLY the query text

Examples:
"blinding lights" → "Blinding Lights The Weeknd"
"spider man remastered theme" → "Marvel's Spider-Man Main Theme OST"
"play naruto sad song" → "Naruto Shippuden Sad Theme OST"
"play something from Black clover" → "Black clover OST"
"""

    out = call_llm(prompt)
    if isinstance(out, str):
        return out.strip()
    return original_query
