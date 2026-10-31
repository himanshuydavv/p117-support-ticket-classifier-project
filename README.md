# AI-Powered Customer Support Ticket Classifier

An end-to-end customer support ticket triage application built with FastAPI, Streamlit, SQLite, and a hybrid AI/ML workflow. It classifies tickets, applies priority and escalation rules, analyzes sentiment, helps agents draft knowledge-base-grounded replies, and records agent corrections.

## 1. Project Overview

Support teams receive tickets across channels and need to quickly understand what each request concerns and how urgently it should be handled. This project provides a lightweight agent console and API for creating, classifying, reviewing, and analyzing customer support tickets.

## 2. Problem Statement

Manual ticket triage can be slow and inconsistent. Agents must interpret ticket text, decide its category and urgency, find relevant support guidance, and ensure critical cases are prioritized. The project automates parts of this workflow while keeping agents in the review loop.

## 3. Objective

- Predict a support category from ticket subject and body.
- Apply deterministic rules for priority and escalation.
- Calculate a response and resolution target based on priority.
- Surface sentiment and semantically similar past tickets.
- Retrieve relevant knowledge-base articles for AI-generated reply suggestions.
- Allow agents to correct category and priority and review aggregate analytics.

## 4. Key Features

- FastAPI REST API for ticket intake, ticket data, analytics, corrections, and related workflows.
- Streamlit agent console with ticket queue, ticket detail, bulk upload, analytics, and knowledge-base pages.
- TF-IDF and Logistic Regression category classification.
- Rule-based priority and escalation decisions.
- SLA target calculation by priority.
- VADER sentiment analysis.
- Knowledge-base search and relevance ranking.
- Gemini API as the active LLM provider for suggested replies.
- Sentence Transformers (`all-MiniLM-L6-v2`) embeddings with FAISS similarity search.
- CSV bulk ticket upload.
- Ticket correction/feedback recording.

## 5. End-to-End Workflow

1. An agent creates a ticket through the API or uploads a CSV file.
2. The backend cleans the subject and body and combines them for classification.
3. The Logistic Regression model predicts the category. A low-confidence fallback hook is also present.
4. The rule engine determines priority and escalation from ticket content and customer tier.
5. The backend calculates SLA targets and analyzes sentiment.
6. Ticket and classification data are stored in SQLite.
7. In the Ticket Detail page, an agent can request a suggested reply or find similar tickets.
8. Suggested replies use relevant knowledge-base context and Gemini; the agent remains responsible for reviewing the draft.
9. Agent corrections to category or priority are applied and stored as correction history.
10. The Analytics page presents ticket totals and classification distributions returned by the backend.

## 6. Hybrid AI Architecture

The workflow combines deterministic rules and learned or pretrained models for different tasks:

```text
Ticket subject/body
        |
   Text cleaning
        |
   +----+---------------------+
   |                          |
TF-IDF + Logistic       Rule engine
Regression category     priority/escalation
   |                          |
   +------ Classification result ------+
                         |
               SLA + VADER sentiment
                         |
                 SQLite persistence

Ticket detail -> TF-IDF knowledge-base retrieval -> Gemini suggested reply
Ticket detail -> Sentence Transformer embeddings -> FAISS similarity search
```

The current category-classifier code includes a low-confidence LLM fallback hook. The model confidence threshold is currently configured as `0.0`, so ordinary non-negative classifier confidence values do not trigger that fallback. Gemini is actively used for suggested-reply generation.

## 7. Technology Stack

| Area | Technology |
| --- | --- |
| API backend | FastAPI, Uvicorn, Pydantic |
| Agent interface | Streamlit |
| Database | SQLite |
| Classification | scikit-learn TF-IDF and Logistic Regression |
| Similar-ticket embeddings | Sentence Transformers, `all-MiniLM-L6-v2` |
| Similarity index | FAISS (`IndexFlatIP`) |
| Sentiment | VADER Sentiment |
| Suggested replies | Gemini API via `google-genai` |
| Configuration | Python dotenv |

## 8. Project Structure

```text
.
├── backend/
│   └── app/
│       ├── ai/                 # Classification pipeline, validators, LLM clients
│       ├── api/routes/         # Ticket and knowledge-base API routes
│       ├── db/                 # SQLite connection and schema initialization
│       └── services/           # ML, rules, SLA, sentiment, retrieval, similarity, replies
├── data/
│   ├── models/                 # Locally generated classifier artifacts (not committed)
│   ├── sample/                 # Sample ticket CSV
│   └── support_ticket_classifier.db  # Local database (not committed)
├── docs/                       # Project architecture, evaluation, and demo material
├── frontend/
│   ├── app.py                  # Streamlit landing page
│   └── pages/                  # Queue, ticket detail, bulk upload, analytics, knowledge base
├── .env.example                # Empty configuration placeholders
└── requirements.txt
```

