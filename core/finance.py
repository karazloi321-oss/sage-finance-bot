def total_balance(section):
    return section.get("cash", 0) + section.get("card", 0)
