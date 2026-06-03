from flask import Flask, request, redirect
import telebot
from telebot import types
import threading
import time
import os
import sqlite3
from datetime import datetime

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

DB_NAME = "sage_finance.db"


# ================= DATABASE =================

def get_db():

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT UNIQUE,

        personal_cash REAL DEFAULT 0,
        personal_card REAL DEFAULT 0,

        business_cash REAL DEFAULT 0,
        business_card REAL DEFAULT 0,

        savings_cash REAL DEFAULT 0,
        savings_card REAL DEFAULT 0

    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS operations (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        telegram_id TEXT,

        type TEXT,
        account TEXT,
        wallet TEXT,
        category TEXT,

        amount REAL,

        created_at TEXT

    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS goals (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        telegram_id TEXT,

        name TEXT,

        target REAL,

        saved REAL DEFAULT 0

    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS debts (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        telegram_id TEXT,

        person TEXT,

        amount REAL,

        type TEXT,

        created_at TEXT

    )
    """)

    conn.commit()
    conn.close()


init_db()


# ================= HELPERS =================

def create_user_if_not_exists(telegram_id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE telegram_id=?",
        (telegram_id,)
    )

    user = cur.fetchone()

    if not user:

        cur.execute("""
        INSERT INTO users (
            telegram_id
        )
        VALUES (?)
        """, (telegram_id,))

        conn.commit()

    conn.close()


def get_user(telegram_id):

    create_user_if_not_exists(telegram_id)

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE telegram_id=?",
        (telegram_id,)
    )

    user = cur.fetchone()

    conn.close()

    return user


def get_operations(telegram_id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT *
    FROM operations

    WHERE telegram_id=?

    ORDER BY id DESC

    LIMIT 20
    """, (telegram_id,))

    operations = cur.fetchall()

    conn.close()

    return operations


def get_goals(telegram_id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM goals WHERE telegram_id=?",
        (telegram_id,)
    )

    goals = cur.fetchall()

    conn.close()

    return goals


def get_debts(telegram_id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT *
    FROM debts

    WHERE telegram_id=?

    ORDER BY id DESC
    """, (telegram_id,))

    debts = cur.fetchall()

    conn.close()

    return debts


# ================= HOME =================

@app.route("/", methods=["GET"])
def home():

    telegram_id = request.args.get(
        "user_id",
        "demo_user"
    )

    user = get_user(telegram_id)

    operations = get_operations(
        telegram_id
    )

    goals = get_goals(
        telegram_id
    )

    debts = get_debts(
        telegram_id
    )

    personal_total = (
        user["personal_cash"]
        + user["personal_card"]
    )

    business_total = (
        user["business_cash"]
        + user["business_card"]
    )

    savings_total = (
        user["savings_cash"]
        + user["savings_card"]
    )

    history_html = ""

    for item in operations:

        icon = "📈"
        color = "#7db1d4"

        if item["type"] == "expense":

            icon = "📉"
            color = "#ff7d7d"

        elif item["type"] == "transfer":

            icon = "💸"
            color = "#9bb6c9"

        history_html += f"""

        <div class="history-item">

            <div>

                <div class="history-title">
                    {icon} {item["category"]}
                </div>

                <div class="history-date">
                    {item["wallet"]} • {item["created_at"]}
                </div>

            </div>

            <div
            class="history-amount"
            style="color:{color};"
            >
                {item["amount"]} ₽
            </div>

        </div>

        """

    goals_html = ""

    for goal in goals:

        progress = 0

        if goal["target"] > 0:

            progress = int(
                (goal["saved"] / goal["target"]) * 100
            )

        goals_html += f"""

        <div class="goal-card">

            <div class="goal-top">

                <div>
                    🎯 {goal["name"]}
                </div>

                <div>
                    {goal["saved"]} / {goal["target"]} ₽
                </div>

            </div>

            <div class="progress">

                <div
                class="progress-fill"
                style="width:{progress}%"
                ></div>

            </div>

        </div>

        """

    debts_html = ""

    for debt in debts:

        icon = "📤" if debt["type"] == "give" else "📥"

        debts_html += f"""

        <div class="history-item">

            <div>

                <div class="history-title">
                    {icon} {debt["person"]}
                </div>

                <div class="history-date">
                    {debt["created_at"]}
                </div>

            </div>

            <div class="history-amount">
                {debt["amount"]} ₽
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
/>

<title>Sage Finance</title>

<style>

*{{
box-sizing:border-box;
-webkit-tap-highlight-color:transparent;
}}

body{{
margin:0;
background:#0d1118;
color:white;
font-family:-apple-system,BlinkMacSystemFont,sans-serif;
}}

.container{{
max-width:700px;
margin:auto;
padding:20px;
padding-bottom:40px;
}}

.card{{
background:#161f2d;
padding:24px;
border-radius:28px;
margin-top:18px;
}}

.balance-card{{
background:linear-gradient(
135deg,
#6d8ea6,
#9bb6c9
);
}}

.balance{{
font-size:42px;
font-weight:900;
margin-top:10px;
}}

.input{{
width:100%;
padding:18px;
border:none;
border-radius:20px;
background:#222d40;
color:white;
margin-top:12px;
font-size:16px;
outline:none;
}}

.button{{
width:100%;
padding:18px;
border:none;
border-radius:20px;
margin-top:14px;
font-size:16px;
font-weight:900;
background:linear-gradient(
135deg,
#6d8ea6,
#9bb6c9
);
color:white;
}}

.history-item{{
background:#222d40;
padding:18px;
border-radius:22px;
margin-top:12px;
display:flex;
justify-content:space-between;
align-items:center;
}}

.history-title{{
font-weight:900;
font-size:16px;
}}

.history-date{{
opacity:0.6;
margin-top:5px;
font-size:13px;
}}

.history-amount{{
font-weight:900;
font-size:18px;
}}

.goal-card{{
background:#222d40;
padding:18px;
border-radius:20px;
margin-top:12px;
}}

.goal-top{{
display:flex;
justify-content:space-between;
margin-bottom:10px;
font-size:14px;
font-weight:800;
}}

.progress{{
height:10px;
background:#2d3a52;
border-radius:20px;
overflow:hidden;
}}

.progress-fill{{
height:100%;
background:#9bb6c9;
}}

.section-title{{
font-size:24px;
font-weight:900;
margin-bottom:18px;
}}

</style>

</head>

<body>

<div class="container">

<div class="card balance-card">

<div>
👤 Личный баланс
</div>

<div class="balance">
{personal_total} ₽
</div>

</div>

<div class="card balance-card">

<div>
💼 Бизнес баланс
</div>

<div class="balance">
{business_total} ₽
</div>

</div>

<div class="card balance-card">

<div>
💎 Сбережения
</div>

<div class="balance">
{savings_total} ₽
</div>

</div>

<div class="card">

<div class="section-title">
➕ Новая операция
</div>

<form
method="post"
action="/add_operation"
>

<input
type="hidden"
name="telegram_id"
value="{telegram_id}"
>

<select
class="input"
name="type"
>

<option value="income">
📈 Доход
</option>

<option value="expense">
📉 Расход
</option>

</select>

<select
class="input"
name="account"
>

<option value="personal">
👤 Личный
</option>

<option value="business">
💼 Бизнес
</option>

</select>

<select
class="input"
name="wallet"
>

<option value="cash">
💵 Наличные
</option>

<option value="card">
💳 Карта
</option>

</select>

<input
class="input"
type="number"
step="0.01"
name="amount"
placeholder="Сумма"
required
>

<input
class="input"
type="text"
name="category"
placeholder="Категория"
required
>

<button
class="button"
type="submit"
>
Сохранить
</button>

</form>

</div>

<div class="card">

<div class="section-title">
🎯 Цели
</div>

<form
method="post"
action="/add_goal"
>

<input
type="hidden"
name="telegram_id"
value="{telegram_id}"
>

<input
class="input"
type="text"
name="name"
placeholder="Название цели"
required
>

<input
class="input"
type="number"
name="target"
placeholder="Сумма"
required
>

<button
class="button"
type="submit"
>
Добавить цель
</button>

</form>

{goals_html}

</div>

<div class="card">

<div class="section-title">
💸 Долги
</div>

<form
method="post"
action="/add_debt"
>

<input
type="hidden"
name="telegram_id"
value="{telegram_id}"
>

<input
class="input"
type="text"
name="person"
placeholder="Имя"
required
>

<input
class="input"
type="number"
step="0.01"
name="amount"
placeholder="Сумма"
required
>

<select
class="input"
name="type"
>

<option value="give">
📤 Я дал
</option>

<option value="take">
📥 Я взял
</option>

</select>

<button
class="button"
type="submit"
>
Добавить долг
</button>

</form>

{debts_html}

</div>

<div class="card">

<div class="section-title">
🕓 История операций
</div>

{history_html}

</div>

</div>

</body>

</html>

"""


# ================= ADD OPERATION =================

@app.route("/add_operation", methods=["POST"])
def add_operation():

    telegram_id = request.form.get(
        "telegram_id"
    )

    account = request.form.get(
        "account"
    )

    wallet = request.form.get(
        "wallet"
    )

    type_op = request.form.get(
        "type"
    )

    amount = float(
        request.form.get(
            "amount",
            0
        )
    )

    category = request.form.get(
        "category"
    )

    conn = get_db()
    cur = conn.cursor()

    field = f"{account}_{wallet}"

    if type_op == "income":

        cur.execute(f"""
        UPDATE users
        SET {field} = {field} + ?
        WHERE telegram_id=?
        """, (amount, telegram_id))

    else:

        cur.execute(f"""
        UPDATE users
        SET {field} = {field} - ?
        WHERE telegram_id=?
        """, (amount, telegram_id))

    cur.execute("""
    INSERT INTO operations (

        telegram_id,
        type,
        account,
        wallet,
        category,
        amount,
        created_at

    )

    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (

        telegram_id,
        type_op,
        account,
        wallet,
        category,
        amount,
        datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        )

    ))

    conn.commit()
    conn.close()

    return redirect(
        f"/?user_id={telegram_id}"
    )


