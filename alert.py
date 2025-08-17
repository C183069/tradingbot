import ccxt
import time
import winsound
import requests
from datetime import datetime, timezone

# --- SETTINGS ---
symbols = ["TAO/USDT", "SEI/USDT", "SUI/USDT", "SOL/USDT",
           "LTC/USDT", "BTC/USDT", "ETH/USDT", "POL/USDT",
           "NEAR/USDT", "XRP/USDT"]
interval = 15  # seconds between checks

# Telegram config
TELEGRAM_TOKEN = "8405317760:AAHPqWN0M-4Sozxz7SpR7e7xke-eECfJwSE"
CHAT_ID = "702410253"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg}
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print("Telegram Error:", e)

# --- INIT ---
exchange = ccxt.binance()
levels = {}
triggered = {}
current_day = datetime.now(timezone.utc).date()

def load_levels():
    global levels, triggered
    levels = {}
    triggered = {}
    for sym in symbols:
        try:
            ohlcv = exchange.fetch_ohlcv(sym, timeframe="1d", limit=2)
            y_high = ohlcv[-2][2]
            y_low = ohlcv[-2][3]
            levels[sym] = {"high": y_high, "low": y_low}
            triggered[sym] = {"high": False, "low": False}
            print(f"{sym}: High={y_high} Low={y_low}")
        except Exception as e:
            print(f"Error loading {sym}: {e}")

print("Loading yesterday's levels...")
load_levels()
print("\nMonitoring started...\n")

# --- LOOP ---
while True:
    # Reset at midnight UTC
    if datetime.now(timezone.utc).date() != current_day:
        current_day = datetime.now(timezone.utc).date()
        print("\nNew day detected. Reloading levels...\n")
        load_levels()

    try:
        tickers = exchange.fetch_tickers(symbols)
    except Exception as e:
        print("Error fetching tickers:", e)
        time.sleep(interval)
        continue

    for sym in symbols:
        try:
            price = tickers[sym]['last']
            y_high = levels[sym]["high"]
            y_low = levels[sym]["low"]

            if not triggered[sym]["high"] and price >= y_high:
                msg = f"ALERT 🚨 {sym} broke DAILY HIGH {y_high} (Price: {price})"
                print(msg)
                winsound.Beep(1000, 400)
                send_telegram(msg)
                triggered[sym]["high"] = True

            if not triggered[sym]["low"] and price <= y_low:
                msg = f"ALERT 🚨 {sym} broke DAILY LOW {y_low} (Price: {price})"
                print(msg)
                winsound.Beep(600, 400)
                send_telegram(msg)
                triggered[sym]["low"] = True

        except Exception as e:
            print(f"Error {sym}: {e}")

    time.sleep(interval)