# System Architecture

## 1. Architecture Overview

The AI-Powered Customer Support Ticket Classifier is a local web application with a Streamlit agent interface, a FastAPI service layer, and a SQLite database. The backend combines deterministic business rules with a scikit-learn classifier, sentiment analysis, semantic similarity search, knowledge-base retrieval, and Gemini-generated reply drafts.

The SQLite database and trained classifier artifacts are generated locally and
are not repository inputs. Train the classifier from the bundled sample CSV
before starting the API; the application initializes its database schema on
backend startup. Do not use the development configuration as a public
deployment configuration.

The workflow can be viewed across the ticket lifecycle as:

```text
Ticket
→ Preprocessing
→ Rules + ML Classifier
→ Priority / Category
→ Sentence Transformer Embedding
→ FAISS Similarity Search
→ Knowledge Base Retrieval
→ Gemini Suggested Reply
→ Agent Review
→ Correction / Feedback
```

This represents the user-facing lifecycle, not a single synchronous classification call. Ticket creation performs preprocessing, rules, ML classification, SLA calculation, and sentiment analysis. Similar-ticket search and suggested-reply generation are separate operations initiated from the ticket detail page.

## 2. System Components

| Component | Responsibility |
| --- | --- |
| Streamlit frontend | Provides dashboard, queue, ticket detail, upload, analytics, and knowledge-base pages |
| FastAPI backend | Validates and processes requests, coordinates AI/ML services, and returns JSON |
| Preprocessing | Normalizes ticket text for classification |
| Hybrid classification engine | Combines rule-based priority/escalation and ML category prediction |
| Sentiment service | Assigns positive, neutral, or negative sentiment with VADER |
| Similarity service | Embeds ticket text and ranks candidates using FAISS |
| Knowledge-base services | Lists/searches articles and ranks context for reply drafting |
| Gemini reply service | Drafts a support response grounded in retrieved knowledge-base content |
| SQLite | Stores tickets, classification results, response drafts, knowledge articles, and corrections |

## 3. End-to-End Data Flow

1. A ticket is submitted via the ticket API or included in a CSV upload.
2. The backend preprocesses the ticket subject and body.
3. The rule engine evaluates urgency signals and customer tier while the ML layer predicts a category.
4. The backend stores the ticket, category, priority, sentiment, confidence, and source in SQLite, along with SLA information in the API response.
5. In ticket detail, the frontend can request similar-ticket search. The backend embeds the current and candidate ticket texts, searches them, and returns similarity-ranked matches.
6. When a suggested reply is requested, the backend retrieves relevant knowledge-base articles and passes their content with the ticket to Gemini.
7. The generated draft and its sources are returned to the frontend and the draft is saved in the responses table.
8. An agent reviews the ticket and draft, then may submit a category and/or priority correction.
9. The backend updates the latest classification and records the changed values in correction history.
10. Analytics requests aggregate ticket and classification data from SQLite for display.

## 4. Hybrid AI Engine

The hybrid engine coordinates preprocessing, rule evaluation, category classification, and SLA calculation. The rule engine produces priority and escalation; the Logistic Regression classifier produces category and confidence. These are complementary tasks rather than competing predictions of the same field.

The engine contains a low-confidence LLM classification fallback hook. Its configured confidence threshold is currently `0.0`; normal non-negative classifier confidence therefore does not ordinarily trigger the fallback. Gemini is actively used for suggested-reply generation.

## 5. Rule Engine

The rule engine applies deterministic checks to the normalized subject/body and customer tier:

- Starts at priority P4.
- Assigns P2 for VIP customer tier.
- Assigns P1 for critical keywords such as outage, chargeback, and legal.
- Assigns P2 for configured high-priority phrases such as refund, payment failure, login failure, crash, and not-working issues, unless the ticket is already P1.
- Marks a ticket escalated when the resulting priority is P1.

Rule results include reasons used to explain why a priority was selected. Priority also determines the response and resolution targets returned by the SLA service.

## 6. ML Classification Layer

The category model uses scikit-learn `TfidfVectorizer` with lowercase text, unigram/bigram features, and a maximum feature vocabulary of 5,000. A Logistic Regression estimator predicts a category and provides a confidence estimate.

