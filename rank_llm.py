def select_best_track(call_llm, query, candidates):
    formatted = "\n".join(
        f"{i+1}. {c['title']} | {c['uploader']} | {c['duration']}s"
        for i, c in enumerate(candidates)
    )

    prompt = f"""
You are selecting the BEST music audio result.

User wants:
"{query}"

Candidates:
{formatted}

Rules:
- Prefer official audio or topic channels
- Avoid videos, live, remixes, loops
- Prefer duration 2–6 minutes

Return ONLY the index number (1-based).
"""

    llm_output = call_llm(prompt)

    # --- Case 1: tool-style output ---
    if isinstance(llm_output, dict) and "parameters" in llm_output:
        params = llm_output["parameters"]

        # If model tried to "play" something, map it back to a candidate
        music_query = params.get("music_query", "").lower()

        for i, c in enumerate(candidates):
            if music_query in c["title"].lower():
                return candidates[i]

        # fallback: first reasonable candidate
        return candidates[0]

    # --- Case 2: plain index ---
    try:
        index = int(str(llm_output).strip()) - 1
        return candidates[index]
    except Exception:
        # absolute fallback
        return candidates[0]
