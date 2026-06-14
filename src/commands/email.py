"""
Email sending.

Default mode (EMAIL_USE_SMTP=False): opens the system default mail client
via a mailto: URI — zero configuration needed.

SMTP mode (EMAIL_USE_SMTP=True): sends via SMTP with credentials from settings.
Use a Gmail App Password, not your real password.
"""
import os
import subprocess
import smtplib
from email.mime.text import MIMEText
from urllib.parse import quote

from config.settings import (
    EMAIL_USE_SMTP, SMTP_HOST, SMTP_PORT,
    SMTP_USER, SMTP_PASSWORD, EMAIL_FROM,
)


def send_email(to: str, body: str, subject: str = "Message from Antonella") -> str:
    if EMAIL_USE_SMTP and SMTP_USER:
        return _send_smtp(to, subject, body)
    else:
        return _open_mailto(to, subject, body)


def _open_mailto(to: str, subject: str, body: str) -> str:
    """Open the default mail client with pre-filled fields."""
    uri = f"mailto:{quote(to)}?subject={quote(subject)}&body={quote(body)}"
    # Use explorer to open mailto: — works on all Windows versions
    subprocess.Popen(["explorer", uri], shell=True)
    return f"Opening your mail client to send a message to {to}."


def _send_smtp(to: str, subject: str, body: str) -> str:
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM or SMTP_USER
        msg["To"] = to

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, [to], msg.as_string())

        return f"Email sent to {to}."
    except Exception as e:
        return f"Couldn't send email: {e}"
