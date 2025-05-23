import requests

def get_technical_analysis(coin):
    url = f"https://api.binance.com/api/v3/klines?symbol={coin}&interval=1h&limit=100"
    response = requests.get(url)
    data = response.json()

    close_prices = [float(kline[4]) for kline in data]
    deltas = [close_prices[i] - close_prices[i - 1] for i in range(1, len(close_prices))]

    gain = sum(d for d in deltas if d > 0) / 14
    loss = -sum(d for d in deltas if d < 0) / 14
    rs = gain / loss if loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))

    if rsi < 30:
        signal = "BUY"
    elif rsi > 70:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "rsi": round(rsi, 2),
        "signal": signal
    }
