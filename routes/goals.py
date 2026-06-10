from flask import Blueprint, request, jsonify
import sqlite3

goals_bp = Blueprint(
    "goals",
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
# SAVE GOAL
# =====================================================

@goals_bp.route(
    "/save_goal",
    methods=["POST"]
)
def save_goal():

    data = request.json

    user_id = str(
        data.get("user_id")
    )

    title = data.get(
        "title"
    )

    target = float(
        data.get(
            "target",
            0
        )
    )

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    INSERT INTO goals
    (
        user_id,
        title,
        target
    )

    VALUES (?, ?, ?)

    """, (

        user_id,
        title,
        target

    ))

    conn.commit()
    conn.close()

    return jsonify({

        "status":"success"

    })


# =====================================================
# GET GOALS
# =====================================================

@goals_bp.route(
    "/goals/<user_id>"
)
def get_goals(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT *

    FROM goals

    WHERE user_id=?

    ORDER BY id DESC

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    result = []

    for row in rows:

        result.append({

            "id":row["id"],

            "title":row["title"],

            "target":row["target"],

            "saved":row["saved"]

        })

    return jsonify(result)


# =====================================================
# ADD MONEY
# =====================================================

@goals_bp.route(
    "/add_goal_money/<int:goal_id>",
    methods=["POST"]
)
def add_goal_money(goal_id):

    data = request.json

    amount = float(

        data.get(
            "amount",
            0
        )

    )

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    UPDATE goals

    SET saved = saved + ?

    WHERE id=?

    """, (

        amount,
        goal_id

    ))

    conn.commit()
    conn.close()

    return jsonify({

        "status":"success"

    })


# =====================================================
# DELETE GOAL
# =====================================================

@goals_bp.route(
    "/delete_goal/<int:goal_id>",
    methods=["DELETE"]
)
def delete_goal(goal_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    DELETE FROM goals

    WHERE id=?

    """, (goal_id,))

    conn.commit()
    conn.close()

    return jsonify({

        "status":"deleted"

    })


# =====================================================
# GOALS SUMMARY
# =====================================================

@goals_bp.route(
    "/goals_summary/<user_id>"
)
def goals_summary(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT *

    FROM goals

    WHERE user_id=?

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    total_target = 0
    total_saved = 0

    for row in rows:

        total_target += row["target"]
        total_saved += row["saved"]

    percent = 0

    if total_target > 0:

        percent = round(
            (total_saved / total_target) * 100,
            1
        )

    return jsonify({

        "target":total_target,

        "saved":total_saved,

        "percent":percent

    })
