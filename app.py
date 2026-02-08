import streamlit as st
import requests
from transformers import pipeline

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="AI News Summarization Dashboard",
    page_icon="📰",
    layout="wide"
)

st.title("📰 AI News Summarization Dashboard")
st.write("Enter a **keyword** and get summarized news instantly.")

# -------------------------------
# Get API Key from Streamlit Secrets
# -------------------------------
try:
    NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
except KeyError:
    st.error("NEWS_API_KEY not found. Please add it in Streamlit Secrets.")
    st.stop()

# -------------------------------
# Load Summarization Model
# -------------------------------
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

summarizer = load_summarizer()

# -------------------------------
# User Input
# -------------------------------
keyword = st.text_input("🔍 Enter keyword (e.g. AI, Technology, India, Space):")

country = st.selectbox("🌍 Select Country", ["in", "us", "gb"])
category = st.selectbox("📂 Select Category", ["technology", "business", "science", "health", "sports"])

# -------------------------------
# Fetch News Function
# -------------------------------
def fetch_news(keyword, country, category):
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "q": keyword,
        "country": country,
        "category": category,
        "apiKey": NEWS_API_KEY,
        "pageSize": 5
    }
    response = requests.get(url, params=params)
    return response.json()

# -------------------------------
# Summarize Text Function
# -------------------------------
def summarize_text(text):
    summary = summarizer(
        text,
        max_length=130,
        min_length=40,
        do_sample=False
    )
    return summary[0]["summary_text"]

# -------------------------------
# Button Action
# -------------------------------
if st.button("🧠 Get News Summary"):
    if not keyword.strip():
        st.warning("Please enter a keyword.")
    else:
        with st.spinner("Fetching and summarizing news..."):
            data = fetch_news(keyword, country, category)

            if data.get("status") != "ok" or not data.get("articles"):
                st.error("No articles found for this keyword.")
            else:
                for i, article in enumerate(data["articles"], 1):
                    st.subheader(f"{i}. {article['title']}")

                    content = article.get("content") or article.get("description")

                    if content:
                        summary = summarize_text(content)
                        st.write("**📝 Summary:**")
                        st.success(summary)
                    else:
                        st.warning("No content available to summarize.")

                    st.markdown(f"[🔗 Read full article]({article['url']})")
                    st.divider()
