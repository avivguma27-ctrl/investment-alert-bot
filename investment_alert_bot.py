import os
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import feedparser
from send_email import send_email

# רשימת מניות לדוגמה (אפשר להרחיב)
TICKERS = [
    "AAPL", "MSFT", "NVDA", "TSLA", "AMZN",
    "GOOG", "META", "NFLX", "INTC", "AMD",
    "IBM", "ORCL", "BABA", "DIS", "PYPL"
]

def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2d")
        if len(hist) < 2:
            return None
        today_close = hist['Close'].iloc[-1]
        yesterday_close = hist['Close'].iloc[-2]
        change_pct = ((today_close - yesterday_close) / yesterday_close) * 100
        return {
            "ticker": ticker,
            "today_close": today_close,
            "change_pct": change_pct
        }
    except Exception as e:
        print(f"Error fetching stock data for {ticker}: {e}")
        return None

def get_news(ticker, max_items=3):
    rss_url = f"https://news.google.com/rss/search?q={ticker}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    news_items = []
    for entry in feed.entries[:max_items]:
        news_items.append(entry.title)
    return news_items

def score_stock(stock_data):
    if not stock_data:
        return 0
    score = 0
    if abs(stock_data['change_pct']) > 3:
        score += 5
    if stock_data['change_pct'] > 5:
        score += 3
    return score

def main():
    target_email = os.getenv("TARGET_EMAIL")
    if not target_email:
        print("ERROR: TARGET_EMAIL is not set in environment variables.")
        return

    messages = []
    for ticker in TICKERS:
        data = get_stock_data(ticker)
        if not data:
            continue
        news = get_news(ticker)
        score = score_stock(data)
        if score >= 5:
            msg = (
                f"📈 מניה: {ticker}\n"
                f"מחיר סגירה היום: {data['today_close']:.2f}$\n"
                f"שינוי יומי: {data['change_pct']:.2f}%\n"
                f"חדשות אחרונות: {', '.join(news)}\n"
                f"ניקוד: {score}\n"
                "-------------------------"
            )
            messages.append(msg)

    body = "\n\n".join(messages) if messages else "אין הזדמנויות חמות כרגע."
    send_email("דוח הזדמנויות מניות", body, target_email)

if __name__ == "__main__":
    main()

