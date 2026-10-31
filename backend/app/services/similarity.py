from functools import lru_cache

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def _get_embedding_model():
    return SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )


def find_similar_tickets(
    new_ticket: str,
    existing_tickets: list,
    threshold: float = 0.70
):
    """
    Find semantically similar tickets using normalized sentence embeddings.
    """

    if not existing_tickets:
        return []

    model = _get_embedding_model()
    embeddings = model.encode(
        [new_ticket] + existing_tickets,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )
    embeddings = np.ascontiguousarray(
        embeddings,
        dtype=np.float32
    )
    faiss.normalize_L2(embeddings)

    candidate_embeddings = embeddings[1:]
    query_embedding = embeddings[0:1]
    index = faiss.IndexFlatIP(candidate_embeddings.shape[1])
    index.add(candidate_embeddings)

    similarities, ticket_indices = index.search(
        query_embedding,
        len(existing_tickets)
    )

    results = []

    for ticket_index, score in zip(
        ticket_indices[0],
        similarities[0]
    ):
        if score >= threshold:
            results.append({
                "ticket_index": int(ticket_index),
                "similarity": float(score)
            })

    return results