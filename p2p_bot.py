import json
import time
import requests
import hmac
import hashlib
import os

# Загружаем конфиг
with open("config.json") as config_file:
    config = json.load(config_file)

BINANCE_API_KEY = config["BINANCE_API_KEY"]
BINANCE_SECRET_KEY = config["BINANCE_SECRET_KEY"]
TELEGRAM_BOT_TOKEN = config["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = config["TELEGRAM_CHAT_ID"]
TRADE_AMOUNT = config["TRADE_AMOUNT"]
MAX_BALANCE_PERCENT = config["MAX_BALANCE_PERCENT"]
PROFIT_THRESHOLD = config["PROFIT_THRESHOLD"]
FIAT = config["FIAT"] if isinstance(config["FIAT"], list) else [config["FIAT"]]
AUTO_UPDATE = config["AUTO_UPDATE"]

# Функция отправки сообщений в Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

# Функция получения P2P-цен Binance
def get_p2p_prices(trade_type):
    best_deal = None
    for currency in FIAT:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        data = {
            "asset": "USDT",
            "tradeType": trade_type,
            "fiat": currency,
            "page": 1,
            "rows": 10
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            prices = response.json().get("data", [])
            if prices:
                best_price = float(prices[0]["adv"]["price"])
                if best_deal is None or (trade_type == "BUY" and best_price < best_deal["price"]) or (trade_type == "SELL" and best_price > best_deal["price"]):
                    best_deal = {"price": best_price, "fiat": currency}
    return best_deal

# Функция покупки USDT
def buy_usdt():
    best_deal = get_p2p_prices("BUY")
    if not best_deal:
        send_telegram_message("❌ Нет доступных предложений на покупку USDT.")
        return

    best_price = best_deal["price"]
    currency = best_deal["fiat"]
    send_telegram_message(f"🔍 Лучшая цена покупки: {best_price} {currency} за 1 USDT")

# Функция продажи USDT
def sell_usdt():
    best_deal = get_p2p_prices("SELL")
    if not best_deal:
        send_telegram_message("❌ Нет доступных предложений на продажу USDT.")
        return

    best_price = best_deal["price"]
    currency = best_deal["fiat"]
    send_telegram_message(f"💰 Лучшая цена продажи: {best_price} {currency} за 1 USDT")

# Функция автообновления
def update_bot():
    if AUTO_UPDATE:
        send_telegram_message("Обновление бота... 🔄")
        os.system("git pull origin main")
        send_telegram_message("Бот обновлён! Перезапускаем... ✅")
        os.system("python3 p2p_bot.py")

# Главный цикл бота
def main():
    send_telegram_message("🤖 P2P-бот запущен!")
    while True:
        buy_usdt()
        sell_usdt()
        time.sleep(60)

if __name__ == "__main__":
    update_bot()
    main()
