import csv
import io

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile, File

from backend.app.schemas import TicketCreate, TicketCorrection
from backend.app.db.session import get_connection
from backend.app.ai.hybrid_engine import classify_ticket
from backend.app.services.sentiment import analyze_sentiment
from backend.app.services.sla import get_sla


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)


# ============================================================
# STEP 1: CREATE SINGLE TICKET
# ============================================================

@router.post("/")
def create_ticket(ticket: TicketCreate):

    ticket_data = ticket.model_dump()

    # Run hybrid classification
    result = classify_ticket(ticket_data)

    # Sentiment analysis
    sentiment_result = analyze_sentiment(
        f"{ticket.subject} {ticket.body}"
    )

    connection = get_connection()
    cursor = connection.cursor()

    # Insert ticket
    cursor.execute(
        """
        INSERT INTO tickets
        (subject, body, channel, customer_tier)
        VALUES (?, ?, ?, ?)
        """,
        (
            ticket.subject,
            ticket.body,
            ticket.channel,
            ticket.customer_tier
        )
    )

    ticket_id = cursor.lastrowid

    # Insert classification
    cursor.execute(
        """
        INSERT INTO classifications
        (ticket_id, category, priority, sentiment, confidence, source)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            ticket_id,
            result["category"],
            result["priority"],
            sentiment_result["sentiment"],
            result["confidence"],
            result["source"]
        )
    )

    connection.commit()
    connection.close()

    return {
        "ticket_id": ticket_id,
        "subject": ticket.subject,
        "category": result["category"],
        "priority": result["priority"],
        "sentiment": sentiment_result["sentiment"],
        "confidence": result["confidence"],
        "source": result["source"],
        "escalated": result["escalated"],
        "sla": result["sla"]
    }


# ============================================================
# STEP 2: GET ALL TICKETS
# ============================================================

@router.get("/")
def get_tickets():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            t.id,
            t.subject,
            t.body,
            t.channel,
            t.customer_tier,
            t.created_at,
            c.category,
            c.priority,
            c.sentiment,
            c.confidence,
            c.source
        FROM tickets t
        LEFT JOIN classifications c
        ON t.id = c.ticket_id
        ORDER BY t.id DESC
        """
    )

    tickets = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return [
        {
            **ticket,
            "escalated": (ticket.get("priority") == "P1"),
            "sla": get_sla(ticket.get("priority") or "P4")
        }
        for ticket in tickets
    ]


# ============================================================
# STEP 3: UPDATE TICKET
# ============================================================

@router.patch("/{ticket_id}")
def update_ticket(ticket_id: int, updates: dict):

    allowed_ticket_fields = {
        "subject",
        "body",
        "channel",
        "customer_tier"
    }

    allowed_classification_fields = {
        "category",
        "priority",
        "sentiment"
    }

    connection = get_connection()
    cursor = connection.cursor()

    # Check ticket
    cursor.execute(
        """
        SELECT *
        FROM tickets
        WHERE id = ?
        """,
        (ticket_id,)
    )

    ticket = cursor.fetchone()

    if not ticket:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # Update ticket fields
    for field, new_value in updates.items():

        if field in allowed_ticket_fields:

            old_value = ticket[field]

            cursor.execute(
                f"""
                UPDATE tickets
                SET {field} = ?
                WHERE id = ?
                """,
                (
                    new_value,
                    ticket_id
                )
            )

            if str(old_value) != str(new_value):

                cursor.execute(
                    """
                    INSERT INTO corrections
                    (ticket_id, field, old_value, new_value)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        ticket_id,
                        field,
                        str(old_value),
                        str(new_value)
                    )
                )

    # Get classification
    cursor.execute(
        """
        SELECT *
        FROM classifications
        WHERE ticket_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (ticket_id,)
    )

    classification = cursor.fetchone()

    # Update classification fields
    if classification:

        for field, new_value in updates.items():

            if field in allowed_classification_fields:

                old_value = classification[field]

                cursor.execute(
                    f"""
                    UPDATE classifications
                    SET {field} = ?
                    WHERE id = ?
                    """,
                    (
                        new_value,
                        classification["id"]
                    )
                )

                if str(old_value) != str(new_value):

                    cursor.execute(
                        """
                        INSERT INTO corrections
                        (ticket_id, field, old_value, new_value)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            ticket_id,
                            field,
                            str(old_value),
                            str(new_value)
                        )
                    )

    connection.commit()
    connection.close()

    return {
        "message": "Ticket updated successfully",
        "ticket_id": ticket_id
    }


# ============================================================
# STEP 4: BULK CSV UPLOAD
# ============================================================

@router.post("/bulk")
async def bulk_upload(
    file: UploadFile = File(...)
):

    """
    Upload multiple support tickets from a CSV file.
    """

    # Check file type
    if not file.filename.lower().endswith(".csv"):

        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed."
        )

    # Read file
    content = await file.read()

    try:

        text = content.decode("utf-8")

    except UnicodeDecodeError:

        raise HTTPException(
            status_code=400,
            detail="CSV file must use UTF-8 encoding."
        )

    # Create CSV reader
    reader = csv.DictReader(
        io.StringIO(text)
    )

    # Required columns
    required_columns = {
        "subject",
        "body",
        "channel",
        "customer_tier"
    }

    actual_columns = set(
        reader.fieldnames or []
    )

    if not required_columns.issubset(
        actual_columns
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "CSV must contain these columns: "
                "subject, body, channel, customer_tier"
            )
        )

    connection = get_connection()
    cursor = connection.cursor()

    created_tickets = []

    try:

        for row in reader:

            subject = row["subject"].strip()
            body = row["body"].strip()
            channel = row["channel"].strip()
            customer_tier = row["customer_tier"].strip()

            # Skip empty rows
            if not subject or not body:
                continue

            ticket_data = {
                "subject": subject,
                "body": body,
                "channel": channel,
                "customer_tier": customer_tier
            }

            # Run hybrid AI classification
            result = classify_ticket(
                ticket_data
            )

            # Sentiment analysis
            sentiment_result = analyze_sentiment(
                f"{subject} {body}"
            )

            # Insert ticket
            cursor.execute(
                """
                INSERT INTO tickets
                (subject, body, channel, customer_tier)
                VALUES (?, ?, ?, ?)
                """,
                (
                    subject,
                    body,
                    channel,
                    customer_tier
                )
            )

            ticket_id = cursor.lastrowid

            # Insert classification
            cursor.execute(
                """
                INSERT INTO classifications
                (ticket_id, category, priority, sentiment, confidence, source)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    ticket_id,
                    result["category"],
                    result["priority"],
                    sentiment_result["sentiment"],
                    result["confidence"],
                    result["source"]
                )
            )

            created_tickets.append(
                {
                    "ticket_id": ticket_id,
                    "category": result["category"],
                    "priority": result["priority"],
                    "sentiment": sentiment_result["sentiment"]
                }
            )

        connection.commit()

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()

    return {
        "message": "Bulk upload successful",
        "total_tickets": len(created_tickets),
        "tickets": created_tickets
    }


