# Browser voice is the primary prototype path: Web Speech API in static/js/voice.js.
# Server-side transcription is intentionally optional because Whisper/Torch builds
# are platform-heavy. This endpoint accepts text fallback safely.
def normalize_transcript(text): return " ".join((text or "").split())
