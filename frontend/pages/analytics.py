import json
import urllib.error
import urllib.request

import streamlit as st


st.set_page_config(
    page_title="Analytics",
    page_icon="📊",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000/tickets/analytics"


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


st.title("📊 Analytics")
st.caption("Live customer support ticket analytics")
st.divider()


def get_analytics():
    request = urllib.request.Request(
        API_URL,
        headers={"Accept": "application/json"}
    )

    with urllib.request.urlopen(
        request,
        timeout=15
    ) as response:
        return json.loads(response.read().decode("utf-8"))


try:
    analytics = get_analytics()

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
        f"Unable to load analytics (HTTP {error.code}): {error_message}"
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
    st.error("The analytics endpoint returned invalid JSON.")
    st.stop()

except Exception as error:
    st.error(f"Unable to load analytics: {error}")
    st.stop()


if not isinstance(analytics, dict):
    st.error("The analytics endpoint returned an unexpected response.")
    st.stop()


categories = analytics.get("categories", [])
priorities = analytics.get("priorities", [])
sentiments = analytics.get("sentiments", [])

for name, distribution in (
    ("categories", categories),
    ("priorities", priorities),
    ("sentiments", sentiments),
):
    if not isinstance(distribution, list):
        st.error(
            f"The analytics response contains an invalid {name} summary."
        )
        st.stop()


def distribution_rows(distribution):
    rows = []

    for item in distribution:
        if not isinstance(item, dict):
            continue

        label = item.get(
            "category",
            item.get("priority", item.get("sentiment"))
        )
        count = item.get("count")

        if label is not None and isinstance(count, (int, float)):
            rows.append(
                {
                    "Name": label,
                    "Tickets": count,
                }
            )

    return rows


category_rows = distribution_rows(categories)
priority_rows = distribution_rows(priorities)
sentiment_rows = distribution_rows(sentiments)

total_tickets = analytics.get("total_tickets", "N/A")
high_priority_tickets = sum(
    row["Tickets"]
    for row in priority_rows
    if str(row["Name"]).strip().upper() in {"P1", "P2"}
)


kpi_total, kpi_high_priority, kpi_escalated = st.columns(3)

with kpi_total:
    st.metric("Total Tickets", total_tickets)

with kpi_high_priority:
    st.metric("P1/P2 High Priority Tickets", high_priority_tickets)

with kpi_escalated:
    st.metric("Escalated Tickets", "N/A")

st.caption(
    "Escalated ticket totals are not included in the existing analytics "
    "endpoint response."
)

st.divider()


st.subheader("Tickets by Category")
if category_rows:
    st.dataframe(category_rows, hide_index=True, width="stretch")
else:
    st.info("No category analytics are available.")


st.subheader("Tickets by Priority")
if priority_rows:
    st.dataframe(priority_rows, hide_index=True, width="stretch")
else:
    st.info("No priority analytics are available.")


st.subheader("Tickets by Sentiment")
if sentiment_rows:
    st.dataframe(sentiment_rows, hide_index=True, width="stretch")
else:
    st.info("No sentiment analytics are available.")