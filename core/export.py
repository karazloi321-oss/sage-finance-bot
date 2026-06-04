import csv

# =========================
# EXPORT TO CSV
# =========================

def export_to_csv(rows, filename="export.csv"):

    headers = [
        "id",
        "type",
        "amount",
        "category",
        "wallet",
        "date",
        "timestamp"
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)

        writer.writeheader()

        for r in rows:
            writer.writerow({
                "id": r["id"],
                "type": r["type"],
                "amount": r["amount"],
                "category": r["category"],
                "wallet": r["wallet"],
                "date": r["date"],
                "timestamp": r["timestamp"]
            })

    return filename
