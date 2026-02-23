import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import torch

SAMPLE_RATE = 16000
RECORD_SECONDS = 4

# Load model once
model = WhisperModel(
    "medium",
    device="cuda",
    compute_type="float16"
)

def record_audio():
    print("🎤 Listening...")
    audio = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype=np.float32
    )
    sd.wait()
    print("done recording")
    return audio.flatten()


def speech_to_text() -> str:
    audio = record_audio()

    segments, _ = model.transcribe(
    audio,
    language="en",
    vad_filter=True,
    vad_parameters=dict(
        min_silence_duration_ms=250
    )
)


    text = " ".join(segment.text for segment in segments).strip()

    if not text:
        return ""

    return text


if __name__ == "__main__":
    text = speech_to_text()
    print("🗣️ Transcribed:", text)
