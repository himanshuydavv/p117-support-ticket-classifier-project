from fastapi import APIRouter, HTTPException

from backend.app.db.session import get_connection


router = APIRouter(
    prefix="/knowledge-base",
    tags=["Knowledge Base"],
)


def fetch_articles(where_clause="", parameters=()):
    connection = get_connection()
    try:
        query = """
            SELECT id, title, body, category, embedding_ref
            FROM kb_articles
        """
        if where_clause:
            query += f" WHERE {where_clause}"
        query += " ORDER BY category COLLATE NOCASE, title COLLATE NOCASE"
        rows = connection.execute(query, parameters).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


@router.get("/")
def list_articles(category: str | None = None):
    if category and category.strip():
        return fetch_articles(
            "category = ? COLLATE NOCASE",
            (category.strip(),),
        )
    return fetch_articles()


@router.get("/search")
def search_articles(q: str | None = None, category: str | None = None):
    conditions = []
    parameters = []

    if q and q.strip():
        search_term = f"%{q.strip()}%"
        conditions.append(
            "(title LIKE ? COLLATE NOCASE "
            "OR body LIKE ? COLLATE NOCASE "
            "OR category LIKE ? COLLATE NOCASE)"
        )
        parameters.extend((search_term, search_term, search_term))

    if category and category.strip():
        conditions.append("category = ? COLLATE NOCASE")
        parameters.append(category.strip())

    if not conditions:
        raise HTTPException(
            status_code=400,
            detail="Provide a search query or category.",
        )

    return fetch_articles(" AND ".join(conditions), parameters)
