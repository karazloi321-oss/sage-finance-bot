from flask import Blueprint, jsonify
import sqlite3

ai_bp = Blueprint(
    "ai",
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
# AI ANALYTICS
# =====================================================

@ai_bp.route(
    "/ai/<user_id>"
)
def ai(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT *

    FROM transactions

    WHERE user_id=?

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    income = 0
    expense = 0

    business_income = 0
    business_expense = 0

    categories = {}

    for row in rows:

        amount = row["amount"]

        if row["type"] == "income":

            income += amount

        else:

            expense += amount

            cat = row["category"]

            if cat not in categories:

                categories[cat] = 0

            categories[cat] += amount

        if row["account"] == "business":

            if row["type"] == "income":

                business_income += amount

            else:

                business_expense += amount

    profit = business_income - business_expense

    text = []

    # Общий анализ

    if income == 0 and expense == 0:

        text.append(
            "📊 Пока нет данных для анализа."
        )

    else:

        if expense > income:

            text.append(
                "⚠️ Расходы превышают доходы."
            )

        elif income > expense * 2:

            text.append(
                "🚀 Доходы значительно выше расходов."
            )

        else:

            text.append(
                "✅ Финансовый баланс стабильный."
            )

    # Бизнес

    if business_income > 0:

        if profit > 0:

            text.append(

                f"💼 Бизнес прибыльный. "
                f"Прибыль: {profit:.0f} ₽"

            )

        else:

            text.append(

                "📉 Бизнес работает "
                "в убыток."

            )

    # Категория-лидер расходов

    if categories:

        top_category = max(
            categories,
            key=categories.get
        )

        text.append(

            f"🔥 Больше всего расходов "
            f"в категории "
            f"{top_category}"

        )

    return jsonify({

        "text":"\n\n".join(text)

    })


# =====================================================
# DASHBOARD SUMMARY
# =====================================================

@ai_bp.route(
    "/dashboard_summary/<user_id>"
)
def dashboard_summary(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT *

    FROM transactions

    WHERE user_id=?

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

    return jsonify({

        "income":income,
        "expense":expense,
        "balance":income-expense

    })
