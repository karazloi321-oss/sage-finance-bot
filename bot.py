# =====================================================
# SAGE FINANCE V5 PRO
# FINTECH LEVEL
# =====================================================

from flask import (
    Flask,
    request,
    redirect,
    jsonify,
    send_file
)

import telebot
from telebot import types

import threading
import sqlite3
import os
import json

from datetime import (
    datetime,
    date
)

from openpyxl import Workbook

# =====================================================
# INIT
# =====================================================

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise Exception("TOKEN missing")

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

    # ================================================
    # OPERATIONS
    # ================================================

    c.execute("""

    CREATE TABLE IF NOT EXISTS operations (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        type TEXT,

        wallet TEXT,

        amount REAL,

        category TEXT,

        comment TEXT,

        timestamp TEXT,

        day TEXT

    )

    """)

    # ================================================
    # BUDGETS
    # ================================================

    c.execute("""

    CREATE TABLE IF NOT EXISTS budgets (

        user_id INTEGER PRIMARY KEY,

        monthly_limit REAL DEFAULT 0

    )

    """)

    # ================================================
    # RECURRING
    # ================================================

    c.execute("""

    CREATE TABLE IF NOT EXISTS recurring (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        title TEXT,

        amount REAL,

        next_date TEXT

    )

    """)

    conn.commit()
    conn.close()


init_db()

# =====================================================
# AI CATEGORY
# =====================================================

def auto_category(text):

    text = text.lower()

    rules = {

        "🍔 Еда": [
            "еда",
            "кафе",
            "ресторан",
            "burger",
            "pizza",
            "coffee"
        ],

        "🚕 Транспорт": [
            "такси",
            "metro",
            "bus",
            "fuel"
        ],

        "🛒 Покупки": [
            "shop",
            "одежда",
            "nike",
            "zara"
        ],

        "🎮 Развлечения": [
            "game",
            "steam",
            "netflix",
            "youtube"
        ]

    }

    for category, words in rules.items():

        for word in words:

            if word in text:

                return category

    return "📦 Другое"

# =====================================================
# ADD OPERATION
# =====================================================

