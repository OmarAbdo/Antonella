"""
Wake word detection using VAD + whisper.

Listens for speech, runs whisper when silence is detected, and fires if
"Antonella" (or a known mishearing) appears in the transcription.

Returns both the detection signal AND any command that followed the wake word
in the same utterance — so "Hey Antonella, shut down" fires immediately and
passes "shut down" to the main loop without a second recording step.
"""
import numpy as np
from config.settings import SAMPLE_RATE, CHUNK_SAMPLES, WAKE_WORD

SPEECH_THRESHOLD = 0.008

_SILENCE_CHUNKS = int(0.6 * SAMPLE_RATE / CHUNK_SAMPLES)
_MIN_SPEECH_CHUNKS = int(0.3 * SAMPLE_RATE / CHUNK_SAMPLES)
_MAX_SPEECH_CHUNKS = int(3.0 * SAMPLE_RATE / CHUNK_SAMPLES)

# All strings whisper might produce for whatever WAKE_WORD is set to
_ANTONELLA_ALIASES = {
    "antonella", "antonela", "antonell", "antoniela",
    "antenna", "anton", "antonia", "toniella", "antonio",
    "and tonal", "a tonal", "and nella",
}

def _aliases_for(wake_word: str) -> set:
    """Return the alias set for the configured wake word."""
    if wake_word.lower() == "antonella":
        return _ANTONELLA_ALIASES
    return {wake_word.lower()}


class WakeWordDetector:
    def __init__(self, transcriber):
        self._transcribe = transcriber.transcribe
        self._aliases = _aliases_for(WAKE_WORD)
        self._speech_buf = []
        self._silence_count = 0
        self._in_speech = False
        print(f"[wake] Ready (wake_word='{WAKE_WORD}', threshold={SPEECH_THRESHOLD})")

    def feed(self, chunk: np.ndarray) -> tuple[bool, str]:
        """
        Feed one 80ms float32 chunk.
        Returns (True, inline_command) when wake word is confirmed.
        inline_command is whatever was said after "Antonella" in the same breath —
        may be empty string if only the wake word was spoken.
        """
        rms = float(np.sqrt(np.mean(chunk ** 2)))
        is_speech = rms >= SPEECH_THRESHOLD

        if is_speech:
            self._silence_count = 0
            if not self._in_speech:
                self._in_speech = True
                self._speech_buf = []
            self._speech_buf.append(chunk.copy())
            if len(self._speech_buf) > _MAX_SPEECH_CHUNKS:
                self._speech_buf.pop(0)

        elif self._in_speech:
            self._silence_count += 1
            self._speech_buf.append(chunk.copy())

            if self._silence_count >= _SILENCE_CHUNKS:
                self._in_speech = False
                n = len(self._speech_buf)
                self._silence_count = 0

                if n < _MIN_SPEECH_CHUNKS:
                    self._speech_buf = []
                    return False, ""

                audio = np.concatenate(self._speech_buf)
                self._speech_buf = []

                text = self._transcribe(audio, prompt="Antonella").strip().lower()
                first_word = text.split()[0].strip(".,!?") if text.split() else ""
                print(f"[wake] heard: '{text}'")

                wake_hit = (first_word in self._aliases or
                            any(a in text[:25] for a in self._aliases))

                if wake_hit:
                    inline = self._extract_command(text)
                    print(f"[wake] confirmed — inline='{inline}'")
                    return True, inline

        return False, ""

    def _extract_command(self, text: str) -> str:
        """Strip the wake word (and any leading 'hey') and return the remainder."""
        text = text.strip().lstrip("hey, ").lstrip("hey ")
        for alias in sorted(self._aliases, key=len, reverse=True):
            idx = text.find(alias)
            if idx != -1:
                remainder = text[idx + len(alias):].lstrip(" ,.")
                return remainder
        return ""

    def reset(self):
        self._speech_buf = []
        self._silence_count = 0
        self._in_speech = False
