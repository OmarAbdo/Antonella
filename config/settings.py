import os

# ── Audio ──────────────────────────────────────────────────────────────────────
SAMPLE_RATE = 16000
CHUNK_DURATION = 0.08
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_DURATION)

# Set to None to auto-select the best mic at startup.
# Set to an integer to pin a specific device (run diag_mic.py to find indices).
MIC_DEVICE = None

COMMAND_DURATION = 5.0
SILENCE_THRESHOLD = 0.008
SILENCE_DURATION = 1.2

# ── Wake word ──────────────────────────────────────────────────────────────────
# Change this to whatever name you want to call your assistant.
WAKE_WORD = "antonella"

# ── Whisper STT ───────────────────────────────────────────────────────────────
WHISPER_MODEL = "base"        # tiny (~150MB) | base (~300MB) | small (~500MB)
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"
WHISPER_LANGUAGE = "en"
WHISPER_BEAM_SIZE = 3

# ── TTS voice ─────────────────────────────────────────────────────────────────
# Leave empty to use the Windows default voice.
# Run this in PowerShell to list installed voices:
#   Add-Type -AssemblyName System.Speech
#   (New-Object System.Speech.Synthesis.SpeechSynthesizer).GetInstalledVoices() | % { $_.VoiceInfo.Name }
# Common values: "Microsoft Zira Desktop" (female), "Microsoft David Desktop" (male)
TTS_VOICE = ""
TTS_RATE = 1    # -10 (slowest) to 10 (fastest), 0 = default, 1 = slightly faster

# ── Apps (for "open X" command) ────────────────────────────────────────────────
# Keys are what you say, values are the executable name or full path.
APP_MAP = {
    # Code editors
    "vs code": "code",
    "vscode": "code",
    "visual studio code": "code",

    # Browsers
    "chrome": "chrome",
    "google chrome": "chrome",
    "firefox": "firefox",
    "edge": "msedge",
    "microsoft edge": "msedge",

    # Office
    "word": "winword",
    "microsoft word": "winword",
    "excel": "excel",
    "microsoft excel": "excel",
    "powerpoint": "powerpnt",
    "microsoft powerpoint": "powerpnt",
    "outlook": "outlook",
    "microsoft outlook": "outlook",

    # Windows built-ins
    "notepad": "notepad",
    "notebook": "notepad",       # common whisper mishearing
    "note pad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "explorer": "explorer",
    "file explorer": "explorer",
    "files": "explorer",
    "paint": "mspaint",
    "task manager": "taskmgr",
    "snipping tool": "snippingtool",
    "snip": "snippingtool",

    # Terminal
    "terminal": "wt",
    "windows terminal": "wt",
    "powershell": "powershell",
    "command prompt": "cmd",
    "cmd": "cmd",

    # Apps
    "spotify": "spotify",
    "discord": "discord",
    "teams": "teams",
    "microsoft teams": "teams",
    "slack": "slack",
    "zoom": "zoom",
}

# ── Email ──────────────────────────────────────────────────────────────────────
# Default: opens your system mail client (no config needed).
# For direct sending, set EMAIL_USE_SMTP = True and fill in credentials.
EMAIL_USE_SMTP = False
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = ""
SMTP_PASSWORD = ""   # use a Gmail App Password, never your real password
EMAIL_FROM = ""

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
