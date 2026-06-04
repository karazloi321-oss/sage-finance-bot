# =====================================================
# SAGE FINANCE V5 LEGACY PRO
# Stable Legacy UI + SQLite + Multi User
# =====================================================

from flask import Flask, request, redirect
import telebot
from telebot import types
import threading
import sqlite3
import os
import time
from datetime import datetime

# =====================================================
# INIT
# =====================================================

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise Exception("TOKEN environment variable missing")

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

DB_PATH = "data.db"

# =====================================================
# DATABASE
# =====================================================

def db():

    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = db()

    c = conn.cursor()

    # =================================================
    # OPERATIONS
    # =================================================

    c.execute("""

    CREATE TABLE IF NOT EXISTS operations (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        account TEXT,

        type TEXT,

        wallet TEXT,

        amount REAL,

        category TEXT,

        comment TEXT,

        created_at TEXT

    )

    """)

    # =================================================
    # GOALS
    # =================================================

    c.execute("""

    CREATE TABLE IF NOT EXISTS goals (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        name TEXT,

        target REAL,

        saved REAL DEFAULT 0

    )

    """)

    # =================================================
    # DEBTS
    # =================================================

    c.execute("""

    CREATE TABLE IF NOT EXISTS debts (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        person TEXT,

        amount REAL,

        type TEXT,

        created_at TEXT

    )

    """)

    # =================================================
    # SAVINGS
    # =================================================

    c.execute("""

    CREATE TABLE IF NOT EXISTS savings (

        user_id INTEGER PRIMARY KEY,

        cash REAL DEFAULT 0,

        card REAL DEFAULT 0

    )

    """)

    conn.commit()

    conn.close()


init_db()

# =====================================================
# HELPERS
# =====================================================

def get_user_id():

    try:

        return int(
            request.args.get(
                "user_id",
                request.form.get(
                    "user_id",
                    0
                )
            )
        )

    except:

        return 0


def execute(query, params=()):

    conn = db()

    c = conn.cursor()

    c.execute(query, params)

    conn.commit()

    conn.close()


def fetchall(query, params=()):

    conn = db()

    c = conn.cursor()

    c.execute(query, params)

    rows = c.fetchall()

    conn.close()

    return rows


def fetchone(query, params=()):

    conn = db()

    c = conn.cursor()

    c.execute(query, params)

    row = c.fetchone()

    conn.close()

    return row

# =====================================================
# AI CATEGORY
# =====================================================

def auto_category(text):

    if not text:
        return "📦 Другое"

    text = text.lower()

    rules = {

        "🍔 Еда": [
            "еда",
            "кафе",
            "ресторан",
            "coffee",
            "pizza",
            "burger"
        ],

        "🚕 Транспорт": [
            "taxi",
            "bus",
            "metro",
            "fuel",
            "заправка"
        ],

        "🛒 Покупки": [
            "shop",
            "nike",
            "zara",
            "одежда"
        ],

        "🎮 Развлечения": [
            "game",
            "steam",
            "youtube",
            "netflix"
        ]

    }

    for category, words in rules.items():

        for word in words:

            if word in text:
                return category

    return "📦 Другое"

# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    user_id = get_user_id()

    # =================================================
    # OPERATIONS
    # =================================================

    operations = fetchall("""

    SELECT * FROM operations

    WHERE user_id=?

    ORDER BY id DESC

    LIMIT 50

    """, (user_id,))

    # =================================================
    # TOTALS
    # =================================================

    income = 0
    expense = 0

    for item in operations:

        if item["type"] == "income":
            income += item["amount"]

        else:
            expense += item["amount"]

    balance = income - expense

    # =================================================
    # GOALS
    # =================================================

    goals = fetchall("""

    SELECT * FROM goals

    WHERE user_id=?

    ORDER BY id DESC

    """, (user_id,))

    goals_html = ""

    for goal in goals:

        progress = 0

        if goal["target"] > 0:

            progress = int(
                (
                    goal["saved"]
                    / goal["target"]
                ) * 100
            )

        if progress > 100:
            progress = 100

        goals_html += f"""

        <div
        style="
        background:#222d40;
        padding:16px;
        border-radius:18px;
        margin-top:12px;
        "
        >

            <div
            style="
            display:flex;
            justify-content:space-between;
            "
            >

                <div>
                    🎯 {goal["name"]}
                </div>

                <div>
                    {goal["saved"]} / {goal["target"]} ₽
                </div>

            </div>

            <div
            style="
            width:100%;
            height:10px;
            background:#2e3a4d;
            border-radius:10px;
            margin-top:12px;
            overflow:hidden;
            "
            >

                <div
                style="
                width:{progress}%;
                height:100%;
                background:#7db1d4;
                "
                ></div>

            </div>

        </div>

        """

    # =================================================
    # HISTORY
    # =================================================

    history_html = ""

    for item in operations:

        color = "#7db1d4"
        icon = "📈"

        if item["type"] == "expense":

            color = "#ff7d7d"
            icon = "📉"

        history_html += f"""

        <div
        style="
        background:#222d40;
        padding:16px;
        border-radius:18px;
        margin-top:12px;
        display:flex;
        justify-content:space-between;
        align-items:center;
        "
        >

            <div>

                <div
                style="
                font-weight:bold;
                "
                >
                    {icon} {item["category"]}
                </div>

                <div
                style="
                opacity:0.7;
                font-size:12px;
                margin-top:4px;
                "
                >
                    {item["created_at"]}
                </div>

                <div
                style="
                opacity:0.85;
                font-size:13px;
                margin-top:4px;
                "
                >
                    {item["comment"] or ""}
                </div>

            </div>

            <div
            style="
            color:{color};
            font-weight:bold;
            "
            >
                {item["amount"]} ₽
            </div>

        </div>

        """

    # =================================================
    # HTML
    # =================================================

    return f"""

<!DOCTYPE html>

<html lang="ru">

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width, initial-scale=1"
/>

<title>
Sage Finance V5
</title>

<style>

*{{
box-sizing:border-box;
}}

body{{
margin:0;
background:#0d1118;
color:white;
font-family:Arial,sans-serif;
}}

.container{{
max-width:760px;
margin:auto;
padding:20px;
padding-bottom:120px;
}}

.card{{
background:#161f2d;
padding:22px;
border-radius:26px;
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
padding:16px;
margin-top:12px;
border:none;
border-radius:18px;
background:#222d40;
color:white;
font-size:15px;
}}

.button{{
width:100%;
padding:16px;
margin-top:16px;
border:none;
border-radius:20px;
background:#7db1d4;
color:white;
font-size:16px;
font-weight:bold;
}}

.section-title{{
font-size:24px;
font-weight:900;
margin-bottom:14px;
}}

.export-btn{{
display:block;
margin-top:18px;
background:#222d40;
padding:16px;
border-radius:18px;
text-align:center;
color:#7db1d4;
text-decoration:none;
font-weight:bold;
}}

</style>

</head>

<body>

<div class="container">

<div class="card balance-card">

<div>
💰 Общий баланс
</div>

<div class="balance">
{balance} ₽
</div>

<div style="margin-top:14px;">
📈 Доходы: {income} ₽
</div>

<div style="margin-top:8px;">
📉 Расходы: {expense} ₽
</div>

</div>

<!-- ADD -->

<div class="card">

<div class="section-title">
➕ Добавить операцию
</div>

<form
action="/add_operation"
method="POST"
>

<input
type="hidden"
name="user_id"
value="{user_id}"
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
name="comment"
placeholder="Комментарий"
>

<button
class="button"
type="submit"
>
Сохранить
</button>

</form>

</div>

<!-- GOALS -->

<div class="card">

<div class="section-title">
🎯 Цели
</div>

<form
action="/add_goal"
method="POST"
>

<input
type="hidden"
name="user_id"
value="{user_id}"
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
step="0.01"
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

<!-- HISTORY -->

<div class="card">

<div class="section-title">
🕓 История
</div>

{history_html}

</div>

<a
class="export-btn"
href="/export_json?user_id={user_id}"
>
📤 Export JSON
</a>

</div>

</body>

</html>

"""

# =====================================================
# ADD OPERATION
# =====================================================

@app.route(
    "/add_operation",
    methods=["POST"]
)
def add_operation():

    user_id = get_user_id()

    op_type = request.form.get(
        "type",
        "expense"
    )

    wallet = request.form.get(
        "wallet",
        "cash"
    )

    amount = float(
        request.form.get(
            "amount",
            0
        ) or 0
    )

    comment = request.form.get(
        "comment",
        ""
    )

    if amount <= 0:

        return redirect(
            f"/?user_id={user_id}"
        )

    category = auto_category(comment)

    execute("""

    INSERT INTO operations (

        user_id,
        account,
        type,
        wallet,
        amount,
        category,
        comment,
        created_at

    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        user_id,
        "personal",
        op_type,
        wallet,
        amount,
        category,
        comment,
        datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        )

    ))

    # =================================================
    # TELEGRAM NOTIFICATION
    # =================================================

    try:

        icon = "📈"

        if op_type == "expense":
            icon = "📉"

        bot.send_message(

            user_id,

            f"""

{icon} Операция добавлена

💰 {amount} ₽

📦 {category}

📝 {comment}

            """

        )

    except:
        pass

    return redirect(
        f"/?user_id={user_id}"
    )

# =====================================================
# ADD GOAL
# =====================================================

@app.route(
    "/add_goal",
    methods=["POST"]
)
def add_goal():

    user_id = get_user_id()

    name = request.form.get(
        "name"
    )

    target = float(
        request.form.get(
            "target",
            0
        ) or 0
    )

    if target <= 0:

        return redirect(
            f"/?user_id={user_id}"
        )

    execute("""

    INSERT INTO goals (

        user_id,
        name,
        target,
        saved

    )

    VALUES (?, ?, ?, ?)

    """, (

        user_id,
        name,
        target,
        0

    ))

    return redirect(
        f"/?user_id={user_id}"
    )

# =====================================================
# EXPORT JSON
# =====================================================

@app.route("/export_json")
def export_json():

    user_id = get_user_id()

    operations = fetchall("""

    SELECT * FROM operations

    WHERE user_id=?

    ORDER BY id DESC

    """, (user_id,))

    data = []

    for item in operations:

        data.append(dict(item))

    return {
        "operations": data
    }

# =====================================================
# TELEGRAM
# =====================================================

@bot.message_handler(commands=["start"])
def start(message):

    user_id = message.from_user.id

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    web_app = types.WebAppInfo(

        f"https://sage-finance.onrender.com/?user_id={user_id}"

    )

    button = types.KeyboardButton(

        text="🏦 Открыть Sage Finance",

        web_app=web_app

    )

    markup.add(button)

    bot.send_message(

        message.chat.id,

        "🏦 Sage Finance V5 готов",

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

            bot.infinity_polling(

                timeout=30,
                long_polling_timeout=30,
                skip_pending=True

            )

        except Exception as e:

            print("BOT ERROR:", e)

            time.sleep(5)

# =====================================================
# RUN
# =====================================================

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
