# =========================================================
# SAGE FINANCE V4 FULL BOT.PY
# =========================================================

from flask import Flask, request, jsonify
import telebot
from telebot import types
import threading
import sqlite3
import time
import os
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)

bot = telebot.TeleBot(TOKEN)

DB_NAME = "sage_finance.db"

# =========================================================
# DATABASE
# =========================================================

def db():

    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = db()

    cur = conn.cursor()

    # USERS

    cur.execute("""

    CREATE TABLE IF NOT EXISTS users (

        telegram_id TEXT PRIMARY KEY,

        personal_cash REAL DEFAULT 0,
        personal_card REAL DEFAULT 0,

        business_cash REAL DEFAULT 0,
        business_card REAL DEFAULT 0,

        savings_cash REAL DEFAULT 0,
        savings_card REAL DEFAULT 0

    )

    """)

    # OPERATIONS

    cur.execute("""

    CREATE TABLE IF NOT EXISTS operations (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        telegram_id TEXT,

        type TEXT,
        account TEXT,
        wallet TEXT,

        category TEXT,

        amount REAL,

        note TEXT,

        created_at TEXT

    )

    """)

    # GOALS

    cur.execute("""

    CREATE TABLE IF NOT EXISTS goals (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        telegram_id TEXT,

        name TEXT,

        target REAL,

        saved REAL DEFAULT 0

    )

    """)

    # DEBTS

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

# =========================================================
# HELPERS
# =========================================================

def ensure_user(user_id):

    conn = db()

    cur = conn.cursor()

    cur.execute("""

    SELECT *
    FROM users
    WHERE telegram_id=?

    """, (user_id,))

    user = cur.fetchone()

    if not user:

        cur.execute("""

        INSERT INTO users (
            telegram_id
        )

        VALUES (?)

        """, (user_id,))

        conn.commit()

    conn.close()


def get_user(user_id):

    ensure_user(user_id)

    conn = db()

    cur = conn.cursor()

    cur.execute("""

    SELECT *
    FROM users
    WHERE telegram_id=?

    """, (user_id,))

    user = cur.fetchone()

    conn.close()

    return user


def get_operations(user_id, account=None):

    conn = db()

    cur = conn.cursor()

    if account:

        cur.execute("""

        SELECT *
        FROM operations
        WHERE telegram_id=?
        AND account=?
        ORDER BY id DESC

        """, (

            user_id,
            account

        ))

    else:

        cur.execute("""

        SELECT *
        FROM operations
        WHERE telegram_id=?
        ORDER BY id DESC

        """, (user_id,))

    rows = cur.fetchall()

    conn.close()

    return rows


def get_debts(user_id):

    conn = db()

    cur = conn.cursor()

    cur.execute("""

    SELECT *
    FROM debts
    WHERE telegram_id=?
    ORDER BY id DESC

    """, (user_id,))

    rows = cur.fetchall()

    conn.close()

    return rows


