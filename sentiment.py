import sqlite3
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

DB_PATH = "data/reddit.db"

def add_sentiment():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM posts", conn)
    conn.close()

    print(f"Analyzing sentiment for {len(df)} posts...")

    analyzer = SentimentIntensityAnalyzer()

    def get_sentiment(text):
        if pd.isna(text) or text == "":
            return 0.0
        return analyzer.polarity_scores(str(text))['compound']

    def get_label(score):
        if score >= 0.05:
            return "Positive"
        elif score <= -0.05:
            return "Negative"
        else:
            return "Neutral"

    df['sentiment_score'] = df['title'].apply(get_sentiment)
    df['sentiment_label'] = df['sentiment_score'].apply(get_label)

    pos = len(df[df['sentiment_label'] == 'Positive'])
    neg = len(df[df['sentiment_label'] == 'Negative'])
    neu = len(df[df['sentiment_label'] == 'Neutral'])

    print(f"Positive: {pos} | Negative: {neg} | Neutral: {neu}")

    conn = sqlite3.connect(DB_PATH)
    df.to_sql("posts", conn, if_exists="replace", index=False)
    conn.close()

    print("Sentiment scores saved to database!")

if __name__ == "__main__":
    add_sentiment()