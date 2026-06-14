"""
Power management: shutdown, hibernate, sleep, restart, cancel.
Uses Windows shutdown.exe for shutdown/restart (supports timers natively).
Uses PowerShell SetSuspendState for hibernate/sleep (Windows Forms API).
"""
import subprocess


def _run(cmd: list) -> bool:
    """Run a command, return True on success."""
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def _popen_hidden(ps_cmd: str):
    subprocess.Popen(
        ["powershell", "-WindowStyle", "Hidden", "-Command", ps_cmd],
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def shutdown(minutes: int | None = None) -> str:
    seconds = (minutes * 60) if (minutes and minutes > 0) else 5
    ok = _run(["shutdown", "/s", "/t", str(seconds)])
    if not ok:
        return "Shutdown failed. Try running Antonella as administrator."
    if minutes and minutes > 0:
        return f"Shutting down in {minutes} minute{'s' if minutes != 1 else ''}."
    return "Shutting down now."


def hibernate(minutes: int | None = None) -> str:
    if minutes and minutes > 0:
        seconds = minutes * 60
        _popen_hidden(
            f"Start-Sleep -Seconds {seconds}; "
            "Add-Type -AssemblyName System.Windows.Forms; "
            "[System.Windows.Forms.Application]::SetSuspendState('Hibernate', $false, $false)"
        )
        return f"Hibernating in {minutes} minute{'s' if minutes != 1 else ''}."
    ok = _run(["shutdown", "/h"])
    if not ok:
        return "Hibernate failed. Hibernate may be disabled on this PC."
    return "Hibernating now."


def sleep_pc(minutes: int | None = None) -> str:
    if minutes and minutes > 0:
        seconds = minutes * 60
        _popen_hidden(
            f"Start-Sleep -Seconds {seconds}; "
            "Add-Type -AssemblyName System.Windows.Forms; "
            "[System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)"
        )
        return f"Going to sleep in {minutes} minute{'s' if minutes != 1 else ''}."
    try:
        subprocess.run(
            ["powershell", "-Command",
             "Add-Type -AssemblyName System.Windows.Forms; "
             "[System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)"]
        )
    except Exception as e:
        return f"Sleep failed: {e}"
    return "Going to sleep."


def restart(minutes: int | None = None) -> str:
    seconds = (minutes * 60) if (minutes and minutes > 0) else 5
    ok = _run(["shutdown", "/r", "/t", str(seconds)])
    if not ok:
        return "Restart failed. Try running Antonella as administrator."
    if minutes and minutes > 0:
        return f"Restarting in {minutes} minute{'s' if minutes != 1 else ''}."
    return "Restarting now."


def cancel_shutdown() -> str:
    result = subprocess.run(["shutdown", "/a"], capture_output=True, text=True)
    if result.returncode == 0:
        return "Scheduled shutdown cancelled."
    return "No shutdown was scheduled."
