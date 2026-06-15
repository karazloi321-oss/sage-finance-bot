from flask import Flask, render_template, jsonify
import telebot
from telebot import types
import sqlite3
import threading
import logging
import time
import os

# =====================================================
# ROUTES
# =====================================================

from routes.transactions import transactions_bp
from routes.goals import goals_bp
from routes.debts import debts_bp
from routes.ai import ai_bp
from routes.warehouse import warehouse_bp

# =====================================================
# CONFIG
# =====================================================

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)

bot = telebot.TeleBot(
    TOKEN,
    parse_mode="HTML"
)

DB_NAME = "finance.db"

# =====================================================
# LOGGER
# =====================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(
    "sage_finance"
)

# =====================================================
# DATABASE
# =====================================================

def get_conn():

    conn = sqlite3.connect(

        DB_NAME,

        check_same_thread=False

    )

    conn.row_factory = sqlite3.Row

    return conn

# =====================================================
# INIT DATABASE
# =====================================================

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

        account TEXT,

        type TEXT,

        amount REAL,

        category TEXT,

        created_at TEXT,

        timestamp REAL

    )

    """)

    # GOALS

    c.execute("""

    CREATE TABLE IF NOT EXISTS goals (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id TEXT,

        title TEXT,

        target REAL,

        saved REAL DEFAULT 0

    )

    """)

    # DEBTS

    c.execute("""

    CREATE TABLE IF NOT EXISTS debts (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id TEXT,

        person TEXT,

        amount REAL,

        type TEXT,

        created_at TEXT

    )

    """)

    # PRODUCTS

c.execute("""

CREATE TABLE IF NOT EXISTS products (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT,

    category TEXT,

    quantity REAL DEFAULT 0,

    buy_price REAL DEFAULT 0,

    sell_price REAL DEFAULT 0,

    barcode TEXT,

    created_at TEXT

)

""")
    conn.commit()

    conn.close()

init_db()

# =====================================================
# REGISTER BLUEPRINTS
# =====================================================

app.register_blueprint(
    transactions_bp
)

app.register_blueprint(
    goals_bp
)

app.register_blueprint(
    debts_bp
)

app.register_blueprint(
    ai_bp
)
app.register_blueprint(
    warehouse_bp
)
# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )

# =====================================================
# HEALTH
# =====================================================

@app.route("/health")
def health():

    return jsonify({

        "status":"ok"

    })

# =====================================================
# AUTH
# =====================================================

@app.route(
    "/auth",
    methods=["POST"]
)
def auth():

    from flask import request

    data = request.json

    telegram_id = str(
        data.get("id")
    )

    first_name = data.get(
        "first_name",
        ""
    )

    username = data.get(
        "username",
        ""
    )

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    INSERT OR IGNORE INTO users
    (
        telegram_id,
        first_name,
        username
    )

    VALUES (?, ?, ?)

    """, (

        telegram_id,
        first_name,
        username

    ))

    conn.commit()

    conn.close()

    return jsonify({

        "status":"authorized"

    })

# =====================================================
# TELEGRAM START
# =====================================================

@bot.message_handler(
    commands=["start"]
)
def start(message):

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    web_app = types.WebAppInfo(
        "https://sage-finance.onrender.com"
    )

    button = types.KeyboardButton(

        text="🏦 Открыть Sage Finance",

        web_app=web_app

    )

    markup.add(button)

    bot.send_message(

        message.chat.id,

        "🏦 Sage Finance V26",

        reply_markup=markup

    )

# =====================================================
# BOT LOOP
# =====================================================

def run_bot():

    while True:

        try:

            logger.info(
                "BOT START"
            )

            bot.remove_webhook()

            time.sleep(2)

            bot.infinity_polling(

                timeout=30,

                long_polling_timeout=30,

                skip_pending=True,

                allowed_updates=[
                    "message"
                ]

            )

        except Exception as e:

            logger.error(

                f"BOT ERROR: {e}"

            )

            try:

                bot.stop_polling()

            except:
                pass

            time.sleep(10)

# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":

    port = int(

        os.environ.get(
            "PORT",
            10000
        )

    )

    threading.Thread(

        target=run_bot,

        daemon=True

    ).start()

    logger.info(

        f"APP START {port}"

    )

    app.run(

        host="0.0.0.0",

        port=port,

        debug=False,

        use_reloader=False

    )