def add_operation_to_db(
    user_id,
    op_type,
    account,
    wallet,
    category,
    amount,
    note
):

    conn = db()

    cur = conn.cursor()

    field = f"{account}_{wallet}"

    if op_type == "income":

        cur.execute(f"""

        UPDATE users
        SET {field} = {field} + ?
        WHERE telegram_id=?

        """, (

            amount,
            user_id

        ))

    else:

        cur.execute(f"""

        UPDATE users
        SET {field} = {field} - ?
        WHERE telegram_id=?

        """, (

            amount,
            user_id

        ))

    cur.execute("""

    INSERT INTO operations (

        telegram_id,
        type,
        account,
        wallet,
        category,
        amount,
        note,
        created_at

    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        user_id,
        op_type,
        account,
        wallet,
        category,
        amount,
        note,
        datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        )

    ))

    conn.commit()

    conn.close()


def add_debt_to_db(
    user_id,
    person,
    amount,
    debt_type
):

    conn = db()

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

        user_id,
        person,
        amount,
        debt_type,
        datetime.now().strftime(
            "%d.%m.%Y"
        )

    ))

    conn.commit()

    conn.close()

# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    user_id = request.args.get(
        "user_id",
        "demo"
    )

    user = get_user(user_id)

    operations = get_operations(user_id)

    business_operations = get_operations(
        user_id,
        "business"
    )

    debts = get_debts(user_id)

    # =====================================================
    # BALANCES
    # =====================================================

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

    total_balance = (
        personal_total
        + business_total
        + savings_total
    )

    # =====================================================
    # ANALYTICS
    # =====================================================

    income_total = 0
    expense_total = 0

    for item in operations:

        if item["type"] == "income":

            income_total += item["amount"]

        else:

            expense_total += item["amount"]

    # =====================================================
    # BUSINESS ANALYTICS
    # =====================================================

    business_income = 0
    business_expense = 0

    for item in business_operations:

        if item["type"] == "income":

            business_income += item["amount"]

        else:

            business_expense += item["amount"]

    # =====================================================
    # DEBTS
    # =====================================================

    debt_total = 0

    for debt in debts:

        debt_total += debt["amount"]

    # =====================================================
    # HISTORY
    # =====================================================

    history_html = ""

    for item in operations[:25]:

        icon = "📈"
        color = "#7db1d4"

        if item["type"] == "expense":

            icon = "📉"
            color = "#ff7d7d"

        history_html += f"""

        <div class="history-item">

            <div class="history-left">

                <div
                class="history-icon"
                style="background:{color}20;"
                >
                    {icon}
                </div>

                <div>

                    <div class="history-title">
                        {item["category"]}
                    </div>

                    <div class="history-date">
                        {item["created_at"]}
                    </div>

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

    # =====================================================
    # DEBTS HTML
    # =====================================================

    debts_html = ""

    for debt in debts:

        icon = "📤"

        if debt["type"] == "take":

            icon = "📥"

        debts_html += f"""

        <div class="history-item">

            <div class="history-left">

                <div class="history-icon">
                    {icon}
                </div>

                <div>

                    <div class="history-title">
                        {debt["person"]}
                    </div>

                    <div class="history-date">
                        {debt["created_at"]}
                    </div>

                </div>

            </div>

            <div class="history-amount">
                {debt["amount"]} ₽
            </div>

        </div>

        """

    # =====================================================
    # AI
    # =====================================================

    ai_text = "Финансы стабильны"

    if expense_total > income_total:

        ai_text = "Расходы превышают доходы"

    elif savings_total < total_balance * 0.1:

        ai_text = "Увеличьте накопления"

    elif income_total > expense_total:

        ai_text = "Доходы растут быстрее расходов"

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
Sage Finance
</title>

<link
rel="stylesheet"
href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
/>

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
overflow-x:hidden;
}}

.container{{
max-width:760px;
margin:auto;
padding:20px;
padding-bottom:130px;
}}

.topbar{{
display:flex;
justify-content:space-between;
align-items:center;
margin-bottom:20px;
}}

.logo{{
font-size:34px;
font-weight:900;
}}

.menu-btn{{
width:56px;
height:56px;
border-radius:20px;
background:#161f2d;
display:flex;
align-items:center;
justify-content:center;
font-size:22px;
cursor:pointer;
}}

.card{{
background:#161f2d;
padding:24px;
border-radius:32px;
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
font-size:48px;
font-weight:900;
margin-top:12px;
}}

.sub-balance{{
display:grid;
grid-template-columns:1fr 1fr;
gap:14px;
margin-top:20px;
}}

.sub-box{{
background:rgba(255,255,255,0.12);
padding:16px;
border-radius:22px;
}}

.sub-title{{
font-size:13px;
opacity:0.8;
}}

.sub-value{{
margin-top:8px;
font-size:22px;
font-weight:900;
}}

.section-title{{
font-size:24px;
font-weight:900;
margin-bottom:18px;
}}

.stats-grid{{
display:grid;
grid-template-columns:1fr 1fr;
gap:14px;
margin-top:18px;
}}

.stat-box{{
background:#222d40;
padding:20px;
border-radius:24px;
}}

.stat-title{{
font-size:13px;
opacity:0.7;
}}

