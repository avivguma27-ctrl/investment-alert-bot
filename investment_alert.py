import os
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import feedparser
from telegram import Bot

# קבלת הטוקן והצ'אט מהסביבה (GitHub Secrets)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(message):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("Message sent")
    except Exception as e:
        print("Failed to send telegram message:", e)

def get_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2d")
        if len(hist) < 2:
            return None
        today_close = hist['Close'][-1]
        yesterday_close = hist['Close'][-2]
        change_pct = ((today_close - yesterday_close) / yesterday_close) * 100
        return {"ticker": ticker, "today_close": today_close, "change_pct": change_pct}
    except Exception as e:
        print("Error getting stock price:", e)
        return None

def get_recent_13f_filings(count=5):
    try:
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=13F-HR&count={count}"
        headers = {'User-Agent': 'Mozilla/5.0'}
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
        return filings
    except Exception as e:
        print("Error fetching 13F filings:", e)
        return []

def get_recent_politician_trades(count=5):
    try:
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=form4&count={count}"
        headers = {'User-Agent': 'Mozilla/5.0'}
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
        return trades
    except Exception as e:
        print("Error fetching politician trades:", e)
        return []

def get_google_news(ticker, max_items=3):
    try:
        rss_url = f"https://news.google.com/rss/search?q={ticker}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        news_items = []
        for entry in feed.entries[:max_items]:
            news_items.append({"title": entry.title, "link": entry.link})
        return news_items
    except Exception as e:
        print("Error fetching news:", e)
        return []

def run_and_notify(ticker="AAPL"):
    stock_data = get_stock_price(ticker)
    filings = get_recent_13f_filings()
    politician_trades = get_recent_politician_trades()
    news = get_google_news(ticker)

    score = 0
    if stock_data and abs(stock_data.get("change_pct", 0)) > 3:
        score += 3
    score += len(filings)
    score += len(news)
    score += len(politician_trades)

    message = f"🔔 הזדמנות ל-{ticker}\n"
    if stock_data:
        message += f"מחיר סגירה: {stock_data['today_close']:.2f}$\n"
        message += f"שינוי יומי: {stock_data['change_pct']:.2f}%\n"
    message += f"דיווחי 13F: {len(filings)}\n"
    message += f"רכישות פוליטיקאים: {len(politician_trades)}\n"
    message += f"חדשות אחרונות: {len(news)}\n"
    message += f"ניקוד: {score}\n\n"

    message += "חדשות לדוגמה:\n"
    for item in news:
        message += f"- {item['title']}\n"

    send_telegram_message(message)

if __name__ == "__main__":
    run_and_notify()
