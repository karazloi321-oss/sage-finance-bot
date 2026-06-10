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
# BALANCE
# =====================================================

@app.route("/balance/<user_id>")
def balance(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT type, SUM(amount) as total

    FROM transactions

    WHERE user_id=?

    GROUP BY type

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    income = 0
    expense = 0

    for row in rows:

        if row["type"] == "income":
            income = row["total"] or 0

        if row["type"] == "expense":
            expense = row["total"] or 0

    total = income - expense

    return jsonify({

        "income":income,

        "expense":expense,

        "total":total

    })

# =====================================================
# SAVE GOAL
# =====================================================

@app.route(
    "/save_goal",
    methods=["POST"]
)
def save_goal():

    data = request.json

    user_id = str(
        data.get("user_id")
    )

    title = data.get(
        "title"
    )

    target = float(
        data.get(
            "target",
            0
        )
    )

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    INSERT INTO goals
    (
        user_id,
        title,
        target
    )

    VALUES (?, ?, ?)

    """, (

        user_id,
        title,
        target

    ))

    conn.commit()

    conn.close()

    return jsonify({
        "status":"success"
    })

# =====================================================
# GET GOALS
# =====================================================

@app.route("/goals/<user_id>")
def goals(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT *
    FROM goals

    WHERE user_id=?

    ORDER BY id DESC

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    result = []

    for row in rows:

        result.append({

            "id":row["id"],

            "title":row["title"],

            "target":row["target"],

            "saved":row["saved"]

        })

    return jsonify(result)


# =====================================================
# ADD MONEY TO GOAL
# =====================================================

@app.route(

    "/add_goal_money/<int:goal_id>",

    methods=["POST"]

)
def add_goal_money(goal_id):

    data = request.json

    amount = float(

        data.get(
            "amount",
            0
        )

    )

    if amount <= 0:

        return jsonify({

            "error":"invalid amount"

        }), 400

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    UPDATE goals

    SET saved = saved + ?

    WHERE id = ?

    """, (

        amount,

        goal_id

    ))

    conn.commit()

    conn.close()

    return jsonify({

        "status":"success"

    })

# =====================================================
# DELETE DEBT
# =====================================================

@app.route(

    "/delete_debt/<int:debt_id>",

    methods=["DELETE"]

)
def delete_debt(debt_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    DELETE FROM debts

    WHERE id=?

    """, (debt_id,))

    conn.commit()

    conn.close()

    return jsonify({

        "status":"deleted"

    })

# =====================================================
# DELETE GOAL
# =====================================================

@app.route(

    "/delete_goal/<int:goal_id>",

    methods=["DELETE"]

)
def delete_goal(goal_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    DELETE FROM goals

    WHERE id=?

    """, (goal_id,))

    conn.commit()

    conn.close()

    return jsonify({

        "status":"deleted"

    })



# =====================================================
# ADD MONEY TO GOAL
# =====================================================

@app.route(
    "/add_goal_money",
    methods=["POST"]
)
def add_goal_money():

    data = request.json

    goal_id = data.get(
        "goal_id"
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

    UPDATE goals

    SET saved = saved + ?

    WHERE id=?

    """, (

        amount,
        goal_id

    ))

    conn.commit()

    conn.close()

    return jsonify({
        "status":"success"
    })

# =====================================================
# DELETE GOAL
# =====================================================

@app.route(
    "/delete_goal/<int:goal_id>",
    methods=["DELETE"]
)
def delete_goal(goal_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    DELETE FROM goals
    WHERE id=?

    """, (goal_id,))

    conn.commit()

    conn.close()

    return jsonify({
        "status":"deleted"
    })

# =====================================================
# SAVE DEBT
# =====================================================

@app.route(
    "/save_debt",
    methods=["POST"]
)
def save_debt():

    data = request.json

    user_id = str(
        data.get("user_id")
    )

    person = data.get(
        "person"
    )

    amount = float(
        data.get(
            "amount",
            0
        )
    )

    d_type = data.get(
        "type"
    )

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    INSERT INTO debts
    (
        user_id,
        person,
        amount,
        type,
        created_at
    )

    VALUES (?, ?, ?, ?, ?)

    """, (

        user_id,

        person,

        amount,

        d_type,

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
# GET DEBTS
# =====================================================

@app.route("/debts/<user_id>")
def debts(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT *
    FROM debts

    WHERE user_id=?

    ORDER BY id DESC

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    result = []

    for row in rows:

        result.append({

            "id":row["id"],

            "person":row["person"],

            "amount":row["amount"],

            "type":row["type"],

            "created_at":row["created_at"]

        })

    return jsonify(result)

# =====================================================
# DELETE DEBT
# =====================================================

@app.route(
    "/delete_debt/<int:debt_id>",
    methods=["DELETE"]
)
def delete_debt(debt_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    DELETE FROM debts
    WHERE id=?

    """, (debt_id,))

    conn.commit()

    conn.close()

    return jsonify({
        "status":"deleted"
    })

# =====================================================
# AI
# =====================================================

@app.route("/ai/<user_id>")
def ai(user_id):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""

    SELECT type, SUM(amount) as total

    FROM transactions

    WHERE user_id=?

    GROUP BY type

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    income = 0
    expense = 0

    for row in rows:

        if row["type"] == "income":
            income = row["total"] or 0

        if row["type"] == "expense":
            expense = row["total"] or 0

    text = "Финансы стабильны"

    if expense > income:
        text = "Расходы превышают доходы"

    elif income > expense * 2:
        text = "Отличный рост капитала"

    elif expense > income * 0.8:
        text = "Высокая нагрузка на бюджет"

    return jsonify({
        "text":text
    })

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

        "🏦 Sage Finance V24 готов",

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

            time.sleep(2)

            bot.infinity_polling(

                timeout=30,

                long_polling_timeout=30,

                skip_pending=True,

                allowed_updates=["message"]

            )

        except Exception as e:

            logger.error(f"BOT ERROR: {e}")

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
