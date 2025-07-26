import requests
import time
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, COINGLASS_API_KEY

def get_coinglass_data():
    url = "https://open-api.coinglass.com/public/v2/futures/longShortRate"
    headers = {"coinglassSecret": COINGLASS_API_KEY}
    params = {"symbol": "BTC", "interval": "15m"}
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        return data["data"]
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def generate_signal(data):
    if not data or "list" not in data or not data["list"]:
        return None

    ratio = float(data["list"][-1]["longShortRate"])
    price = float(data["list"][-1]["price"])

    if ratio > 1.1:
        direction = "LONG"
    elif ratio < 0.9:
        direction = "SHORT"
    else:
        return None

    sl = round(price * (0.99 if direction == "LONG" else 1.01), 2)
    tp = round(price * (1.02 if direction == "LONG" else 0.98), 2)

    return {
        "direction": direction,
        "entry": price,
        "sl": sl,
        "tp": tp
    }

def send_telegram_message(signal):
    message = (
        f"📢 *BTC 15m Signal*\n"
        f"📈 Direction: *{signal['direction']}*\n"
        f"💰 Entry: `{signal['entry']}`\n"
        f"🛑 Stop Loss: `{signal['sl']}`\n"
        f"🎯 Take Profit: `{signal['tp']}`"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Failed to send message: {e}")

def main():
    last_signal = None
    while True:
        data = get_coinglass_data()
        signal = generate_signal(data)
        if signal and signal != last_signal:
            send_telegram_message(signal)
            last_signal = signal
        time.sleep(60)  # check every minute

if __name__ == "__main__":
    main()
