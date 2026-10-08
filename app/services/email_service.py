import smtplib
from email.message import EmailMessage
from flask import current_app


def send_password_reset_email(to_email: str, reset_url: str):
    host = current_app.config.get("SMTP_HOST")
    if not host:
        current_app.logger.warning("SMTP not configured. Password reset URL for development: %s", reset_url)
        return

    msg = EmailMessage()
    msg["Subject"] = "Reset your password"
    msg["From"] = current_app.config["SMTP_FROM_EMAIL"]
    msg["To"] = to_email
    msg.set_content(f"Use this link to reset your password: {reset_url}\n\nIf you did not request this, ignore this email.")

    with smtplib.SMTP(host, current_app.config["SMTP_PORT"], timeout=15) as server:
        if current_app.config.get("SMTP_USE_TLS"):
            server.starttls()
        username = current_app.config.get("SMTP_USERNAME")
        if username:
            server.login(username, current_app.config.get("SMTP_PASSWORD", ""))
        server.send_message(msg)
