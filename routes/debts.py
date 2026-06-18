from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime

debts_bp = Blueprint(
    "debts",
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
# SAVE DEBT
# =====================================================

@debts_bp.route(
    "/save_debt",
    methods=["POST"]
)
def save_debt():

    data = request.json

    user_id = str(
        data.get("user_id")
    )

    person = data.get(
        "person"
    )

    amount = float(
        data.get(
            "amount",
            0
        )
    )

    debt_type = data.get(
        "type"
    )

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    INSERT INTO debts
    (
        user_id,
        person,
        amount,
        type,
        created_at
    )

    VALUES (?, ?, ?, ?, ?)

    """, (

        user_id,
        person,
        amount,
        debt_type,
        datetime.now().strftime(
            "%d.%m.%Y"
        )

    ))

    conn.commit()
    conn.close()

    return jsonify({

        "status":"success"

    })


# =====================================================
# GET DEBTS
# =====================================================

@debts_bp.route(
    "/debts/<user_id>"
)
def get_debts(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT *

    FROM debts

    WHERE user_id=?

    ORDER BY id DESC

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    result = []

    for row in rows:

        result.append({

            "id":row["id"],

            "person":row["person"],

            "amount":row["amount"],

            "type":row["type"],

            "created_at":row["created_at"]

        })

    return jsonify(result)


# =====================================================
# DELETE DEBT
# =====================================================

@debts_bp.route(
    "/delete_debt/<int:debt_id>",
    methods=["DELETE"]
)
def delete_debt(debt_id):

    data = request.json or {}

    user_id = str(
        data.get("user_id", "")
    )

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    DELETE FROM debts

    WHERE id=?
    AND user_id=?

    """, (

        debt_id,
        user_id

    ))

    conn.commit()
    conn.close()

    return jsonify({

        "status":"deleted"

    })


# =====================================================
# UPDATE DEBT
# =====================================================

@debts_bp.route(
    "/update_debt/<int:debt_id>",
    methods=["POST"]
)
def update_debt(debt_id):

    data = request.json

    user_id = str(
        data.get("user_id")
    )

    amount = float(
        data.get(
            "amount",
            0
        )
    )

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    UPDATE debts

    SET amount=?

    WHERE id=?
    AND user_id=?

    """, (

        amount,
        debt_id,
        user_id

    ))

    conn.commit()
    conn.close()

    return jsonify({

        "status":"updated"

    })


# =====================================================
# DEBTS SUMMARY
# =====================================================

@debts_bp.route(
    "/debts_summary/<user_id>"
)
def debts_summary(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT *

    FROM debts

    WHERE user_id=?

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    i_owe = 0
    owe_me = 0

    for row in rows:

        if row["type"] == "i_debt":

            i_owe += row["amount"]

        else:

            owe_me += row["amount"]

    net = owe_me - i_owe

    return jsonify({

        "i_owe":i_owe,

        "owe_me":owe_me,

        "net":net

    })
