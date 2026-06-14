"""
Open applications by name.
"""
import os
import shutil
import subprocess
import glob

# Common install locations for apps not on PATH
_FALLBACK_PATHS = {
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ],
    "msedge": [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ],
    "winword": [
        r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
        r"C:\Program Files\Microsoft Office\Office16\WINWORD.EXE",
    ],
    "excel": [
        r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE",
    ],
    "powerpnt": [
        r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE",
    ],
    "outlook": [
        r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\OUTLOOK.EXE",
    ],
    "spotify": [
        os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Spotify\Spotify.exe"),
    ],
    "discord": [
        os.path.expandvars(r"%LOCALAPPDATA%\Discord\app-*\Discord.exe"),
        os.path.expandvars(r"%APPDATA%\Discord\Discord.exe"),
    ],
    "teams": [
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Teams\current\Teams.exe"),
        os.path.expandvars(r"%APPDATA%\Microsoft\Teams\current\Teams.exe"),
    ],
    "zoom": [
        os.path.expandvars(r"%APPDATA%\Zoom\bin\Zoom.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Zoom\bin\Zoom.exe"),
    ],
    "slack": [
        os.path.expandvars(r"%LOCALAPPDATA%\slack\slack.exe"),
    ],
}


def _resolve(app_cmd: str) -> str | None:
    """Return a launchable path for app_cmd, or None if not found."""
    if shutil.which(app_cmd):
        return app_cmd

    for path_pattern in _FALLBACK_PATHS.get(app_cmd, []):
        # Support glob patterns (e.g. Discord's versioned folder)
        matches = glob.glob(path_pattern)
        if matches:
            return matches[-1]   # newest match
        if os.path.exists(path_pattern):
            return path_pattern

    return None


def open_app(app_cmd: str, raw_text: str = "") -> str:
    resolved = _resolve(app_cmd)

    if not resolved:
        friendly = _friendly_name(raw_text, app_cmd)
        return (
            f"I couldn't find {friendly} on this computer. "
            f"Make sure it's installed, or add its path to APP_MAP in settings."
        )

    try:
        subprocess.Popen([resolved], shell=True,
                         creationflags=subprocess.CREATE_NO_WINDOW)
        return f"Opening {_friendly_name(raw_text, app_cmd)}."
    except Exception as e:
        return f"Couldn't open {app_cmd}: {e}"


def _friendly_name(raw_text: str, app_cmd: str) -> str:
    for kw in ("open", "launch", "start", "run"):
        idx = raw_text.lower().find(kw)
        if idx != -1:
            name = raw_text[idx + len(kw):].strip(" ,.")
            if name:
                return name
    return app_cmd
