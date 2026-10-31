from .session import get_connection


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    # Tickets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            channel TEXT,
            customer_tier TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Classifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            category TEXT,
            priority TEXT,
            sentiment TEXT,
            confidence REAL,
            source TEXT,
            FOREIGN KEY (ticket_id) REFERENCES tickets(id)
        )
    """)

    # Responses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            draft TEXT,
            final_text TEXT,
            status TEXT,
            approved_by TEXT,
            FOREIGN KEY (ticket_id) REFERENCES tickets(id)
        )
    """)

    # Knowledge base articles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kb_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'General',
            embedding_ref TEXT
        )
    """)

    kb_columns = {
        row["name"]
        for row in cursor.execute("PRAGMA table_info(kb_articles)").fetchall()
    }
    if "category" not in kb_columns:
        cursor.execute(
            "ALTER TABLE kb_articles ADD COLUMN category TEXT NOT NULL DEFAULT 'General'"
        )

    sample_articles = [
        (
            "Billing",
            "Understanding an invoice or charge",
            "Compare the charge with the invoice date, plan, and any recent account changes. When contacting support, include the invoice number and charge date, but never send full payment-card details.",
        ),
        (
            "Technical",
            "Basic troubleshooting for technical issues",
            "Refresh the page and try again. If the issue continues, restart the app or browser, note the exact error and the steps that led to it, and share your device and browser details with support.",
        ),
        (
            "Account",
            "Recovering access to an account",
            "Use the password-reset flow for the email address on the account and check its spam folder for the verification message. Never share your password or one-time verification code with anyone, including support.",
        ),
        (
            "Shipping",
            "Checking a delayed shipment",
            "Review the latest carrier scan using the tracking link and confirm the delivery address on the order. If tracking has not updated or the expected delivery date has passed, contact support with the order number and tracking number.",
        ),
        (
            "General",
            "Preparing a useful support request",
            "Describe what you were trying to do, what happened instead, and when it happened. Include relevant order or ticket references, but omit passwords, payment-card details, and other sensitive information.",
        ),
    ]
    for category, title, body in sample_articles:
        cursor.execute(
            """
            INSERT INTO kb_articles (title, body, category)
            SELECT ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM kb_articles WHERE title = ? COLLATE NOCASE
            )
            """,
            (title, body, category, title),
        )

    # Corrections table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            field TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            corrected_at TEXT,
            FOREIGN KEY (ticket_id) REFERENCES tickets(id)
        )
    """)

    correction_columns = {
        row["name"]
        for row in cursor.execute("PRAGMA table_info(corrections)").fetchall()
    }
    if "corrected_at" not in correction_columns:
        cursor.execute("ALTER TABLE corrections ADD COLUMN corrected_at TEXT")

    connection.commit()
    connection.close()