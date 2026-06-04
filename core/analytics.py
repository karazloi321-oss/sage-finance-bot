def calculate_income(history):
    return sum(x["amount"] for x in history if x["type"] == "income")


def calculate_expense(history):
    return sum(x["amount"] for x in history if x["type"] == "expense")


def expense_stats(expenses):
    stats = {}

    for item in expenses:
        cat = item["category"]
        stats[cat] = stats.get(cat, 0) + item["amount"]

    return stats


def top_category(expense_stats_dict):
    if not expense_stats_dict:
        return "Нет данных"

    return max(expense_stats_dict, key=expense_stats_dict.get)
