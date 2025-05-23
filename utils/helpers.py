def format_signal_result(result):
    return (
        f"🧠 News Sentiment: {result['news_sentiment']}\n"
        f"📈 Technical Signal: {result['technical_signal']}\n"
        f"✅ Final Signal: {result['final_signal']}"
    )
