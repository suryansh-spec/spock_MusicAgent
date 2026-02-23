import subprocess
import os
import audio_state

MPV_BIN = "/usr/bin/mpv"

def play_track(track):
    stop_playback()

    cmd = [
        MPV_BIN,
        "--no-video",
        "--audio-device=pipewire",
        "--force-window=no",
        track["url"]
    ]

    try:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            env=os.environ.copy()
        )
        audio_state.AUDIO_PLAYING = True
        return f"▶️ Playing: {track['title']}"
    except Exception as e:
        audio_state.AUDIO_PLAYING = False
        raise RuntimeError(str(e))


def set_volume(volume: int):
    subprocess.run(
        ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{volume}%"],
        stdout=subprocess.DEVNULL
    )


def stop_playback():
    subprocess.run(
        ["pkill", "-f", MPV_BIN],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    audio_state.AUDIO_PLAYING = False
    return "⏹ Playback stopped"



import subprocess

def set_volume(volume: int):
    volume = max(0, min(100, volume))

    subprocess.run(
        ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{volume}%"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return f"🔊 Volume set to {volume}%"
