```
   _   _   _ _____ ___  _   _ _____ _     _        _
  / \ | \ | |_   _/ _ \| \ | | ____| |   | |      / \
 / _ \|  \| | | || | | |  \| |  _| | |   | |     / _ \
/ ___ \ |\  | | || |_| | |\  | |___| |___| |___ / ___ \
/_/   \_\_| \_| |_| \___/|_| \_|_____|_____|_____/_/   \_\
```

> **Offline. Free. Always on.**
> A voice assistant for Windows that runs entirely on your machine — no API keys, no cloud, no cost.

---

## What it can do

| Say this | What happens |
|----------|--------------|
| *"Antonella, shut down"* | Shuts down immediately |
| *"Antonella, shut down in 30 minutes"* | Schedules a shutdown |
| *"Antonella, sleep"* | Puts the PC to sleep |
| *"Antonella, sleep in 2 hours"* | Sleeps after 2 hours |
| *"Antonella, hibernate in 15 minutes"* | Hibernates after 15 min |
| *"Antonella, restart"* | Reboots the PC |
| *"Antonella, cancel"* | Cancels a scheduled shutdown |
| *"Antonella, open Chrome"* | Launches Chrome |
| *"Antonella, open VS Code"* | Launches VS Code |
| *"Antonella, open Word"* | Launches Microsoft Word |
| *"Antonella, open Spotify"* | Launches Spotify |
| *"Antonella, mute"* | Mutes system volume |
| *"Antonella, volume up"* | Increases volume |
| *"Antonella, send an email to John saying hello"* | Opens mail client |

You can say the command in the same breath as the wake word — no pause needed.

---

## Installation

**Requirements:** Python 3.10+ (tested on 3.14.3), Windows 10/11

```bash
git clone https://github.com/OmarAbdo/Antonella.git
cd Antonella
pip install -r requirements.txt
```

**First run** (downloads the Whisper base model, ~300MB):
```bash
python antonella.py
```

Or double-click `start.bat`.

---

## Configuration

All settings live in [`config/settings.py`](config/settings.py).

### Wake word

Change what name you call the assistant:

```python
WAKE_WORD = "antonella"   # say whatever you like here
```

### Voice

List installed voices in PowerShell:

```powershell
Add-Type -AssemblyName System.Speech
(New-Object System.Speech.Synthesis.SpeechSynthesizer).GetInstalledVoices() | % { $_.VoiceInfo.Name }
```

Then set the voice and speaking rate:

```python
TTS_VOICE = "Microsoft Zira Desktop"   # female — leave "" for Windows default
TTS_RATE  = 0                          # -10 (slowest) to 10 (fastest)
```

### Whisper model

Trade speed vs. accuracy:

```python
WHISPER_MODEL = "base"   # tiny (~150 MB, fastest) | base (~300 MB) | small (~500 MB, most accurate)
```

### Add apps

Map voice phrases to executables in `APP_MAP`:

```python
APP_MAP = {
    ...
    "my app": "myapp",   # or full path: r"C:\Tools\myapp.exe"
}
```

If the app is not on `PATH`, add a fallback path in `src/commands/apps.py` under `_FALLBACK_PATHS`.

---

## Architecture

```
antonella.py          ← entry point, main loop
config/settings.py    ← all user-facing configuration
src/
  audio.py            ← mic auto-selection, recording, VAD helpers
  stt.py              ← faster-whisper wrapper (offline, CPU)
  wake_word.py        ← VAD + Whisper wake word detection
  tts.py              ← PowerShell SAPI speech synthesis
  intent.py           ← rule-based intent parser
  router.py           ← routes intents to commands
  commands/
    power.py          ← shutdown / sleep / hibernate / restart / cancel
    apps.py           ← open application by name
    email.py          ← send email (mailto: or SMTP)
    volume.py         ← mute / volume up / down
tools/
  diag_mic.py         ← probe all mic devices and report signal strength
  diag_wake.py        ← live wake word detection test with RMS meter
  diag_live.py        ← full pipeline test (mic → wake → transcribe)
```

**Stack:**
- **STT** — [faster-whisper](https://github.com/SYSTRAN/faster-whisper) `base` model, int8 CPU, ~0.3–0.5s latency
- **TTS** — Windows SAPI via PowerShell subprocess (no pyttsx3 reuse bug, isolated from mic stream)
- **Wake word** — VAD energy gate → Whisper transcription → alias matching (no separate model required)
- **Intent** — pure rule-based regex/keyword parser, zero latency, no LLM

---

## Diagnostic tools

Run from the project root:

```bash
# Find your microphone device index
python tools/diag_mic.py

# Test wake word detection live
python tools/diag_wake.py

# Test the full pipeline (mic → wake → transcribe → print)
python tools/diag_live.py
```

---

## Privacy

Everything runs locally. The only network activity is the one-time model download on first run. After that, no internet connection is required.

---

## License

MIT
