from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def retrieve_articles(query: str, articles: list, top_k: int = 3):
    """
    Retrieve the most relevant knowledge-base articles.
    """

    if not articles:
        return []

    article_texts = [
        f"{article['title']} {article['body']}"
        for article in articles
    ]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2)
    )

    vectors = vectorizer.fit_transform(
        [query] + article_texts
    )

    scores = cosine_similarity(
        vectors[0:1],
        vectors[1:]
    )[0]

    ranked = []

    for index, score in enumerate(scores):
        ranked.append({
            "article": articles[index],
            "score": float(score)
        })

    ranked.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked[:top_k]