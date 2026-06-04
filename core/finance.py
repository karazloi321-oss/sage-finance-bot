def calculate_income(rows):
    return sum(r["amount"] for r in rows if r["type"] == "income")


def calculate_expense(rows):
    return sum(r["amount"] for r in rows if r["type"] == "expense")


def expense_stats(rows):
    stats = {}

    for r in rows:
        if r["type"] == "expense":
            cat = r["category"] or "other"
            stats[cat] = stats.get(cat, 0) + r["amount"]

    return stats


def total_balance(rows):
    income = sum(r["amount"] for r in rows if r["type"] == "income")
    expense = sum(r["amount"] for r in rows if r["type"] == "expense")
    return income - expense
