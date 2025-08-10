import os
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import feedparser
from telegram import Bot
from transformers import pipeline
import pandas as pd
import datetime
import time

# הגדרות בסיסיות מהסביבה
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

# מודל לניתוח סנטימנט (רגשות)
sentiment_analyzer = pipeline("sentiment-analysis")

# רשימת מניות לדוגמה
TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META",
    "BRK-B", "JPM", "V", "JNJ", "WMT", "UNH", "HD", "PG"
]

# מילות מפתח לאירועים משמעותיים
EVENT_KEYWORDS = [
    "earnings", "revenue", "profit", "lawsuit", "FDA", "approval",
    "launch", "regulation", "investigation", "acquisition", "merger"
]

def send_telegram_message(message):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("Sent Telegram message")
    except Exception as e:
        print("Telegram send failed:", e)

def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        if len(hist) < 2:
            return None
        close_prices = hist['Close']
        pct_change = ((close_prices[-1] - close_prices[-2]) / close_prices[-2]) * 100
        volume = hist['Volume'][-1]
        return {"ticker": ticker, "close": close_prices[-1], "change_pct": pct_change, "volume": volume}
    except Exception as e:
        print(f"Error fetching stock data {ticker}:", e)
        return None

def get_sec_13f_filings(count=50):
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=13F-HR&count={count}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    filings = []
    rows = soup.find_all('tr')[1:]
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 5:
            continue
        company = cols[1].text.strip()
        filings.append(company)
    return filings

def get_sec_form4_trades(count=50):
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=form4&count={count}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    trades = []
    rows = soup.find_all('tr')[1:]
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 5:
            continue
        filer = cols[1].text.strip()
        trades.append(filer)
    return trades

def fetch_news(ticker, max_items=10):
    rss_url = f"https://news.google.com/rss/search?q={ticker}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    news = []
    for entry in feed.entries[:max_items]:
        news.append({"title": entry.title, "link": entry.link})
    return news

def analyze_sentiment(text):
    result = sentiment_analyzer(text[:512])  # מגבלת אורך לטקסט
    return result[0]

def contains_event_keywords(text):
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in EVENT_KEYWORDS)

def calculate_score(stock_data, filings_count, form4_count, news, sentiments):
    score = 0
    # שינוי מחירים
    if stock_data:
        if abs(stock_data['change_pct']) > 3:
            score += 5

        if stock_data['volume'] > 1_000_000:
            score += 2

    # דיווחי 13F
    score += filings_count * 3

    # דיווחי פוליטיקאים (Form4)
    score += form4_count * 2

    # חדשות חיוביות
    positive_news = sum(1 for s in sentiments if s['label'] == 'POSITIVE' and s['score'] > 0.7)
    negative_news = sum(1 for s in sentiments if s['label'] == 'NEGATIVE' and s['score'] > 0.7)
    score += positive_news * 3
    score -= negative_news * 3

    # חדשות עם מילות מפתח חשובות
    event_news = sum(1 for n in news if contains_event_keywords(n['title']))
    score += event_news * 4

    return score

def run():
    filings_list = get_sec_13f_filings()
    form4_list = get_sec_form4_trades()

    final_messages = []

    for ticker in TICKERS:
        stock_data = get_stock_data(ticker)
        if not stock_data:
            continue

        filings_count = sum(1 for f in filings_list if ticker in f.upper())
        form4_count = sum(1 for f in form4_list if ticker in f.upper())
        news = fetch_news(ticker, max_items=10)
        sentiments = [analyze_sentiment(n['title']) for n in news]

        score = calculate_score(stock_data, filings_count, form4_count, news, sentiments)

        if score >= 7:  # סף גבוה לאפשרות טובה
            msg = f"📊 הזדמנות: {ticker}\n"
            msg += f"מחיר סגירה: {stock_data['close']:.2f}$\n"
            msg += f"שינוי יומי: {stock_data['change_pct']:.2f}%\n"
            msg += f"נפח מסחר: {stock_data['volume']}\n"
            msg += f"דיווחי 13F: {filings_count}\n"
            msg += f"רכישות פוליטיקאים: {form4_count}\n"
            msg += f"ניקוד: {score}\n\n"
            msg += "חדשות ומידע:\n"
            for n, s in zip(news, sentiments):
                msg += f"- {n['title']} [{s['label']} {s['score']:.2f}]\n"
            final_messages.append(msg)

        # זמן המתנה קטן בין מניות למנוע חסימות (אם רוצים)
        time.sleep(1)

    if final_messages:
        full_report = "\n\n".join(final_messages)
        send_telegram_message(full_report)
    else:
        send_telegram_message("אין הזדמנויות חמות כרגע.")

if __name__ == "__main__":
    run()
