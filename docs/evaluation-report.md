# Evaluation Report

## 1. Evaluation Objective

This report describes what has and has not been evaluated in the current AI-Powered Customer Support Ticket Classifier. It separates implemented behavior from measured quality. The repository includes a sample dataset and a classifier smoke-test script, but it does not include a completed, recorded benchmark with held-out predictions and aggregate classification metrics.

The evaluation objective is to assess the workflow's ability to classify and prioritize support tickets, analyze sentiment, retrieve similar tickets and knowledge-base articles, generate grounded reply drafts, accept agent corrections, process CSV uploads, and display analytics.

## 2. Dataset Description

The repository includes `data/sample/tickets.csv`, a small example dataset with 40 ticket rows. Its columns are:

- `id`
- `subject`
- `body`
- `channel`
- `customer_tier`
- `category`
- `priority`

The records cover billing, account, shipping, technical, and general support examples, with selected high-priority scenarios such as outages. The file is used by the model training utility for category labels. No separate train/validation/test split or independently curated test set is defined in the repository.

The sample data is suitable for demonstrating the application flow, but its size and construction do not establish generalization to real support traffic.

The repository's classifier smoke-test utility prints predictions for a few
example messages; these are illustrative outputs, not an evaluation dataset or
measured test results. No evaluation scores or performance claims are inferred
from the presence of that script or the sample data.

## 3. Classification Evaluation

The category classifier is implemented using scikit-learn TF-IDF features and Logistic Regression. A classifier smoke-test script includes five example ticket texts and prints predicted category, confidence, source, and fallback status.

**Aggregate classification performance: Not evaluated yet.** The repository does not contain a documented evaluation run, a held-out dataset, or saved prediction results sufficient to calculate reliable metrics. The smoke-test examples are not a substitute for a controlled benchmark.

## 4. Precision

**Not evaluated yet.** No measured per-class or macro/micro/weighted precision values are available in the repository.

## 5. Recall

**Not evaluated yet.** No measured per-class or macro/micro/weighted recall values are available in the repository.

## 6. F1 Score

**Not evaluated yet.** No measured per-class or macro/micro/weighted F1 scores are available in the repository.

## 7. Confusion Matrix

**Not evaluated yet.** The project does not include a recorded confusion matrix. It should be computed from predictions on a labeled held-out test set rather than inferred from the training examples.

## 8. Critical Ticket Escalation Evaluation

The rule engine implements deterministic urgency rules. For example, a critical keyword such as `outage` assigns P1 and marks the ticket as escalated. VIP tier can raise priority to P2, while other configured critical and high-priority phrases affect priority according to the rule logic.

**Systematic escalation precision/recall: Not evaluated yet.** There is no labeled escalation test set or recorded false-positive/false-negative analysis.

There is also a current integration limitation: ticket creation returns the computed escalation flag, but the ticket-list API does not include that field. The detail UI relies on listed ticket data, so its escalation display may not reflect the rule result for an existing ticket. The backend rule outcome and UI display should not be treated as equivalent until that contract is addressed.

## 9. Sentiment Analysis Evaluation

VADER is implemented for ticket text. Its compound score is mapped to positive, neutral, or negative using configured thresholds.

**Sentiment quality: Not evaluated yet.** The repository has no human-labeled sentiment test set, agreement analysis, or sentiment metric results.

## 10. Similar Ticket / Semantic Search Evaluation

Ticket similarity is implemented with Sentence Transformers using `sentence-transformers/all-MiniLM-L6-v2`. The service normalizes embeddings and uses FAISS `IndexFlatIP` to rank candidates; results below the configured threshold are excluded.

**Retrieval quality: Not evaluated yet.** No labeled query-to-relevant-ticket judgments, ranking metrics, latency benchmark, or comparison against a baseline are recorded.

## 11. Suggested Reply Evaluation

Gemini is the current LLM provider for suggested replies. The backend retrieves up to three knowledge-base articles using TF-IDF similarity and passes their content with the ticket text to Gemini. The prompt instructs the model to be professional and concise, use only knowledge-base information, avoid inventing policies, and not claim an action was completed unless the ticket says so.

**Reply quality and grounding: Not evaluated yet.** No human rubric results, factuality measurements, or systematic hallucination assessment are present. Suggested replies are drafts; a human agent must review and approve them before sending. The system does not automatically send the generated reply.

