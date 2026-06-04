# =========================================================
# SAGE FINANCE V2
# STAGE 1 — STABLE ARCHITECTURE + LIVE UI BASE
# FULL bot.py
# =========================================================

from flask import Flask, request, redirect, jsonify
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

PRIMARY = "#9bb6c9"
BG = "#0d1118"
CARD = "#161f2d"

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


def get_operations(user_id):

    conn = db()

    cur = conn.cursor()

    cur.execute("""

    SELECT *
    FROM operations
    WHERE telegram_id=?
    ORDER BY id DESC

    """, (user_id,))

    rows = cur.fetchall()

    conn.close()

    return rows


def get_goals(user_id):

    conn = db()

    cur = conn.cursor()

    cur.execute("""

    SELECT *
    FROM goals
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
    amount
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
        created_at

    )

    VALUES (?, ?, ?, ?, ?, ?, ?)

    """, (

        user_id,
        op_type,
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

    goals = get_goals(user_id)

    debts = get_debts(user_id)

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

    # =====================================================
    # ANALYTICS
    # =====================================================

    stats = {}

    for item in operations:

        if item["type"] == "expense":

            cat = item["category"]

            if cat not in stats:

                stats[cat] = 0

            stats[cat] += item["amount"]

    labels = list(stats.keys())

    values = list(stats.values())

    # =====================================================
    # HISTORY HTML
    # =====================================================

    history_html = ""

    for item in operations[:15]:

        color = "#7db1d4"
        icon = "📈"

        if item["type"] == "expense":

            color = "#ff7d7d"
            icon = "📉"

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
    # GOALS HTML
    # =====================================================

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

        goals_html += f"""

        <div class="goal-card">

            <div class="goal-top">

                <div>
                    🎯 {goal["name"]}
                </div>

                <div>
                    {goal["saved"]} /
                    {goal["target"]} ₽
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

    # =====================================================
    # DEBTS HTML
    # =====================================================

    debts_html = ""

    for debt in debts:

        icon = "📤" if debt["type"] == "give" else "📥"

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

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

*{{
box-sizing:border-box;
-webkit-tap-highlight-color:transparent;
}}

body{{
margin:0;
background:{BG};
color:white;
font-family:-apple-system,BlinkMacSystemFont,sans-serif;
}}

.container{{
max-width:700px;
margin:auto;
padding:20px;
padding-bottom:140px;
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

.profile{{
width:54px;
height:54px;
border-radius:20px;
background:#1c2431;
display:flex;
align-items:center;
justify-content:center;
font-size:20px;
}}

.card{{
background:{CARD};
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
font-size:46px;
font-weight:900;
margin-top:12px;
}}

.sub-balance{{
display:flex;
gap:14px;
margin-top:20px;
}}

.sub-box{{
flex:1;
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
font-size:26px;
font-weight:900;
margin-bottom:18px;
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

.button:active{{
transform:scale(0.98);
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

.goal-card{{
background:#222d40;
padding:18px;
border-radius:24px;
margin-top:14px;
}}

.goal-top{{
display:flex;
justify-content:space-between;
margin-bottom:12px;
}}

.progress{{
width:100%;
height:12px;
background:#2e3a4d;
border-radius:20px;
overflow:hidden;
}}

.progress-fill{{
height:100%;
background:{PRIMARY};
}}

.navbar{{
position:fixed;
bottom:16px;
left:50%;
transform:translateX(-50%);
width:92%;
background:#161f2d;
border-radius:30px;
display:flex;
justify-content:space-around;
padding:16px 0;
overflow-x:auto;
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
color:{PRIMARY};
}}

.section{{
display:none;
}}

.section.active-section{{
display:block;
animation:fade .2s ease;
}}

@keyframes fade{{
from{{
opacity:0;
transform:translateY(10px);
}}
to{{
opacity:1;
transform:translateY(0);
}}
}}

.toast{{
position:fixed;
top:20px;
left:50%;
transform:translateX(-50%);
background:#1f2a3b;
padding:16px 22px;
border-radius:18px;
display:none;
z-index:9999;
font-weight:700;
}}

.loader{{
display:none;
position:fixed;
top:0;
left:0;
width:100%;
height:100%;
background:rgba(0,0,0,0.4);
z-index:9998;
align-items:center;
justify-content:center;
}}

.spinner{{
width:60px;
height:60px;
border-radius:50%;
border:6px solid #2f3a4d;
border-top:6px solid {PRIMARY};
animation:spin 1s linear infinite;
}}

@keyframes spin{{
100%{{
transform:rotate(360deg);
}}
}}

</style>

</head>

<body>

<div class="toast" id="toast">
Успешно
</div>

<div class="loader" id="loader">

<div class="spinner"></div>

</div>

<div class="container">

<div class="topbar">

<div class="logo">
Sage Finance
</div>

<div class="profile">
<i class="fa-solid fa-user"></i>
</div>

</div>

<!-- HOME -->

<div
class="section active-section"
id="home-section"
>

<div class="card balance-card">

<div>
👤 Личный баланс
</div>

<div class="balance">
{personal_total} ₽
</div>

<div class="sub-balance">

<div class="sub-box">

<div class="sub-title">
💵 Наличные
</div>

<div class="sub-value">
{user["personal_cash"]} ₽
</div>

</div>

<div class="sub-box">

<div class="sub-title">
💳 Карта
</div>

<div class="sub-value">
{user["personal_card"]} ₽
</div>

</div>

</div>

</div>

<div class="card">

<div class="section-title">
➕ Новая операция
</div>

<form id="operationForm">

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

<select
class="input"
name="category"
>

<option value="Зарплата">
💼 Зарплата
</option>

<option value="Продукты">
🛒 Продукты
</option>

<option value="Кафе">
🍔 Кафе
</option>

<option value="Транспорт">
🚕 Транспорт
</option>

<option value="Развлечения">
🎮 Развлечения
</option>

<option value="Здоровье">
💊 Здоровье
</option>

<option value="Подписки">
📱 Подписки
</option>

<option value="Бизнес">
🏢 Бизнес
</option>

<option value="Другое">
📦 Другое
</option>

</select>

<button
class="button"
type="submit"
>
Сохранить операцию
</button>

</form>

</div>

</div>

<!-- ANALYTICS -->

<div
class="section"
id="analytics-section"
>

<div class="card">

<div class="section-title">
📊 Аналитика
</div>

<canvas id="chart"></canvas>

</div>

</div>

<!-- GOALS -->

<div
class="section"
id="goals-section"
>

<div class="card">

<div class="section-title">
🎯 Цели
</div>

{goals_html}

</div>

</div>

<!-- HISTORY -->

<div
class="section"
id="history-section"
>

<div class="card">

<div class="section-title">
🕓 История
</div>

{history_html}

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

{debts_html}

</div>

</div>

<!-- NAVBAR -->

<div class="navbar">

<div
class="nav-item active"
data-target="home-section"
>
<i class="fa-solid fa-house"></i>
Главная
</div>

<div
class="nav-item"
data-target="analytics-section"
>
<i class="fa-solid fa-chart-pie"></i>
Аналитика
</div>

<div
class="nav-item"
data-target="goals-section"
>
<i class="fa-solid fa-bullseye"></i>
Цели
</div>

<div
class="nav-item"
data-target="history-section"
>
<i class="fa-solid fa-clock"></i>
История
</div>

<div
class="nav-item"
data-target="debts-section"
>
<i class="fa-solid fa-money-bill-wave"></i>
Долги
</div>

</div>

</div>

<script>

const navItems =
document.querySelectorAll(
'.nav-item'
);

const sections =
document.querySelectorAll(
'.section'
);

navItems.forEach(item => {{

item.addEventListener(
'click',
() => {{

navItems.forEach(nav => {{
nav.classList.remove('active');
}});

item.classList.add('active');

sections.forEach(section => {{
section.classList.remove(
'active-section'
);
}});

const target =
item.getAttribute(
'data-target'
);

document
.getElementById(target)
.classList
.add(
'active-section'
);

}}

);

}});

const ctx =
document.getElementById(
'chart'
);

if(ctx){{

new Chart(ctx, {{

type:'doughnut',

data: {{

labels: {labels},

datasets:[{{

data:{values},

backgroundColor:[
'#6d8ea6',
'#9bb6c9',
'#7db1d4',
'#5d738a',
'#bfd3e2'
],

borderWidth:0

}}]

}}

}});

}}

function toast(text){{

const t =
document.getElementById(
'toast'
);

t.innerText = text;

t.style.display = 'block';

setTimeout(() => {{

t.style.display = 'none';

}}, 2000);

}}

const form =
document.getElementById(
'operationForm'
);

form.addEventListener(
'submit',
async(e)=>{{

e.preventDefault();

document.getElementById(
'loader'
).style.display='flex';

const formData =
new FormData(form);

const response =
await fetch('/api/add_operation',{{

method:'POST',

body:formData

}});

const data =
await response.json();

document.getElementById(
'loader'
).style.display='none';

if(data.success){{

toast('Операция добавлена');

setTimeout(()=>{{

location.reload();

}},700);

}}

}}
);

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

    add_operation_to_db(

        user_id,
        op_type,
        account,
        wallet,
        category,
        amount

    )

    return jsonify({

        "success": True

    })

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