.stat-value{{
margin-top:8px;
font-size:28px;
font-weight:900;
}}

.ai-box{{
background:linear-gradient(
135deg,
#1e2b3d,
#2b3b52
);
padding:22px;
border-radius:28px;
display:flex;
align-items:center;
gap:16px;
font-weight:700;
margin-top:18px;
}}

.ai-icon{{
width:60px;
height:60px;
border-radius:20px;
background:#9bb6c920;
display:flex;
align-items:center;
justify-content:center;
font-size:24px;
}}

.section{{
display:none;
}}

.section.active-section{{
display:block;
}}

.input{{
width:100%;
padding:18px;
border:none;
border-radius:22px;
margin-top:14px;
background:#222d40;
color:white;
font-size:16px;
outline:none;
}}

.button{{
width:100%;
padding:18px;
border:none;
border-radius:24px;
margin-top:18px;
font-size:17px;
font-weight:900;
background:linear-gradient(
135deg,
#6d8ea6,
#9bb6c9
);
color:white;
cursor:pointer;
}}

.operation-tabs{{
display:flex;
gap:10px;
margin-bottom:14px;
}}

.op-tab{{
flex:1;
padding:16px;
border:none;
border-radius:20px;
background:#222d40;
color:white;
font-size:15px;
font-weight:900;
cursor:pointer;
}}

.active-op{{
background:linear-gradient(
135deg,
#6d8ea6,
#9bb6c9
);
}}

.history-item{{
display:flex;
justify-content:space-between;
align-items:center;
padding:18px;
background:#222d40;
border-radius:24px;
margin-top:14px;
}}

.history-left{{
display:flex;
align-items:center;
gap:14px;
}}

.history-icon{{
width:52px;
height:52px;
border-radius:18px;
background:#2d3a52;
display:flex;
align-items:center;
justify-content:center;
font-size:20px;
}}

.history-title{{
font-size:16px;
font-weight:900;
}}

.history-date{{
opacity:0.6;
font-size:13px;
margin-top:4px;
}}

.history-amount{{
font-size:18px;
font-weight:900;
}}

.navbar{{
position:fixed;
bottom:16px;
left:50%;
transform:translateX(-50%);
width:94%;
background:#161f2d;
border-radius:30px;
display:flex;
justify-content:space-around;
padding:16px 0;
z-index:100;
}}

.nav-item{{
display:flex;
flex-direction:column;
align-items:center;
font-size:11px;
opacity:0.55;
cursor:pointer;
min-width:70px;
}}

.nav-item i{{
font-size:22px;
margin-bottom:6px;
}}

.active{{
opacity:1;
color:#9bb6c9;
}}

.sidebar{{
position:fixed;
top:0;
left:-280px;
width:280px;
height:100%;
background:#161f2d;
z-index:999;
padding:26px;
transition:.25s;
overflow-y:auto;
}}

.sidebar.open{{
left:0;
}}

.sidebar-title{{
font-size:28px;
font-weight:900;
margin-bottom:24px;
}}

.side-item{{
display:flex;
align-items:center;
gap:14px;
padding:18px;
background:#222d40;
border-radius:20px;
margin-top:12px;
font-weight:700;
cursor:pointer;
}}

.overlay{{
position:fixed;
top:0;
left:0;
width:100%;
height:100%;
background:rgba(0,0,0,0.45);
z-index:998;
display:none;
}}

.overlay.show{{
display:block;
}}

</style>

</head>

<body>

<!-- SIDEBAR -->

<div class="sidebar" id="sidebar">

<div class="sidebar-title">
Sage Finance
</div>

<div
class="side-item"
onclick="openSection('history-section')"
>
<i class="fa-solid fa-clock"></i>
История
</div>

<div
class="side-item"
onclick="openSection('settings-section')"
>
<i class="fa-solid fa-gear"></i>
Настройки
</div>

</div>

<div
class="overlay"
id="overlay"
onclick="closeSidebar()"
></div>

<div class="container">

<!-- TOPBAR -->

<div class="topbar">

<div class="logo">
Sage Finance
</div>