# ============================================================
# STEP 5: SUGGESTED REPLY
# ============================================================

@router.post("/{ticket_id}/suggest-reply")
def suggest_reply(ticket_id: int):

    from backend.app.services.kb_retriever import retrieve_articles
    from backend.app.services.reply_drafter import draft_reply

    connection = None

    try:

        # ====================================================
        # 1. Get database connection
        # ====================================================

        connection = get_connection()
        cursor = connection.cursor()

        # ====================================================
        # 2. Get ticket
        # ====================================================

        cursor.execute(
            """
            SELECT *
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id,)
        )

        ticket = cursor.fetchone()

        if not ticket:

            raise HTTPException(
                status_code=404,
                detail=f"Ticket {ticket_id} not found"
            )

        # ====================================================
        # 3. Get knowledge-base articles
        # ====================================================

        cursor.execute(
            """
            SELECT id, title, body
            FROM kb_articles
            """
        )

        articles = [
            dict(row)
            for row in cursor.fetchall()
        ]

        connection.close()
        connection = None

        # ====================================================
        # 4. Prepare ticket text
        # ====================================================

        ticket_text = (
            f"{ticket['subject'] or ''} "
            f"{ticket['body'] or ''}"
        ).strip()

        # ====================================================
        # 5. Retrieve relevant KB articles
        # ====================================================

        retrieved = retrieve_articles(
            ticket_text,
            articles,
            top_k=3
        )

        relevant_articles = [
            item["article"]
            for item in retrieved
        ]

        # ====================================================
        # 6. Generate reply
        # ====================================================

        draft = draft_reply(
            ticket_text,
            relevant_articles
        )

        # ====================================================
        # 7. Save draft
        # ====================================================

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO responses
            (
                ticket_id,
                draft,
                final_text,
                status,
                approved_by
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                ticket_id,
                draft,
                None,
                "draft",
                None
            )
        )

        connection.commit()
        connection.close()
        connection = None

        # ====================================================
        # 8. Return response
        # ====================================================

        return {
            "ticket_id": ticket_id,
            "draft": draft,
            "status": "draft",
            "sources": relevant_articles
        }

    except HTTPException:
        raise

    except Exception as error:

        if connection is not None:

            try:
                connection.rollback()
                connection.close()
            except Exception:
                pass

        raise HTTPException(
            status_code=500,
            detail=f"Suggested reply error: {str(error)}"
        )


# ============================================================
# STEP 6: ANALYTICS
# ============================================================

@router.get("/analytics")
def get_analytics():

    connection = get_connection()
    cursor = connection.cursor()

    # Total tickets
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM tickets
        """
    )

    total = cursor.fetchone()["total"]

    # Category distribution
    cursor.execute(
        """
        SELECT category, COUNT(*) AS count
        FROM classifications
        GROUP BY category
        ORDER BY count DESC
        """
    )

    categories = [
        dict(row)
        for row in cursor.fetchall()
    ]

    # Priority distribution
    cursor.execute(
        """
        SELECT priority, COUNT(*) AS count
        FROM classifications
        GROUP BY priority
        ORDER BY priority
        """
    )

    priorities = [
        dict(row)
        for row in cursor.fetchall()
    ]

    # Sentiment distribution
    cursor.execute(
        """
        SELECT sentiment, COUNT(*) AS count
        FROM classifications
        GROUP BY sentiment
        """
    )

    sentiments = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return {
        "total_tickets": total,
        "categories": categories,
        "priorities": priorities,
        "sentiments": sentiments
    }


