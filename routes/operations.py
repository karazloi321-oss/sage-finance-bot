from flask import Blueprint, request, redirect
import time
from datetime import datetime

from core.storage import load_data, save_data

operations_bp = Blueprint("operations", __name__)

@operations_bp.route("/add_operation", methods=["POST"])
def add_operation():

    data = load_data()

    account = request.form.get("account")
    op_type = request.form.get("type")
    wallet = request.form.get("wallet")
    amount = float(request.form.get("amount", 0))
    category = request.form.get("category")

    if amount <= 0:
        return redirect("/")

    if op_type == "income":
        data[account][wallet] += amount
    else:
        data[account][wallet] -= amount

    op_id = str(int(time.time() * 1000))

    data[account]["history"].append({
        "id": op_id,
        "type": op_type,
        "amount": amount,
        "category": category,
        "wallet": wallet,
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "timestamp": time.time()
    })

    save_data(data)

    return redirect("/")
