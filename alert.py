import ccxt
import time
import requests
import sys
from datetime import datetime, timezone

# ================== SETTINGS ==================
symbols = ["TAOUSDT", "SEIUSDT", "SUIUSDT", "SOLUSDT", "LTCUSDT",
           "ZORAUSDT", "BTCUSDT", "ETHUSDT", "POLUSDT", "NEARUSDT", "XRPUSDT"]

TELEGRAM_TOKEN = "8405317760:AAHPqWN0M-4Sozxz7SpR7e7xke-eECfJwSE"
CHAT_ID = "702410253"

check_interval = 60  # seconds
# ==============================================

# Winsound only works on Windows
if sys.platform == "win32":
    import winsound

exchange = ccxt.binance()

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        requests.post(url, data={"chat_id": telegram_chat_id, "text": msg})
    except Exception as e:
        print("Telegram Error:", e)

def beep():
    if sys.platform == "win32":
        winsound.Beep(1000, 500)

def get_levels(symbol):
    """Fetch previous day, week, and month high/low"""
    levels = {}

    try:
        # Previous Day
        daily = exchange.fetch_ohlcv(symbol, timeframe="1d", limit=2)
        y_high = daily[-2][2]
        y_low = daily[-2][3]
        levels["day_high"] = y_high
        levels["day_low"] = y_low

        # Previous Week
        weekly = exchange.fetch_ohlcv(symbol, timeframe="1w", limit=2)
        w_high = weekly[-2][2]
        w_low = weekly[-2][3]
        levels["week_high"] = w_high
        levels["week_low"] = w_low

        # Previous Month
        monthly = exchange.fetch_ohlcv(symbol, timeframe="1M", limit=2)
        m_high = monthly[-2][2]
        m_low = monthly[-2][3]
        levels["month_high"] = m_high
        levels["month_low"] = m_low

    except Exception as e:
        print(f"Error fetching levels for {symbol}: {e}")

    return levels

def main():
    print("Starting Alert Bot...")
    levels_map = {}

    # Load all levels at start
    for sym in symbols:
        levels_map[sym] = get_levels(sym)

    while True:
        for sym in symbols:
            try:
                ticker = exchange.fetch_ticker(sym)
                price = ticker["last"]
                lv = levels_map[sym]

                # Check against stored levels
                checks = {
                    "DAILY HIGH": lv["day_high"],
                    "DAILY LOW": lv["day_low"],
                    "WEEKLY HIGH": lv["week_high"],
                    "WEEKLY LOW": lv["week_low"],
                    "MONTHLY HIGH": lv["month_high"],
                    "MONTHLY LOW": lv["month_low"],
                }

                for label, level in checks.items():
                    if price >= level and "HIGH" in label:
                        msg = f"🚨 {sym} broke {label} {level:.2f} (Price: {price:.2f})"
                        print(msg)
                        send_telegram(msg)
                        beep()
                    elif price <= level and "LOW" in label:
                        msg = f"🚨 {sym} broke {label} {level:.2f} (Price: {price:.2f})"
                        print(msg)
                        send_telegram(msg)
                        beep()

            except Exception as e:
                print(f"Error {sym}: {e}")

        # Reset levels every UTC midnight
        now = datetime.now(timezone.utc)
        if now.hour == 0 and now.minute < 5:  # within first 5 minutes of new day
            for sym in symbols:
                levels_map[sym] = get_levels(sym)

        time.sleep(check_interval)

if __name__ == "__main__":
    main()
