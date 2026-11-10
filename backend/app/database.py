import sqlite3
from pathlib import Path


# Store the database in the main project folder
DATABASE_PATH = Path(__file__).resolve().parents[2] / "studymind.db"


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def initialize_database():
    """Create the documents table if it does not exist."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_documents(documents):
    """Save documents without creating duplicates."""

    connection = get_connection()
    cursor = connection.cursor()

    for document in documents:
        cursor.execute(
            "INSERT OR IGNORE INTO documents (content) VALUES (?)",
            (document,)
        )

    connection.commit()
    connection.close()


def get_all_documents():
    """Retrieve all previously stored documents."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT content FROM documents ORDER BY id"
    )

    documents = [row[0] for row in cursor.fetchall()]

    connection.close()

    return documents