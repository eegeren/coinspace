import requests
import os
from dotenv import load_dotenv
import openai

load_dotenv()
CRYPTO_PANIC_API = os.getenv("CRYPTO_PANIC_API")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

def analyze_news(coin):
    try:
        url = f"https://cryptopanic.com/api/v1/posts/?auth_token={CRYPTO_PANIC_API}&currencies={coin}&public=true"
        response = requests.get(url, timeout=10)
        articles = response.json().get("results", [])[:5]

        headlines = [article.get("title", "No Title") for article in articles if "title" in article]

        sentiment_score = 0
        for headline in headlines:
            sentiment = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial sentiment analyzer."},
                    {"role": "user", "content": f"Determine if this news is Positive, Negative or Neutral: '{headline}'"}
                ]
            ).choices[0].message.content.strip().lower()

            if "positive" in sentiment:
                sentiment_score += 1
            elif "negative" in sentiment:
                sentiment_score -= 1

        if sentiment_score >= 2:
            final_sentiment = "Positive"
        elif sentiment_score <= -2:
            final_sentiment = "Negative"
        else:
            final_sentiment = "Neutral"

        return {
            "sentiment": final_sentiment,
            "headlines": headlines
        }

    except Exception as e:
        print(f"News analysis error: {e}")
        return {
            "sentiment": "N/A",
            "headlines": []
        }