The sample CSV is included for local model training and bulk-upload demos. The
SQLite database and generated pickle model artifacts are local files and are
excluded from Git. Generate the classifier artifacts with the training command
in the setup steps before starting the API.

## 9. AI/ML Components

- **Text preprocessing:** Lowercases text, removes URLs and special characters, and collapses whitespace.
- **Category classifier:** A scikit-learn `TfidfVectorizer` with unigram/bigram features feeds a Logistic Regression classifier. The trained model and vectorizer are stored in `data/models/`.
- **Rule engine:** Assigns priority levels P1-P4 using critical/high-priority keywords and VIP customer tier. P1 cases are marked escalated by the rule engine.
- **SLA calculation:** Maps priority to response and resolution targets.
- **Sentiment analysis:** VADER compound scores are categorized as positive, neutral, or negative.
- **Knowledge-base retrieval:** TF-IDF cosine similarity ranks articles by ticket relevance; the top three are supplied as context to reply generation.
- **Suggested reply generation:** Gemini drafts professional, concise responses using retrieved knowledge-base content and rules against inventing policies or claiming uncompleted actions.
- **Similar-ticket detection:** Sentence Transformer embeddings are normalized and searched using FAISS inner product, with results below the configured similarity threshold omitted.

## 10. Database Structure

SQLite is stored at `data/support_ticket_classifier.db`. The application initializes the schema on backend startup.

| Table | Purpose |
| --- | --- |
| `tickets` | Ticket subject, body, channel, customer tier, and creation timestamp |
| `classifications` | Category, priority, sentiment, confidence, and classification source for a ticket |
| `responses` | Suggested draft and response review/status fields |
| `kb_articles` | Knowledge-base title, body, category, and embedding reference field |
| `corrections` | Ticket correction field, previous/new values, and correction timestamp |

The application inserts starter knowledge-base articles during schema initialization when matching titles are not already present.

## 11. API Endpoints

The FastAPI application exposes interactive API documentation at `/docs` while running.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Backend health/message endpoint |
| `POST` | `/tickets/` | Create and classify one ticket |
| `GET` | `/tickets/` | List tickets and latest classification fields |
| `PATCH` | `/tickets/{ticket_id}` | Update supported ticket/classification fields |
| `POST` | `/tickets/bulk` | Upload tickets from a multipart CSV file (`file` field) |
| `POST` | `/tickets/{ticket_id}/suggest-reply` | Retrieve knowledge context and save/return a Gemini reply draft |
| `GET` | `/tickets/analytics` | Return total ticket count and category, priority, and sentiment distributions |
| `GET` | `/tickets/{ticket_id}/similar` | Find semantically similar tickets |
| `POST` | `/tickets/{ticket_id}/correction` | Save category and/or priority correction and history |
| `GET` | `/knowledge-base/` | List knowledge-base articles; optionally filter by category |
| `GET` | `/knowledge-base/search?q=...` | Search article title, body, and category; optional category filter |

## 12. Frontend Pages

- **Dashboard (`frontend/app.py`):** Landing page and navigation to ticket management and analytics.
- **Ticket Queue (`frontend/pages/ticket-queue.py`):** Lists and filters tickets from the API.
- **Ticket Detail & Suggested Reply (`frontend/pages/ticket-detail-suggested-reply.py`):** Displays ticket details, generates a reply, submits agent corrections, and displays similar tickets.
- **Submit / Bulk Upload (`frontend/pages/submit-bulk-upload.py`):** Sends a CSV file to the bulk upload endpoint and summarizes the response.
- **Analytics (`frontend/pages/analytics.py`):** Displays total tickets and category, priority, and sentiment distributions.
- **Knowledge Base (`frontend/pages/knowledge-base.py`):** Lists and searches articles.

## 13. How the System Works

Ticket and article data are persisted in SQLite and exposed through FastAPI. The Streamlit application calls those endpoints over HTTP. Ticket creation runs preprocessing, category classification, rule-based priority/escalation, SLA calculation, and sentiment analysis before storing the result.

When a reply is requested, the backend ranks knowledge-base articles against the ticket text, passes the most relevant articles to Gemini, saves the generated draft, and returns both the draft and its sources. The similar-ticket route embeds the current ticket and candidate ticket text, uses FAISS to rank normalized vectors, and returns the highest-scoring matches.

## 14. Installation and Setup

Run commands from the repository root. The examples below use Windows PowerShell.

1. Install Python compatible with the pinned project dependencies.
2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install project dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Create a root `.env` file from `.env.example` if you do not already have one. Set the Gemini key locally in `.env`; never commit the real file:

   ```powershell
   Copy-Item .env.example .env
   ```

   If `.env` already exists, edit it locally rather than overwriting it.

5. Train or refresh the category model artifacts from the included sample dataset:

   ```powershell
   python -m backend.app.services.train
   ```

