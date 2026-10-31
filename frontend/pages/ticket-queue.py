import json
import urllib.request
import urllib.error

import streamlit as st


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Ticket Queue",
    page_icon="🎫",
    layout="wide"
)


# ---------------- API CONFIG ----------------
API_URL = "http://127.0.0.1:8000/tickets/"


# ---------------- SIDEBAR ----------------
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


# ---------------- HEADER ----------------
st.title("🎫 Ticket Queue")
st.caption("View and manage customer support tickets")

st.divider()


# ---------------- FETCH TICKETS ----------------
def get_tickets():
    try:
        with urllib.request.urlopen(API_URL, timeout=10) as response:
            data = response.read().decode("utf-8")
            return json.loads(data)

    except urllib.error.URLError:
        return None

    except Exception:
        return None


tickets = get_tickets()


# ---------------- ERROR ----------------
if tickets is None:
    st.error("Unable to connect to the FastAPI backend.")

    st.info(
        "Make sure your FastAPI server is running on "
        "http://127.0.0.1:8000"
    )

    st.stop()


# ---------------- HANDLE RESPONSE ----------------
if isinstance(tickets, dict):

    if "tickets" in tickets:
        tickets = tickets["tickets"]

    elif "data" in tickets:
        tickets = tickets["data"]

    else:
        tickets = []


# ---------------- KPI ----------------
total_tickets = len(tickets)

high_priority = sum(
    1
    for ticket in tickets
    if ticket.get("priority") in ["P1", "P2"]
)

escalated = sum(
    1
    for ticket in tickets
    if ticket.get("escalated") is True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Tickets",
        total_tickets
    )

with col2:
    st.metric(
        "High Priority",
        high_priority
    )

with col3:
    st.metric(
        "Escalated",
        escalated
    )


st.divider()


# ---------------- FILTERS ----------------
st.subheader("🔎 Filter Tickets")

filter_col1, filter_col2 = st.columns(2)

with filter_col1:

    category_filter = st.selectbox(
        "Category",
        [
            "All",
            "billing",
            "technical",
            "account",
            "shipping",
            "general"
        ]
    )

with filter_col2:

    priority_filter = st.selectbox(
        "Priority",
        [
            "All",
            "P1",
            "P2",
            "P3",
            "P4"
        ]
    )


# ---------------- APPLY FILTERS ----------------
filtered_tickets = tickets

if category_filter != "All":

    filtered_tickets = [
        ticket
        for ticket in filtered_tickets
        if ticket.get("category") == category_filter
    ]


if priority_filter != "All":

    filtered_tickets = [
        ticket
        for ticket in filtered_tickets
        if ticket.get("priority") == priority_filter
    ]


st.write(
    f"Showing **{len(filtered_tickets)}** tickets"
)


# ---------------- TICKET TABLE ----------------
if not filtered_tickets:

    st.warning("No tickets found.")

else:

    table_data = []

    for ticket in filtered_tickets:

        confidence = ticket.get("confidence")

        if confidence is not None:
            confidence_value = round(
                float(confidence) * 100,
                1
            )
        else:
            confidence_value = 0

        table_data.append(
            {
                "ID": ticket.get("id", ""),
                "Subject": ticket.get("subject", ""),
                "Category": ticket.get("category", "N/A"),
                "Priority": ticket.get("priority", "N/A"),
                "Sentiment": ticket.get("sentiment", "N/A"),
                "Confidence": confidence_value,
                "Source": ticket.get("source", "N/A"),
                "Escalated": (
                    "Yes"
                    if ticket.get("escalated")
                    else "No"
                )
            }
        )

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True
    )


st.divider()


# ---------------- SELECT TICKET ----------------
if filtered_tickets:

    st.subheader("📄 Open Ticket")

    ticket_ids = [
        ticket.get("id")
        for ticket in filtered_tickets
        if ticket.get("id") is not None
    ]

    selected_id = st.selectbox(
        "Select Ticket ID",
        ticket_ids
    )

    if st.button(
        "Open Ticket Detail",
        use_container_width=True
    ):

        # Store selected ticket ID in Streamlit session state
        st.session_state["selected_ticket_id"] = selected_id

        # Open ticket detail page
        st.switch_page(
            "pages/ticket-detail-suggested-reply.py"
        )