<div
class="menu-btn"
onclick="openSidebar()"
>
<i class="fa-solid fa-bars"></i>
</div>

</div>

<!-- HOME -->

<div
class="section active-section"
id="home-section"
>

<div class="card balance-card">

<div>
💰 Общий баланс
</div>

<div class="balance">
{total_balance} ₽
</div>

<div class="sub-balance">

<div class="sub-box">

<div class="sub-title">
👤 Личный
</div>

<div class="sub-value">
{personal_total} ₽
</div>

</div>

<div class="sub-box">

<div class="sub-title">
💼 Бизнес
</div>

<div class="sub-value">
{business_total} ₽
</div>

</div>

</div>

</div>

<div class="stats-grid">

<div class="stat-box">

<div class="stat-title">
📈 Доходы
</div>

<div class="stat-value">
{income_total} ₽
</div>

</div>

<div class="stat-box">

<div class="stat-title">
📉 Расходы
</div>

<div class="stat-value">
{expense_total} ₽
</div>

</div>

<div class="stat-box">

<div class="stat-title">
💸 Долги
</div>

<div class="stat-value">
{debt_total} ₽
</div>

</div>

<div class="stat-box">

<div class="stat-title">
💎 Накопления
</div>

<div class="stat-value">
{savings_total} ₽
</div>

</div>

</div>

<div class="ai-box">

<div class="ai-icon">
🤖
</div>

<div>
{ai_text}
</div>

</div>

</div>

<!-- OPERATIONS -->

<div
class="section"
id="operations-section"
>

<div class="card">

<div class="section-title">
💸 Личные операции
</div>

<div class="operation-tabs">

<button
class="op-tab active-op"
onclick="showIncome()"
id="incomeTab"
>
📈 Доход
</button>

<button
class="op-tab"
onclick="showExpense()"
id="expenseTab"
>
📉 Расход
</button>

</div>

<form
action="/api/add_operation"
method="POST"
>

<input
type="hidden"
name="user_id"
value="{user_id}"
>

<input
type="hidden"
name="account"
value="personal"
>

<input
type="hidden"
name="type"
id="typeInput"
value="income"
>

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

<select
class="input"
name="category"
id="categorySelect"
>

<option value="Зарплата">
💼 Зарплата
</option>

<option value="Бизнес">
🏢 Бизнес
</option>

<option value="Инвестиции">
📈 Инвестиции
</option>

<option value="Другое">
📦 Другое
</option>

</select>

<input
class="input"
type="text"
name="note"
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

</div>

<!-- BUSINESS -->

<div
class="section"
id="business-section"
>

<div class="card balance-card">

<div>
💼 Бизнес баланс
</div>

<div class="balance">
{business_total} ₽
</div>

</div>

<div class="stats-grid">

<div class="stat-box">

<div class="stat-title">
📈 Доход
</div>

<div class="stat-value">
{business_income} ₽
</div>

</div>

<div class="stat-box">

<div class="stat-title">
📉 Расход
</div>

<div class="stat-value">
{business_expense} ₽
</div>

</div>

</div>

<div class="card">

<div class="section-title">
💼 Бизнес операции
</div>

<form
action="/api/add_operation"
method="POST"
>

<input
type="hidden"
name="user_id"
value="{user_id}"
>

<input
type="hidden"
name="account"
value="business"
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

<select
class="input"
name="category"
>

<option value="Товар">
📦 Товар
</option>

<option value="Закупка">
🛒 Закупка
</option>

<option value="Реклама">
📢 Реклама
</option>

<option value="Логистика">
🚚 Логистика
</option>

<option value="Комиссии">
💳 Комиссии
</option>

<option value="Другое">
📦 Другое
</option>

</select>

<input
class="input"
type="text"
name="note"
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

</div>

<!-- DEBTS -->

<div
class="section"
id="debts-section"
>

<div class="card">

<div class="section-title">
💸 Долги
</div>

<form
action="/api/add_debt"
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
📥 Мне должны
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

</div>

<!-- HISTORY -->

<div
class="section"
id="history-section"
>

<div class="card">