# ================= ADD GOAL =================

@app.route("/add_goal", methods=["POST"])
def add_goal():

    telegram_id = request.form.get(
        "telegram_id"
    )

    name = request.form.get(
        "name"
    )

    target = float(
        request.form.get(
            "target",
            0
        )
    )

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO goals (

        telegram_id,
        name,
        target

    )

    VALUES (?, ?, ?)
    """, (

        telegram_id,
        name,
        target

    ))

    conn.commit()
    conn.close()

    return redirect(
        f"/?user_id={telegram_id}"
    )


# ================= ADD DEBT =================

@app.route("/add_debt", methods=["POST"])
def add_debt():

    telegram_id = request.form.get(
        "telegram_id"
    )

    person = request.form.get(
        "person"
    )

    amount = float(
        request.form.get(
            "amount",
            0
        )
    )

    debt_type = request.form.get(
        "type"
    )

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO debts (

        telegram_id,
        person,
        amount,
        type,
        created_at

    )

    VALUES (?, ?, ?, ?, ?)
    """, (

        telegram_id,
        person,
        amount,
        debt_type,
        datetime.now().strftime(
            "%d.%m.%Y"
        )

    ))

    conn.commit()
    conn.close()

    return redirect(
        f"/?user_id={telegram_id}"
    )


# ================= TELEGRAM =================

@bot.message_handler(commands=["start"])
def start(message):

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    web_app = types.WebAppInfo(
        f"https://sage-finance.onrender.com/?user_id={message.from_user.id}"
    )

    button = types.KeyboardButton(

        text="🏦 Открыть Sage Finance",

        web_app=web_app

    )

    markup.add(button)

    bot.send_message(

        message.chat.id,

        "🏦 Sage Finance готов",

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


# ================= RUN =================

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
