def format_signal_result(result: dict) -> str:
    return (
        f"🧠 News Sentiment: {result['news_sentiment']}\n"
        f"📊 RSI: {result['rsi']}\n"
        f"📈 Technical Signal: {result['tech_signal']}\n"
        f"✅ Final Signal: {result['final_signal']}\n\n"
        + "\n".join([f"- {h}" for h in result['headlines']])
    )
