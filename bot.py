from flask import Flask, render_template, request, jsonify
import sqlite3
import threading
import telebot
from telebot import types
import os
import time
import logging
from datetime import datetime

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

    # INVENTORY

    c.execute("""

    CREATE TABLE IF NOT EXISTS inventory (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id TEXT,

        name TEXT,

        quantity REAL,

        purchase_price REAL,

        sell_price REAL,

        created_at TEXT

    )

    """)

    conn.commit()

    conn.close()

init_db()

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
# ADD TRANSACTION
# =====================================================

@app.route(
    "/add_transaction",
    methods=["POST"]
)
def add_transaction():

    data = request.json

    user_id = str(
        data.get("user_id")
    )

    account = data.get(
        "account"
    )

    t_type = data.get(
        "type"
    )

    amount = float(
        data.get(
            "amount",
            0
        )
    )

    category = data.get(
        "category",
        "Другое"
    )

    if amount <= 0:

        return jsonify({

            "error":"invalid amount"

        }), 400

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    INSERT INTO transactions
    (
        user_id,
        account,
        type,
        amount,
        category,
        created_at,
        timestamp
    )

    VALUES (?, ?, ?, ?, ?, ?, ?)

    """, (

        user_id,
        account,
        t_type,
        amount,
        category,

        datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        ),

        time.time()

    ))

    conn.commit()

    conn.close()

    return jsonify({

        "status":"success"

    })

# =====================================================
# GET TRANSACTIONS
# =====================================================

@app.route("/transactions/<user_id>")
def get_transactions(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT *
    FROM transactions

    WHERE user_id=?

    ORDER BY timestamp DESC

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    result = []

    for row in rows:

        result.append({

            "id":row["id"],
            "account":row["account"],
            "type":row["type"],
            "amount":row["amount"],
            "category":row["category"],
            "created_at":row["created_at"]

        })

    return jsonify(result)

# =====================================================
# DELETE TRANSACTION
# =====================================================

@app.route(
    "/delete_transaction/<int:transaction_id>",
    methods=["DELETE"]
)
def delete_transaction(transaction_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    DELETE FROM transactions
    WHERE id=?

    """, (transaction_id,))

    conn.commit()

    conn.close()

    return jsonify({

        "status":"deleted"

    })

# =====================================================
# DASHBOARD
# =====================================================

@app.route("/dashboard/<user_id>")
def dashboard(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT *
    FROM transactions

    WHERE user_id=?

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    income = 0
    expense = 0

    business_income = 0
    business_expense = 0

    for row in rows:

        amount = row["amount"]

        if row["type"] == "income":

            income += amount

            if row["account"] == "business":

                business_income += amount

        else:

            expense += amount

            if row["account"] == "business":

                business_expense += amount

    profit = business_income - business_expense

    margin = 0

    if business_income > 0:

        margin = round(

            (profit / business_income) * 100,
            1

        )

    return jsonify({

        "income":income,
        "expense":expense,

        "business_income":business_income,
        "business_expense":business_expense,

        "profit":profit,
        "margin":margin

    })

# =====================================================
# AI ANALYTICS
# =====================================================

@app.route("/ai/<user_id>")
def ai(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT *
    FROM transactions

    WHERE user_id=?

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    income = 0
    expense = 0

    for row in rows:

        if row["type"] == "income":

            income += row["amount"]

        else:

            expense += row["amount"]

    text = "Финансы стабильны"

    if expense > income:

        text = (
            "⚠️ Расходы превышают доходы"
        )

    elif income > expense * 2:

        text = (
            "🚀 Отличный рост капитала"
        )

    elif expense > income * 0.8:

        text = (
            "📉 Высокая нагрузка на бюджет"
        )

    return jsonify({

        "text":text

    })

# =====================================================
# ADD PRODUCT
# =====================================================

@app.route(
    "/add_product",
    methods=["POST"]
)
def add_product():

    data = request.json

    user_id = str(
        data.get("user_id")
    )

    name = data.get(
        "name"
    )

    quantity = float(
        data.get(
            "quantity",
            0
        )
    )

    purchase_price = float(
        data.get(
            "purchase_price",
            0
        )
    )

    sell_price = float(
        data.get(
            "sell_price",
            0
        )
    )

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    INSERT INTO inventory
    (
        user_id,
        name,
        quantity,
        purchase_price,
        sell_price,
        created_at
    )

    VALUES (?, ?, ?, ?, ?, ?)

    """, (

        user_id,
        name,
        quantity,
        purchase_price,
        sell_price,

        datetime.now().strftime(
            "%d.%m.%Y"
        )

    ))

    conn.commit()

    conn.close()

    return jsonify({

        "status":"success"

    })

# =====================================================
# GET INVENTORY
# =====================================================

@app.route("/inventory/<user_id>")
def inventory(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT *
    FROM inventory

    WHERE user_id=?

    ORDER BY id DESC

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    result = []

    for row in rows:

        result.append({

            "id":row["id"],
            "name":row["name"],
            "quantity":row["quantity"],
            "purchase_price":row["purchase_price"],
            "sell_price":row["sell_price"]

        })

    return jsonify(result)

# =====================================================
# TELEGRAM START
# =====================================================

@bot.message_handler(commands=["start"])
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

        "🏦 Sage Finance V21 готов",

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

                allowed_updates=["message"]

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

    if not app.debug:

        threading.Thread(

            target=run_bot,

            daemon=True

        ).start()

    logger.info(
        f"APP START PORT {port}"
    )

    app.run(

        host="0.0.0.0",

        port=port,

        debug=False,

        use_reloader=False

    )
