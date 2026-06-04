import sqlite3

DB_NAME = "finance.db"


def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # ТРАНЗАКЦИИ (С USER_ID)
    c.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        account TEXT,
        type TEXT,
        wallet TEXT,
        amount REAL,
        category TEXT,
        date TEXT,
        timestamp REAL
    )
    """)

    # ЦЕЛИ
    c.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        name TEXT,
        target REAL,
        saved REAL DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()
