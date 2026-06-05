from flask import Flask, request, jsonify
import telebot
import threading
import os
import time
import sqlite3
import logging

# =========================
# CONFIG
# =========================

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

DB_NAME = "finance.db"

# =========================
# LOGGER
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("sage_finance")

# =========================
# DATABASE
# =========================

def get_conn():

    conn = sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_conn()

    c = conn.cursor()

    # USERS
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT UNIQUE,
        first_name TEXT,
        username TEXT
    )
    """)

    # TRANSACTIONS
    c.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        type TEXT,
        amount REAL,
        category TEXT,
        timestamp REAL
    )
    """)

    conn.commit()
    conn.close()

# =========================
# INIT DB
# =========================

init_db()

# =========================
# HOME
# =========================

from flask import render_template

@app.route("/")
def home():

    return render_template("index.html")

# =========================
# HEALTH
# =========================

@app.route("/health")
def health():

    return {
        "status": "ok"
    }

# =========================
# AUTH
# =========================

@app.route("/auth", methods=["POST"])
def auth():

    data = request.json

    telegram_id = str(data.get("id"))
    first_name = data.get("first_name", "")
    username = data.get("username", "")

    conn = get_conn()

    c = conn.cursor()

    c.execute("""
    INSERT OR IGNORE INTO users
    (telegram_id, first_name, username)
    VALUES (?, ?, ?)
    """, (
        telegram_id,
        first_name,
        username
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "authorized"
    })

# =========================
# ADD TRANSACTION
# =========================

@app.route("/add_transaction", methods=["POST"])
def add_transaction():

    data = request.json

    user_id = str(data.get("user_id"))
    t_type = data.get("type")
    amount = float(data.get("amount", 0))
    category = data.get("category", "other")

    if amount <= 0:

        return jsonify({
            "error": "invalid amount"
        }), 400

    conn = get_conn()

    c = conn.cursor()

    c.execute("""
    INSERT INTO transactions
    (user_id, type, amount, category, timestamp)
    VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        t_type,
        amount,
        category,
        time.time()
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success"
    })
@app.route("/analytics/<user_id>")
def analytics(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""
    SELECT category, SUM(amount) as total
    FROM transactions
    WHERE user_id=?
    AND type='expense'
    GROUP BY category
    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    result = []

    for r in rows:

        result.append({
            "category": r["category"],
            "total": r["total"]
        })

    return jsonify(result)
# =========================
# GET TRANSACTIONS
# =========================

@app.route("/transactions/<user_id>")
def transactions(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""
    SELECT * FROM transactions
    WHERE user_id=?
    ORDER BY timestamp DESC
    """, (user_id,))

    rows = c.fetchall()

    conn.close()

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
        "https://sage-finance.onrender.com"
    )

    btn = telebot.types.KeyboardButton(
        text="🏦 Open Sage Finance",
        web_app=web_app
    )

    markup.add(btn)

    bot.send_message(
        message.chat.id,
        "🏦 Sage Finance работает",
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

            logger.error(f"BOT ERROR: {e}")

            time.sleep(5)

# =========================
# START
# =========================

if __name__ == "__main__":

    threading.Thread(
        target=run_bot,
        daemon=True
    ).start()

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    logger.info(f"APP START PORT {port}")

    app.run(
        host="0.0.0.0",
        port=port
    )
