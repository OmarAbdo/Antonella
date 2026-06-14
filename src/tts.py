"""
TTS via PowerShell System.Speech.Synthesis.SpeechSynthesizer.

Fresh subprocess per call — no pyttsx3 reuse bug, no interference with
the sounddevice mic stream. Voice and rate are configured in settings.py.
"""
import subprocess
import threading

from config.settings import TTS_VOICE, TTS_RATE


def _build_ps_command(text: str) -> str:
    safe = text.replace("'", "''").replace('"', '""')
    voice_line = f"$s.SelectVoice('{TTS_VOICE}'); " if TTS_VOICE else ""
    return (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"{voice_line}"
        f"$s.Rate = {TTS_RATE}; "
        f"$s.Speak('{safe}')"
    )


class Speaker:
    def __init__(self, output_device=None):
        voice_info = f"voice='{TTS_VOICE}'" if TTS_VOICE else "voice=default"
        print(f"[tts] Engine ready (PowerShell SAPI, {voice_info}, rate={TTS_RATE})")

    def say(self, text: str):
        print(f"[tts] '{text}'")
        subprocess.run(
            ["powershell", "-WindowStyle", "Hidden", "-Command", _build_ps_command(text)],
            capture_output=True,
        )

    def say_async(self, text: str):
        t = threading.Thread(target=self.say, args=(text,), daemon=True)
        t.start()
        return t
