import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

DB_PATH = "data/reddit.db"
AI_CSV = "data/The Rise Of Artificial Intellegence2.csv"

st.set_page_config(
    page_title="Reddit Sentiment Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_posts():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM posts", conn)
    conn.close()
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['month'] = df['timestamp'].dt.to_period('M').astype(str)
    df['year'] = df['timestamp'].dt.year
    return df

@st.cache_data
def load_ai_trends():
    df = pd.read_csv(AI_CSV)
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if col != 'Year':
            df[col] = pd.to_numeric(df[col].astype(str).str.replace('%','').str.replace('$','').str.replace(',','').str.strip(), errors='coerce')
    return df

def analyze_live(text):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)['compound']
    if score >= 0.05:
        return score, "Positive", "🟢"
    elif score <= -0.05:
        return score, "Negative", "🔴"
    else:
        return score, "Neutral", "🟡"

df = load_posts()
ai_df = load_ai_trends()

colors = {'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#95a5a6'}

st.title("Reddit & AI Sentiment Dashboard")
st.caption("Analyzing 1,757 r/technology posts + AI industry trends")

tab1, tab2, tab3 = st.tabs(["📱 Reddit Sentiment", "🤖 AI Industry Trends", "🔍 Live Analyzer"])

with tab1:
    st.subheader("r/technology Sentiment Analysis")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Posts", f"{len(df):,}")
    col2.metric("Positive", f"{len(df[df['sentiment_label']=='Positive']):,}", "12.5%")
    col3.metric("Negative", f"{len(df[df['sentiment_label']=='Negative']):,}", "-15.4%")
    col4.metric("Neutral", f"{len(df[df['sentiment_label']=='Neutral']):,}", "72.1%")

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Sentiment breakdown")
        sentiment_counts = df['sentiment_label'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        fig1 = px.pie(
            sentiment_counts,
            names='Sentiment',
            values='Count',
            color='Sentiment',
            color_discrete_map=colors,
            hole=0.4
        )
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.markdown("#### Sentiment over time")
        monthly = df.groupby(['month', 'sentiment_label']).size().reset_index(name='count')
        monthly = monthly.sort_values('month')
        fig2 = px.line(
            monthly,
            x='month',
            y='count',
            color='sentiment_label',
            color_discrete_map=colors,
            markers=True
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20),
            xaxis_tickangle=45,
            legend_title="Sentiment"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("#### Score distribution by sentiment")
        fig3 = px.box(
            df,
            x='sentiment_label',
            y='score',
            color='sentiment_label',
            color_discrete_map=colors
        )
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20),
            showlegend=False
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        st.markdown("#### Top scoring posts")
        top_posts = df.nlargest(10, 'score')[['title', 'score', 'sentiment_label', 'comms_num']]
        top_posts.columns = ['Title', 'Score', 'Sentiment', 'Comments']
        st.dataframe(top_posts, use_container_width=True, hide_index=True)

    st.divider()

    st.markdown("#### Filter posts by sentiment")
    sentiment_filter = st.selectbox("Select sentiment", ["All", "Positive", "Negative", "Neutral"])
    filtered = df if sentiment_filter == "All" else df[df['sentiment_label'] == sentiment_filter]
    st.dataframe(
        filtered[['title', 'score', 'sentiment_label', 'sentiment_score', 'comms_num']].head(50),
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.subheader("AI Industry Trends")

    latest = ai_df.iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("AI Market Value", f"${latest['Global AI Market Value(in Billions)']:.0f}B")
    col2.metric("AI Adoption", f"{latest['AI Adoption (%)']:.0f}%")
    col3.metric("New Jobs Created", f"{latest['Estimated New Jobs Created by AI (millions)']:.1f}M")

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Global AI market value over time")
        fig4 = px.area(
            ai_df,
            x='Year',
            y='Global AI Market Value(in Billions)',
            color_discrete_sequence=['#3498db']
        )
        fig4.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig4, use_container_width=True)

    with col_b:
        st.markdown("#### AI adoption rate over time")
        fig5 = px.line(
            ai_df,
            x='Year',
            y='AI Adoption (%)',
            markers=True,
            color_discrete_sequence=['#2ecc71']
        )
        fig5.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig5, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("#### Jobs eliminated vs created by AI")
        fig6 = px.bar(
            ai_df,
            x='Year',
            y=[
                'Estimated Jobs Eliminated by AI (millions)',
                'Estimated New Jobs Created by AI (millions)'
            ],
            barmode='group',
            color_discrete_sequence=['#e74c3c', '#2ecc71'],
            text_auto=True
        )
        fig6.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20),
            legend_title="Job type"
        )
        st.plotly_chart(fig6, use_container_width=True)

    with col_d:
        st.markdown("#### AI software revenue over time")
        fig7 = px.area(
            ai_df,
            x='Year',
            y='AI Software Revenue(in Billions)',
            color_discrete_sequence=['#9b59b6']
        )
        fig7.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig7, use_container_width=True)

with tab3:
    st.subheader("Live sentiment analyzer")
    st.caption("Type any headline or text and get instant sentiment analysis")

    user_input = st.text_area(
        "Enter text to analyze",
        placeholder="e.g. This is absolutely wonderful and amazing news for everyone...",
        height=120
    )

    if st.button("Analyze sentiment", use_container_width=True):
        if user_input.strip():
            score, label, emoji = analyze_live(user_input)

            col1, col2, col3 = st.columns(3)
            col1.metric("Sentiment", f"{emoji} {label}")
            col2.metric("Compound score", f"{score:.3f}")
            col3.metric("Range", "-1.0 to +1.0")

            analyzer = SentimentIntensityAnalyzer()
            scores = analyzer.polarity_scores(user_input)

            fig8 = px.bar(
                x=['Positive', 'Neutral', 'Negative'],
                y=[scores['pos'], scores['neu'], scores['neg']],
                color=['Positive', 'Neutral', 'Negative'],
                color_discrete_map={
                    'Positive': '#2ecc71',
                    'Neutral': '#95a5a6',
                    'Negative': '#e74c3c'
                },
                text_auto='.2f'
            )
            fig8.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=20, b=20),
                showlegend=False,
                yaxis_range=[0, 1],
                xaxis_title="Sentiment",
                yaxis_title="Score"
            )
            fig8.update_traces(width=0.4)
            st.plotly_chart(fig8, use_container_width=True)
        else:
            st.warning("Please enter some text first!")