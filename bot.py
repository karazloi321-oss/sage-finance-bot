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
        account TEXT,
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


def add_transaction(
    user_id,
    ttype,
    category,
    account,
    amount
):

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO transactions(
        user_id,
        type,
        category,
        account,
        amount
    )
    VALUES(?,?,?,?,?)
    """, (
        user_id,
        ttype,
        category,
        account,
        amount
    ))

    conn.commit()

    conn.close()


def get_transactions(user_id):

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        type,
        category,
        account,
        amount
    FROM transactions
    WHERE user_id=?
    ORDER BY id DESC
    LIMIT 20
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

    income_total = 0
    expense_total = 0

    history_html = ""

    analytics = {}

    for ttype, category, account, amount in transactions:

        if ttype == "income":

            emoji = "➕"
            color = "#4caf50"

            income_total += amount

        else:

            emoji = "➖"
            color = "#ff5252"

            expense_total += amount

            if category not in analytics:

                analytics[category] = 0

            analytics[category] += amount

        history_html += f"""

        <div class="transaction">

            <div>

                <div class="transaction-title">

                    {emoji} {category}

                </div>

                <div class="transaction-account">

                    {account}

                </div>

            </div>

            <div
                class="transaction-amount"
                style="color:{color};"
            >

                {amount} ₽

            </div>

        </div>
        """

    analytics_html = ""

    for category, amount in analytics.items():

        width = min(amount / 15, 100)

        analytics_html += f"""

        <div class="analytics-item">

            <div class="analytics-top">

                <span>{category}</span>

                <span>{amount} ₽</span>

            </div>

            <div class="bar-bg">

                <div
                    class="bar"
                    style="width:{width}%"
                ></div>

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

            *{
    box-sizing:border-box;
}

body{
    margin:0;
    background:#0f1115;
    color:white;
    font-family:sans-serif;
}

.container{
    max-width:520px;
    margin:auto;
    padding:14px;
}

.header{
    font-size:24px;
    font-weight:bold;
    margin-bottom:14px;
}

.balance-card{
    background:linear-gradient(
        135deg,
        #1f8bff,
        #6c63ff
    );
    border-radius:22px;
    padding:20px;
    margin-bottom:14px;
}

.balance-label{
    opacity:0.8;
    font-size:13px;
}

.balance{
    font-size:34px;
    font-weight:bold;
    margin-top:6px;
}

.stats{
    display:flex;
    gap:8px;
    margin-top:14px;
}

.stat{
    flex:1;
    padding:10px;
    border-radius:14px;
    text-align:center;
    font-size:13px;
}

.income{
    background:#143d1f;
}

.expense{
    background:#4a1717;
}

.card{
    background:#1a1d24;
    border-radius:18px;
    padding:14px;
    margin-top:14px;
}

h2{
    margin-top:0;
    font-size:18px;
}

input, select{
    width:100%;
    padding:12px;
    margin-top:8px;
    border:none;
    border-radius:12px;
    background:#2a2f3a;
    color:white;
    box-sizing:border-box;
    font-size:14px;
}

button{
    width:100%;
    padding:12px;
    border:none;
    border-radius:12px;
    margin-top:8px;
    font-size:14px;
    font-weight:bold;
    color:white;
}

.income-btn{
    background:#4caf50;
}

.expense-btn{
    background:#ff5252;
}

.transaction{
    background:#232833;
    border-radius:14px;
    padding:12px;
    margin-top:8px;
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.transaction-title{
    font-weight:bold;
    font-size:14px;
}

.transaction-account{
    opacity:0.7;
    margin-top:2px;
    font-size:11px;
}

.transaction-amount{
    font-weight:bold;
    font-size:15px;
}

.analytics-item{
    margin-top:12px;
}

.analytics-top{
    display:flex;
    justify-content:space-between;
    margin-bottom:5px;
    font-size:13px;
}

.bar-bg{
    width:100%;
    height:10px;
    background:#2a2f3a;
    border-radius:20px;
    overflow:hidden;
}

.bar{
    height:100%;
    background:#4caf50;
}

        </style>

    </head>

    <body>

        <div class="container">

            <div class="header">

                Sage Finance

            </div>

            <div class="balance-card">

                <div class="balance-label">

                    Общий баланс

                </div>

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

            </div>

            <div class="card">

                <h2>
                    Добавить доход
                </h2>

                <form action="/income">

                    <input
                        type="hidden"
                        name="user_id"
                        value="{user_id}"
                    >

                    <input
                        type="number"
                        name="amount"
                        placeholder="Сумма"
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

                    <select name="account">

                        <option>
                            💳 Карта
                        </option>

                        <option>
                            💵 Наличные
                        </option>

                        <option>
                            🏢 Бизнес
                        </option>

                    </select>

                    <button
                        class="income-btn"
                        type="submit"
                    >

                        ➕ Добавить доход

                    </button>

                </form>

            </div>

            <div class="card">

                <h2>
                    Добавить расход
                </h2>

                <form action="/expense">

                    <input
                        type="hidden"
                        name="user_id"
                        value="{user_id}"
                    >

                    <input
                        type="number"
                        name="amount"
                        placeholder="Сумма"
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

                    <select name="account">

                        <option>
                            💳 Карта
                        </option>

                        <option>
                            💵 Наличные
                        </option>

                        <option>
                            🏢 Бизнес
                        </option>

                    </select>

                    <button
                        class="expense-btn"
                        type="submit"
                    >

                        ➖ Добавить расход

                    </button>

                </form>

            </div>

            <div class="card">

                <h2>
                    Аналитика
                </h2>

                {analytics_html}

            </div>

            <div class="card">

                <h2>
                    История операций
                </h2>

                {history_html}

            </div>

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

    account = request.args.get(
        "account",
        "Карта"
    )

    update_balance(user_id, amount)

    add_transaction(
        user_id,
        "income",
        category,
        account,
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

    account = request.args.get(
        "account",
        "Карта"
    )

    update_balance(user_id, -amount)

    add_transaction(
        user_id,
        "expense",
        category,
        account,
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
