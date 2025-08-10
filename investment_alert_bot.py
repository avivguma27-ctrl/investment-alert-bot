import os
import yfinance as yf
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from send_email import send_email  # וודא שיש לך את המודול הזה

# רשימת טיקרס מלאה (שים את הרשימה הארוכה שלך פה, זו רק דוגמה מקוצרת)
TICKERS = [
    TICKERS = [
    "AAPL","MSFT","AMZN","GOOG","GOOGL","FB","TSLA","BRK.B","BRK.A","JNJ",
    "V","WMT","JPM","UNH","NVDA","HD","PG","MA","DIS","BAC",
    "XOM","PYPL","VZ","ADBE","CMCSA","NFLX","T","KO","PFE","NKE",
    "MRK","INTC","PEP","ABT","CVX","CSCO","ORCL","CRM","MCD","ACN",
    "COST","WFC","MDT","TXN","LLY","NEE","HON","QCOM","BMY","LOW",
    "IBM","LIN","SBUX","AMGN","CAT","GE","BKNG","CHTR","USB","INTU",
    "BLK","TMO","MO","MMM","DE","ISRG","ZTS","SPGI","CI","SYK",
    "PLD","LMT","BDX","FIS","CME","GILD","ADI","CB","VRTX","EW",
    "TJX","ATVI","CL","SHW","ICE","MET","GM","SO","ITW","GD",
    "CCI","MCO","EL","NOC","DUK","F","APD","ECL","AON","COF",
    "BSX","PGR","EMR","HCA","AIG","ALL","DD","ADP","REGN","NSC",
    "KLAC","ROST","ADSK","CTSH","EXC","MNST","A","LRCX","MAR","EA",
    "ETN","BIIB","CERN","APH","MCK","MET","MPC","EOG","VLO","KMB",
    "FISV","DHR","BK","BDX","DG","MMC","WBA","TEL","XEL","ORLY",
    "HSY","AFL","KMI","HES","RMD","AEE","ZBRA","VAR","GLW","CINF",
    "FFIV","HOLX","NUE","WRB","CTAS","OKE","PH","AEP","HIG","PSA",
    "NTRS","MTD","TRV","VRSK","STZ","EVRG","WLTW","ABMD","XYL","HWM",
    "PEG","XLNX","LVS","CAG","ESS","XRX","ALGN","SNPS","FLT","MHK",
    "SWK","CBOE","ALB","SRE","ANSS","FTNT","DLR","FMC","TDG","PPL",
    "CNC","HAS","GL","MRO","BKR","NWSA","HLT","MSCI","D","DDOG","DOV",
    "ZBH","TT","WEC","GPN","MGM","XL","HST","TRMB","K","CTXS","COO",
    "GRMN","HPE","ED","PBCT","LYB","ROK","VTR","MCO","VRSN","LDOS","NTAP",
    "DTE","INFO","CHRW","EFX","CTRA","MCK","PHM","FRC","SWKS","MTB",
    "OKE","XYL","PEG","PNC","EIX","EBAY","CMA","ALXN","DGX","HBI","LHX",
    "BAX","TTWO","AKAM","ODFL","PXD","WDC","LEN","ORCL","SYY","STX",
    "CDNS","ZBH","TT","WEC","GPN","MGM","XL","HST","TRMB","K","CTXS",
    "COO","GRMN","HPE","ED","PBCT","LYB","ROK","VTR","VRSN","LDOS","NTAP",
    "DTE","INFO","CHRW","EFX","CTRA","MCK","PHM","FRC","SWKS","MTB",
    "OKE","XYL","PEG","PNC","EIX","EBAY","CMA","ALXN","DGX","HBI","LHX",
    "BAX","TTWO","AKAM","ODFL","PXD","WDC","LEN","ORCL","SYY","STX",
    "CDNS","ALGN","VMC","HSIC","PAYX","CTAS","MTCH","CPRT","L","CE","KEYS",
    "IT","DHI","CAG","RSG","WAB","HUM","DXC","RJF","ES","NDAQ","CERN",
    "WMB","CLX","ODFL","COG","FANG","JBHT","IRM","NWL","GL","CE","CTXS",
    "MKC","IEX","MCHP","XEL","SIVB","MOS","BWA","WEC","CBOE","VRSK","MAS",
    "SNA","WLTW","MS","FANG","STX","TXT","HCA","APH","TTWO","CDW","RHI",
    "VFC","EXPE","ULTA","MSCI","NLOK","OMC","RCL","FANG","WLTW","CAG","GWW",
    "ALGN","LH","HES","XLNX","CMS","ALB","PAYC","MTCH","CE","XEL","RMD","ES",
    "A","MKTX","LEN","VMC","XLNX","HPE","CMA","DLTR","TRMB","CNP","PPG","EVRG",
    "ANET","HSIC","DRE","TDG","HPE","KSU","EFX","KIM","OKE","NWS","HWM","MKC",
    "PKI","ARE","NDAQ","WDC","RJF","CMA","BEN","CTSH","BKR","LH","HIG","DHI",
    "WEC","PHM","VTR","WY","OKE","LNT","CHRW","GPC","PH","AIZ","CNP","AVY",
    "DHI","PPL","WELL","AKAM","VAR","CTRA","MRO","PSX","TRMB","APA","KEYS",
    "ALXN","XEL","MTD","RMD","XLNX","XYL","NTRS","VMC","EFX","HWM","ODFL","CNP",
    "OKE","IDXX","WRK","KSU","XEL","AMCR","PEAK","TTWO","XYL","IDXX","AOS",
    "TXT","WYNN","GLW","BXP","FLS","FANG","PEP","CTAS","PFG","FANG","KEYS",
    "XLNX","NUE","PEG","CDW","JKHY","EBAY","LKQ","DXC","CTAS","RMD","VRSK","TRMB",
    "WMB","MCO","DXC","CDNS","CDW","AKAM","KEYS","CHTR","CDW","FAST","TDG","RSG",
    "CNP","ARE","CLX","ETN","CFG","AEE","KEYS","KSU","ED","PKI","PEAK","FANG",
    "SIVB","SRE","XYL","ALXN","PNC","AMT","WLTW","AEE","PEG","MCHP","VLO","XYL",
    "A","ADM","BLL","WEC","WM","WMB","EXPE","LUV","ODFL","FANG","TROW","NUE",
    "IDXX","AVB","CMA","PKG","DHI","CTAS","XEL","MTD","PAYC","CLX","FANG","WLTW",
    "O","MSCI","EXC","DGX","DTE","OKE","NLSN","IRM","XLNX","MTD","BWA","PEG",
    "TRMB","HUM","CSX","CLX","PRGO","GPN","WMB","EFX","XLNX","CTSH","WLTW","XLNX",
    "EFX","EVRG","REG","GWW","EFX","HPE","GPN","ABMD","HOLX","ZBRA","MAS","NWL",
    "VRSN","GLW","JKHY","VMC","WMB","PPG","BBY","WRB","CDW","MTD","PPG","AEE",
    "NUE","PPL","PEP","PKI","XYL","NTRS","WMB","PFG","DD","AEE","DOV","XLNX",
    "PNC","PFG","XYL","BXP","PHM","PEG","AMT","XYL","LEN","HWM","BXP","PHM",
    "AMCR","XYL","PHM","AVB","XYL","PHM","LEN","XYL","LEN","PHM","PEP","PEG",
    "XYL","PHM","LEN","PHM","XYL","LEN","XYL","LEN","PHM","XYL","LEN","XYL",
    # יש להוסיף עוד אם רוצים, הרשימה פה ארוכה מאוד...
]

    # ... כאן תכניס את כל הרשימה הארוכה שלך כפי שהייתה אצלך בקוד
]

