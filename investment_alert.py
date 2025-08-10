import os
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import feedparser
from telegram import Bot

# Environment variables (set in GitHub Secrets)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")  # יחיד, לא רבים

# הכנת רשימת צ׳אט איידים (רשימה עם איבר אחד או ריקה)
CHAT_IDS = [TELEGRAM_CHAT_ID] if TELEGRAM_CHAT_ID else []

bot = None
if TELEGRAM_TOKEN and CHAT_IDS:
    bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(message):
    print("Trying to send message:", message)
    if not bot:
        print("Telegram bot not configured")
        return
    for cid in CHAT_IDS:
        try:
            bot.send_message(chat_id=cid, text=message)
            print(f"Message sent to chat ID: {cid}")
        except Exception as e:
            print("Failed to send to", cid, e)

# --- Stock price via yfinance
def get_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2d")
        if len(hist) < 2:
            return None
        today_close = float(hist['Close'].iloc[-1])
        yesterday_close = float(hist['Close'].iloc[-2])
        change_pct = ((today_close - yesterday_close) / yesterday_close) * 100
        return {"ticker": ticker.upper(), "today_close": today_close, "yesterday_close": yesterday_close, "change_pct": change_pct}
    except Exception as e:
        print("get_stock_price error:", e)
        return None

# --- SEC 13F (recent)
def get_recent_13f_filings(count=10):
    try:
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=13F-HR&count={count}"
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; InvestmentAlert/1.0)'}
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        filings = []
        for row in soup.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) < 5: continue
            date_filed = cols[3].text.strip()
            company_name = cols[1].text.strip()
            link_tag = cols[1].find('a')
            filing_link = "https://www.sec.gov" + link_tag['href'] if link_tag else ""
            filings.append({"date": date_filed, "company": company_name, "link": filing_link})
        return filings
    except Exception as e:
        print("get_recent_13f_filings error:", e)
        return []

# --- Google News RSS
def get_google_news_rss(query, max_items=5):
    try:
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        news_items = []
        for entry in feed.entries[:max_items]:
            news_items.append({"title": entry.title, "link": entry.link, "published": getattr(entry, 'published', '')})
        return news_items
    except Exception as e:
        print("get_google_news_rss error:", e)
        return []

# --- SEC Form 4 (politician trades)
def get_recent_politician_trades(count=10):
    try:
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=form4&count={count}"
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; InvestmentAlert/1.0)'}
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        trades = []
        for row in soup.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) < 5: continue
            date_filed = cols[3].text.strip()
            filer = cols[1].text.strip()
            link_tag = cols[1].find('a')
            filing_link = "https://www.sec.gov" + link_tag['href'] if link_tag else ""
            trades.append({"date": date_filed, "filer": filer, "link": filing_link})
        return trades
    except Exception as e:
        print("get_recent_politician_trades error:", e)
        return []

# --- scoring
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
    return score

# --- run and optionally notify
def run_and_notify(ticker="AAPL"):
    stock_data = get_stock_price(ticker)
    filings = get_recent_13f_filings()
    news = get_google_news_rss(ticker)
    politician_trades = get_recent_politician_trades()

    score = score_opportunity(stock_data, len(filings), len(news), len(politician_trades))

    if os.getenv("APP_LANG", "en") == "he":
        message = f"🔔 הזדמנות ל-{ticker}\n"
        if stock_data:
            message += f"מחיר סגירה: {stock_data['today_close']}$\nשינוי יומי: {stock_data['change_pct']:.2f}%\n"
        else:
            message += "אין מידע מחיר\n"
        message += f"דיווחי 13F: {len(filings)}\nרכישות פוליטיקאים: {len(politician_trades)}\nחדשות אחרונות: {len(news)}\nניקוד: {score}\n\nחדשות לדוגמה:\n"
        for item in news:
            message += f"- {item['title']}\n"
    else:
        message = f"🔔 Opportunity: {ticker}\n"
        if stock_data:
            message += f"Close price: {stock_data['today_close']}$\nDaily change: {stock_data['change_pct']:.2f}%\n"
        else:
            message += "No price data\n"
        message += f"13F filings: {len(filings)}\nPolitician trades: {len(politician_trades)}\nLatest news: {len(news)}\nScore: {score}\n\nSample news:\n"
        for item in news:
            message += f"- {item['title']}\n"

    send_telegram_message(message)
    return {"ticker": ticker, "score": score}

if __name__ == "__main__":
    run_and_notify()

