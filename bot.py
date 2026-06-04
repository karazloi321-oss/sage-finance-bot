from flask import Flask, request, redirect, render_template
import telebot
from telebot import types
import threading
import time
import os

from core.storage import load_data
from core.finance import total_balance

from routes.operations import operations_bp
from routes.goals import goals_bp
from core.analytics import (
    calculate_income,
    calculate_expense,
    expense_stats,
    top_category
)

from core.safety import (
    safe_add,
    safe_subtract,
    validate_amount
)

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

# =====================================================
# REGISTER ROUTES
# =====================================================

app.register_blueprint(operations_bp)
app.register_blueprint(goals_bp)

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

    income_total = calculate_income(all_history)
    expense_total = calculate_expense(all_history)

    personal_stats = expense_stats(data["personal"]["expenses"])
    top_expense = top_category(personal_stats)

    return render_template(
        "index.html",
        total_all=total_all,
        personal_total=personal_total,
        business_total=business_total,
        savings_total=savings_total,
        history=all_history,
        income_total=income_total,
        expense_total=expense_total,
        top_category=top_expense
    )
# =====================================================
# TELEGRAM
# =====================================================

@bot.message_handler(commands=["start"])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    web_app = types.WebAppInfo(
        "https://sage-finance.onrender.com/"
    )

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

# =====================================================
# BOT LOOP
# =====================================================

def run_bot():

    while True:
        try:
            bot.remove_webhook()
            time.sleep(2)
            bot.infinity_polling(skip_pending=True)
        except Exception as e:
            print("BOT ERROR:", e)
            time.sleep(5)

# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
