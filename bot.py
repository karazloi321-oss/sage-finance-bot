```python
from flask import Flask, render_template, request, jsonify
import sqlite3
import threading
import telebot
import os
import time
import logging

# =====================================================
# CONFIG
# =====================================================

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)

bot = telebot.TeleBot(TOKEN)

DB_NAME = "finance.db"

# =====================================================
# LOGGER
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("sage_finance")

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
# INIT DB
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

        timestamp REAL

    )

    """)

    # BUDGETS

    c.execute("""

    CREATE TABLE IF NOT EXISTS budgets (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id TEXT,

        category TEXT,

        amount REAL

    )

    """)

    # SUBSCRIPTIONS

    c.execute("""

    CREATE TABLE IF NOT EXISTS subscriptions (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id TEXT,

        title TEXT,

        amount REAL

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

    return render_template("index.html")

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
        timestamp
    )
    VALUES (?, ?, ?, ?, ?, ?)

    """, (

        user_id,
        account,
        t_type,
        amount,
        category,
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

@app.route(
    "/transactions/<user_id>"
)
def transactions(user_id):

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

    for r in rows:

        result.append({

            "id":r["id"],

            "account":r["account"],

            "type":r["type"],

            "amount":r["amount"],

            "category":r["category"],

            "timestamp":r["timestamp"]

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
# SAVE BUDGET
# =====================================================

@app.route(
    "/save_budget",
    methods=["POST"]
)
def save_budget():

    data = request.json

    user_id = str(
        data.get("user_id")
    )

    category = data.get(
        "category"
    )

    amount = float(
        data.get(
            "amount",
            0
        )
    )

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    INSERT INTO budgets
    (
        user_id,
        category,
        amount
    )
    VALUES (?, ?, ?)

    """, (

        user_id,
        category,
        amount

    ))

    conn.commit()

    conn.close()

    return jsonify({
        "status":"success"
    })

# =====================================================
# GET BUDGETS
# =====================================================

@app.route(
    "/budgets/<user_id>"
)
def budgets(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT *
    FROM budgets
    WHERE user_id=?

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    result = []

    for r in rows:

        result.append({

            "id":r["id"],

            "category":r["category"],

            "amount":r["amount"]

        })

    return jsonify(result)

# =====================================================
# SAVE SUBSCRIPTION
# =====================================================

@app.route(
    "/save_subscription",
    methods=["POST"]
)
def save_subscription():

    data = request.json

    user_id = str(
        data.get("user_id")
    )

    title = data.get(
        "title"
    )

    amount = float(
        data.get(
            "amount",
            0
        )
    )

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    INSERT INTO subscriptions
    (
        user_id,
        title,
        amount
    )
    VALUES (?, ?, ?)

    """, (

        user_id,
        title,
        amount

    ))

    conn.commit()

    conn.close()

    return jsonify({
        "status":"success"
    })

# =====================================================
# GET SUBSCRIPTIONS
# =====================================================

@app.route(
    "/subscriptions/<user_id>"
)
def subscriptions(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT *
    FROM subscriptions
    WHERE user_id=?

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    result = []

    for r in rows:

        result.append({

            "id":r["id"],

            "title":r["title"],

            "amount":r["amount"]

        })

    return jsonify(result)

# =====================================================
# AI ANALYTICS
# =====================================================

@app.route(
    "/ai_analytics/<user_id>"
)
def ai_analytics(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT
    type,
    SUM(amount) as total

    FROM transactions

    WHERE user_id=?

    GROUP BY type

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    income = 0
    expense = 0

    for r in rows:

        if r["type"] == "income":

            income = r["total"] or 0

        if r["type"] == "expense":

            expense = r["total"] or 0

    text = "Финансы стабильны"

    if expense > income:

        text = "Расходы превышают доходы"

    elif income > expense * 2:

        text = "Отличный контроль финансов"

    elif expense > income * 0.8:

        text = "Высокая финансовая нагрузка"

    return jsonify({
        "text":text
    })

# =====================================================
# TELEGRAM
# =====================================================

@bot.message_handler(commands=["start"])
def start(message):

    markup = telebot.types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    web_app = telebot.types.WebAppInfo(
        "https://sage-finance.onrender.com"
    )

    button = telebot.types.KeyboardButton(

        text="🏦 Открыть Sage Finance",

        web_app=web_app

    )

    markup.add(button)

    bot.send_message(

        message.chat.id,

        "🏦 Sage Finance готов",

        reply_markup=markup

    )

# =====================================================
# BOT LOOP
# =====================================================

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

# =====================================================
# START
# =====================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":

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
```
