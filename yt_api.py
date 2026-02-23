import requests
import os

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

def search_youtube(query: str, max_results: int = 5):
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("YOUTUBE_API_KEY not set")

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": api_key
    }

    r = requests.get(SEARCH_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    results = []
    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]

        results.append({
            "title": title,
            "channel": channel,
            "url": f"https://www.youtube.com/watch?v={video_id}"
        })

    return results
