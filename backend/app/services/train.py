import csv
from pathlib import Path

from backend.app.services.ml_classifier import train_category_model
from backend.app.services.preprocess import clean_text


BASE_DIR = Path(__file__).resolve().parents[3]

DATASET_PATH = BASE_DIR / "data" / "sample" / "tickets.csv"


def load_dataset():
    texts = []
    labels = []

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            subject = clean_text(row["subject"])
            body = clean_text(row["body"])

            text = f"{subject} {body}".strip()

            texts.append(text)
            labels.append(row["category"])

    return texts, labels


def main():
    texts, labels = load_dataset()

    print(f"Loaded {len(texts)} tickets")

    model, vectorizer = train_category_model(
        texts,
        labels
    )

    print("Category model trained successfully.")


if __name__ == "__main__":
    main()