import time
from core.db import get_conn

# =========================
# TRANSACTIONS
# =========================

def add_transaction(user_id, account, t_type, wallet, amount, category):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        INSERT INTO transactions
        (user_id, account, type, wallet, amount, category, date, timestamp)
        VALUES (?, ?, ?, ?, ?, datetime('now'), ?)
    """, (
        user_id,
        account,
        t_type,
        wallet,
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


# =========================
# GOALS
# =========================

def add_goal(user_id, name, target):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        INSERT INTO goals (user_id, name, target, saved)
        VALUES (?, ?, ?, 0)
    """, (user_id, name, target))

    conn.commit()
    conn.close()


def get_goals(user_id):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT * FROM goals WHERE user_id=?
    """, (user_id,))

    rows = c.fetchall()
    conn.close()

    return rows
