from flask import Blueprint, request, jsonify
import sqlite3
import time
from datetime import datetime

transactions_bp = Blueprint(
    "transactions",
    __name__
)

DB_NAME = "finance.db"


def get_conn():

    conn = sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


# =====================================================
# ADD TRANSACTION
# =====================================================

@transactions_bp.route(
    "/add_transaction",
    methods=["POST"]
)
def add_transaction():

    data = request.json

    user_id = str(
        data.get("user_id")
    )

    account = data.get(
        "account"
    )

    t_type = data.get(
        "type"
    )

    amount = float(
        data.get(
            "amount",
            0
        )
    )

    category = data.get(
        "category",
        "Другое"
    )

    if amount <= 0:

        return jsonify({

            "error":"invalid amount"

        }), 400

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    INSERT INTO transactions
    (
        user_id,
        account,
        type,
        amount,
        category,
        created_at,
        timestamp
    )

    VALUES (?, ?, ?, ?, ?, ?, ?)

    """, (

        user_id,
        account,
        t_type,
        amount,
        category,
        datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        ),
        time.time()

    ))

    conn.commit()
    conn.close()

    return jsonify({

        "status":"success"

    })


# =====================================================
# GET TRANSACTIONS
# =====================================================

@transactions_bp.route(
    "/transactions/<user_id>"
)
def get_transactions(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT *

    FROM transactions

    WHERE user_id=?

    ORDER BY timestamp DESC

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    result = []

    for row in rows:

        result.append({

            "id":row["id"],
            "account":row["account"],
            "type":row["type"],
            "amount":row["amount"],
            "category":row["category"],
            "created_at":row["created_at"]

        })

    return jsonify(result)


# =====================================================
# DELETE TRANSACTION
# =====================================================

@transactions_bp.route(
    "/delete_transaction/<int:transaction_id>",
    methods=["DELETE"]
)
def delete_transaction(transaction_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    DELETE FROM transactions

    WHERE id=?

    """, (transaction_id,))

    conn.commit()
    conn.close()

    return jsonify({

        "status":"deleted"

    })


# =====================================================
# BALANCE
# =====================================================

@transactions_bp.route(
    "/balance/<user_id>"
)
def balance(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT type,
    SUM(amount) as total

    FROM transactions

    WHERE user_id=?

    GROUP BY type

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    income = 0
    expense = 0

    for row in rows:

        if row["type"] == "income":

            income = row["total"] or 0

        elif row["type"] == "expense":

            expense = row["total"] or 0

    return jsonify({

        "income":income,
        "expense":expense,
        "total":income-expense

    })


# =====================================================
# BUSINESS SUMMARY
# =====================================================

@transactions_bp.route(
    "/business_summary/<user_id>"
)
def business_summary(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT *

    FROM transactions

    WHERE user_id=?
    AND account='business'

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    income = 0
    expense = 0

    for row in rows:

        if row["type"] == "income":

            income += row["amount"]

        else:

            expense += row["amount"]

    profit = income - expense

    margin = 0

    if income > 0:

        margin = round(
            (profit / income) * 100,
            1
        )

    return jsonify({

        "income":income,
        "expense":expense,
        "profit":profit,
        "margin":margin

    })


# =====================================================
# LAST OPERATIONS
# =====================================================

@transactions_bp.route(
    "/last_transactions/<user_id>"
)
def last_transactions(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT *

    FROM transactions

    WHERE user_id=?

    ORDER BY timestamp DESC

    LIMIT 5

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    result = []

    for row in rows:

        result.append({

            "category":row["category"],
            "amount":row["amount"],
            "type":row["type"],
            "created_at":row["created_at"]

        })

    return jsonify(result)
