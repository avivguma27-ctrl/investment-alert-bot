from twilio.rest import Client
import os

# נטען את הערכים מהסודות
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE")
target_number = os.getenv("TARGET_PHONE")  # המספר שלך בפורמט בינלאומי

client = Client(account_sid, auth_token)

message = client.messages.create(
    body="🔔 הבוט פועל! זהו מסר ניסיוני ב-SMS.",
    from_=twilio_number,
    to=target_number
)

print(f"Message sent! SID: {message.sid}")