Training reads `data/sample/tickets.csv` and creates local model artifacts under
`data/models/`. The Sentence Transformer model may need to be downloaded the
first time similar-ticket search is used. Gemini-powered features require
network access and a valid locally configured Gemini API key.

## 15. Environment Variables

The root `.env.example` contains empty placeholders. Configure the following value in the root `.env` file for Gemini-generated suggested replies:

```dotenv
GEMINI_API_KEY=your-key-set-locally
```

Do not put real keys in source code, README files, or commits. The Gemini client reads the key from the root `.env` file. Other application functionality such as local classification, SQLite storage, sentiment analysis, and the Streamlit UI does not require an API key.

## 16. How to Run the Backend

From the repository root, with the virtual environment activated:

```powershell
uvicorn backend.app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`; interactive API documentation is at `http://127.0.0.1:8000/docs`. Startup initializes the SQLite schema.

## 17. How to Run the Streamlit Frontend

Open a second terminal at the repository root, activate the same environment, then run:

```powershell
streamlit run frontend/app.py
```

The browser opens the agent console. The frontend expects the backend at `http://127.0.0.1:8000`.

## 18. Demo Flow

1. Start the backend and Streamlit frontend.
2. Open Ticket Queue and inspect the existing tickets, or use Submit / Bulk Upload with a CSV containing `subject`, `body`, `channel`, and `customer_tier` columns.
3. Open a ticket to review its category, priority, sentiment, confidence, and SLA information.
4. Generate a suggested reply and review its displayed knowledge-base sources.
5. Submit a changed category or priority using Agent Correction.
6. Review similar tickets and open Knowledge Base to search support articles.
7. Open Analytics to view ticket totals and category, priority, and sentiment distributions.

### Example: create a ticket through the API

With the backend running, submit a JSON ticket using PowerShell:

```powershell
$ticket = @{
    subject = "Unable to access my account"
    body = "The password reset email has not arrived."
    channel = "web"
    customer_tier = "standard"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/tickets/" `
    -Method Post `
    -ContentType "application/json" `
    -Body $ticket
```

The response contains the created ticket ID, predicted category, rule-based
priority and escalation result, sentiment, classifier confidence and source,
and priority-based SLA targets. Exact prediction values depend on the trained
model and ticket text.

## 19. Testing / Verification

- Use `http://127.0.0.1:8000/docs` to inspect and exercise the running API endpoints.
- Train the classifier with `python -m backend.app.services.train`.
- Use `data/sample/tickets.csv` as sample data; for bulk upload, provide the required ticket-input columns.
- Verify the Streamlit workflows against the running backend: ticket queue/detail, reply generation, corrections, similarity search, article search, bulk upload, and analytics.
- Gemini reply generation and first-time model downloads depend on external network connectivity and configuration.

## 20. Limitations

- The analytics API currently returns total tickets and category, priority, and sentiment distributions. It does not provide an escalated-ticket count; the Analytics page cannot calculate that KPI from this endpoint.
- The classifier's low-confidence fallback hook is configured with a confidence threshold of `0.0`, which means valid non-negative confidence scores will not normally activate it.
- Classification quality depends on the included sample training data; broader, representative labeled data and measured evaluation are needed before production use.
- The knowledge-base retriever and article search use lexical matching and may not understand all paraphrases.
- Similar-ticket search may download its pretrained model on first use and currently searches the available candidate tickets in memory.
- Suggested replies require a working Gemini API key and internet access. They are drafts for agent review, not automatically sent responses.
- This is a project/demo implementation and has not been described as a production-secured or high-availability service.

## Security considerations

- Keep `.env` local and provide only placeholder values in `.env.example`. The
  active suggested-reply integration reads `GEMINI_API_KEY` from `.env`.
- Do not commit the local SQLite database, user-submitted tickets, generated
  model files, credentials, or logs. The repository ignore rules exclude these
  local artifacts; review staged paths before every commit.
- The API currently has no authentication or authorization and allows broad
  CORS origins. Do not expose it to an untrusted network without adding access
  controls and restricting allowed origins.
- Treat ticket text, retrieved articles, and AI-generated replies as
  potentially sensitive. Review generated drafts before sharing them with
  customers.

## 21. Future Improvements

- Tune and validate the classifier with a larger, more representative labeled dataset and measurable evaluation metrics.
- Review the low-confidence fallback threshold and add tests for fallback behavior.
- Extend analytics data to include escalation counts and additional operational metrics.
- Add pagination and database-backed semantic/vector indexing for larger ticket collections.
- Improve knowledge-base retrieval with semantic search and article relevance evaluation.
- Add authentication, authorization, audit controls, and production deployment configuration.
- Add automated API and frontend workflow tests and CI verification.
- Support agent review states and capture approved final replies in the response workflow.