The model and vectorizer are loaded from `data/models/category_model.pkl` and `data/models/tfidf_vectorizer.pkl`. The training utility reads the sample ticket dataset and saves these artifacts. Training is a separate command; the backend expects the artifacts to be available when it classifies tickets.

## 7. Sentiment Analysis

VADER analyzes the combined subject and body of a ticket. The compound score is mapped to:

- Positive when the score is at least `0.05`.
- Negative when the score is at most `-0.05`.
- Neutral otherwise.

The sentiment label is stored with the ticket classification and included in analytics distributions.

## 8. Semantic Similarity Layer

Similar-ticket detection compares the selected ticket against other stored tickets using semantic sentence embeddings. The service returns each qualifying candidate's original candidate-list index and similarity score. The route uses those indices to assemble ticket IDs, subjects, categories, priorities, and similarity values for the UI.

Candidates below the service's default similarity threshold of `0.70` are omitted. If there are no candidate tickets, the service returns an empty list.

Similarity is requested separately through `GET /tickets/{ticket_id}/similar`; it is not run as part of ticket insertion.

## 9. Hugging Face Sentence Transformer

The similarity service loads the pretrained Sentence Transformer model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

It encodes the selected ticket and candidate texts into vectors. Model initialization is cached in-process so repeated requests in the same process reuse the loaded model. The first use may require downloading model files from Hugging Face if they are not already cached locally.

## 10. FAISS Search

The service converts embeddings to contiguous `float32` arrays and normalizes them. It builds a FAISS `IndexFlatIP` index over the candidate vectors and searches with the normalized current-ticket vector.

For normalized vectors, inner product is equivalent to cosine similarity. The search scores are filtered by the configured threshold and returned in descending similarity order as `ticket_index` and `similarity`.

The index is created in memory for each similarity request; no persistent FAISS index or embedding database is currently maintained.

## 11. Gemini LLM Layer

Gemini is the active LLM provider for suggested replies. The backend uses the `google-genai` client and the `gemini-3.5-flash-lite` model configured in the reply drafter.

The reply service supplies the ticket text and retrieved knowledge-base articles to the model. Its instructions require replies to be professional and concise, use only knowledge-base information, avoid inventing policies, and avoid claiming an action was completed unless the ticket says so. When generation fails, the service returns a readable fallback message rather than allowing that generation error to crash the Streamlit workflow.

## 12. Knowledge Base and Reply Generation

Knowledge-base articles are stored in SQLite with title, body, category, and an embedding-reference field. The current retrieval service uses TF-IDF vectors and cosine similarity over the ticket text and article title/body, then selects up to three top-ranked articles.

The reply-generation endpoint obtains the ticket and articles, performs retrieval, invokes the Gemini reply drafter with the selected article content, saves the generated draft in the `responses` table, and returns the draft together with its source articles. The Knowledge Base frontend can list articles and search title, body, and category through existing API endpoints.

Knowledge-base retrieval currently uses lexical TF-IDF matching; the Sentence Transformer and FAISS similarity service is used for ticket-to-ticket similarity, not article retrieval.

## 13. Human-in-the-Loop Correction

The ticket detail interface displays the current category and priority and allows an agent to submit corrected values. The correction endpoint updates the classification and inserts a history record for each changed field, including previous value, new value, and timestamp. A request that changes neither field is rejected.

This gives agents a way to override automated results while retaining correction history. The current implementation records corrections but does not retrain the classifier from them automatically.

## 14. Database Layer

The persistence layer uses Python's built-in SQLite support. The database file is located at:

```text
data/support_ticket_classifier.db
```

The schema contains:

- `tickets`: ticket subject, body, channel, customer tier, and creation timestamp.
- `classifications`: category, priority, sentiment, confidence, and source.
- `responses`: suggested draft, final-text/status fields, and approval metadata.
- `kb_articles`: article title, body, category, and embedding reference.
- `corrections`: corrected field, old and new values, and correction timestamp.

The backend initializes or migrates the relevant schema on startup. It also inserts the bundled starter knowledge-base articles if their titles do not already exist.

