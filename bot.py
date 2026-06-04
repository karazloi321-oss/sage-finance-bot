# =====================================================
# SAGE FINANCE FULL BOT.PY
# ANALYTICS UPDATE VERSION
# =====================================================

from flask import Flask, request, redirect
import telebot
from telebot import types
import threading
import time
import os
import json
from datetime import datetime

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "data.json"

# =====================================================
# INIT
# =====================================================

if not os.path.exists(DATA_FILE):

    with open(DATA_FILE, "w", encoding="utf-8") as f:

        json.dump({

            "personal": {
                "cash": 0,
                "card": 0,
                "expenses": [],
                "history": []
            },

            "business": {
                "cash": 0,
                "card": 0,
                "expenses": [],
                "history": []
            },

            "savings": {
                "cash": 0,
                "card": 0
            },

            "debts": [],

            "goals": []

        }, f, ensure_ascii=False, indent=4)

# =====================================================
# HELPERS
# =====================================================

def load_data():

    with open(DATA_FILE, "r", encoding="utf-8") as f:

        return json.load(f)


def save_data(data):

    with open(DATA_FILE, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


def total_balance(section):

    return (
        section["cash"]
        + section["card"]
    )


def expense_stats(expenses):

    stats = {}

    for item in expenses:

        category = item["category"]

        if category not in stats:

            stats[category] = 0

        stats[category] += item["amount"]

    return stats

# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    data = load_data()

    personal_total = total_balance(
        data["personal"]
    )

    business_total = total_balance(
        data["business"]
    )

    savings_total = total_balance(
        data["savings"]
    )

    total_all = (
        personal_total
        + business_total
        + savings_total
    )

    all_history = (
        data["personal"]["history"]
        + data["business"]["history"]
    )

    income_total = 0
    expense_total = 0

    for item in all_history:

        if item["type"] == "income":

            income_total += item["amount"]

        elif item["type"] == "expense":

            expense_total += item["amount"]

    # =================================================
    # ANALYTICS
    # =================================================

    personal_stats = expense_stats(
        data["personal"]["expenses"]
    )

    business_stats = expense_stats(
        data["business"]["expenses"]
    )

    personal_labels = list(
        personal_stats.keys()
    )

    personal_values = list(
        personal_stats.values()
    )

    business_labels = list(
        business_stats.keys()
    )

    business_values = list(
        business_stats.values()
    )

    # =================================================
    # BUSINESS
    # =================================================

    business_income = 0
    business_expense = 0

    for item in data["business"]["history"]:

        if item["type"] == "income":

            business_income += item["amount"]

        elif item["type"] == "expense":

            business_expense += item["amount"]

    # =================================================
    # AI
    # =================================================

    ai_text = "Финансы стабильны"

    if expense_total > income_total:

        ai_text = "Расходы превышают доходы"

    elif savings_total < total_all * 0.1:

        ai_text = "Пополняй накопления чаще"

    elif income_total > expense_total:

        ai_text = "Доходы растут быстрее расходов"

    # =================================================
    # HISTORY
    # =================================================

    history_html = ""

    for index, item in enumerate(
        reversed(all_history[-20:])
    ):

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
                        {item["date"]}
                    </div>

                </div>

            </div>

            <div style="text-align:right;">

                <div
                class="history-amount"
                style="color:{color};"
                >
                    {item["amount"]} ₽
                </div>

            </div>

        </div>

        """

    # =================================================
    # DEBTS
    # =================================================

    debts_html = ""

    debt_total = 0

    for debt in reversed(data["debts"]):

        debt_total += debt["amount"]

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
                        {debt["date"]}
                    </div>

                </div>

            </div>

            <div class="history-amount">
                {debt["amount"]} ₽
            </div>

        </div>

        """

    # =================================================
    # GOALS
    # =================================================

    goals_html = ""

    for goal in data["goals"]:

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
Sage Finance
</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

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
padding-bottom:120px;
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
border-radius:30px;
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
display:grid;
grid-template-columns:1fr 1fr;
gap:14px;
margin-top:18px;
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

.active-section{{
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
padding:24px;
transition:0.25s;
overflow-y:auto;
}}

.sidebar.open{{
left:0;
}}

.side-item{{
display:flex;
align-items:center;
gap:14px;
padding:18px;
background:#222d40;
border-radius:20px;
margin-top:14px;
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
display:none;
z-index:998;
}}

.overlay.show{{
display:block;
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
font-size:14px;
font-weight:800;
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
background:linear-gradient(
135deg,
#6d8ea6,
#9bb6c9
);
}}

canvas{{
margin-top:20px;
}}

</style>

</head>

<body>

<div
class="sidebar"
id="sidebar"
>

<div
class="side-item"
onclick="openSection('history-section')"
>
<i class="fa-solid fa-clock"></i>
История
</div>

<div
class="side-item"
onclick="openSection('goals-section')"
>
<i class="fa-solid fa-bullseye"></i>
Цели
</div>

<div
class="side-item"
onclick="openSection('savings-section')"
>
<i class="fa-solid fa-piggy-bank"></i>
Накопления
</div>

</div>

<div
class="overlay"
id="overlay"
onclick="closeSidebar()"
></div>

<div class="container">

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
{total_all} ₽
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

<form
action="/add_operation"
method="POST"
>

<input
type="hidden"
name="account"
value="personal"
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

</div>

<!-- ANALYTICS -->

<div
class="section"
id="analytics-section"
>

<div class="card">

<div class="section-title">
📊 Личная аналитика
</div>

<canvas id="personalChart"></canvas>

</div>

<div class="card">

<div class="section-title">
🏢 Бизнес аналитика
</div>

<canvas id="businessChart"></canvas>

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
action="/add_operation"
method="POST"
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
action="/add_debt"
method="POST"
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
🕓 История
</div>

{history_html}

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

<form
action="/add_goal"
method="POST"
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

</div>

<!-- SAVINGS -->

<div
class="section"
id="savings-section"
>

<div class="card balance-card">

<div>
💎 Накопления
</div>

<div class="balance">
{savings_total} ₽
</div>

</div>

<div class="card">

<div class="section-title">
🔄 Перевод в накопления
</div>

<form
action="/transfer_savings"
method="POST"
>

<select
class="input"
name="from_account"
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

<button
class="button"
type="submit"
>
Перевести
</button>

</form>

</div>

</div>

<!-- NAVBAR -->

<div class="navbar">

<div
class="nav-item active"
onclick="openSection('home-section', this)"
>
<i class="fa-solid fa-house"></i>
Главная
</div>

<div
class="nav-item"
onclick="openSection('operations-section', this)"
>
<i class="fa-solid fa-plus-minus"></i>
Операции
</div>

<div
class="nav-item"
onclick="openSection('analytics-section', this)"
>
<i class="fa-solid fa-chart-pie"></i>
Статистика
</div>

<div
class="nav-item"
onclick="openSection('business-section', this)"
>
<i class="fa-solid fa-building"></i>
Бизнес
</div>

<div
class="nav-item"
onclick="openSection('debts-section', this)"
>
<i class="fa-solid fa-money-bill-wave"></i>
Долги
</div>

</div>

<script>

function openSection(id, element) {{

document
.querySelectorAll('.section')
.forEach(section => {{

section.classList.remove(
'active-section'
);

}});

document
.getElementById(id)
.classList.add(
'active-section'
);

document
.querySelectorAll('.nav-item')
.forEach(item => {{

item.classList.remove(
'active'
);

}});

if(element){{
element.classList.add(
'active'
);
}}

closeSidebar();

}}

function openSidebar(){{
document
.getElementById('sidebar')
.classList.add('open');

document
.getElementById('overlay')
.classList.add('show');
}}

function closeSidebar(){{
document
.getElementById('sidebar')
.classList.remove('open');

document
.getElementById('overlay')
.classList.remove('show');
}}

const personalCtx =
document.getElementById(
'personalChart'
);

if(personalCtx){{

new Chart(personalCtx, {{

type:'doughnut',

data:{{
labels:{personal_labels},
datasets:[{{

data:{personal_values},

backgroundColor:[
'#6d8ea6',
'#9bb6c9',
'#7db1d4',
'#5d738a',
'#bfd3e2',
'#7f99ad'
],

borderWidth:0

}}]
}}

}});

}}

const businessCtx =
document.getElementById(
'businessChart'
);

if(businessCtx){{

new Chart(businessCtx, {{

type:'bar',

data:{{
labels:{business_labels},
datasets:[{{

data:{business_values}

}}]
}}

}});

}}

</script>

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

    data = load_data()

    account = request.form.get(
        "account"
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

    category = request.form.get(
        "category"
    )

    if op_type == "income":

        data[account][wallet] += amount

    else:

        data[account][wallet] -= amount

        data[account]["expenses"].append({

            "amount": amount,
            "category": category,
            "wallet": wallet,
            "date": datetime.now().strftime(
                "%d.%m.%Y %H:%M"
            )

        })

    data[account]["history"].append({

        "type": op_type,

        "amount": amount,

        "category": category,

        "wallet": wallet,

        "date": datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        )

    })

    save_data(data)

    return redirect("/")

# =====================================================
# SAVINGS
# =====================================================

@app.route(
    "/transfer_savings",
    methods=["POST"]
)
def transfer_savings():

    data = load_data()

    from_account = request.form.get(
        "from_account"
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

    if data[from_account][wallet] >= amount:

        data[from_account][wallet] -= amount

        data["savings"][wallet] += amount

    save_data(data)

    return redirect("/")

# =====================================================
# ADD DEBT
# =====================================================

@app.route(
    "/add_debt",
    methods=["POST"]
)
def add_debt():

    data = load_data()

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

    data["debts"].append({

        "person": person,

        "amount": amount,

        "type": debt_type,

        "date": datetime.now().strftime(
            "%d.%m.%Y"
        )

    })

    save_data(data)

    return redirect("/")

# =====================================================
# ADD GOAL
# =====================================================

@app.route(
    "/add_goal",
    methods=["POST"]
)
def add_goal():

    data = load_data()

    name = request.form.get(
        "name"
    )

    target = float(
        request.form.get(
            "target",
            0
        )
    )

    data["goals"].append({

        "name": name,
        "target": target,
        "saved": 0

    })

    save_data(data)

    return redirect("/")

# =====================================================
# TELEGRAM
# =====================================================

@bot.message_handler(commands=["start"])
def start(message):

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    web_app = types.WebAppInfo(
        "https://sage-finance.onrender.com/"
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

            print(e)

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
