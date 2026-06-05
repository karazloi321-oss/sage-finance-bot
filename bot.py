from flask import Flask, request, jsonify
import telebot
import threading
import os
import time

from core.logger import logger
from core.db import init_db
from core.auth import create_user
from core.storage import add_transaction, get_transactions

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

# =========================
# INIT DB
# =========================

init_db()

# =========================
# HEALTH
# =========================

@app.route("/health")
def health():
    return {
        "status": "ok"
    }

# =========================
# TELEGRAM AUTH
# =========================

@app.route("/auth", methods=["POST"])
def auth():

    data = request.json

    telegram_id = str(data.get("id"))
    first_name = data.get("first_name", "")
    username = data.get("username", "")

    create_user(
        telegram_id,
        first_name,
        username
    )

    return jsonify({
        "status": "authorized",
        "telegram_id": telegram_id
    })

# =========================
# ADD TRANSACTION
# =========================

@app.route("/add_transaction", methods=["POST"])
def add_transaction_route():

    data = request.json

    user_id = str(data.get("user_id"))
    t_type = data.get("type")
    amount = float(data.get("amount", 0))
    category = data.get("category")

    if amount <= 0:
        return jsonify({
            "error": "invalid amount"
        }), 400

    add_transaction(
        user_id,
        t_type,
        amount,
        category
    )

    return jsonify({
        "status": "success"
    })

# =========================
# GET TRANSACTIONS
# =========================

@app.route("/transactions/<user_id>")
def transactions(user_id):

    rows = get_transactions(user_id)

    result = []

    for r in rows:
        result.append({
            "id": r["id"],
            "type": r["type"],
            "amount": r["amount"],
            "category": r["category"],
            "timestamp": r["timestamp"]
        })

    return jsonify(result)

# =========================
# TELEGRAM BOT
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    logger.info(f"USER {message.chat.id}")

    markup = telebot.types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    web_app = telebot.types.WebAppInfo(
        "https://YOUR-RENDER-URL.onrender.com"
    )

    btn = telebot.types.KeyboardButton(
        text="🏦 Open Sage Finance",
        web_app=web_app
    )

    markup.add(btn)

    bot.send_message(
        message.chat.id,
        "🏦 Sage Finance V10",
        reply_markup=markup
    )

# =========================
# BOT LOOP
# =========================

def run_bot():

    while True:

        try:

            logger.info("BOT START")

            bot.remove_webhook()

            bot.infinity_polling(
                timeout=30,
                long_polling_timeout=30,
                skip_pending=True
            )

        except Exception as e:

            logger.error(e)

            time.sleep(5)

# =========================
# START BOT THREAD
# =========================

telegram_thread = threading.Thread(
    target=run_bot,
    daemon=True
)

telegram_thread.start()
