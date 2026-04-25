# Component: Components 3/4 - Schema Extensions

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pams.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def _column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row["name"] == column for row in cursor.fetchall())


def _table_exists(cursor, table):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,))
    return cursor.fetchone() is not None


def extend_schema():
    conn = get_connection()
    cursor = conn.cursor()

    # Add is_active to apartments if missing
    if _table_exists(cursor, "apartments"):
        if not _column_exists(cursor, "apartments", "is_active"):
            cursor.execute(
                "ALTER TABLE apartments ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")

    # Complaints table
    if not _table_exists(cursor, "complaints"):
        cursor.execute("""
            CREATE TABLE complaints (
                complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                linked_request_id INTEGER,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
                FOREIGN KEY (linked_request_id)
                    REFERENCES maintenance_requests(request_id)
            )
        """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    extend_schema()
    print("Schema extended successfully.")
