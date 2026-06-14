"""
Live system diagnostic: auto-selects mic and runs the full wake+transcribe pipeline.
Useful for testing all components together without launching the main assistant.

Usage:
    python tools/diag_live.py
"""
import sys
import numpy as np
sys.path.insert(0, ".")

from src.audio import MicStream, find_best_mic
from src.stt import Transcriber
from src.wake_word import WakeWordDetector

mic_device = find_best_mic()
print(f"Using mic device {mic_device}")
print("Say 'Antonella' — watch for WAKE WORD DETECTED\n")

transcriber = Transcriber()
detector = WakeWordDetector(transcriber=transcriber)

chunk_count = 0
with MicStream(device=mic_device) as mic:
    while True:
        chunk = mic.read()
        rms = float(np.sqrt(np.mean(chunk**2)))
        chunk_count += 1

        if chunk_count % 12 == 0:
            bar = "#" * min(30, int(rms * 400))
            print(f"\r  RMS={rms:.4f}  |{bar:<30}|", end="", flush=True)

        fired, inline_cmd = detector.feed(chunk)
        if fired:
            print(f"\n>>> WAKE WORD DETECTED  inline='{inline_cmd}' <<<\n")
            detector.reset()
