import streamlit as st
import requests
import os
from dotenv import load_dotenv
from transformers import pipeline

# ============================
# Load API key
# ============================
load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not NEWS_API_KEY:
    st.error("NEWS_API_KEY not found. Check your .env file.")
    st.stop()

# ============================
# App Config
# ============================
st.set_page_config(page_title="AI News Dashboard", layout="centered")
st.title("📰 AI News Summary Dashboard")
st.write("Enter a keyword and get an AI-generated summary of latest news")

# ============================
# Load Generative AI Model
# ============================
@st.cache_resource
def load_model():
    return pipeline(
        "text-generation",
        model="facebook/bart-large-cnn",
        max_new_tokens=180
    )

model = load_model()

# ============================
# Fetch News (FREE-TIER SAFE)
# ============================
def fetch_news(keyword):
    articles = []

    # 1️⃣ Try top-headlines with country (works on free tier)
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "in",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY
    }
    r = requests.get(url, params=params)
    data = r.json()
    articles = data.get("articles", [])

    # 2️⃣ Filter by keyword locally
    filtered = []
    for a in articles:
        text = f"{a.get('title','')} {a.get('description','')}".lower()
        if keyword.lower() in text:
            filtered.append(a)

    # 3️⃣ If nothing matches, fallback to everything endpoint
    if not filtered:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": keyword,
            "language": "en",
            "pageSize": 5,
            "sortBy": "publishedAt",
            "apiKey": NEWS_API_KEY
        }
        r = requests.get(url, params=params)
        data = r.json()
        filtered = data.get("articles", [])

    return filtered

# ============================
# User Input
# ============================
keyword = st.text_input(
    "Enter a keyword (e.g., India, cricket, technology, AI):"
)

# ============================
# Generate Summary
# ============================
if st.button("Get AI News Summary"):
    if not keyword.strip():
        st.warning("Please enter a keyword.")
    else:
        with st.spinner("Fetching news and generating summary..."):
            articles = fetch_news(keyword)

            if not articles:
                st.error("No articles found. Try a different keyword.")
            else:
                combined_text = ""
                for a in articles:
                    combined_text += a.get("title", "") + ". "
                    if a.get("description"):
                        combined_text += a["description"] + ". "

                prompt = f"""
                Summarize the following news related to "{keyword}"
                in 5 simple sentences:

                {combined_text}
                """

                output = model(prompt)
                summary = output[0]["generated_text"]

                st.subheader("🤖 AI Generated Summary")
                st.write(summary)

                st.subheader("🗞 Source Headlines")
                for a in articles:
                    st.write("•", a.get("title"))

# ============================
# Footer
# ============================
st.markdown("---")
st.caption("Powered by NewsAPI (Free Tier) + Generative AI")
