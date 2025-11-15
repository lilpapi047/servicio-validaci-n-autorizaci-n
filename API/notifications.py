import smtplib
from email.mime.text import MIMEText
import os

def send_email_mailtrap(to: str, subject: str, body: str):
    """Send email using Mailtrap SMTP."""
    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = os.getenv("EMAIL_FROM", "no-reply@example.com")
    msg["To"] = to

    try:
        with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
            server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
            server.send_message(msg)
            print(f"[Mailtrap] Email sent to {to}")
    except Exception as e:
        print(f"[Mailtrap] Failed to send email: {e}")
