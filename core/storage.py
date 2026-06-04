from core.db import get_conn

def add_transaction(account, t_type, wallet, amount, category):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        INSERT INTO transactions
        (account, type, wallet, amount, category, date, timestamp)
        VALUES (?, ?, ?, ?, ?, datetime('now'), strftime('%s','now'))
    """, (account, t_type, wallet, amount, category))

    conn.commit()
    conn.close()


def get_all_transactions():
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM transactions ORDER BY timestamp DESC")
    rows = c.fetchall()

    conn.close()
    return rows


def get_goals():
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM goals")
    rows = c.fetchall()

    conn.close()
    return rows


def add_goal(name, target):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        INSERT INTO goals (name, target, saved)
        VALUES (?, ?, 0)
    """, (name, target))

    conn.commit()
    conn.close()
