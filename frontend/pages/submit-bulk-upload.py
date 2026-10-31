import json
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections import Counter

import streamlit as st


st.set_page_config(
    page_title="Submit / Bulk Upload",
    page_icon="📤",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000/tickets/bulk"


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


st.title("📤 Submit / Bulk Upload")
st.caption(
    "Upload a CSV file to classify and process multiple support tickets."
)
st.info(
    "CSV files must include: subject, body, channel, customer_tier."
)

with st.form("bulk_ticket_upload_form"):
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"]
    )
    process_upload = st.form_submit_button(
        "Upload / Process",
        type="primary",
        width="stretch"
    )

if process_upload:
    if uploaded_file is None:
        st.error("Choose a CSV file before processing.")
    else:
        boundary = f"----SupportAI{uuid.uuid4().hex}"
        filename = urllib.parse.quote(
            uploaded_file.name.replace("\r", "").replace("\n", ""),
            safe=""
        )
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            "Content-Type: text/csv\r\n\r\n"
        ).encode("utf-8")
        body += uploaded_file.getvalue()
        body += f"\r\n--{boundary}--\r\n".encode("ascii")

        request = urllib.request.Request(
            API_URL,
            data=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
            method="POST"
        )

        try:
            with st.spinner("Uploading and processing tickets..."):
                with urllib.request.urlopen(
                    request,
                    timeout=120
                ) as response:
                    result = json.loads(
                        response.read().decode("utf-8")
                    )

            if not isinstance(result, dict):
                st.error("The backend returned an unexpected processing result.")
            else:
                st.success(
                    result.get("message", "Bulk upload processed successfully.")
                )
                total_tickets = result.get("total_tickets")
                tickets = result.get("tickets", [])

                if total_tickets is None and isinstance(tickets, list):
                    total_tickets = len(tickets)

                st.metric(
                    "Total tickets processed",
                    total_tickets if total_tickets is not None else "N/A"
                )

                if isinstance(tickets, list) and tickets:
                    category_counts = Counter(
                        ticket["category"]
                        for ticket in tickets
                        if isinstance(ticket, dict) and ticket.get("category")
                    )
                    priority_counts = Counter(
                        ticket["priority"]
                        for ticket in tickets
                        if isinstance(ticket, dict) and ticket.get("priority")
                    )

                    if category_counts or priority_counts:
                        st.subheader("Processing summary")
                        summary_col1, summary_col2 = st.columns(2)

                        with summary_col1:
                            if category_counts:
                                st.write("**By category**")
                                for category, count in sorted(category_counts.items()):
                                    st.write(f"- {category}: {count}")

                        with summary_col2:
                            if priority_counts:
                                st.write("**By priority**")
                                for priority, count in sorted(priority_counts.items()):
                                    st.write(f"- {priority}: {count}")

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
                f"Bulk upload failed (HTTP {error.code}): {error_message}"
            )

        except urllib.error.URLError as error:
            st.error(
                "Unable to connect to the FastAPI backend at "
                "http://127.0.0.1:8000. Make sure the backend is running."
            )
            st.caption(str(error.reason))

        except (json.JSONDecodeError, UnicodeDecodeError):
            st.error("The backend returned an invalid response.")

        except Exception as error:
            st.error(f"Unable to process the CSV upload: {error}")