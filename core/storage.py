import time
from core.db import get_conn

def add_transaction(
    user_id,
    t_type,
    amount,
    category
):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""
    INSERT INTO transactions
    (user_id, type, amount, category, timestamp)
    VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        t_type,
        amount,
        category,
        time.time()
    ))

    conn.commit()
    conn.close()


def get_transactions(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""
    SELECT * FROM transactions
    WHERE user_id=?
    ORDER BY timestamp DESC
    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    return rows
