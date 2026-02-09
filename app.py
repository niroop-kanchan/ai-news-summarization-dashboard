import streamlit as st
import requests
import re
from collections import Counter

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="AI News Dashboard",
    layout="wide"
)

st.title("📰 AI News Dashboard")
st.write("Search news by keyword, select an article, and generate an AI summary.")

# -------------------------
# Load API key
# -------------------------
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]

# -------------------------
# Fetch news
# -------------------------
def fetch_news(keyword):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": keyword,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 10,
        "apiKey": NEWS_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get("articles", [])

# -------------------------
# Improved AI summarization
# -------------------------
def summarize_to_points(text, max_points=6):
    if not text:
        return []

    # Clean text
    text = re.sub(r'\s+', ' ', text)
    sentences = re.split(r'(?<=[.!?]) ', text)

    # Remove very short / noisy sentences
    sentences = [
        s.strip() for s in sentences
        if len(s.split()) > 8 and not s.lower().startswith(("click", "read more"))
    ]

    # Stopwords (basic)
    stopwords = set([
        "the","is","in","and","to","of","a","for","on","with","as","by",
        "that","this","it","from","are","was","at","an"
    ])

    words = [
        w for w in re.findall(r'\w+', text.lower())
        if w not in stopwords
    ]

    freq = Counter(words)

    sentence_scores = {}
    for sentence in sentences:
        score = 0
        for word in re.findall(r'\w+', sentence.lower()):
            if word not in stopwords:
                score += freq[word]
        if score > 0:
            sentence_scores[sentence] = score

    ranked = sorted(
        sentence_scores,
        key=sentence_scores.get,
        reverse=True
    )

    return ranked[:max_points]

# -------------------------
# UI
# -------------------------
keyword = st.text_input("🔍 Enter Keyword")

if keyword:
    articles = fetch_news(keyword)

    if not articles:
        st.warning("No articles found for this keyword.")
    else:
        st.subheader("🗞️ Latest News")

        titles = [article["title"] for article in articles]

        selected_title = st.selectbox(
            "Select an article to summarize:",
            titles
        )

        selected_article = next(
            article for article in articles if article["title"] == selected_title
        )

        st.markdown("### 📄 Article Preview")
        st.write(selected_article.get("description", "No description available."))

        st.link_button(
            "🔗 Read full article",
            selected_article["url"]
        )

        if st.button("🧠 Generate AI Summary"):
            # 🔥 Combine title + description + content
            full_text = " ".join(filter(None, [
                selected_article.get("title"),
                selected_article.get("description"),
                selected_article.get("content")
            ]))

            summary_points = summarize_to_points(full_text)

            if summary_points:
                st.subheader("✅ AI Generated Summary (Key Points)")
                for i, point in enumerate(summary_points, 1):
                    st.markdown(f"• **{point}**")
            else:
                st.warning("Not enough content to generate a meaningful summary.")