analyzer = SentimentIntensityAnalyzer()

def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="60d")
        if len(hist) < 60:
            return None

        today_close = hist['Close'][-1]
        yesterday_close = hist['Close'][-2]
        change_pct = ((today_close - yesterday_close) / yesterday_close) * 100

        today_volume = hist['Volume'][-1]
        avg_volume = hist['Volume'][-30:].mean()

        ma10 = hist['Close'][-10:].mean()
        ma50 = hist['Close'][-50:].mean()

        return {
            "ticker": ticker,
            "today_close": today_close,
            "change_pct": change_pct,
            "today_volume": today_volume,
            "avg_volume": avg_volume,
            "ma10": ma10,
            "ma50": ma50,
        }
    except Exception as e:
        print(f"Error getting data for {ticker}: {e}")
        return None

def get_news_sentiment(ticker, max_items=5):
    try:
        rss_url = f"https://news.google.com/rss/search?q={ticker}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        sentiments = []
        for entry in feed.entries[:max_items]:
            title = entry.title
            vs = analyzer.polarity_scores(title)
            sentiments.append(vs['compound'])
        if sentiments:
            avg_sentiment = sum(sentiments) / len(sentiments)
        else:
            avg_sentiment = 0
        return avg_sentiment
    except Exception as e:
        print(f"Error getting news for {ticker}: {e}")
        return 0

def score_stock(stock_data, sentiment):
    score = 0

    # שינוי מחיר
    if abs(stock_data['change_pct']) > 3:
        score += 5
    if stock_data['change_pct'] > 5:
        score += 3

    # נפח מסחר
    if stock_data['today_volume'] > stock_data['avg_volume'] * 1.5:
        score += 3

    # אינדיקטור טכני
    if stock_data['ma10'] > stock_data['ma50']:
        score += 2
    else:
        score -= 1

    # סנטימנט חדשות
    if sentiment > 0.3:
        score += 3
    elif sentiment < -0.3:
        score -= 3

    return score

def main():
    target_email = os.getenv("TARGET_EMAIL")
    if not target_email:
        print("ERROR: TARGET_EMAIL environment variable is not set.")
        return

    messages = []
    for i, ticker in enumerate(TICKERS):
        print(f"Processing {i+1}/{len(TICKERS)}: {ticker}")
        stock_data = get_stock_data(ticker)
        if not stock_data:
            continue
        sentiment = get_news_sentiment(ticker)
        score = score_stock(stock_data, sentiment)

        if score >= 7:  # סף דיוק גבוה - אפשר לשנות לפי רצון
            msg = (
                f"📈 מניה: {ticker}\n"
                f"מחיר סגירה היום: {stock_data['today_close']:.2f}$\n"
                f"שינוי יומי: {stock_data['change_pct']:.2f}%\n"
                f"נפח מסחר היום: {stock_data['today_volume']}\n"
                f"נפח ממוצע 30 יום: {stock_data['avg_volume']:.0f}\n"
                f"ממוצע נע 10 יום: {stock_data['ma10']:.2f}\n"
                f"ממוצע נע 50 יום: {stock_data['ma50']:.2f}\n"
                f"סנטימנט חדשות: {sentiment:.2f}\n"
                f"ניקוד סופי: {score}\n"
                "-------------------------"
            )
            messages.append(msg)

    body = "\n\n".join(messages) if messages else "אין הזדמנויות חמות כרגע."
    send_email("דוח הזדמנויות מניות S&P 500 - מתקדמים", body, target_email)

if __name__ == "__main__":
    main()

