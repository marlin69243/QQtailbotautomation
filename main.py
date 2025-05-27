import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from ta.momentum import RSIIndicator

# --- CONFIG ---
TAIL_RATIO_THRESHOLD = 2
MIN_BODY_SIZE = 0.1
VOLUME_MULTIPLIER = 1.2
LOOKBACK_DAYS = 10
COMPARISON_DAYS = 180

# --- TELEGRAM SETTINGS ---
TELEGRAM_ENABLED = True
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("Telegram credentials not set in environment variables")

def send_telegram(message):
    if TELEGRAM_ENABLED:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"❌ Telegram error: {e}")

# --- Get Nasdaq 100 Tickers ---
def get_nasdaq_100_tickers():
    return ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AVGO", "PEP", "COST", "ADBE", "CSCO",
            "TMUS", "AMD", "NFLX", "QCOM", "TXN", "INTC", "AMAT", "HON", "SBUX", "INTU", "MDLZ", "ISRG",
            "ADI", "PYPL", "AMGN", "BKNG", "GILD", "REGN", "VRTX", "LRCX", "MRNA", "ADP", "MU", "PANW",
            "KDP", "ASML", "MNST", "FTNT", "KLAC", "SNPS", "IDXX", "CTAS", "CDNS", "MAR", "CSX", "ATVI",
            "ORLY", "AEP", "MELI", "PCAR", "CARR", "EXC", "XEL", "ADSK", "FAST", "WDAY", "DXCM", "PAYX",
            "PDD", "CRWD", "EBAY", "ODFL", "TEAM", "MRVL", "ABNB", "ZS", "CHTR", "SPLK", "LCID", "OKTA",
            "ROST", "VRSK", "SGEN", "BKR", "CTSH", "BIIB", "EA", "ANSS", "SWKS", "CPRT", "TTWO", "DLTR",
            "CEG", "VRSN", "ALGN"]

