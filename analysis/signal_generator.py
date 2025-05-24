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

    # Fiyat, Entry, SL, TP
    try:
        price_url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin.upper()}"
        price_response = requests.get(price_url, timeout=10)
        price = float(price_response.json().get("price", 0))

        entry = round(price, 4)
        stop_loss = round(price * 0.97, 4)
        take_profit = round(price * 1.05, 4)
    except Exception as e:
        print(f"Price fetch error: {e}")
        price = "N/A"
        entry = stop_loss = take_profit = "N/A"

    # Kaldıraç önerisi
    if final_signal == "BUY" or final_signal == "SELL":
        leverage = "x5 – Uygun risk, dikkatli ol."
    else:
        leverage = "x1 – Net sinyal yok, düşük risk önerilir."

    # AI Comment
    try:
        prompt = f"""
Coin: {coin}
Haber duyarlılığı: {news_result['sentiment']}
Teknik sinyal: {tech_result['signal']}
Genel öneri: {final_signal}

Yatırımcı dostu, kısa, içten ve sade bir analiz yorumu yap. Tahminde bulunma.
"""
        chat_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen Coinspace adında bir kripto analiz asistanısın."},
                {"role": "user", "content": prompt}
            ]
        )
        ai_comment = chat_response.choices[0].message.content.strip()
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
        "leverage": leverage,
        "ai_comment": ai_comment
    }
