"""
Speech-to-text using faster-whisper (local, offline, int8 CPU).
Uses 'base' model for accuracy on proper nouns like "Antonella".
"""
import numpy as np
from faster_whisper import WhisperModel

from config.settings import (
    WHISPER_MODEL, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE,
    WHISPER_LANGUAGE, WHISPER_BEAM_SIZE, MODELS_DIR
)

# Hint whisper toward "Antonella" — dramatically improves proper noun accuracy
_WAKE_PROMPT = "Antonella"
_COMMAND_PROMPT = "Antonella, shutdown, hibernate, open, VS Code, send email"


class Transcriber:
    def __init__(self):
        print(f"[stt] Loading whisper '{WHISPER_MODEL}' model...")
        self._model = WhisperModel(
            WHISPER_MODEL,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
            download_root=MODELS_DIR,
        )
        print("[stt] Model ready.")

    def transcribe(self, audio: np.ndarray, prompt: str = _COMMAND_PROMPT) -> str:
        """
        audio: float32 numpy array at 16kHz
        prompt: initial_prompt hint — steers whisper toward expected vocabulary
        Returns lowercase transcription string.
        """
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        segments, _ = self._model.transcribe(
            audio,
            language=WHISPER_LANGUAGE,
            beam_size=WHISPER_BEAM_SIZE,
            best_of=WHISPER_BEAM_SIZE,
            temperature=0.0,
            initial_prompt=prompt,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 300},
        )
        return " ".join(s.text.strip() for s in segments).lower().strip()

    def transcribe_wake(self, audio: np.ndarray) -> str:
        """Transcribe with a wake-word-focused prompt."""
        return self.transcribe(audio, prompt=_WAKE_PROMPT)
