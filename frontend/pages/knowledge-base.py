import json
import urllib.error
import urllib.parse
import urllib.request

import streamlit as st


st.set_page_config(
    page_title="Knowledge Base",
    page_icon="📚",
    layout="wide"
)

API_BASE = "http://127.0.0.1:8000/knowledge-base"


st.sidebar.title("🎫 SupportAI")
st.sidebar.caption("Customer Support Console")
st.sidebar.divider()

st.sidebar.page_link(
    "app.py",
    label="Dashboard",
    icon="🏠"
)

st.sidebar.page_link(
    "pages/ticket-queue.py",
    label="Ticket Queue",
    icon="🎫"
)

st.sidebar.page_link(
    "pages/ticket-detail-suggested-reply.py",
    label="Ticket Detail & Suggested Reply",
    icon="📄"
)

st.sidebar.page_link(
    "pages/submit-bulk-upload.py",
    label="Submit / Bulk Upload",
    icon="📤"
)

st.sidebar.page_link(
    "pages/analytics.py",
    label="Analytics",
    icon="📊"
)

st.sidebar.page_link(
    "pages/knowledge-base.py",
    label="Knowledge Base",
    icon="📚"
)


st.title("📚 Knowledge Base")
st.caption("Browse support articles used to assist with customer tickets.")

search_query = st.text_input(
    "Search articles",
    placeholder="Search by title, category, or article content"
)

if search_query.strip():
    query = urllib.parse.urlencode({"q": search_query.strip()})
    articles_url = f"{API_BASE}/search?{query}"
else:
    articles_url = f"{API_BASE}/"

request = urllib.request.Request(
    articles_url,
    headers={"Accept": "application/json"}
)

try:
    with st.spinner("Loading knowledge-base articles..."):
        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:
            articles = json.loads(
                response.read().decode("utf-8")
            )

except urllib.error.HTTPError as error:
    error_body = error.read().decode(
        "utf-8",
        errors="replace"
    )

    try:
        error_data = json.loads(error_body)
        error_message = error_data.get("detail", error_body)
    except json.JSONDecodeError:
        error_message = error_body or error.reason

    st.error(
        f"Unable to load knowledge-base articles "
        f"(HTTP {error.code}): {error_message}"
    )
    st.stop()

except urllib.error.URLError as error:
    st.error(
        "Unable to connect to the FastAPI backend at "
        "http://127.0.0.1:8000. Make sure the backend is running."
    )
    st.caption(str(error.reason))
    st.stop()

except (json.JSONDecodeError, UnicodeDecodeError):
    st.error("The knowledge-base endpoint returned invalid JSON.")
    st.stop()

except Exception as error:
    st.error(f"Unable to load knowledge-base articles: {error}")
    st.stop()


if not isinstance(articles, list):
    st.error("The knowledge-base endpoint returned an unexpected response.")
    st.stop()

if not articles:
    if search_query.strip():
        st.info("No articles matched your search.")
    else:
        st.info("No knowledge-base articles are available.")
else:
    st.caption(f"{len(articles)} article(s)")

    for article in articles:
        if not isinstance(article, dict):
            continue

        title = article.get("title") or "Untitled"
        category = article.get("category")
        body = article.get("body") or ""

        with st.container(border=True):
            st.subheader(title)
            if category:
                st.caption(f"Category: {category}")
            st.write(body if body else "No article content available.")