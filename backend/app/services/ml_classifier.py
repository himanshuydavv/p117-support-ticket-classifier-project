import joblib
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_DIR = BASE_DIR / "data" / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "category_model.pkl"
VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.pkl"


def train_category_model(texts, labels):
    """
    Train TF-IDF + Logistic Regression category classifier.
    """

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        max_features=5000
    )

    X = vectorizer.fit_transform(texts)

    model = LogisticRegression(
        max_iter=1000
    )

    model.fit(X, labels)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    return model, vectorizer


def predict_category(text: str):
    """
    Predict ticket category and confidence.
    """

    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)

    X = vectorizer.transform([text])

    prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]
    confidence = max(probabilities)

    threshold = 0.0

    return {
        "category": prediction,
        "confidence": float(confidence),
        "source": "ml",
        "needs_fallback": confidence < threshold
    }