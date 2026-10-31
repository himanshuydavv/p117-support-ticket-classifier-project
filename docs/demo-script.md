# 5-Minute Live Demonstration Script

**Project:** AI-Powered Customer Support Ticket Classifier
**Target audience:** College project, hackathon, or placement portfolio
**Duration:** Approximately 5 minutes

## Before the Demo

- Start FastAPI from the repository root with `uvicorn backend.app.main:app --reload`.
- Start Streamlit in a second terminal with `streamlit run frontend/app.py`.
- If the classifier artifacts are not present, create them from the bundled sample data with `python -m backend.app.services.train`. Confirm the artifacts exist in `data/models/` and the backend is reachable.
- Have the root `.env` configured locally if demonstrating Gemini replies. Do not show or share the key.
- Make sure the database has sample tickets, including a ticket whose subject or body contains **outage** and whose rule-generated priority is P1. The sample CSV includes outage examples; if loading it beforehand, use the bulk uploader's required columns: `subject`, `body`, `channel`, and `customer_tier`.
- Keep a note of the known escalation display limitation: the ticket-list endpoint does not include the `escalated` field, although ticket creation's classification result does. As a result, the Ticket Detail page may not accurately show the escalation flag for a listed ticket.
- Use only synthetic or approved demonstration tickets. The local database is excluded from Git because it may contain submitted ticket text.

## Demo Script

### 1. Introduce the problem — 0:00-0:20

- **What to click:** Nothing; begin with the project title slide or the running application.
- **What to say:** “Support teams receive requests on billing, account, shipping, and technical issues. Manually deciding what each ticket is about and how urgent it is takes time. This project automates parts of triage and gives agents tools to review and correct the results.”
- **Expected result:** The audience understands the operational problem and the goal.
- **Why the feature matters:** Faster, more consistent triage helps teams focus attention on urgent customer issues.

### 2. Open the Streamlit Dashboard — 0:20-0:35

- **What to click:** Open the Streamlit browser tab at the dashboard.
- **What to say:** “The agent interface is built with Streamlit and talks to a FastAPI backend. From here, an agent can open the queue, review analytics, or use the other support tools.”
- **Expected result:** The SupportAI dashboard, sidebar navigation, and ticket workflow overview are visible.
- **Why the feature matters:** A single agent console brings the main operational workflows together.

### 3. Show Ticket Queue — 0:35-0:55

- **What to click:** Select **Ticket Queue** in the sidebar or choose **Open Ticket Queue**.
- **What to say:** “The queue loads tickets from the API and provides category and priority filters, so an agent can focus on a specific kind of work.”
- **Expected result:** The ticket list and queue metrics appear; demonstrate a filter briefly if time permits.
- **Why the feature matters:** A searchable, filterable queue makes it easier to find tickets needing attention.

### 4. Open a ticket — 0:55-1:05

- **What to click:** Select a ticket in the queue to open its detail page.
- **What to say:** “Each ticket has a detail view that brings classification information and agent actions together.”
- **Expected result:** The selected ticket’s subject and customer message appear.
- **Why the feature matters:** Agents need the original context alongside automated assistance to make informed decisions.

### 5. Show classification, sentiment, confidence, and escalation — 1:05-1:25

- **What to click:** Point to the ticket metrics and classification details, then the SLA section if visible.
- **What to say:** “The detail page presents the category, priority, sentiment, and model confidence, along with SLA targets and an escalation indicator. The backend applies deterministic rules for urgency and VADER for sentiment.”
- **Expected result:** Category, priority, sentiment, confidence, and SLA are visible. Escalation display may be inaccurate for listed tickets because the current GET ticket-list response omits the escalation field; I’ll demonstrate the P1 rule next and note this gap.
- **Why the feature matters:** These signals help agents understand both the model’s classification and operational urgency.

### 6. Demonstrate a P1 escalation ticket using “outage” — 1:25-1:50

- **What to click:** In the queue, open the prepared ticket whose subject or body includes **outage**. Point out the P1 priority in the detail view. If no such ticket is in the queue, explain that the sample dataset contains outage examples and use one loaded before the demo.
- **What to say:** “The rule engine treats a critical keyword such as ‘outage’ as P1 and sets the ticket’s escalation result. This is a deterministic rule, so an obvious critical incident does not depend only on the text classifier.”
- **Expected result:** The ticket has P1 priority. The backend rule result marks P1 tickets as escalated. The page’s visible escalation indicator may not reflect this correctly because the current ticket-list API response does not include the escalation field.
- **Why the feature matters:** Critical service incidents should be prioritized consistently and routed for urgent attention.

### 7. Show Similar Tickets with Sentence Transformer and FAISS — 1:50-2:10

- **What to click:** Scroll to **Similar Tickets** in the ticket detail page.
- **What to say:** “On request, the backend embeds this ticket and the candidates with `all-MiniLM-L6-v2`. It normalizes the vectors and uses FAISS `IndexFlatIP` to rank cosine-style similarity.”
- **Expected result:** Similar ticket cards show ID, subject, category, priority, and similarity percentage, or the page reports that no similar tickets were found.
- **Why the feature matters:** Past related cases can give agents useful context and help them spot recurring issues.