def add_operation(

    user_id,
    op_type,
    wallet,
    amount,
    category,
    comment

):

    conn = db()
    c = conn.cursor()

    c.execute("""

    INSERT INTO operations (

        user_id,
        type,
        wallet,
        amount,
        category,
        comment,
        timestamp,
        day

    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        user_id,
        op_type,
        wallet,
        amount,
        category,
        comment,
        datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        ),
        date.today().isoformat()

    ))

    conn.commit()
    conn.close()

# =====================================================
# GET OPS
# =====================================================

def get_operations(user_id):

    conn = db()
    c = conn.cursor()

    c.execute("""

    SELECT * FROM operations

    WHERE user_id=?

    ORDER BY id DESC

    LIMIT 100

    """, (user_id,))

    rows = c.fetchall()

    conn.close()

    return rows

# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    user_id = request.args.get(
        "user_id",
        type=int,
        default=0
    )

    ops = get_operations(user_id)

    income = sum(

        o["amount"]

        for o in ops

        if o["type"] == "income"

    )

    expense = sum(

        o["amount"]

        for o in ops

        if o["type"] == "expense"

    )

    balance = income - expense

    history = ""

    for o in ops[:30]:

        color = "#7db1d4"

        if o["type"] == "expense":
            color = "#ff7d7d"

        history += f"""

        <div
        style="
        background:#1e2b3d;
        padding:14px;
        border-radius:14px;
        margin-top:10px;
        display:flex;
        justify-content:space-between;
        "
        >

            <div>

                <div>
                    {o["category"]}
                </div>

                <div
                style="
                opacity:0.6;
                font-size:12px;
                "
                >
                    {o["timestamp"]}
                </div>

                <div
                style="
                opacity:0.8;
                font-size:13px;
                "
                >
                    {o["comment"]}
                </div>

            </div>

            <div
            style="
            color:{color};
            font-weight:bold;
            "
            >
                {o["amount"]} ₽
            </div>

        </div>

        """

    return f"""

    <!DOCTYPE html>

    <html>

    <head>

    <meta charset="UTF-8">

    <meta
    name="viewport"
    content="width=device-width, initial-scale=1"
    >

    <title>
    Sage Finance V5
    </title>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    </head>

    <body
    style="
    background:#0d1118;
    color:white;
    font-family:Arial;
    "
    >

    <div
    style="
    max-width:760px;
    margin:auto;
    padding:20px;
    "
    >

        <h1>
        💰 Sage Finance V5
        </h1>

        <div
        style="
        background:#1e2b3d;
        padding:20px;
        border-radius:20px;
        "
        >

            <h2>
            Баланс: {balance} ₽
            </h2>

            <div>
            📈 Доход: {income} ₽
            </div>

            <div>
            📉 Расход: {expense} ₽
            </div>

        </div>

        <h2 style="margin-top:30px;">
        ➕ Добавить операцию
        </h2>

        <form
        method="POST"
        action="/add"
        >

            <input
            type="hidden"
            name="user_id"
            value="{user_id}"
            >

            <select
            name="type"
            style="
            width:100%;
            padding:14px;
            margin-top:10px;
            "
            >

                <option value="income">
                Доход
                </option>

                <option value="expense">
                Расход
                </option>

            </select>

            <select
            name="wallet"
            style="
            width:100%;
            padding:14px;
            margin-top:10px;
            "
            >

                <option value="cash">
                Наличные
                </option>

                <option value="card">
                Карта
                </option>

            </select>

            <input
            type="number"
            name="amount"
            placeholder="Сумма"
            required

            style="
            width:100%;
            padding:14px;
            margin-top:10px;
            "
            >

            <input
            type="text"
            name="comment"
            placeholder="Комментарий"

            style="
            width:100%;
            padding:14px;
            margin-top:10px;
            "
            >

            <button
            style="
            width:100%;
            padding:16px;
            margin-top:16px;
            background:#7db1d4;
            border:none;
            color:white;
            border-radius:14px;
            font-size:16px;
            "
            >
                Сохранить
            </button>

        </form>

        <h2 style="margin-top:30px;">
        📜 История
        </h2>

        {history}

        <h2 style="margin-top:30px;">
        📤 Export
        </h2>

        <a
        href="/export_excel?user_id={user_id}"
        style="color:#7db1d4;"
        >
            Скачать Excel
        </a>

    </div>

    </body>

    </html>

    """

# =====================================================
# ADD ROUTE
# =====================================================

@app.route(
    "/add",
    methods=["POST"]
)
def add():

    user_id = int(
        request.form.get(
            "user_id",
            0
        )
    )

    op_type = request.form.get(
        "type"
    )

    wallet = request.form.get(
        "wallet"
    )

    amount = float(
        request.form.get(
            "amount",
            0
        )
    )

    comment = request.form.get(
        "comment",
        ""
    )

    category = auto_category(comment)

    if amount <= 0:
        return redirect("/")

    add_operation(

        user_id,
        op_type,
        wallet,
        amount,
        category,
        comment

    )

    # ================================================
    # TELEGRAM NOTIFICATION
    # ================================================

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
# EXPORT EXCEL
# =====================================================

@app.route("/export_excel")
def export_excel():

    user_id = request.args.get(
        "user_id",
        type=int,
        default=0
    )

    ops = get_operations(user_id)

    wb = Workbook()
    ws = wb.active

    ws.append([

        "Тип",
        "Сумма",
        "Категория",
        "Комментарий",
        "Дата"

    ])

    for o in ops:

        ws.append([

            o["type"],
            o["amount"],
            o["category"],
            o["comment"],
            o["timestamp"]

        ])

    filename = f"sage_export_{user_id}.xlsx"

    wb.save(filename)

    return send_file(
        filename,
        as_attachment=True
    )

# =====================================================
# TELEGRAM
# =====================================================

@bot.message_handler(commands=["start"])
def start(message):

    uid = message.from_user.id

    web_app = types.WebAppInfo(

        f"https://sage-finance.onrender.com/?user_id={uid}"

    )

    btn = types.KeyboardButton(

        text="🏦 Open Sage Finance",

        web_app=web_app

    )

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.add(btn)

    bot.send_message(

        message.chat.id,

        "💰 Sage Finance V5 ready",

        reply_markup=markup

    )

# =====================================================
# BOT LOOP
# =====================================================

def run_bot():

    while True:

        try:

            bot.infinity_polling(
                skip_pending=True
            )

        except Exception as e:

            print("BOT ERROR:", e)

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
