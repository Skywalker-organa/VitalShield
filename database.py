import sqlite3

def create_tables():
    conn = sqlite3.connect("consent.db")
    cur  = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS consent_requests(
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT    NOT NULL,
        org_name     TEXT    NOT NULL,
        data_type    BLOB    NOT NULL,
        purpose      BLOB    NOT NULL,
        days         INTEGER NOT NULL,
        status       TEXT    DEFAULT 'Pending'
    );
    """)
    conn.commit()
    conn.close()