import sqlite3
import pandas as pd
import os

DB_PATH = "data/reddit.db"

def create_database():
    if os.path.exists(DB_PATH):
        print("Database already exists, skipping.")
        return

    print("Loading technology.csv...")
    df = pd.read_csv("data/technology.csv", encoding="latin-1")

    df.columns = df.columns.str.strip().str.lower()

    df = df[['title', 'score', 'id', 'url', 'comms_num', 'created', 'body', 'timestamp']].copy()
    df = df.dropna(subset=['title'])
    df['subreddit'] = 'r/technology'

    print(f"Loaded {len(df)} posts")
    print("Columns:", df.columns.tolist())

    conn = sqlite3.connect(DB_PATH)
    df.to_sql("posts", conn, if_exists="replace", index=False)
    conn.close()

    print(f"Database created at {DB_PATH}")
    print("Done!")

if __name__ == "__main__":
    create_database()