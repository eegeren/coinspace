import os
import requests
from dotenv import load_dotenv

load_dotenv()
CRYPTO_PANIC_API_KEY = os.getenv("CRYPTO_PANIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def analyze_news(coin: str) -> dict:
    import openai
    openai.api_key = OPENAI_API_KEY

    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={CRYPTO_PANIC_API_KEY}&currencies={coin}&public=true"
    response = requests.get(url)
    data = response.json()

    headlines = []
    sentiment_score = 0
    analyzed_count = 0

    for post in data.get("results", [])[:5]:
        title = post.get("title", "")
        if not title:
            continue
        headlines.append(title)
        prompt = f"Haber: {title}\nBu haber {coin} hakkında olumlu mu, olumsuz mu, yoksa tarafsız mı? Sadece tek kelimeyle cevap ver: Olumlu, Olumsuz, Tarafsız."
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            result = completion.choices[0].message.content.strip().lower()
            if "olumlu" in result:
                sentiment_score += 1
            elif "olumsuz" in result:
                sentiment_score -= 1
            analyzed_count += 1
        except Exception:
            continue

    final_sentiment = "Tarafsız"
    if sentiment_score >= 1:
        final_sentiment = "Olumlu"
    elif sentiment_score <= -1:
        final_sentiment = "Olumsuz"

    return {
        "score": sentiment_score,
        "sentiment": final_sentiment,
        "headlines": headlines
    }
