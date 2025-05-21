import requests

def get_technical_analysis(coin: str) -> dict:
    symbol = coin.upper()
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
    response = requests.get(url)
    data = response.json()

    closes = [float(candle[4]) for candle in data]

    if len(closes) < 15:
        return {"rsi": None, "signal": "Not enough data"}

    delta = [closes[i+1] - closes[i] for i in range(len(closes)-1)]
    gains = sum([d for d in delta if d > 0]) / 14
    losses = abs(sum([d for d in delta if d < 0])) / 14
    rs = gains / losses if losses != 0 else 0
    rsi = 100 - (100 / (1 + rs))

    if rsi < 30:
        signal = "Buy"
    elif rsi > 70:
        signal = "Sell"
    else:
        signal = "Hold"

    return {"rsi": round(rsi, 2), "signal": signal}
