# setup_db.py  –  run ONCE to create the file & table
import sqlite3

def init_db():
    conn = sqlite3.connect("consent.db")
    cur  = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS consent_requests (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT    NOT NULL,
        org_name     TEXT    NOT NULL,
        data_type    BLOB    NOT NULL,   -- encrypted
        purpose      BLOB    NOT NULL,   -- encrypted
        days         INTEGER NOT NULL,
        status       TEXT    DEFAULT 'Pending',
        created_at   TEXT    DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()
    print("✅ consent.db & table ready")

if __name__ == "__main__":
    init_db()