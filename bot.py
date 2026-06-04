from flask import Flask, request, redirect, render_template
import telebot
from telebot import types
import threading
import time
import os
import json
from datetime import datetime

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "data.json"

# =====================================================
# INIT DATA
# =====================================================

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "personal": {"cash": 0, "card": 0, "expenses": [], "history": []},
            "business": {"cash": 0, "card": 0, "expenses": [], "history": []},
            "savings": {"cash": 0, "card": 0},
            "debts": [],
            "goals": []
        }, f, ensure_ascii=False, indent=4)


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def total_balance(section):
    return section["cash"] + section["card"]


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
        history=all_history,
        data=data
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


# =====================================================
# TELEGRAM
# =====================================================

@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    web_app = types.WebAppInfo("https://sage-finance.onrender.com/")

    button = types.KeyboardButton(
        text="🏦 Open Sage Finance",
        web_app=web_app
    )

    markup.add(button)

    bot.send_message(
        message.chat.id,
        "🏦 Sage Finance ready",
        reply_markup=markup
    )


def run_bot():
    while True:
        try:
            bot.remove_webhook()
            time.sleep(2)
            bot.infinity_polling(skip_pending=True)
        except Exception as e:
            print(e)
            time.sleep(5)


if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
