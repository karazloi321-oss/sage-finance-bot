def calculate_income(history):
    return sum(x["amount"] for x in history if x["type"] == "income")


def calculate_expense(history):
    return sum(x["amount"] for x in history if x["type"] == "expense")


def expense_stats(expenses):
    stats = {}

    for item in expenses:
        cat = item.get("category", "other")
        stats[cat] = stats.get(cat, 0) + item.get("amount", 0)

    return stats


def top_category(stats):
    if not stats:
        return "Нет данных"
    return max(stats, key=stats.get)
