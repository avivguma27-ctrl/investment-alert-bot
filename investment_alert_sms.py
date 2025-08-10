import os
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import feedparser
from twilio.rest import Client

# --- Twilio config from env secrets
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")
TARGET_PHONE = os.getenv("TARGET_PHONE")

def send_sms(message):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            body=message,
            from_=TWILIO_PHONE,
            to=TARGET_PHONE
        )
        print(f"[INFO] SMS sent! SID: {msg.sid}")
    except Exception as e:
        print(f"[ERROR] Failed to send SMS: {e}")

def get_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2d")
        if len(hist) < 2:
            print("[WARN] Not enough historical data for stock price.")
            return None
        today_close = float(hist['Close'].iloc[-1])
        yesterday_close = float(hist['Close'].iloc[-2])
        change_pct = ((today_close - yesterday_close) / yesterday_close) * 100
        print(f"[INFO] Stock {ticker}: Today close={today_close}, Change%={change_pct:.2f}")
        return {"ticker": ticker.upper(), "today_close": today_close, "yesterday_close": yesterday_close, "change_pct": change_pct}
    except Exception as e:
        print(f"[ERROR] get_stock_price error: {e}")
        return None

def get_recent_13f_filings(count=5):
    try:
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=13F-HR&count={count}"
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; InvestmentAlert/1.0)'}
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        filings = []
        for row in soup.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) < 5:
                continue
            date_filed = cols[3].text.strip()
            company_name = cols[1].text.strip()
            filings.append({"date": date_filed, "company": company_name})
        print(f"[INFO] Found {len(filings)} recent 13F filings.")
        return filings
    except Exception as e:
        print(f"[ERROR] get_recent_13f_filings error: {e}")
        return []

def get_google_news_rss(query, max_items=3):
    try:
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        news_items = []
        for entry in feed.entries[:max_items]:
            news_items.append(entry.title)
        print(f"[INFO] Found {len(news_items)} news items for query '{query}'.")
        return news_items
    except Exception as e:
        print(f"[ERROR] get_google_news_rss error: {e}")
        return []

def get_recent_politician_trades(count=5):
    try:
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=form4&count={count}"
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; InvestmentAlert/1.0)'}
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        trades = []
        for row in soup.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) < 5:
                continue
            date_filed = cols[3].text.strip()
            filer = cols[1].text.strip()
            trades.append({"date": date_filed, "filer": filer})
        print(f"[INFO] Found {len(trades)} recent politician trades.")
        return trades
    except Exception as e:
        print(f"[ERROR] get_recent_politician_trades error: {e}")
        return []

def score_opportunity(stock_data, filings_count, news_count, politician_trades_count):
    score = 0
    if stock_data and abs(stock_data.get("change_pct", 0)) > 5:
        score += 3
    if filings_count > 0:
        score += filings_count * 2
    if news_count > 0:
        score += news_count
    if politician_trades_count > 0:
        score += politician_trades_count * 2
    print(f"[INFO] Calculated opportunity score: {score}")
    return score

def run_and_notify(ticker="AAPL"):
    print("[START] Running investment alert bot...")

    stock_data = get_stock_price(ticker)
    filings = get_recent_13f_filings()
    news = get_google_news_rss(ticker)
    politician_trades = get_recent_politician_trades()

    score = score_opportunity(stock_data, len(filings), len(news), len(politician_trades))

    message = f"🔔 הזדמנות ל-{ticker}\n"
    if stock_data:
        message += f"מחיר סגירה: {stock_data['today_close']}$\n"
        message += f"שינוי יומי: {stock_data['change_pct']:.2f}%\n"
    else:
        message += "אין מידע מחיר\n"

    message += f"דיווחי 13F: {len(filings)}\n"
    message += f"רכישות פוליטיקאים: {len(politician_trades)}\n"
    message += f"חדשות אחרונות: {len(news)}\n"
    message += f"ניקוד: {score}\n\n"

    message += "חדשות לדוגמה:\n"
    for n in news:
        message += f"- {n}\n"

    try:
        send_sms(message)
    except Exception as e:
        print(f"[ERROR] Exception during send_sms: {e}")

    print("[END] Bot run complete.")

if __name__ == "__main__":
    run_and_notify()


if __name__ == "__main__":
    run_and_notify()
