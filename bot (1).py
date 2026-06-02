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

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({
            "personal": {"cash": 0, "card": 0, "expenses": []},
            "business": {"cash": 0, "card": 0, "expenses": []}
        }, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_total_balance(section):
    return section["cash"] + section["card"]

def get_expense_stats(expenses):
    stats = {}
    for item in expenses:
        category = item["category"]
        stats[category] = stats.get(category, 0) + item["amount"]
    return sorted(stats.items(), key=lambda x: x[1], reverse=True)[:5]

@app.route("/", methods=["GET"])
def home():

    data = load_data()

    personal_total = get_total_balance(data["personal"])
    business_total = get_total_balance(data["business"])

    personal_chart = get_expense_stats(
        data["personal"]["expenses"]
    )

    labels = [item[0] for item in personal_chart]
    values = [item[1] for item in personal_chart]

    return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sage Finance</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<link rel="stylesheet"
href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"/>

<style>

*{{
box-sizing:border-box;
}}

body{{
margin:0;
background:#0b1020;
color:white;
font-family:-apple-system,BlinkMacSystemFont,sans-serif;
}}

.container{{
max-width:700px;
margin:auto;
padding:20px;
padding-bottom:120px;
}}

.topbar{{
display:flex;
justify-content:space-between;
align-items:center;
}}

.logo{{
font-size:30px;
font-weight:700;
}}

.profile{{
width:46px;
height:46px;
border-radius:50%;
background:#171d31;
display:flex;
align-items:center;
justify-content:center;
}}

.card{{
background:#151b2e;
border-radius:30px;
padding:24px;
margin-top:20px;
}}

.balance-card{{
background:linear-gradient(135deg,#1f8bff,#6c63ff);
}}

.balance-label{{
opacity:0.8;
font-size:14px;
}}

.balance{{
font-size:42px;
font-weight:700;
margin-top:12px;
}}

.sub-balance{{
display:flex;
gap:14px;
margin-top:18px;
}}

.sub-box{{
flex:1;
background:rgba(255,255,255,0.12);
padding:14px;
border-radius:20px;
}}

.sub-title{{
opacity:0.7;
font-size:13px;
}}

.sub-value{{
margin-top:8px;
font-size:20px;
font-weight:700;
}}

.section-title{{
font-size:24px;
font-weight:700;
margin-bottom:18px;
}}

.input{{
width:100%;
padding:16px;
border:none;
border-radius:18px;
margin-top:12px;
background:#202944;
color:white;
font-size:16px;
}}

.button{{
width:100%;
border:none;
padding:18px;
border-radius:20px;
margin-top:16px;
font-size:16px;
font-weight:700;
color:white;
background:linear-gradient(135deg,#34c759,#30d158);
}}

.transfer-btn{{
background:linear-gradient(135deg,#ff9500,#ffb340);
}}

.navbar{{
position:fixed;
bottom:0;
left:0;
width:100%;
background:#111827;
display:flex;
justify-content:space-around;
padding:16px 0;
border-top:1px solid rgba(255,255,255,0.06);
}}

.nav-item{{
display:flex;
flex-direction:column;
align-items:center;
font-size:12px;
opacity:0.65;
cursor:pointer;
}}

.nav-item i{{
font-size:22px;
margin-bottom:5px;
}}

.active{{
opacity:1;
color:#1f8bff;
}}

.chart-card{{
background:#151b2e;
border-radius:30px;
padding:24px;
margin-top:20px;
}}

.section{{
display:none;
}}

.section.active-section{{
display:block;
}}

</style>

</head>

<body>

<div class="container">

<div class="topbar">

<div class="logo">
Sage Finance
</div>

<div class="profile">
<i class="fa-solid fa-user"></i>
</div>

</div>

<div class="section active-section" id="personal-section">

<div class="card balance-card">

<div class="balance-label">
<i class="fa-solid fa-wallet"></i>
Личный баланс
</div>

<div class="balance">
{personal_total} ₽
</div>

<div class="sub-balance">

<div class="sub-box">

<div class="sub-title">
<i class="fa-solid fa-money-bill-wave"></i>
Наличные
</div>

<div class="sub-value">
{data["personal"]["cash"]} ₽
</div>

</div>

<div class="sub-box">

<div class="sub-title">
<i class="fa-solid fa-credit-card"></i>
Карта
</div>

<div class="sub-value">
{data["personal"]["card"]} ₽
</div>

</div>

</div>

</div>

<div class="card">

<div class="section-title">
<i class="fa-solid fa-plus"></i>
Добавить операцию
</div>

<form method="post" action="/add_operation">

<select class="input" name="account">
<option value="personal">👤 Личный</option>
<option value="business">💼 Бизнес</option>
</select>

<select class="input" name="type">
<option value="income">📈 Доход</option>
<option value="expense">📉 Расход</option>
</select>

<select class="input" name="wallet">
<option value="cash">💵 Наличные</option>
<option value="card">💳 Карта</option>
</select>

<input class="input"
type="number"
step="0.01"
name="amount"
placeholder="Введите сумму"
required>

<input class="input"
type="text"
name="category"
placeholder="Категория">

<button class="button" type="submit">
Сохранить операцию
</button>

</form>

</div>

<div class="card">

<div class="section-title">
<i class="fa-solid fa-right-left"></i>
Перевод между счетами
</div>

<form method="post" action="/transfer">

<select class="input" name="from_wallet">
<option value="cash">💵 Из наличных</option>
<option value="card">💳 Из карты</option>
</select>

<select class="input" name="to_wallet">
<option value="card">💳 На карту</option>
<option value="cash">💵 В наличные</option>
</select>

<input class="input"
type="number"
step="0.01"
name="amount"
placeholder="Сумма перевода"
required>

<button class="button transfer-btn" type="submit">
Выполнить перевод
</button>

</form>

</div>

<div class="chart-card">

<div class="section-title">
<i class="fa-solid fa-chart-pie"></i>
Аналитика расходов
</div>

<canvas id="expenseChart"></canvas>

</div>

</div>

<div class="section" id="analytics-section">

<div class="card">

<div class="section-title">
<i class="fa-solid fa-chart-line"></i>
Аналитика
</div>

<p>
Здесь будет расширенная аналитика...
</p>

</div>

</div>

<div class="section" id="business-section">

<div class="card balance-card">

<div class="balance-label">
<i class="fa-solid fa-briefcase"></i>
Бизнес баланс
</div>

<div class="balance">
{business_total} ₽
</div>

<div class="sub-balance">

<div class="sub-box">

<div class="sub-title">
<i class="fa-solid fa-money-bill-wave"></i>
Наличные
</div>

<div class="sub-value">
{data["business"]["cash"]} ₽
</div>

</div>

<div class="sub-box">

<div class="sub-title">
<i class="fa-solid fa-credit-card"></i>
Карта
</div>

<div class="sub-value">
{data["business"]["card"]} ₽
</div>

</div>

</div>

</div>

</div>

<div class="section" id="settings-section">

<div class="card">

<div class="section-title">
<i class="fa-solid fa-gear"></i>
Настройки
</div>

<p>
Панель настроек в разработке...
</p>

</div>

</div>

</div>

<div class="navbar">

<div class="nav-item active"
data-target="personal-section">

<i class="fa-solid fa-house"></i>
Главная

</div>

<div class="nav-item"
data-target="analytics-section">

<i class="fa-solid fa-chart-line"></i>
Аналитика

</div>

<div class="nav-item"
data-target="business-section">

<i class="fa-solid fa-building"></i>
Бизнес

</div>

<div class="nav-item"
data-target="settings-section">

<i class="fa-solid fa-gear"></i>
Настройки

</div>

</div>

<script>

const ctx = document
.getElementById('expenseChart');

new Chart(ctx, {{

type:'doughnut',

data: {{

labels: {labels},

datasets:[{{

data:{values},

backgroundColor:[
'#1f8bff',
'#34c759',
'#ff9500',
'#ff3b30',
'#6c63ff'
],

borderWidth:0

}}]

}},

options: {{

plugins: {{

legend: {{

labels: {{
color:'white'
}}

}}

}}

}}

}});

const navItems =
document.querySelectorAll('.nav-item');

const sections =
document.querySelectorAll('.section');

navItems.forEach(item => {{

item.addEventListener('click', () => {{

navItems.forEach(nav => {{
nav.classList.remove('active');
}});

item.classList.add('active');

sections.forEach(section => {{
section.classList.remove('active-section');
}});

const target =
item.getAttribute('data-target');

document
.getElementById(target)
.classList
.add('active-section');

}});

}});

</script>

</body>
</html>
"""

@app.route("/add_operation", methods=["POST"])
def add_operation():

    data = load_data()

    account = request.form.get("account")
    type_op = request.form.get("type")
    wallet = request.form.get("wallet")

    amount = float(
        request.form.get("amount", 0)
    )

    category = (
        request.form.get("category")
        or "Другое"
    )

    if type_op == "income":

        data[account][wallet] += amount

    else:

        data[account][wallet] -= amount

        data[account]["expenses"].append({

            "amount": amount,
            "category": category,
            "wallet": wallet,
            "date": str(datetime.now())

        })

    save_data(data)

    return redirect("/")

@app.route("/transfer", methods=["POST"])
def transfer():

    data = load_data()

    from_wallet = request.form.get("from_wallet")
    to_wallet = request.form.get("to_wallet")

    amount = float(
        request.form.get("amount", 0)
    )

    if data["personal"][from_wallet] >= amount:

        data["personal"][from_wallet] -= amount
        data["personal"][to_wallet] += amount

    save_data(data)

    return redirect("/")

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

def run_bot():

    while True:

        try:

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