## 12. Correction / Feedback Evaluation

The correction workflow allows an agent to change category and/or priority. The API updates the classification and records changed fields with old/new values and a timestamp. A request that makes no change is rejected.

**Correction usability and impact: Not evaluated yet.** Corrections are stored, but the current implementation does not automatically use them to retrain or recalibrate the classifier.

## 13. Bulk Upload Evaluation

The bulk-upload API accepts a multipart CSV file and checks the `.csv` filename, UTF-8 decoding, and required columns: `subject`, `body`, `channel`, and `customer_tier`. It processes non-empty rows and returns the number of created tickets and classification fields.

**Bulk throughput, maximum supported file size, and failure-recovery behavior: Not evaluated yet.** No load test or systematic partial/invalid-row evaluation is documented.

## 14. Analytics Evaluation

The analytics endpoint aggregates total tickets and classification distributions for category, priority, and sentiment. The Streamlit Analytics page reads those values and displays them.

**Analytics correctness against an independent reference: Not evaluated yet.** The endpoint currently does not return an escalated-ticket aggregate; the Analytics page displays the escalation KPI as unavailable rather than deriving an unsupported value.

## 15. System Robustness

Implemented behavior includes:

- Database schema initialization during backend startup.
- Input validation for ticket creation and CSV upload requirements.
- Transaction rollback in several database-writing paths when processing fails.
- Readable frontend messages for HTTP and backend connection errors in the implemented pages.
- A cached Sentence Transformer model within the process.
- A readable fallback message when Gemini reply generation fails.
- A no-candidates path that returns an empty similarity result.

**Operational robustness: Not evaluated yet.** The repository does not document load, stress, long-duration, concurrency, recovery, or deployment-security testing.

## 16. Current Limitations

- The sample dataset is small and there is no defined held-out evaluation split.
- Precision, recall, F1, confusion-matrix, and sentiment-quality results are not available.
- Rule-based escalation has not been evaluated against labeled incident outcomes.
- The ticket-list response omits escalation status, so the UI may not show the backend rule result.
- The classifier's low-confidence fallback threshold is configured as `0.0`, so ordinary non-negative confidence scores do not normally activate the fallback.
- Knowledge-base retrieval uses lexical TF-IDF similarity; paraphrases may not retrieve the best article.
- Similar-ticket search rebuilds an in-memory FAISS index from candidates per request.
- Reply quality, knowledge grounding, and Gemini service availability have not been systematically benchmarked.
- Corrections are recorded but do not automatically update the model.
- Production-scale performance, authentication, authorization, and operational safeguards have not been validated.

## 17. Future Improvements

1. Create a larger, representative, human-labeled dataset and define train, validation, and held-out test splits.
2. Record per-class and aggregate precision, recall, F1, support counts, and a confusion matrix.
3. Evaluate escalation rules against labeled urgent/non-urgent cases, including false positives and false negatives.
4. Assess VADER sentiment results against human-labeled sentiment examples.
5. Build a relevance-labeled similarity benchmark and report ranking metrics and query latency.
6. Evaluate suggested replies with agent scoring for correctness, grounding, tone, completeness, and policy compliance.
7. Add integration tests for CSV validation, error handling, corrections, and analytics.
8. Include escalation data in the ticket-list and analytics API contracts and verify the frontend representation.
9. Calibrate the low-confidence fallback threshold using validation evidence.
10. Evaluate persistent vector indexing and semantic knowledge-base retrieval as the dataset grows.
11. Define load, concurrency, and recovery targets before deployment beyond a local demo.

## 18. Final Evaluation Summary

The project has implemented an end-to-end prototype covering ticket intake, TF-IDF/Logistic Regression category prediction, rule-based priority and escalation, VADER sentiment, Sentence Transformer and FAISS ticket similarity, TF-IDF knowledge-base retrieval, Gemini suggested replies, agent correction, bulk CSV upload, and aggregate analytics.

The repository does **not** provide measured classifier, sentiment, escalation, retrieval, or generated-reply quality results. Those metrics remain **Not evaluated yet** and should be measured with representative labeled data and documented test procedures before making claims about accuracy or production readiness. Human review remains required before a suggested reply is sent to a customer.