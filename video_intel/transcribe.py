"""Transcription step: local Whisper. Processes audio in 30s windows, so long
videos are fine. Set VIP_WHISPER_MODEL to trade speed for accuracy."""
from . import config

_MODEL = None


class TranscribeError(Exception):
    pass


def _load():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    try:
        import whisper
    except Exception as e:  # pragma: no cover
        raise TranscribeError(
            "openai-whisper not installed. Run: pip install -U openai-whisper"
        ) from e
    _MODEL = whisper.load_model(config.WHISPER_MODEL)
    return _MODEL


def transcribe(wav_path: str) -> dict:
    """Return {'text': str, 'language': str}. Original-language transcript;
    translation/cleanup is handled later by the analyzer."""
    model = _load()
    try:
        result = model.transcribe(wav_path, fp16=False)
    except Exception as e:
        raise TranscribeError(f"whisper failed: {e}") from e
    return {
        "text": (result.get("text") or "").strip(),
        "language": result.get("language") or "",
    }