### 8. Generate an AI Suggested Reply using Gemini — 2:10-2:35

- **What to click:** Scroll to **Suggested Reply** and click **Generate Suggested Reply**.
- **What to say:** “The backend finds relevant knowledge-base articles and sends their content with the ticket to Gemini, the active LLM provider for reply suggestions.”
- **Expected result:** A professional, concise draft appears, or a visible message explains that reply generation was unavailable. Do not expose the local API key during the demo.
- **Why the feature matters:** Drafting support language can save agent time while keeping the human agent responsible for review.

### 9. Show Knowledge Base sources — 2:35-2:45

- **What to click:** Point to the **Knowledge Base Sources** shown below the generated reply.
- **What to say:** “These are the articles retrieved for this ticket. The reply prompt asks Gemini to use only this knowledge-base information and not invent policies.”
- **Expected result:** Source article titles and, when available, article excerpts are visible.
- **Why the feature matters:** Showing sources makes the draft’s grounding easier for an agent to assess.

### 10. Submit a category/priority correction — 2:45-3:05

- **What to click:** In **Agent Correction**, choose a different category or priority and click **Submit Correction**.
- **What to say:** “The agent can correct either classification field. The API updates the classification and records the old and new values in correction history.”
- **Expected result:** A correction-saved success message appears. Avoid submitting unchanged values, which are rejected as no change.
- **Why the feature matters:** Human feedback can fix an individual ticket and is retained for later review.

### 11. Demonstrate CSV Bulk Upload — 3:05-3:30

- **What to click:** Select **Submit / Bulk Upload** in the sidebar, choose a CSV, then click **Upload / Process**. Use a prepared CSV with `subject`, `body`, `channel`, and `customer_tier` columns.
- **What to say:** “Bulk upload sends the selected CSV as multipart form data to the existing FastAPI endpoint. Each valid row is processed through the ticket workflow.”
- **Expected result:** The page reports success, total processed tickets, and category/priority summaries when returned by the API. Invalid files or backend problems are shown as visible errors.
- **Why the feature matters:** Batch intake avoids entering tickets individually when importing a group of requests.

### 12. Show Analytics Dashboard — 3:30-3:50

- **What to click:** Select **Analytics** in the sidebar.
- **What to say:** “This page loads live aggregates from the analytics endpoint and displays totals and distributions for category, priority, and sentiment.”
- **Expected result:** Total-ticket and P1/P2 counts and the three classification distribution tables are shown. Escalated total is N/A because the endpoint does not return that aggregate.
- **Why the feature matters:** Aggregates help teams understand the overall ticket mix and workload.

### 13. Show Knowledge Base page — 3:50-4:05

- **What to click:** Select **Knowledge Base**, then enter a word such as “billing” or “account” in the search box.
- **What to say:** “Agents can browse the stored articles or search title, category, and article content through the existing Knowledge Base API.”
- **Expected result:** Matching articles display their title, category when available, and body.
- **Why the feature matters:** Consistent support guidance is easier to find and can be reused in suggested replies.

### 14. Give the final architecture summary — 4:05-4:35

- **What to click:** Optionally return to the Dashboard or show the architecture diagram in the project documentation.
- **What to say:** “The system uses Streamlit for the agent interface, FastAPI for APIs, and SQLite for storage. Ticket text is preprocessed, category is predicted with TF-IDF and Logistic Regression, urgency is handled by rules, and sentiment uses VADER. Separate detail-page workflows use Sentence Transformer embeddings with FAISS for similar tickets and TF-IDF knowledge-base retrieval with Gemini for suggested replies.”
- **Expected result:** The audience sees how the UI, API, database, deterministic rules, and AI/ML services fit together.
- **Why the feature matters:** A clear separation of components makes the project easier to explain, test, and extend.

### 15. Mention limitations and future improvements — 4:35-5:00

- **What to click:** Nothing; close with the limitations and next steps.
- **What to say:** “This is a project-scale implementation. The analytics API does not yet expose escalation totals, and the ticket-list response omits the escalation flag used by the detail UI. The low-confidence classification fallback threshold also needs calibration. Future work includes broader evaluation data, fixing those API gaps, persistent vector indexing, semantic knowledge retrieval, and authentication.”
- **Expected result:** The demo closes with a realistic account of current behavior and a practical improvement roadmap.
- **Why the feature matters:** Explicit limitations demonstrate technical understanding and provide measurable next steps.

## Presenter Notes

- Keep the prepared P1 “outage” ticket openable from the queue before beginning.
- For Gemini, confirm connectivity and local configuration before the presentation, but never display the secret value.
- If the model download or Gemini service is unavailable during a live demo, use the page’s visible error behavior and explain the external dependency; do not claim a reply or similarity result that was not produced.
- Because the current ticket list omits escalation data, describe the P1 rule result accurately and do not claim the detail page visibly confirms escalation.