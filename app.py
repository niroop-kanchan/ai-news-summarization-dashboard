import streamlit as st
import requests

st.set_page_config(page_title="AI News", layout="wide")
st.title("📰 AI News Dashboard")

# Streamlit secrets ONLY
try:
    NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
except:
    st.error("❌ Add NEWS_API_KEY in Manage app → Settings → Secrets")
    st.stop()

keyword = st.text_input("🔍 Keyword:")

if st.button("🚀 Get News") and keyword:
    url = "https://newsapi.org/v2/everything"
    params = {"q": keyword, "pageSize": 5, "apiKey": NEWS_API_KEY}
    r = requests.get(url, params=params)
    articles = r.json().get("articles", [])
    
    if articles:
        for a in articles[:3]:
            st.write(f"**{a['title']}** - {a.get('source', {}).get('name', '')}")
    else:
        st.error("No news found")