# ============================================================
# STEP 7: SIMILAR TICKETS
# ============================================================

@router.get("/{ticket_id}/similar")
def get_similar_tickets(ticket_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT t.id, t.subject, t.body
        FROM tickets t
        WHERE t.id = ?
        """,
        (ticket_id,),
    )

    current_ticket = cursor.fetchone()

    if not current_ticket:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    cursor.execute(
        """
        SELECT
            t.id,
            t.subject,
            t.body,
            c.category,
            c.priority
        FROM tickets t
        LEFT JOIN classifications c
        ON t.id = c.ticket_id
        WHERE t.id != ?
        ORDER BY t.id DESC
        """,
        (ticket_id,),
    )

    candidate_tickets = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    current_text = (
        f"{current_ticket['subject'] or ''} "
        f"{current_ticket['body'] or ''}"
    ).strip()

    candidate_texts = [
        (
            f"{ticket['subject'] or ''} "
            f"{ticket['body'] or ''}"
        ).strip()
        for ticket in candidate_tickets
    ]

    try:

        from backend.app.services.similarity import find_similar_tickets
        matches = find_similar_tickets(
            current_text,
            candidate_texts
        )

    except ValueError:

        matches = []

    return [
        {
            "id": candidate_tickets[
                match["ticket_index"]
            ]["id"],

            "subject": candidate_tickets[
                match["ticket_index"]
            ]["subject"],

            "category": candidate_tickets[
                match["ticket_index"]
            ]["category"],

            "priority": candidate_tickets[
                match["ticket_index"]
            ]["priority"],

            "similarity": max(
                0.0,
                min(
                    1.0,
                    float(match["similarity"])
                )
            ),
        }

        for match in matches[:5]
    ]


# ============================================================
# STEP 8: CORRECTION
# ============================================================

@router.post("/{ticket_id}/correction")
def create_ticket_correction(
    ticket_id: int,
    correction: TicketCorrection
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            "SELECT id FROM tickets WHERE id = ?",
            (ticket_id,)
        )

        if not cursor.fetchone():

            raise HTTPException(
                status_code=404,
                detail="Ticket not found"
            )

        cursor.execute(
            """
            SELECT id, category, priority
            FROM classifications
            WHERE ticket_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (ticket_id,)
        )

        classification = cursor.fetchone()

        original = {
            "category": (
                classification["category"]
                if classification
                else None
            ),
            "priority": (
                classification["priority"]
                if classification
                else None
            ),
        }

        corrected = {
            "category": (
                correction.category
                if correction.category is not None
                else original["category"]
            ),
            "priority": (
                correction.priority
                if correction.priority is not None
                else original["priority"]
            ),
        }

        changed_fields = [
            field

            for field in (
                "category",
                "priority"
            )

            if getattr(
                correction,
                field
            ) is not None

            and getattr(
                correction,
                field
            ) != original[field]
        ]

        if not changed_fields:

            raise HTTPException(
                status_code=400,
                detail=(
                    "The correction does not change "
                    "the current classification."
                ),
            )

        corrected_at = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        # Update classification
        if classification:

            cursor.execute(
                """
                UPDATE classifications
                SET category = ?, priority = ?
                WHERE id = ?
                """,
                (
                    corrected["category"],
                    corrected["priority"],
                    classification["id"]
                ),
            )

        else:

            cursor.execute(
                """
                INSERT INTO classifications
                (
                    ticket_id,
                    category,
                    priority
                )
                VALUES (?, ?, ?)
                """,
                (
                    ticket_id,
                    corrected["category"],
                    corrected["priority"]
                ),
            )

        # Save correction history
        saved_corrections = []

        for field in changed_fields:

            new_value = getattr(
                correction,
                field
            )

            cursor.execute(
                """
                INSERT INTO corrections
                (
                    ticket_id,
                    field,
                    old_value,
                    new_value,
                    corrected_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    ticket_id,
                    field,
                    original[field],
                    new_value,
                    corrected_at
                ),
            )

            saved_corrections.append(
                {
                    "id": cursor.lastrowid,
                    "field": field,
                    "old_value": original[field],
                    "new_value": new_value,
                    "corrected_at": corrected_at,
                }
            )

        connection.commit()

        return {
            "message": (
                "Ticket correction "
                "saved successfully"
            ),
            "ticket_id": ticket_id,
            "original": original,
            "corrected": corrected,
            "corrected_at": corrected_at,
            "corrections": saved_corrections,
        }

    except HTTPException:
        raise

    except Exception:
        connection.rollback()
        raise

    finally:

        connection.close()