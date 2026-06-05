from core.db import get_conn

def create_user(telegram_id, first_name, username):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    INSERT OR IGNORE INTO users
    (telegram_id, first_name, username)
    VALUES (?, ?, ?)
    """, (
        telegram_id,
        first_name,
        username
    ))

    conn.commit()
    conn.close()


def get_user(telegram_id):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT * FROM users
    WHERE telegram_id=?
    """, (telegram_id,))

    user = c.fetchone()

    conn.close()

    return user
