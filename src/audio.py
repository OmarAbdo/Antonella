"""
Handles microphone capture and speaker output via sounddevice.
Auto-selects the best active input/output device at startup.
"""
import numpy as np
import sounddevice as sd
import queue
import sys
import threading

from config.settings import (
    SAMPLE_RATE, CHUNK_SAMPLES, COMMAND_DURATION,
    SILENCE_THRESHOLD, SILENCE_DURATION, MIC_DEVICE
)

# Keywords in device names that indicate loopback / virtual / unwanted devices
_SKIP_NAMES = ("stereo mix", "what u hear", "wave out", "mapper", "primary sound capture")


def find_best_mic() -> int:
    """
    Pick the best mic device:
    - If MIC_DEVICE is set in settings.py, use it unconditionally.
    - Otherwise: probe all real input devices simultaneously for 1.5s,
      pick the one with highest RMS (the active mic).
    Falls back to sounddevice default if nothing works.
    """
    if MIC_DEVICE is not None:
        print(f"[audio] Using pinned mic device {MIC_DEVICE}")
        return MIC_DEVICE

    devices = sd.query_devices()
    candidates = []
    for idx, d in enumerate(devices):
        if d["max_input_channels"] < 1:
            continue
        name_lower = d["name"].lower()
        if any(skip in name_lower for skip in _SKIP_NAMES):
            continue
        candidates.append(idx)

    if not candidates:
        print("[audio] No input devices found, using default (0)")
        return 0

    # Probe all candidates in parallel threads
    results = {}
    lock = threading.Lock()

    def probe(idx):
        try:
            frames = int(SAMPLE_RATE * 1.5)
            buf = np.zeros(frames, dtype=np.float32)
            event = threading.Event()

            def _cb(indata, f, t, status):
                nonlocal buf
                n = min(f, len(buf))
                buf[:n] = indata[:n, 0]
                event.set()

            stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="float32",
                device=idx,
                blocksize=frames,
                callback=_cb,
            )
            stream.start()
            event.wait(timeout=2.5)
            stream.stop()
            stream.close()

            rms = float(np.sqrt(np.mean(buf ** 2)))
            with lock:
                results[idx] = rms
        except Exception:
            pass

    threads = [threading.Thread(target=probe, args=(i,), daemon=True) for i in candidates]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=3.0)

    if not results:
        print("[audio] All probes failed, using default (0)")
        return 0

    best = max(results, key=results.__getitem__)
    print(f"[audio] Auto-selected device {best} — '{devices[best]['name']}' (RMS={results[best]:.4f})")
    for idx, rms in sorted(results.items(), key=lambda x: -x[1]):
        print(f"         [{idx:2d}] {devices[idx]['name'][:50]:<50}  RMS={rms:.4f}")
    return best


def find_best_speaker(mic_device: int) -> int | None:
    """
    Find the output device whose name best matches the active mic device name.
    Returns None (system default) if no good match found.
    Does NOT open any streams — avoids driver crashes from rapid open/close.
    """
    devices = sd.query_devices()
    mic_name = devices[mic_device]["name"].lower() if mic_device < len(devices) else ""

    mic_words = {w for w in mic_name.split() if len(w) > 3
                 and w not in ("audio", "input", "output", "sound", "capture", "playback")}

    best_idx, best_score = None, -1
    for idx, d in enumerate(devices):
        if d["max_output_channels"] < 1:
            continue
        out_name = d["name"].lower()
        if any(skip in out_name for skip in _SKIP_NAMES):
            continue
        score = sum(1 for w in mic_words if w in out_name)
        if score > best_score:
            best_score = score
            best_idx = idx

    if best_idx is not None and best_score > 0:
        print(f"[audio] Speaker device {best_idx} — '{devices[best_idx]['name']}' (score={best_score})")
        return best_idx

    print("[audio] Speaker: using system default output")
    return None


def list_input_devices():
    devices = sd.query_devices()
    print("\nAvailable input devices:")
    for i, d in enumerate(devices):
        if d["max_input_channels"] > 0:
            print(f"  [{i}] {d['name']}")
    print()


class MicStream:
    """Continuous mic stream that yields numpy float32 chunks."""

    def __init__(self, device=None):
        self._q: queue.Queue = queue.Queue()
        self._device = device
        self._stream = None

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"[audio] {status}", file=sys.stderr)
        self._q.put(indata[:, 0].copy())

    def start(self):
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=CHUNK_SAMPLES,
            device=self._device,
            callback=self._callback,
        )
        self._stream.start()
        devices = sd.query_devices()
        name = devices[self._device]["name"] if self._device is not None else "default"
        print(f"[audio] Streaming from device {self._device} — '{name}'")

    def stop(self):
        if self._stream:
            self._stream.stop()
            self._stream.close()

    def read(self) -> np.ndarray:
        try:
            return self._q.get(timeout=1.0)
        except queue.Empty:
            return np.zeros(CHUNK_SAMPLES, dtype="float32")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()


def record_command(stream: MicStream, listen_timeout: float = 3.0) -> np.ndarray | None:
    """
    Wait up to listen_timeout seconds for speech to start, then record until
    silence. Returns float32 audio array, or None if nothing was spoken.
    """
    drain_queue(stream)

    chunk_secs = CHUNK_SAMPLES / SAMPLE_RATE
    timeout_chunks = int(listen_timeout / chunk_secs)
    max_speech_chunks = int(COMMAND_DURATION / chunk_secs)
    silence_chunks_needed = int(SILENCE_DURATION / chunk_secs)

    # Phase 1: wait for speech to start (up to listen_timeout)
    waited = 0
    while waited < timeout_chunks:
        chunk = stream.read()
        waited += 1
        rms = float(np.sqrt(np.mean(chunk ** 2)))
        if rms >= SILENCE_THRESHOLD:
            chunks = [chunk]
            break
    else:
        return None

    # Phase 2: record until silence
    silence_count = 0
    for _ in range(max_speech_chunks):
        chunk = stream.read()
        chunks.append(chunk)
        rms = float(np.sqrt(np.mean(chunk ** 2)))
        if rms >= SILENCE_THRESHOLD:
            silence_count = 0
        else:
            silence_count += 1
            if silence_count >= silence_chunks_needed:
                break

    return np.concatenate(chunks)


def drain_queue(stream: MicStream):
    """Discard all buffered audio — call after TTS to prevent echo re-triggering."""
    while not stream._q.empty():
        try:
            stream._q.get_nowait()
        except Exception:
            break
