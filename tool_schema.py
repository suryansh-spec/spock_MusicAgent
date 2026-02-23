# tool_schema.py

YOUTUBE_MUSIC_AGENT_SCHEMA = {
    "name": "play_youtube_music",
    "parameters": {
        "intent": {
            "type": str,
            "allowed": [
                "play",
                "queue",
                "adjust_volume",
                "query_status",
                "stop"   # 🔒 REQUIRED
            ]
        },
        "music_query": {
            "type": str,
            "optional": True,
            "min_length": 1,
            "max_length": 200
        },
        "volume_change": {
            "type": int,
            "optional": True,
            "min": -50,
            "max": 50
        },
        "candidate_index": {
        "type": int,
        "optional": True,
        "min": 0,
        "max": 50
         }

        
    },
    "required": ["intent"]
}
