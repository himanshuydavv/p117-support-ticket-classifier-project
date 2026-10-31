import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="SupportAI",
    page_icon="🎫",
    layout="wide"
)

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
st.title("AI-Powered Customer Support")
st.subheader("Agent Console & Dashboard")

st.write(
    "AI-assisted ticket classification, prioritization, "
    "suggested replies and support analytics."
)

st.divider()

# ---------------- KPI CARDS ----------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🎫 Total Tickets",
        value="0"
    )

with col2:
    st.metric(
        label="🔴 High Priority",
        value="0"
    )

with col3:
    st.metric(
        label="🚨 Escalated",
        value="0"
    )

with col4:
    st.metric(
        label="✅ Resolved",
        value="0"
    )

st.divider()

# ---------------- MAIN SECTIONS ----------------
left, right = st.columns(2)

with left:
    st.subheader("🎫 Ticket Management")

    st.info(
        "Open the Ticket Queue to view customer tickets, "
        "classification, priority, sentiment and SLA information."
    )

    if st.button("Open Ticket Queue", use_container_width=True):
        st.switch_page("pages/ticket-queue.py")


with right:
    st.subheader("📊 Analytics")

    st.info(
        "View ticket volume, categories, priorities, sentiment "
        "and other support metrics."
    )

    if st.button("Open Analytics", use_container_width=True):
        st.switch_page("pages/analytics.py")


st.divider()

# ---------------- AI WORKFLOW ----------------
st.subheader("🤖 AI Support Workflow")

st.markdown(
    """
    **Ticket Intake**

    ↓

    **Text Preprocessing**

    ↓

    **Rules + ML Classification**

    ↓

    **LLM Fallback for Low Confidence**

    ↓

    **Similarity Search + Knowledge Base**

    ↓

    **Suggested Reply**

    ↓

    **Agent Review & Correction**

    ↓

    **Feedback / Analytics**
    """
)

st.divider()

# ---------------- QUICK ACTIONS ----------------
st.subheader("⚡ Quick Actions")

q1, q2, q3 = st.columns(3)

with q1:
    if st.button(
        "📤 Submit / Bulk Upload",
        use_container_width=True
    ):
        st.switch_page("pages/submit-bulk-upload.py")

with q2:
    if st.button(
        "📚 Knowledge Base",
        use_container_width=True
    ):
        st.switch_page("pages/knowledge-base.py")

with q3:
    if st.button(
        "🎫 View Tickets",
        use_container_width=True
    ):
        st.switch_page("pages/ticket-queue.py")


st.divider()

# ---------------- STATUS ----------------
st.success("Streamlit frontend is running successfully.")

st.caption(
    "SupportAI • AI-Powered Customer Support Ticket Classifier"
)