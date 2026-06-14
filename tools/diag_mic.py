"""
Microphone diagnostic: probes every input device and reports RMS signal strength.
Run this to identify which device index is your working microphone.

Usage:
    python tools/diag_mic.py
"""
import sys
import numpy as np
sys.path.insert(0, ".")

import sounddevice as sd
from config.settings import SAMPLE_RATE

print("Speak continuously while this runs...\n")
devices = sd.query_devices()
input_devices = [(i, d) for i, d in enumerate(devices) if d["max_input_channels"] > 0]

print("Testing each input device for 1.5 seconds...")
for idx, d in input_devices:
    try:
        audio = sd.rec(int(SAMPLE_RATE * 1.5), samplerate=SAMPLE_RATE,
                       channels=1, dtype="float32", device=idx)
        sd.wait()
        rms = float(np.sqrt(np.mean(audio**2)))
        peak = float(np.max(np.abs(audio)))
        name = d["name"][:50]
        marker = "  <-- has signal" if rms > 0.005 else ""
        print(f"  [{idx:2d}] {name:<50}  RMS={rms:.5f}  peak={peak:.5f}{marker}")
    except Exception as e:
        print(f"  [{idx:2d}] {d['name'][:50]:<50}  ERROR: {e}")

print("\nTo pin a specific device, set MIC_DEVICE = <index> in config/settings.py")