# --- Get S&P 500 Tickers ---
def get_sp500_tickers():
    return [
        "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "BRK.B", "TSLA", "UNH",
        "LLY", "JPM", "XOM", "JNJ", "V", "PG", "AVGO", "MA", "HD", "CVX",
        "MRK", "ABBV", "PEP", "COST", "ADBE", "KO", "CSCO", "WMT", "TMO", "MCD",
        "PFE", "CRM", "BAC", "ACN", "CMCSA", "LIN", "NFLX", "ABT", "ORCL", "DHR",
        "AMD", "WFC", "DIS", "TXN", "PM", "VZ", "INTU", "COP", "CAT", "AMGN",
        "NEE", "INTC", "UNP", "LOW", "IBM", "BMY", "SPGI", "RTX", "HON", "BA",
        "UPS", "GE", "QCOM", "AMAT", "NKE", "PLD", "NOW", "BKNG", "SBUX", "MS",
        "ELV", "MDT", "GS", "DE", "ADP", "LMT", "TJX", "T", "BLK", "ISRG",
        "MDLZ", "GILD", "MMC", "AXP", "SYK", "REGN", "VRTX", "ETN", "LRCX", "ADI",
        "SCHW", "CVS", "ZTS", "CI", "CB", "AMT", "SLB", "C", "BDX", "MO",
        "PGR", "TMUS", "FI", "SO", "EOG", "BSX", "CME", "EQIX", "MU", "DUK",
        "PANW", "PYPL", "AON", "SNPS", "ITW", "KLAC", "LULU", "ICE", "APD", "SHW",
        "CDNS", "CSX", "NOC", "CL", "MPC", "HUM", "FDX", "WM", "MCK", "TGT",
        "ORLY", "HCA", "FCX", "EMR", "PXD", "MMM", "MCO", "ROP", "CMG", "PSX",
        "MAR", "PH", "APH", "GD", "USB", "NXPI", "AJG", "NSC", "PNC", "VLO",
        "F", "MSI", "GM", "TT", "EW", "CARR", "AZO", "ADSK", "TDG", "ANET",
        "SRE", "ECL", "OXY", "PCAR", "ADM", "MNST", "KMB", "PSA", "CCI", "CHTR",
        "MCHP", "MSCI", "CTAS", "WMB", "AIG", "STZ", "HES", "NUE", "ROST", "AFL",
        "KVUE", "AEP", "IDXX", "D", "TEL", "JCI", "MET", "GIS", "IQV", "EXC",
        "WELL", "DXCM", "HLT", "ON", "COF", "PAYX", "TFC", "BIIB", "O", "FTNT",
        "DOW", "TRV", "DLR", "MRNA", "CPRT", "ODFL", "DHI", "YUM", "SPG", "CTSH",
        "AME", "BKR", "SYY", "A", "CTVA", "CNC", "EL", "AMP", "CEG", "HAL",
        "OTIS", "ROK", "PRU", "DD", "KMI", "VRSK", "LHX", "DG", "FIS", "CMI",
        "CSGP", "FAST", "PPG", "GPN", "GWW", "HSY", "BK", "XEL", "DVN", "EA",
        "NEM", "ED", "URI", "VICI", "PEG", "KR", "RSG", "LEN", "PWR", "WST",
        "COR", "OKE", "VMC", "KDP", "WBD", "HIG", "EFX", "MTD", "STT", "AVB",
        "KEYS", "ZBH", "RMD", "MLM", "FANG", "DLTR", "ALB", "EIX", "EXR", "ARE",
        "SBAC", "TSCO", "CDW", "CNP", "NVR", "HPE", "DGX", "BR", "TRGP", "CFG",
        "INVH", "PPL", "ETR", "TER", "AKAM", "CAG", "VTR", "WDC", "FE", "STE",
        "ESS", "PAYC", "WAT", "FRC", "NDAQ", "LNT", "CMS", "DOV", "MTCH", "HWM",
        "NDSN", "PKG", "FLT", "WRB", "BALL", "BAX", "CHD", "HOLX", "TYL", "AEE",
        "ATO", "EXPD", "MAA", "CINF", "DRI", "IT", "PHM", "BIO", "BXP", "BRO",
        "VTRS", "CTLT", "ZBRA", "SJM", "VFC", "UDR", "NTRS", "JKHY", "HBAN", "IP",
        "GRMN", "MKTX", "IPG", "TFX", "RHI", "LW", "NCLH", "BBY", "TSN", "COO",
        "FMC", "KIM", "AIZ", "REG", "OMC", "PFG", "L", "XRAY", "HBAN", "WHR",
        "ALLE", "CMA", "TFX", "BWA", "GL", "HII", "UHS", "NWL", "HAS", "PNR",
        "SEE", "BEN", "IVZ", "APA", "AAL", "ALK", "RL", "NI", "NRG", "FOX",
        "FOX", "DVA", "MHK", "NWSA", "NWS", "TPR", "DXC", "FRT", "AOS", "MOS",
        "GNRC", "ROL", "JBHT", "PNW", "CBOE", "LNC", "RJF", "HST", "WRK", "LW",
        "CPB", "K", "SNA", "CZR", "NLSN", "HBI", "HRL", "LUMN", "PVH", "LEG",
        "NWSA", "NWS", "FOX", "FOX"
    ]


# --- Get Additional Tickers ---
def get_other_tickers():
    return ["GNRC", "PTON", "DDOG", "DOCU", "ENPH", "FANG", "HAL", "TRMB", "MTCH", "T", "AA", "AEM",
            "AG", "ALB", "ALLY", "AMC", "BABA", "BAX", "BITI", "CAVA", "CCI", "CCJ", "CCL", "CHW", "CHWY",
            "CLF", "CLH", "COPX", "CSIQ", "CVNA", "DBA", "DD", "DDD", "DELL", "DIA", "DIG", "DJI", "DJT",
            "DOTUSDT", "DXY", "ELF", "EWZ", "FCG", "FL", "FSLR", "FSLY", "GIS", "GLD", "GOLD", "HPE",
            "HPQ", "HSY", "HUM", "IBKR", "IEP", "ING", "IOO", "IOZ", "IWM", "JBHT", "JBLU", "JETS", "KBH",
            "KHC", "KRE", "KWEB", "LAC", "LEN", "LULU", "LUV", "LVS", "M", "MARA", "MASI", "MBLY", "MED",
            "MJ", "MMM", "MSTR", "MTA", "NDQ", "NCLH", "NET", "NEM", "NUE", "NYCB", "OIH", "ON", "PALL",
            "PARA", "PBR", "QID", "RCL", "RDDT", "REZ", "RH", "RIOT", "RIVN", "RGLD", "RSPD", "RSPR", "SAP",
            "SCO", "SE", "SILJ", "SILVER", "SIVR", "SLB", "SLV", "SYM", "TBT", "TCEHY", "TLRY", "TLT",
            "TOL", "TREE", "TRIP", "TSM", "UAL", "UBER", "UPST", "URA", "URBN", "URNM", "US10Y", "USO",
            "USOIL", "V", "VDE", "VFS", "VGT", "VIX", "VIXY", "VST", "VXX", "VZ", "WBA", "WBD", "WDC",
            "WFC", "WHR", "WMT", "WSM", "WTI", "WYNN", "X", "XAU", "XAUUSD", "XHB", "XLE", "XLF", "XLI",
            "XOP", "XYZ"]

