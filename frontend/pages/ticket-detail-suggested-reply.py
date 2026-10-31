import json
import urllib.request
import urllib.error

import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Ticket Detail",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# API CONFIG
# ============================================================

API_BASE = "http://127.0.0.1:8000"


# ============================================================
# SIDEBAR
# ============================================================

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


# ============================================================
# GET SELECTED TICKET
# ============================================================

ticket_id = st.session_state.get(
    "selected_ticket_id"
)


# ============================================================
# PAGE HEADER
# ============================================================

st.title("📄 Ticket Detail & Suggested Reply")


# ============================================================
# NO TICKET SELECTED
# ============================================================

if not ticket_id:

    st.warning(
        "No ticket selected. Please open a ticket from Ticket Queue."
    )

    if st.button(
        "← Back to Ticket Queue"
    ):

        st.switch_page(
            "pages/ticket-queue.py"
        )

    st.stop()


# ============================================================
# GET TICKET
# ============================================================

def get_ticket(ticket_id):

    url = f"{API_BASE}/tickets/"

    try:

        with urllib.request.urlopen(
            url,
            timeout=10
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        if isinstance(data, dict):

            if "tickets" in data:

                data = data["tickets"]

            elif "data" in data:

                data = data["data"]

            else:

                data = []

        for ticket in data:

            if str(ticket.get("id")) == str(ticket_id):

                return ticket

        return None

    except Exception as error:

        st.error(
            f"Unable to load ticket: {error}"
        )

        return None


# ============================================================
# LOAD TICKET
# ============================================================

ticket = get_ticket(ticket_id)


if ticket is None:

    st.error(
        f"Ticket #{ticket_id} was not found."
    )

    if st.button(
        "← Back to Ticket Queue"
    ):

        st.switch_page(
            "pages/ticket-queue.py"
        )

    st.stop()


# ============================================================
# TICKET HEADER
# ============================================================

st.caption(
    f"Ticket ID: #{ticket.get('id')}"
)

st.header(
    ticket.get(
        "subject",
        "No Subject"
    )
)

st.divider()


# ============================================================
# TICKET METRICS
# ============================================================

info1, info2, info3, info4 = st.columns(4)


with info1:

    st.metric(
        "Category",
        ticket.get(
            "category",
            "N/A"
        )
    )


with info2:

    st.metric(
        "Priority",
        ticket.get(
            "priority",
            "N/A"
        )
    )


with info3:

    st.metric(
        "Sentiment",
        ticket.get(
            "sentiment",
            "N/A"
        )
    )


with info4:

    confidence = ticket.get(
        "confidence"
    )

    if confidence is not None:

        confidence_text = (
            f"{float(confidence) * 100:.1f}%"
        )

    else:

        confidence_text = "N/A"

    st.metric(
        "Confidence",
        confidence_text
    )


# ============================================================
# CUSTOMER MESSAGE
# ============================================================

st.subheader(
    "📝 Customer Message"
)

st.text_area(
    "Ticket Body",
    value=ticket.get(
        "body",
        ""
    ),
    height=180,
    disabled=True
)


# ============================================================
# CLASSIFICATION DETAILS
# ============================================================

st.subheader(
    "🔎 Classification Details"
)

detail1, detail2, detail3 = st.columns(3)


with detail1:

    st.write(
        f"**Channel:** "
        f"{ticket.get('channel', 'N/A')}"
    )

    st.write(
        f"**Customer Tier:** "
        f"{ticket.get('customer_tier', 'N/A')}"
    )


with detail2:

    st.write(
        f"**Classification Source:** "
        f"{ticket.get('source', 'N/A')}"
    )


with detail3:

    escalated = ticket.get(
        "escalated",
        False
    )

    if escalated:

        st.error(
            "🚨 Ticket is escalated"
        )

    else:

        st.success(
            "Normal escalation status"
        )


# ============================================================
# SLA
# ============================================================

sla = ticket.get(
    "sla"
)


if sla:

    st.subheader(
        "⏱️ SLA"
    )

    sla1, sla2 = st.columns(2)

    with sla1:

        st.info(
            f"Response Time: "
            f"{sla.get('response_time', 'N/A')}"
        )

    with sla2:

        st.info(
            f"Resolution Time: "
            f"{sla.get('resolution_time', 'N/A')}"
        )


st.divider()


# ============================================================
# SUGGESTED REPLY
# ============================================================

st.subheader(
    "🤖 Suggested Reply"
)

if st.button(
    "Generate Suggested Reply",
    use_container_width=True
):

    try:

        url = (
            f"{API_BASE}/tickets/"
            f"{ticket_id}/suggest-reply"
        )

        request = urllib.request.Request(
            url,
            method="POST"
        )

        with st.spinner(
            "Generating AI suggested reply..."
        ):

            with urllib.request.urlopen(
                request,
                timeout=60
            ) as response:

                result = json.loads(
                    response.read().decode("utf-8")
                )

        draft = result.get(
            "draft",
            ""
        )

        if draft:

            st.success(
                "Suggested reply generated successfully!"
            )

            st.text_area(
                "AI Suggested Reply",
                value=draft,
                height=220
            )

            # =================================================
            # KNOWLEDGE BASE SOURCES
            # =================================================

            sources = result.get(
                "sources",
                []
            )

            if sources:

                st.subheader(
                    "📚 Knowledge Base Sources"
                )

                for article in sources:

                    st.write(
                        f"**{article.get('title', 'Untitled')}**"
                    )

                    article_body = article.get(
                        "body",
                        ""
                    )

                    if article_body:

                        st.caption(
                            article_body
                        )

        else:

            st.warning(
                "No suggested reply was generated."
            )


    except urllib.error.HTTPError as error:

        error_body = error.read().decode(
            "utf-8",
            errors="ignore"
        )

        st.error(
            f"API error ({error.code}): {error_body}"
        )


    except urllib.error.URLError as error:

        st.error(
            "Unable to connect to FastAPI backend."
        )

        st.caption(
            str(error)
        )


    except Exception as error:

        st.error(
            f"Unable to generate suggested reply: {error}"
        )


# ============================================================
# AGENT CORRECTION
# ============================================================

st.divider()

st.subheader(
    "✏️ Agent Correction"
)

current_category = ticket.get(
    "category",
    "general"
)


current_priority = ticket.get(
    "priority",
    "P4"
)

st.write(
    f"**Current Category:** {current_category}"
)

st.write(
    f"**Current Priority:** {current_priority}"
)

category_options = [
    "billing",
    "technical",
    "account",
    "shipping",
    "general"
]


priority_options = [
    "P1",
    "P2",
    "P3",
    "P4"
]


with st.form("ticket_correction_form"):

    correction1, correction2 = st.columns(2)

    with correction1:

        new_category = st.selectbox(
            "Correct Category",
            category_options,
            index=(
                category_options.index(
                    current_category
                )
                if current_category in category_options
                else 0
            )
        )


    with correction2:

        new_priority = st.selectbox(
            "Correct Priority",
            priority_options,
            index=(
                priority_options.index(
                    current_priority
                )
                if current_priority in priority_options
                else 3
            )
        )


    submitted = st.form_submit_button(
        "Submit Correction",
        width="stretch"
    )


if submitted:

    if (
        new_category == current_category
        and
        new_priority == current_priority
    ):

        st.warning(
            "No changes were made to the classification."
        )

    else:

        url = (
            f"{API_BASE}/tickets/"
            f"{ticket_id}/correction"
        )
        correction_data = json.dumps(
            {
                "category": new_category,
                "priority": new_priority,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=correction_data,
            headers={
                "Content-Type": "application/json",
            },
            method="POST"
        )

        try:

            with urllib.request.urlopen(
                request,
                timeout=10
            ) as response:

                response.read()

            st.success(
                "Correction saved successfully."
            )

        except urllib.error.HTTPError as error:

            error_body = error.read().decode(
                "utf-8",
                errors="replace"
            )

            try:
                error_details = json.loads(error_body)
                error_message = error_details.get(
                    "detail",
                    error_body
                )
            except json.JSONDecodeError:
                error_message = error_body or error.reason

            st.error(
                f"Unable to save correction "
                f"(HTTP {error.code}): {error_message}"
            )

        except urllib.error.URLError as error:

            st.error(
                "Unable to connect to the FastAPI backend "
                "to save the correction."
            )

            st.caption(
                str(error.reason)
            )

        except Exception as error:

            st.error(
                f"Unable to save correction: {error}"
            )


# ============================================================
# SIMILAR TICKETS
# ============================================================

st.divider()

st.subheader(
    "🔗 Similar Tickets"
)

similar_tickets_url = (
    f"{API_BASE}/tickets/{ticket_id}/similar"
)

try:

    with st.spinner("Finding similar tickets..."):

        with urllib.request.urlopen(
            similar_tickets_url,
            timeout=30
        ) as response:

            similar_tickets = json.loads(
                response.read().decode("utf-8")
            )

    if not isinstance(similar_tickets, list):

        st.error(
            "The similar tickets endpoint returned an unexpected response."
        )

    elif not similar_tickets:

        st.info("No similar tickets found.")

    else:

        for similar_ticket in similar_tickets:

            similarity = similar_ticket.get(
                "similarity"
            )

            if isinstance(similarity, (int, float)):

                similarity_text = (
                    f"{float(similarity) * 100:.1f}%"
                )

            else:

                similarity_text = "N/A"

            with st.container(border=True):

                st.write(
                    f"**Ticket ID:** "
                    f"#{similar_ticket.get('id', 'N/A')}"
                )

                st.write(
                    f"**Subject:** "
                    f"{similar_ticket.get('subject') or 'No Subject'}"
                )

                st.write(
                    f"**Category:** "
                    f"{similar_ticket.get('category') or 'N/A'}"
                )

                st.write(
                    f"**Priority:** "
                    f"{similar_ticket.get('priority') or 'N/A'}"
                )

                st.write(
                    f"**Similarity:** {similarity_text}"
                )

except urllib.error.HTTPError as error:

    error_body = error.read().decode(
        "utf-8",
        errors="replace"
    )

    try:
        error_details = json.loads(error_body)
        error_message = error_details.get(
            "detail",
            error_body
        )
    except json.JSONDecodeError:
        error_message = error_body or error.reason

    st.error(
        f"Unable to load similar tickets "
        f"(HTTP {error.code}): {error_message}"
    )

except urllib.error.URLError as error:

    st.error(
        "Unable to connect to the FastAPI backend "
        "to load similar tickets."
    )

    st.caption(str(error.reason))

except (json.JSONDecodeError, UnicodeDecodeError):

    st.error(
        "The similar tickets endpoint returned invalid JSON."
    )

except Exception as error:

    st.error(
        f"Unable to load similar tickets: {error}"
    )