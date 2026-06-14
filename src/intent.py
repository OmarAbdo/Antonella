"""
Offline rule-based intent parser.
Maps a transcribed command string to (intent, params) tuples.

Intents:
    shutdown        {}
    hibernate       {"minutes": int | None}
    sleep           {"minutes": int | None}   (same as hibernate on Windows)
    open_app        {"app": str}
    send_email      {"to": str, "body": str}
    unknown         {"text": str}
"""
import re
from dataclasses import dataclass, field
from typing import Any

from config.settings import APP_MAP, WAKE_WORD


@dataclass
class Intent:
    name: str
    params: dict[str, Any] = field(default_factory=dict)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _strip_wake_word(text: str) -> str:
    """Remove 'antonella' (and common mishearings) from the start of text."""
    text = text.strip().lower()
    for prefix in (WAKE_WORD, "antenna", "antonela", "antonell", "antoniela"):
        if text.startswith(prefix):
            text = text[len(prefix):].lstrip(" ,")
            break
    return text


_WORD_TO_NUM = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20,
    "thirty": 30, "forty": 40, "forty-five": 45, "forty five": 45,
    "sixty": 60, "ninety": 90, "hundred": 100,
    "a": 1, "an": 1, "half": 0,  # "half an hour" handled separately
}

def _extract_minutes(text: str) -> int | None:
    """Pull a minute value out of text like 'in 30 minutes' or 'in two hours'."""
    # "half an hour" → 30
    if re.search(r"half\s+an?\s+hour", text):
        return 30

    # "X hour(s)" → X * 60
    m = re.search(r"(\d+|[a-z]+)\s+hours?", text)
    if m:
        raw = m.group(1)
        val = int(raw) if raw.isdigit() else _WORD_TO_NUM.get(raw)
        if val is not None:
            return val * 60

    # "X minute(s)"
    m = re.search(r"(\d+|[a-z]+)\s+min(?:ute)?s?", text)
    if m:
        raw = m.group(1)
        val = int(raw) if raw.isdigit() else _WORD_TO_NUM.get(raw)
        if val is not None:
            return val

    # bare number at end: "hibernate in 10"
    m = re.search(r"\bin\s+(\d+)\b", text)
    if m:
        return int(m.group(1))

    return None


def _extract_app(text: str) -> str | None:
    """Match app names from APP_MAP, longest match first."""
    lower = text.lower()
    # Sort by length descending so "visual studio code" beats "code"
    for key in sorted(APP_MAP.keys(), key=len, reverse=True):
        if key in lower:
            return APP_MAP[key]
    return None


_EMAIL_PATTERNS = [
    # "send an email to X saying Y"
    re.compile(r"send\s+(?:an?\s+)?email\s+to\s+(.+?)\s+(?:saying|that|with body|message)\s+(.+)", re.I),
    # "email X saying Y"
    re.compile(r"email\s+(.+?)\s+(?:saying|that|with body|message)\s+(.+)", re.I),
    # "send a message to X saying Y"
    re.compile(r"send\s+(?:a\s+)?message\s+to\s+(.+?)\s+(?:saying|that)\s+(.+)", re.I),
    # "send email to X: Y"
    re.compile(r"send\s+(?:an?\s+)?email\s+to\s+(.+?):\s+(.+)", re.I),
]


# ── Public API ─────────────────────────────────────────────────────────────────

def parse(raw_text: str) -> Intent:
    """
    Parse a raw transcription into a structured Intent.
    raw_text may or may not include the wake word.
    """
    text = _strip_wake_word(raw_text)
    lower = text.lower()

    # ── Shutdown ───────────────────────────────────────────────────────────────
    if any(kw in lower for kw in ("shut down", "shutdown", "turn off", "power off")):
        minutes = _extract_minutes(lower)
        return Intent("shutdown", {"minutes": minutes})

    # ── Hibernate ──────────────────────────────────────────────────────────────
    if any(kw in lower for kw in ("hibernate",)):
        minutes = _extract_minutes(lower)
        return Intent("hibernate", {"minutes": minutes})

    # ── Sleep ──────────────────────────────────────────────────────────────────
    if any(kw in lower for kw in ("sleep", "suspend")):
        minutes = _extract_minutes(lower)
        return Intent("sleep", {"minutes": minutes})

    # ── Restart ────────────────────────────────────────────────────────────────
    if any(kw in lower for kw in ("restart", "reboot")):
        minutes = _extract_minutes(lower)
        return Intent("restart", {"minutes": minutes})

    # ── Cancel scheduled action ────────────────────────────────────────────────
    if any(kw in lower for kw in ("cancel", "abort", "stop shutdown", "stop hibernate")):
        return Intent("cancel_shutdown", {})

    # ── Open app ───────────────────────────────────────────────────────────────
    if any(kw in lower for kw in ("open", "launch", "start", "run")):
        app = _extract_app(lower)
        if app:
            return Intent("open_app", {"app": app, "raw": lower})

    # ── Send email ─────────────────────────────────────────────────────────────
    for pattern in _EMAIL_PATTERNS:
        m = pattern.search(text)
        if m:
            return Intent("send_email", {"to": m.group(1).strip(), "body": m.group(2).strip()})

    # ── Volume shortcuts ───────────────────────────────────────────────────────
    if "mute" in lower:
        return Intent("mute", {})
    if "volume up" in lower or "turn up" in lower:
        return Intent("volume_up", {})
    if "volume down" in lower or "turn down" in lower:
        return Intent("volume_down", {})

    return Intent("unknown", {"text": text})