# --- Tail Pattern Detection ---
def detect_bottoming_tails(data, ticker):
    alerts = []
    now = datetime.now()
    one_year_ago = now - timedelta(days=LOOKBACK_DAYS)
    six_months_ago = now - timedelta(days=COMPARISON_DAYS)

    data['AvgVolume'] = data['Volume'].rolling(window=5).mean()
    data['RSI'] = RSIIndicator(close=data['Close']).rsi()

    for i in range(LOOKBACK_DAYS, len(data)):
        row = data.iloc[i]
        past_data = data.loc[(data.index < row.name) & (data.index >= six_months_ago)]
        if past_data.empty:
            continue

        o, h, l, c, v = float(row['Open']), float(row['High']), float(row['Low']), float(row['Close']), float(row['Volume'])
        body = abs(c - o)
        if body < MIN_BODY_SIZE:
            continue

        avg_vol = row['AvgVolume']
        if pd.notna(avg_vol) and v < VOLUME_MULTIPLIER * avg_vol:
            continue

        lower_wick = max(min(c, o) - l, 0)
        upper_quarter = h - (h - l) * 0.25
        close_near_high = c >= upper_quarter

        if (
            lower_wick > TAIL_RATIO_THRESHOLD * body and
            close_near_high and
            l < past_data['Low'].min() and
            row.name >= one_year_ago
        ):
            range_ = h - l
            entry = l + 0.4 * range_
            stop_loss = entry * 0.91
            take_profit = entry * 1.12

            alert = (
                f"🔹 {row.name.date()}: Bottoming Tail on {ticker} (RSI: {row['RSI']:.2f})\n"
                f"Entry: {entry:.2f}, Stop Loss: {stop_loss:.2f}, Take Profit: {take_profit:.2f}"
            )
            alerts.append(alert)

    return alerts

def detect_topping_tails(data, ticker):
    alerts = []
    now = datetime.now()
    one_year_ago = now - timedelta(days=LOOKBACK_DAYS)
    six_months_ago = now - timedelta(days=COMPARISON_DAYS)

    data['AvgVolume'] = data['Volume'].rolling(window=5).mean()
    data['RSI'] = RSIIndicator(close=data['Close']).rsi()

    for i in range(LOOKBACK_DAYS, len(data)):
        row = data.iloc[i]
        past_data = data.loc[(data.index < row.name) & (data.index >= six_months_ago)]
        if past_data.empty:
            continue

        o, h, l, c, v = float(row['Open']), float(row['High']), float(row['Low']), float(row['Close']), float(row['Volume'])
        body = abs(c - o)
        if body < MIN_BODY_SIZE:
            continue

        avg_vol = row['AvgVolume']
        if pd.notna(avg_vol) and v < VOLUME_MULTIPLIER * avg_vol:
            continue

        upper_wick = max(h - max(c, o), 0)
        lower_quarter = l + (h - l) * 0.25
        close_near_low = c <= lower_quarter

        if (
            upper_wick > TAIL_RATIO_THRESHOLD * body and
            close_near_low and
            h > past_data['High'].max() and
            row.name >= one_year_ago
        ):
            range_ = h - l
            entry = h - 0.4 * range_
            stop_loss = entry * 1.09
            take_profit = entry * 0.88

            alert = (
                f"🔻 {row.name.date()}: Topping Tail on {ticker} (RSI: {row['RSI']:.2f})\n"
                f"Entry: {entry:.2f}, Stop Loss: {stop_loss:.2f}, Take Profit: {take_profit:.2f}"
            )
            alerts.append(alert)

    return alerts

