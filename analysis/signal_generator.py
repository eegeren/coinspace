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
        stop_loss = round(price * 0.97, 4)  # %3 aşağı
        take_profit = round(price * 1.05, 4)  # %5 yukarı
    except Exception as e:
        print(f"Price fetch error: {e}")
        price = "N/A"
        entry = stop_loss = take_profit = "N/A"

    # Kaldıraç önerisi
    if final_signal == "BUY":
        leverage = "5x-10x önerilir (orta risk)"
    elif final_signal == "SELL":
        leverage = "3x-5x önerilir (düşük risk)"
    else:
        leverage = "Kaldıraç önerilmez (belirsiz trend)"

    # AI Comment üretimi (kısa ve yatırımcı dostu)
    try:
        prompt = f"""
Coin: {coin}
Haber duyarlılığı: {news_result['sentiment']}
Teknik analiz sinyali: {tech_result['signal']}
Genel öneri: {final_signal}

Kullanıcı dostu, kısa, net, içten bir analiz özeti yap. Yatırım tavsiyesi verme. Tahmin yürütme.
"""
        chat_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen Coinspace adlı kullanıcı dostu bir kripto analiz asistanısın."},
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
