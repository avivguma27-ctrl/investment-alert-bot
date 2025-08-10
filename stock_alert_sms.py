import os
import yfinance as yf
from twilio.rest import Client

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")
TARGET_PHONE = os.getenv("TARGET_PHONE")

def send_sms(message):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    msg = client.messages.create(body=message, from_=TWILIO_PHONE, to=TARGET_PHONE)
    print(f"Sent SMS with SID: {msg.sid}")

def check_stock(ticker="AAPL"):
    print("=== Starting stock check ===")
    stock = yf.Ticker(ticker)
    hist = stock.history(period="2d")
    if len(hist) < 2:
        print("Not enough data to compare.")
        return
    today_close = hist['Close'].iloc[-1]
    yesterday_close = hist['Close'].iloc[-2]
    change_pct = ((today_close - yesterday_close) / yesterday_close) * 100
    print(f"{ticker}: Close={today_close}, Change={change_pct:.2f}%")
    if abs(change_pct) >= 2:
        msg = f"Stock Alert: {ticker} closed at ${today_close:.2f} ({change_pct:.2f}%)"
        send_sms(msg)
    else:
        print("Change less than 2%, no SMS sent.")
    print("=== Finished stock check ===")

if __name__ == "__main__":
    check_stock()