## 15. FastAPI Backend

FastAPI hosts the ticket and knowledge-base routers, initializes the database schema, and serves JSON APIs. The current route groups support:

- Ticket creation, listing, and updates.
- Multipart CSV bulk upload.
- Suggested-reply generation.
- Ticket analytics.
- Similar-ticket search.
- Ticket corrections.
- Knowledge-base article listing, filtering, and search.

Interactive endpoint documentation is provided by FastAPI at `/docs` while the backend is running. The frontend expects the API at `http://127.0.0.1:8000`.

## 16. Streamlit Frontend

Streamlit provides the agent-facing pages:

- Dashboard and navigation.
- Ticket Queue for browsing tickets.
- Ticket Detail & Suggested Reply for classification details, generated drafts, corrections, and similar tickets.
- Submit / Bulk Upload for multipart CSV submission and processing summaries.
- Analytics for totals and classification distributions.
- Knowledge Base for article browsing and search.

The pages make HTTP requests to FastAPI and report backend/HTTP errors in the interface.

## 17. API Flow

| Method | Endpoint | Role |
| --- | --- | --- |
| `GET` | `/` | Backend status response |
| `POST` | `/tickets/` | Create/classify a ticket |
| `GET` | `/tickets/` | List tickets |
| `PATCH` | `/tickets/{ticket_id}` | Update supported ticket/classification fields |
| `POST` | `/tickets/bulk` | Process uploaded CSV ticket rows |
| `POST` | `/tickets/{ticket_id}/suggest-reply` | Retrieve knowledge context, generate and save a draft |
| `GET` | `/tickets/analytics` | Return total tickets and category/priority/sentiment distributions |
| `GET` | `/tickets/{ticket_id}/similar` | Return similar ticket matches |
| `POST` | `/tickets/{ticket_id}/correction` | Apply and record agent category/priority corrections |
| `GET` | `/knowledge-base/` | List articles, optionally filtered by category |
| `GET` | `/knowledge-base/search` | Search articles by query and optional category |

The Streamlit frontend currently connects to these routes on the local backend address.

## 18. Security / Secret Handling

The Gemini client reads `GEMINI_API_KEY` from the root `.env` file via dotenv configuration. The key must be configured locally and must not be committed, included in documentation, or displayed in application output. The repository's `.env.example` is for empty placeholders only.

The current backend configuration permits cross-origin requests broadly and does not implement user authentication or authorization. These settings are suitable only for a local project/demo environment and should be revisited before any network-accessible deployment. The local SQLite database can contain submitted ticket text and should not be committed or shared. No API key is needed for local SQLite operations, rule evaluation, or the trained local classifier.

## 19. Current Limitations

- The ML fallback threshold is `0.0`, so its low-confidence LLM classification branch ordinarily does not run for valid confidence values.
- Similarity uses an in-memory FAISS index rebuilt from candidates for each request.
- Similarity model files may need an initial external download.
- Knowledge-base retrieval uses lexical TF-IDF similarity, not semantic embeddings.
- The analytics API returns ticket totals and category, priority, and sentiment groupings, but no escalation count.
- Training data and model evaluation are limited to the included project dataset and utilities.
- Corrections are recorded but are not yet used in an automated model retraining loop.
- Gemini-generated replies require a valid API key and network access and are drafts for agent review.
- Authentication, authorization, and production-grade operational safeguards are not implemented.

## 20. Future Architecture Improvements

- Evaluate classifier performance on a held-out, representative dataset and calibrate the fallback threshold.
- Add authenticated agent accounts, role-based permissions, and secure deployment configuration.
- Restrict CORS to configured frontend origins and centralize deployment settings.
- Use correction history as reviewed training feedback, with validation before model updates.
- Add persistent embedding storage and reuse a FAISS index for larger ticket collections.
- Evaluate semantic retrieval for knowledge-base articles independently from ticket similarity.
- Extend analytics APIs with escalation, SLA, volume-over-time, and correction metrics.
- Add pagination, structured logging without secrets, automated integration tests, and deployment monitoring.
- Add a reply approval workflow that stores and tracks agent-approved final responses.