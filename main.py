import time
import re

from wake import is_wake_word, strip_wake_word
from stt import speech_to_text
from yt_api import search_youtube
from tools import play_track, stop_playback, set_volume
from agent_state import STATE
from agent_llm import decide_action
from update_validator import validate_action
from tool_schema import YOUTUBE_MUSIC_AGENT_SCHEMA
import audio_state
from update_validator import ValidationError



# RULE-BASED VOLUME


def try_rule_based_volume(command_lower: str):
    match = re.search(r"\b(\d{1,3})\b", command_lower)
    if match:
        return max(0, min(100, int(match.group(1))))

    if any(w in command_lower for w in ["up", "increase", "louder"]):
        return "UP"

    if any(w in command_lower for w in ["down", "decrease", "lower", "quieter"]):
        return "DOWN"

    if any(w in command_lower for w in ["mute", "off"]):
        return 0

    return None



# CONFIG


GLOBAL_COMMANDS = {"stop", "exit", "quit"}
CURRENT_VOLUME = 80

wake_armed = False
wake_time = 0
WAKE_TIMEOUT = 5  # seconds



# COMMAND HANDLER


def handle_command(command: str):
    global CURRENT_VOLUME

    command_lower = command.lower()


    # FAST PATH: VOLUME (NO LLM)

    if any(w in command_lower for w in ["volume", "louder", "quieter", "mute"]):
        result = try_rule_based_volume(command_lower)

        if isinstance(result, int):
            CURRENT_VOLUME = result
        elif result == "UP":
            CURRENT_VOLUME = min(100, CURRENT_VOLUME + 15)
        elif result == "DOWN":
            CURRENT_VOLUME = max(0, CURRENT_VOLUME - 15)
        else:
            result = None

        if result is not None:
            set_volume(CURRENT_VOLUME)
            STATE.volume = CURRENT_VOLUME
            STATE.last_intent = "adjust_volume"
            print(f"🔊 Volume set to {CURRENT_VOLUME}%", flush=True)
            return


    #  LLM DECISION
  
    action = decide_action(command, STATE.snapshot())

    try:
        params = validate_action(action, YOUTUBE_MUSIC_AGENT_SCHEMA)
    except ValidationError:
        print("🤖 I didn't understand that as a music command.", flush=True)
        return

    intent = params["intent"]


    #  STOP

    if intent == "stop":
        print(stop_playback(), flush=True)
        STATE.now_playing = None
        STATE.last_intent = "stop"
        return

   
    #  VOLUME (LLM FALLBACK)
 
    if intent == "adjust_volume":
        delta = params.get("volume_change", 0)
        CURRENT_VOLUME = max(0, min(100, STATE.volume + delta))
        set_volume(CURRENT_VOLUME)
        STATE.volume = CURRENT_VOLUME
        STATE.last_intent = "adjust_volume"
        print(f"🔊 Volume set to {CURRENT_VOLUME}%", flush=True)
        return


    #  STATUS
    
    if intent == "query_status":
        print(f"🎶 Now playing: {STATE.now_playing}", flush=True)
        return

   
    #  PLAY (mpv ytsearch)
   
   # ----------------------------------
#  PLAY (mpv ytsearch)

    if intent == "play":
        query = params.get("music_query")
    if not query:
        print("❌ No music query.", flush=True)
        return

    try:
        results = search_youtube(query)
    except Exception as e:
        print(f"❌ YouTube API error: {e}", flush=True)
        return

    if not results:
        print("❌ No results found.", flush=True)
        return

    track = results[0]  # best match
    try:
        print(play_track(track), flush=True)
        STATE.now_playing = track["title"]
        STATE.last_intent = "play"
    except Exception:
        print("⚠️ Playback failed, agent still running.", flush=True)

    return



print("🤖 Command not supported.", flush=True)



# MAIN LOOP


def main():
    global wake_armed, wake_time

    print("Agent starting...", flush=True)

    while True:

       
        #  PLAYBACK MODE
    
        if audio_state.AUDIO_PLAYING:
            text = speech_to_text()
            if not text:
                time.sleep(0.2)
                continue

            text_lower = text.lower().strip()
            print(f"👂 Heard (during playback): {text}", flush=True)

            #  GLOBAL OVERRIDES (NO WAKE WORD)
            if "stop" in text_lower:
                print(stop_playback(), flush=True)
                STATE.now_playing = None
                continue  # stay in loop

            if "exit" in text_lower or "quit" in text_lower:
                print("👋 Shutting down.", flush=True)
                return  # 🔥 EXIT PROGRAM CLEANLY

            #  WAKE WORD COMMANDS
            if is_wake_word(text):
                remainder = strip_wake_word(text)
                if remainder:
                    print(f"🧠 Command: {remainder}", flush=True)
                    handle_command(remainder)

            time.sleep(0.2)
            continue  #  CRITICAL: DO NOT FALL THROUGH

        #  IDLE MODE
        
        text = speech_to_text()
        if not text:
            continue

        now = time.time()
        text_lower = text.lower().strip()
        print(f"👂 Heard: {text}", flush=True)

        if wake_armed and (now - wake_time > WAKE_TIMEOUT):
            wake_armed = False

        # GLOBAL
        if "stop" in text_lower:
            print(stop_playback(), flush=True)
            wake_armed = False
            continue

        if "exit" in text_lower or "quit" in text_lower:
            print("👋 Shutting down.", flush=True)
            return  #  CLEAN EXIT

        # WAKE WORD
        if not wake_armed and is_wake_word(text):
            print("🟡 Wake word detected!", flush=True)
            wake_time = now
            remainder = strip_wake_word(text)

            if remainder:
                print(f"🧠 Command: {remainder}", flush=True)
                handle_command(remainder)
            else:
                wake_armed = True
            continue

        # POST-WAKE
        if wake_armed:
            print(f"🧠 Command: {text}", flush=True)
            handle_command(text)
            wake_armed = False



if __name__ == "__main__":
    main()
