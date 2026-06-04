from datetime import datetime

# =========================
# МЕСЯЧНЫЙ ФИЛЬТР
# =========================

def filter_by_month(rows, month=None, year=None):

    if not rows:
        return []

    if month is None or year is None:
        now = datetime.now()
        month = now.month
        year = now.year

    result = []

    for r in rows:
        try:
            dt = datetime.fromtimestamp(r["timestamp"])
            if dt.month == month and dt.year == year:
                result.append(r)
        except:
            continue

    return result


# =========================
# ДОХОД / РАСХОД
# =========================

def calculate_income(rows):
    return sum(r["amount"] for r in rows if r["type"] == "income")


def calculate_expense(rows):
    return sum(r["amount"] for r in rows if r["type"] == "expense")


# =========================
# СТАТИСТИКА КАТЕГОРИЙ
# =========================

def expense_stats(rows):

    stats = {}

    for r in rows:
        if r["type"] == "expense":
            cat = r.get("category", "other")
            stats[cat] = stats.get(cat, 0) + r["amount"]

    return stats


def top_category(stats):

    if not stats:
        return "Нет данных"

    return max(stats, key=stats.get)


# =========================
# БАЛАНС
# =========================

def total_balance(rows):

    income = calculate_income(rows)
    expense = calculate_expense(rows)

    return income - expense
