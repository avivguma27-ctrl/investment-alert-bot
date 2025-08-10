import os
import smtplib
from email.mime.text import MIMEText

def send_email(subject, body, to_email):
    from_email = os.getenv("GMAIL_EMAIL")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not from_email or not app_password:
        print("ERROR: Missing Gmail credentials in environment variables.")
        return

    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, app_password)
            server.sendmail(from_email, to_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)
