from analysis.news_analyzer import analyze_news
from analysis.technical_analyzer import get_technical_analysis

def generate_signal(coin: str) -> dict:
    news = analyze_news(coin)
    tech = get_technical_analysis(coin)

    total_score = 0
    if news["sentiment"] == "Positive":
        total_score += 1
    elif news["sentiment"] == "Negative":
        total_score -= 1

    if tech["signal"] == "Buy":
        total_score += 1
    elif tech["signal"] == "Sell":
        total_score -= 1

    if total_score >= 2:
        final = "BUY"
    elif total_score <= -2:
        final = "SELL"
    else:
        final = "HOLD"

    return {
        "news_sentiment": news["sentiment"],
        "rsi": tech["rsi"],
        "tech_signal": tech["signal"],
        "final_signal": final,
        "headlines": news["headlines"]
    }
