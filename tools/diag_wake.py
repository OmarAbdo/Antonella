"""
Wake word diagnostic: live VAD + Whisper transcription test.
Say "Antonella" and watch it transcribe. Shows RMS meter.

Usage:
    python tools/diag_wake.py
"""
import sys
import queue
import numpy as np
sys.path.insert(0, ".")

import sounddevice as sd
from src.audio import find_best_mic
from src.stt import Transcriber
from src.wake_word import WakeWordDetector
from config.settings import SAMPLE_RATE, CHUNK_SAMPLES

mic_device = find_best_mic()
print(f"\nMic: device {mic_device}")
print("Say 'Antonella' to test. Ctrl+C to stop.\n")

transcriber = Transcriber()
detector = WakeWordDetector(transcriber=transcriber)

q: queue.Queue = queue.Queue()

def callback(indata, frames, time, status):
    q.put(indata[:, 0].copy())

with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                    blocksize=CHUNK_SAMPLES, device=mic_device, callback=callback):
    while True:
        chunk = q.get()
        rms = float(np.sqrt(np.mean(chunk ** 2)))
        speech = "SPEAKING" if rms >= 0.015 else "       "
        print(f"\r  RMS={rms:.4f}  {speech}", end="", flush=True)

        fired, inline_cmd = detector.feed(chunk)
        if fired:
            print(f"\n>>> WAKE WORD DETECTED  inline='{inline_cmd}' <<<\n")
            detector.reset()
