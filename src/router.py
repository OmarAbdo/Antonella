"""
Routes parsed intents to command modules.
"""
from src.intent import Intent
from src.commands import power, apps, email, volume

CAPABILITIES = (
    "I can help with: "
    "shutdown, hibernate, or sleep — with or without a timer in minutes. "
    "Open apps like VS Code, Chrome, Notepad, or Word. "
    "Send emails. "
    "Control volume. "
    "Just say what you need."
)


def route(intent: Intent) -> str:
    name = intent.name
    p = intent.params

    if name == "shutdown":
        return power.shutdown(p.get("minutes"))

    if name == "hibernate":
        return power.hibernate(p.get("minutes"))

    if name == "sleep":
        return power.sleep_pc(p.get("minutes"))

    if name == "restart":
        return power.restart(p.get("minutes"))

    if name == "cancel_shutdown":
        return power.cancel_shutdown()

    if name == "open_app":
        return apps.open_app(p["app"], p.get("raw", ""))

    if name == "send_email":
        return email.send_email(p["to"], p["body"])

    if name == "mute":
        return volume.mute()

    if name == "volume_up":
        return volume.volume_up()

    if name == "volume_down":
        return volume.volume_down()

    if name == "unknown":
        text = p.get("text", "").strip()
        if text:
            return f"I'm not sure how to '{text}'. {CAPABILITIES}"
        return CAPABILITIES

    return f"I don't know how to do that yet. {CAPABILITIES}"
