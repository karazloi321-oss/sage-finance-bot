def safe_add(balance, amount):
    if amount < 0:
        return balance
    return balance + amount


def safe_subtract(balance, amount):
    if amount < 0:
        return balance

    if balance - amount < 0:
        return 0

    return balance


def validate_amount(amount):
    try:
        amount = float(amount)
        return amount if amount > 0 else 0
    except:
        return 0
