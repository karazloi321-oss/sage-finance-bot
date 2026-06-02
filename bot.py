from flask import Flask, request
import telebot
from telebot import types
import os
import threading
import time
import sqlite3

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)

bot = telebot.TeleBot(TOKEN)

DB_FILE = "finance.db"


def init_db():

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        category TEXT,
        amount INTEGER
    )
    """)

    conn.commit()

    conn.close()


init_db()


def get_balance(user_id):

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute(
        "SELECT balance FROM users WHERE user_id=?",
        (user_id,)
    )

    row = cursor.fetchone()

    if row is None:

        cursor.execute(
            "INSERT INTO users(user_id,balance) VALUES(?,?)",
            (user_id, 0)
        )

        conn.commit()

        balance = 0

    else:

        balance = row[0]

    conn.close()

    return balance


def update_balance(user_id, amount):

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    balance = get_balance(user_id)

    new_balance = balance + amount

    cursor.execute(
        "UPDATE users SET balance=? WHERE user_id=?",
        (new_balance, user_id)
    )

    conn.commit()

    conn.close()


def add_transaction(user_id, ttype, category, amount):

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO transactions(
        user_id,
        type,
        category,
        amount
    )
    VALUES(?,?,?,?)
    """, (
        user_id,
        ttype,
        category,
        amount
    ))

    conn.commit()

    conn.close()


def get_transactions(user_id):

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT type, category, amount
    FROM transactions
    WHERE user_id=?
    ORDER BY id DESC
    LIMIT 10
    """, (user_id,))

    rows = cursor.fetchall()

    conn.close()

    return rows


@app.route("/", methods=["GET", "HEAD"])
def home():

    if request.method == "HEAD":

        return "", 200

    user_id = request.args.get(
        "user_id",
        "1"
    )

    balance = get_balance(user_id)

    transactions = get_transactions(user_id)

    history_html = ""

    income_total = 0
    expense_total = 0

    for ttype, category, amount in transactions:

        if ttype == "income":

            emoji = "➕"
            color = "#2e7d32"

            income_total += amount

        else:

            emoji = "➖"
            color = "#c62828"

            expense_total += amount

        history_html += f"""

        <div class="item">

            <div>

                {emoji}
                {category}

            </div>

            <div style="
                color:{color};
                font-weight:bold;
            ">

                {amount} ₽

            </div>

        </div>
        """

    return f"""

    <!DOCTYPE html>

    <html lang="ru">

    <head>

        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1"
        >

        <title>
            Sage Finance
        </title>

        <style>

            body{{
                margin:0;
                padding:20px;
                background:#d9e5d6;
                font-family:sans-serif;
            }}

            .card{{
                background:white;
                border-radius:24px;
                padding:25px;
                max-width:480px;
                margin:auto;
            }}

            h1{{
                text-align:center;
            }}

            .balance{{
                font-size:42px;
                font-weight:bold;
                text-align:center;
                margin:25px 0;
            }}

            .stats{{
                display:flex;
                gap:10px;
                margin-bottom:20px;
            }}

            .stat{{
                flex:1;
                padding:14px;
                border-radius:16px;
                color:white;
                text-align:center;
                font-weight:bold;
            }}

            .income{{
                background:#2e7d32;
            }}

            .expense{{
                background:#c62828;
            }}

            form{{
                margin-top:15px;
            }}

            input, select{{
                width:100%;
                padding:18px;
                border:none;
                border-radius:18px;
                box-sizing:border-box;
                font-size:18px;
                margin-top:10px;
            }}

            button{{
                width:100%;
                padding:18px;
                border:none;
                border-radius:18px;
                background:#7c9b76;
                color:white;
                font-size:18px;
                margin-top:10px;
            }}

            .item{{
                background:#f2f2f2;
                padding:12px;
                border-radius:12px;
                margin-top:10px;
                display:flex;
                justify-content:space-between;
            }}

        </style>

    </head>

    <body>

        <div class="card">

            <h1>
                Sage Finance
            </h1>

            <div class="balance">

                {balance} ₽

            </div>

            <div class="stats">

                <div class="stat income">

                    Доход<br>
                    {income_total} ₽

                </div>

                <div class="stat expense">

                    Расход<br>
                    {expense_total} ₽

                </div>

            </div>

            <form action="/income">

                <input
                    type="hidden"
                    name="user_id"
                    value="{user_id}"
                >

                <input
                    type="number"
                    name="amount"
                    placeholder="Сумма дохода"
                    required
                >

                <select name="category">

                    <option>
                        💼 Зарплата
                    </option>

                    <option>
                        💰 Подработка
                    </option>

                    <option>
                        📦 Другое
                    </option>

                </select>

                <button type="submit">

                    ➕ Добавить доход

                </button>

            </form>

            <form action="/expense">

                <input
                    type="hidden"
                    name="user_id"
                    value="{user_id}"
                >

                <input
                    type="number"
                    name="amount"
                    placeholder="Сумма расхода"
                    required
                >

                <select name="category">

                    <option>
                        🍔 Еда
                    </option>

                    <option>
                        🚕 Транспорт
                    </option>

                    <option>
                        🛍 Покупки
                    </option>

                    <option>
                        🎮 Развлечения
                    </option>

                    <option>
                        📦 Другое
                    </option>

                </select>

                <button type="submit">

                    ➖ Добавить расход

                </button>

            </form>

            <h2>
                История
            </h2>

            {history_html}

        </div>

    </body>

    </html>
    """


@app.route("/income")
def income():

    user_id = request.args.get(
        "user_id",
        "1"
    )

    amount = int(
        request.args.get(
            "amount",
            0
        )
    )

    category = request.args.get(
        "category",
        "Доход"
    )

    update_balance(user_id, amount)

    add_transaction(
        user_id,
        "income",
        category,
        amount
    )

    return f"""
    <meta http-equiv="refresh"
    content="0; url=/?user_id={user_id}">
    """


@app.route("/expense")
def expense():

    user_id = request.args.get(
        "user_id",
        "1"
    )

    amount = int(
        request.args.get(
            "amount",
            0
        )
    )

    category = request.args.get(
        "category",
        "Расход"
    )

    update_balance(user_id, -amount)

    add_transaction(
        user_id,
        "expense",
        category,
        amount
    )

    return f"""
    <meta http-equiv="refresh"
    content="0; url=/?user_id={user_id}">
    """


@bot.message_handler(commands=["start"])
def start(message):

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    web_app = types.WebAppInfo(
        f"https://sage-finance.onrender.com/?user_id={message.from_user.id}"
    )

    button = types.KeyboardButton(
        text="📱 Открыть Sage Finance",
        web_app=web_app
    )

    markup.add(button)

    bot.send_message(
        message.chat.id,
        "🚀 Sage Finance готов",
        reply_markup=markup
    )


def run_bot():

    while True:

        try:

            bot.remove_webhook()

            time.sleep(2)

            bot.infinity_polling(
                timeout=30,
                long_polling_timeout=30,
                skip_pending=True
            )

        except Exception as e:

            print(e)

            time.sleep(5)


if __name__ == "__main__":

    threading.Thread(
        target=run_bot,
        daemon=True
    ).start()

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                10000
            )
        )
    )
