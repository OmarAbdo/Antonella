"""
Volume control via Windows COM (pycaw not required — uses PowerShell).
"""
import subprocess


def _ps(cmd: str):
    subprocess.run(
        ["powershell", "-WindowStyle", "Hidden", "-Command", cmd],
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def mute() -> str:
    _ps(r"""
$obj = New-Object -ComObject WScript.Shell
$obj.SendKeys([char]173)
""")
    return "Muted."


def volume_up() -> str:
    _ps(r"""
$obj = New-Object -ComObject WScript.Shell
for ($i=0; $i -lt 5; $i++) { $obj.SendKeys([char]175) }
""")
    return "Volume up."


def volume_down() -> str:
    _ps(r"""
$obj = New-Object -ComObject WScript.Shell
for ($i=0; $i -lt 5; $i++) { $obj.SendKeys([char]174) }
""")
    return "Volume down."
