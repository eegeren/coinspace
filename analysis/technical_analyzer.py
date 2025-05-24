import requests
import ta
import pandas as pd

def get_technical_analysis(coin):
    try:
        symbol = coin.upper()
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
        response = requests.get(url)
        data = response.json()

        if not data or isinstance(data, dict) and data.get("code"):
            return {
                "rsi": "N/A",
                "signal": "N/A",
                "ema_trend": "N/A",
                "macd": "N/A"
            }

        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
        ])

        df["close"] = pd.to_numeric(df["close"])

        rsi = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi().iloc[-1]
        macd_diff = ta.trend.MACD(close=df["close"]).macd_diff().iloc[-1]
        ema_20 = df["close"].ewm(span=20).mean().iloc[-1]
        ema_50 = df["close"].ewm(span=50).mean().iloc[-1]

        signal = "BUY" if rsi < 30 else "SELL" if rsi > 70 else "HOLD"
        macd_trend = "Bullish" if macd_diff > 0 else "Bearish"
        ema_trend = "Uptrend" if ema_20 > ema_50 else "Downtrend"

        return {
            "rsi": round(rsi, 2),
            "signal": signal,
            "ema_trend": ema_trend,
            "macd": macd_trend
        }

    except Exception as e:
        print(f"Technical analysis error: {e}")
        return {
            "rsi": "N/A",
            "signal": "N/A",
            "ema_trend": "N/A",
            "macd": "N/A"
        }
