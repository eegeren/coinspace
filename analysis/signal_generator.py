from analysis.news_analyzer import analyze_news
from analysis.technical_analyzer import get_technical_analysis
import openai
import os
import requests

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_signal(coin):
    news_result = analyze_news(coin)
    tech_result = get_technical_analysis(coin)

    sentiment_score = 0

    if news_result["sentiment"] == "Positive":
        sentiment_score += 1
    elif news_result["sentiment"] == "Negative":
        sentiment_score -= 1

    if tech_result["signal"] == "BUY":
        sentiment_score += 1
    elif tech_result["signal"] == "SELL":
        sentiment_score -= 1

    if sentiment_score >= 2:
        final_signal = "BUY"
    elif sentiment_score <= -2:
        final_signal = "SELL"
    else:
        final_signal = "HOLD"

    # Entry, SL, TP tahmini (örnek mantık: fiyat üzerinden +/- oranlarla)
    try:
        price_url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin.upper()}"
        price_response = requests.get(price_url, timeout=10)
        price = float(price_response.json().get("price", 0))

        entry = round(price, 4)
        stop_loss = round(price * 0.97, 4)  # -3%
        take_profit = round(price * 1.05, 4)  # +5%
    except Exception as e:
        print(f"Price fetch error: {e}")
        price = "N/A"
        entry = stop_loss = take_profit = "N/A"

    # AI comment üret
    try:
        ai_prompt = f"""
Sen Coinspace adında kullanıcı dostu bir kripto analiz asistanısın.

Coin: {coin}
Haber duyarlılığı: {news_result['sentiment']}
Teknik analiz sinyali: {tech_result['signal']}
Genel öneri: {final_signal}

Kullanıcıya 1 cümleyle samimi, kısa ve analiz odaklı bir yatırım yorumu yap.
Yatırım tavsiyesi verme, sadece durumun özetini sade bir dille paylaş.
"""

        ai_comment = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen Coinspace adında bir kripto yatırım analiz asistanısın."},
                {"role": "user", "content": ai_prompt}
            ]
        ).choices[0].message.content.strip()

    except Exception as e:
        print(f"AI comment error: {e}")
        ai_comment = "N/A"

    return {
        "price": price,
        "news_sentiment": news_result["sentiment"],
        "technical_signal": tech_result["signal"],
        "final_signal": final_signal,
        "entry": entry,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "ai_comment": ai_comment
    }
