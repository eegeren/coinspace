from analysis.news_analyzer import analyze_news
from analysis.technical_analyzer import get_technical_analysis

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

    return {
        "news_sentiment": news_result["sentiment"],
        "technical_signal": tech_result["signal"],
        "final_signal": final_signal
    }