def detect_weekly_bottoming_tails(data, ticker):
    alerts = []
    now = datetime.now()
    one_year_ago = now - timedelta(days=LOOKBACK_DAYS)
    six_months_ago = now - timedelta(days=COMPARISON_DAYS)

    data['AvgVolume'] = data['Volume'].rolling(window=3).mean()
    data['RSI'] = RSIIndicator(close=data['Close']).rsi()

    for i in range(LOOKBACK_DAYS // 7, len(data)):
        row = data.iloc[i]
        past_data = data.loc[(data.index < row.name) & (data.index >= six_months_ago)]
        if past_data.empty:
            continue

        o, h, l, c, v = row['Open'], row['High'], row['Low'], row['Close'], row['Volume']
        body = abs(c - o)
        if body < MIN_BODY_SIZE:
            continue

        avg_vol = row['AvgVolume']
        if pd.notna(avg_vol) and v < VOLUME_MULTIPLIER * avg_vol:
            continue

        lower_wick = max(min(c, o) - l, 0)
        upper_quarter = h - (h - l) * 0.25
        close_near_high = c >= upper_quarter

        if (
            lower_wick > TAIL_RATIO_THRESHOLD * body and
            close_near_high and
            l < past_data['Low'].min() and
            row.name >= one_year_ago
        ):
            range_ = h - l
            entry = l + 0.4 * range_
            stop_loss = entry * 0.91
            take_profit = entry * 1.12

            alert = (
                f"📅 {row.name.date()}: Weekly Bottoming Tail on {ticker} (RSI: {row['RSI']:.2f})\n"
                f"Entry: {entry:.2f}, Stop Loss: {stop_loss:.2f}, Take Profit: {take_profit:.2f}"
            )
            alerts.append(alert)

    return alerts


def detect_weekly_topping_tails(data, ticker):
    alerts = []
    now = datetime.now()
    one_year_ago = now - timedelta(days=LOOKBACK_DAYS)
    six_months_ago = now - timedelta(days=COMPARISON_DAYS)

    data['AvgVolume'] = data['Volume'].rolling(window=3).mean()
    data['RSI'] = RSIIndicator(close=data['Close']).rsi()

    for i in range(LOOKBACK_DAYS // 7, len(data)):
        row = data.iloc[i]
        past_data = data.loc[(data.index < row.name) & (data.index >= six_months_ago)]
        if past_data.empty:
            continue

        o, h, l, c, v = row['Open'], row['High'], row['Low'], row['Close'], row['Volume']
        body = abs(c - o)
        if body < MIN_BODY_SIZE:
            continue

        avg_vol = row['AvgVolume']
        if pd.notna(avg_vol) and v < VOLUME_MULTIPLIER * avg_vol:
            continue

        upper_wick = max(h - max(c, o), 0)
        lower_quarter = l + (h - l) * 0.25
        close_near_low = c <= lower_quarter

        if (
            upper_wick > TAIL_RATIO_THRESHOLD * body and
            close_near_low and
            h > past_data['High'].max() and
            row.name >= one_year_ago
        ):
            range_ = h - l
            entry = h - 0.4 * range_
            stop_loss = entry * 1.09
            take_profit = entry * 0.88

            alert = (
                f"📅 {row.name.date()}: Weekly Topping Tail on {ticker} (RSI: {row['RSI']:.2f})\n"
                f"Entry: {entry:.2f}, Stop Loss: {stop_loss:.2f}, Take Profit: {take_profit:.2f}"
            )
            alerts.append(alert)

    return alerts


# --- Main Execution ---
def main():
    # Combine tickers, avoiding duplicates
    tickers = list(set(get_nasdaq_100_tickers() + get_sp500_tickers() + get_other_tickers()))
    all_alerts = []

    for ticker in tickers:
        print(f"Processing {ticker}...")
        try:
            # === DAILY DATA ===
            data = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True)
            data = data.dropna()

            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            if len(data) < (LOOKBACK_DAYS + 1):
                print(f"❌ Not enough daily data for {ticker}. Skipping.")
                continue

            topping_alerts = detect_topping_tails(data, ticker)
            bottoming_alerts = detect_bottoming_tails(data, ticker)
            all_alerts.extend(topping_alerts + bottoming_alerts)

            # === WEEKLY DATA ===
            weekly_data = yf.download(ticker, period="1y", interval="1wk", auto_adjust=True)
            weekly_data = weekly_data.dropna()

            if isinstance(weekly_data.columns, pd.MultiIndex):
                weekly_data.columns = weekly_data.columns.get_level_values(0)

            weekly_topping_alerts = detect_weekly_topping_tails(weekly_data, ticker)
            weekly_bottoming_alerts = detect_weekly_bottoming_tails(weekly_data, ticker)
            all_alerts.extend(weekly_topping_alerts + weekly_bottoming_alerts)

        except Exception as e:
            print(f"❌ Error processing {ticker}: {e}")
            continue

    # === ALERT OUTPUT ===
    if all_alerts:
        for alert in all_alerts:
            print(alert)
            send_telegram(alert)
    else:
        print("No tail signals detected this year.")


if __name__ == "__main__":
    main()
