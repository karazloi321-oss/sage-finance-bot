from flask import Flask, request, redirect, render_template
import telebot
from telebot import types
import threading
import time
import os
from datetime import datetime

from core.storage import load_data, save_data
from core.finance import total_balance

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():
    data = load_data()

    personal_total = total_balance(data["personal"])
    business_total = total_balance(data["business"])
    savings_total = total_balance(data["savings"])

    total_all = personal_total + business_total + savings_total

    all_history = (
        data["personal"]["history"] +
        data["business"]["history"]
    )

    all_history = sorted(all_history, key=lambda x: x["timestamp"], reverse=True)

    return render_template(
        "index.html",
        total_all=total_all,
        personal_total=personal_total,
        business_total=business_total,
        savings_total=savings_total,
        history=all_history
    )

# =====================================================
# ADD OPERATION
# =====================================================

@app.route("/add_operation", methods=["POST"])
def add_operation():
    data = load_data()

    account = request.form.get("account")
    op_type = request.form.get("type")
    wallet = request.form.get("wallet")
    amount = float(request.form.get("amount", 0))
    category = request.form.get("category")

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