<div class="section-title">
🕓 История операций
</div>

{history_html}

</div>

</div>

<!-- NAVBAR -->

<div class="navbar">

<div
class="nav-item active"
onclick="openSection('home-section')"
>
<i class="fa-solid fa-house"></i>
Главная
</div>

<div
class="nav-item"
onclick="openSection('operations-section')"
>
<i class="fa-solid fa-plus-minus"></i>
Операции
</div>

<div
class="nav-item"
onclick="openSection('business-section')"
>
<i class="fa-solid fa-building"></i>
Бизнес
</div>

<div
class="nav-item"
onclick="openSection('debts-section')"
>
<i class="fa-solid fa-money-bill-wave"></i>
Долги
</div>

<div
class="nav-item"
onclick="openSection('history-section')"
>
<i class="fa-solid fa-clock"></i>
История
</div>

</div>

<script>

function openSidebar(){

document
.getElementById('sidebar')
.classList.add('open');

document
.getElementById('overlay')
.classList.add('show');

}

function closeSidebar(){

document
.getElementById('sidebar')
.classList.remove('open');

document
.getElementById('overlay')
.classList.remove('show');

}

function openSection(id){

document
.querySelectorAll('.section')
.forEach(section=>{

section.classList.remove(
'active-section'
);

});

document
.getElementById(id)
.classList.add(
'active-section'
);

closeSidebar();

}

function showIncome(){

document
.getElementById('incomeTab')
.classList.add('active-op');

document
.getElementById('expenseTab')
.classList.remove('active-op');

document
.getElementById('typeInput')
.value='income';

document
.getElementById(
'categorySelect'
).innerHTML=`

<option value="Зарплата">
💼 Зарплата
</option>

<option value="Бизнес">
🏢 Бизнес
</option>

<option value="Инвестиции">
📈 Инвестиции
</option>

<option value="Подарок">
🎁 Подарок
</option>

<option value="Другое">
📦 Другое
</option>

`;

}

function showExpense(){

document
.getElementById('expenseTab')
.classList.add('active-op');

document
.getElementById('incomeTab')
.classList.remove('active-op');

document
.getElementById('typeInput')
.value='expense';

document
.getElementById(
'categorySelect'
).innerHTML=`

<option value="Продукты">
🛒 Продукты
</option>

<option value="Кафе">
🍔 Кафе
</option>

<option value="Транспорт">
🚕 Транспорт
</option>

<option value="Подписки">
📱 Подписки
</option>

<option value="Развлечения">
🎮 Развлечения
</option>

<option value="Здоровье">
💊 Здоровье
</option>

<option value="Одежда">
👕 Одежда
</option>

<option value="Другое">
📦 Другое
</option>

`;

}

</script>

</body>

</html>

"""

# =========================================================
# API ADD OPERATION
# =========================================================

@app.route(
    "/api/add_operation",
    methods=["POST"]
)
def api_add_operation():

    user_id = request.form.get(
        "user_id"
    )

    op_type = request.form.get(
        "type"
    )

    account = request.form.get(
        "account"
    )

    wallet = request.form.get(
        "wallet"
    )

    category = request.form.get(
        "category"
    )

    amount = float(
        request.form.get(
            "amount",
            0
        )
    )

    note = request.form.get(
        "note",
        ""
    )

    add_operation_to_db(

        user_id,
        op_type,
        account,
        wallet,
        category,
        amount,
        note

    )

    return home()

# =========================================================
# API ADD DEBT
# =========================================================

@app.route(
    "/api/add_debt",
    methods=["POST"]
)
def api_add_debt():

    user_id = request.form.get(
        "user_id"
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

    add_debt_to_db(

        user_id,
        person,
        amount,
        debt_type

    )

    return home()

# =========================================================
# TELEGRAM
# =========================================================

@bot.message_handler(commands=["start"])
def start(message):

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    web_app = types.WebAppInfo(
        "https://sage-finance.onrender.com/?user_id="
        + str(message.from_user.id)
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

# =========================================================
# BOT LOOP
# =========================================================

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

# =========================================================
# RUN
# =========================================================

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
