# market_summary.py
import requests

def get_market_summary():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url)
    data = response.json()

    sorted_data = sorted(data, key=lambda x: float(x["priceChangePercent"]), reverse=True)

    top_gainers = sorted_data[:3]
    top_losers = sorted_data[-3:]

    return top_gainers, top_losers

def format_market_summary(gainers, losers):
    message = "📊 *Günlük Market Özeti*\n\n"
    message += "🚀 *En Çok Yükselenler:*\n"
    for coin in gainers:
        message += f"• {coin['symbol']}: +{float(coin['priceChangePercent']):.2f}%\n"

    message += "\n📉 *En Çok Düşenler:*\n"
    for coin in losers:
        message += f"• {coin['symbol']}: {float(coin['priceChangePercent']):.2f}%\n"

    message += "\n🕘 Bu özet her gün saat 21:00'de otomatik gönderilir."
    return message
