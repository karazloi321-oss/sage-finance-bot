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

# ====== ИНИЦИАЛИЗАЦИЯ ======
if not os.path.exists(DATA_FILE):

    with open(DATA_FILE, "w") as f:

        json.dump({
            "income": [],
            "expenses": [],
            "salary": 0
        }, f)


def load_data():

    with open(DATA_FILE, "r") as f:

        return json.load(f)


def save_data(data):

    with open(DATA_FILE, "w") as f:

        json.dump(
            data,
            f,
            indent=4
        )


# ====== АНАЛИТИКА ======
def get_expense_stats(expenses):

    stats = {}

    for item in expenses:

        category = item["category"]
        amount = item["amount"]

        if category not in stats:

            stats[category] = 0

        stats[category] += amount

    sorted_stats = sorted(
        stats.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return sorted_stats[:5]


def get_balance(data):

    total_income = (
        sum(
            item["amount"]
            for item in data["income"]
        )
        + data["salary"]
    )

    total_expenses = sum(
        item["amount"]
        for item in data["expenses"]
    )

    return (
        total_income,
        total_expenses,
        total_income - total_expenses
    )


# ====== WEBAPP ======
@app.route("/", methods=["GET", "HEAD"])
def home():

    data = load_data()

    total_income, total_expenses, balance = (
        get_balance(data)
    )

    top_expenses = get_expense_stats(
        data["expenses"]
    )

    chart_labels = [
        item[0]
        for item in top_expenses
    ]

    chart_data = [
        item[1]
        for item in top_expenses
    ]

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

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<link
    rel="stylesheet"
    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
>

<style>

*{{
    box-sizing:border-box;
}}

body{{
    margin:0;
    background:#0b0f19;
    color:white;
    font-family:-apple-system,BlinkMacSystemFont,sans-serif;
}}

.container{{
    padding:20px;
    max-width:600px;
    margin:auto;
    padding-bottom:120px;
}}

.header{{
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
    background:#1b2235;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:20px;
}}

.balance-card{{
    margin-top:24px;
    border-radius:32px;
    padding:28px;
    background:linear-gradient(
        135deg,
        #1f8bff,
        #6c63ff
    );
    box-shadow:0 15px 35px rgba(0,0,0,0.4);
}}

.balance-label{{
    opacity:0.8;
    font-size:14px;
}}

.balance{{
    font-size:44px;
    font-weight:700;
    margin-top:12px;
}}

.card-number{{
    margin-top:30px;
    letter-spacing:3px;
    font-size:18px;
    opacity:0.9;
}}

.stats{{
    display:flex;
    gap:14px;
    margin-top:20px;
}}

.stat-card{{
    flex:1;
    background:#141b2d;
    border-radius:24px;
    padding:18px;
}}

.stat-icon{{
    width:42px;
    height:42px;
    border-radius:14px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:18px;
    margin-bottom:14px;
}}

.income-icon{{
    background:rgba(52,199,89,0.15);
    color:#34c759;
}}

.expense-icon{{
    background:rgba(255,59,48,0.15);
    color:#ff3b30;
}}

.stat-title{{
    opacity:0.7;
    font-size:13px;
}}

.stat-value{{
    font-size:24px;
    font-weight:700;
    margin-top:8px;
}}

.section{{
    margin-top:26px;
}}

.section-title{{
    font-size:22px;
    font-weight:700;
    margin-bottom:16px;
}}

.form-card{{
    background:#141b2d;
    border-radius:28px;
    padding:22px;
}}

.input{{
    width:100%;
    padding:16px;
    margin-top:12px;
    border:none;
    border-radius:18px;
    background:#1d263b;
    color:white;
    font-size:16px;
}}

.select{{
    width:100%;
    padding:16px;
    margin-top:12px;
    border:none;
    border-radius:18px;
    background:#1d263b;
    color:white;
    font-size:16px;
}}

.button{{
    width:100%;
    border:none;
    padding:18px;
    border-radius:20px;
    background:linear-gradient(
        135deg,
        #34c759,
        #30d158
    );
    color:white;
    font-size:17px;
    font-weight:700;
    margin-top:18px;
}}

.chart-card{{
    background:#141b2d;
    border-radius:28px;
    padding:24px;
}}

.bottom-nav{{
    position:fixed;
    bottom:0;
    left:0;
    width:100%;
    background:#111827;
    display:flex;
    justify-content:space-around;
    padding:16px 0;
    border-top:1px solid rgba(255,255,255,0.05);
}}

.nav-item{{
    display:flex;
    flex-direction:column;
    align-items:center;
    font-size:12px;
    opacity:0.7;
}}

.nav-item i{{
    font-size:22px;
    margin-bottom:6px;
}}

.active{{
    opacity:1;
    color:#1f8bff;
}}

.tip-card{{
    margin-top:20px;
    background:#141b2d;
    border-radius:24px;
    padding:20px;
    line-height:1.6;
}}

</style>

</head>

<body>

<div class="container">

<div class="header">

<div class="logo">
    Sage
</div>

<div class="profile">
    <i class="fa-solid fa-user"></i>
</div>

</div>

<div class="balance-card">

<div class="balance-label">
    Общий баланс
</div>

<div class="balance">
    {balance} ₽
</div>

<div class="card-number">
    •••• •••• •••• 2026
</div>

</div>

<div class="stats">

<div class="stat-card">

<div class="stat-icon income-icon">
    <i class="fa-solid fa-arrow-down"></i>
</div>

<div class="stat-title">
    Доходы
</div>

<div class="stat-value">
    {total_income} ₽
</div>

</div>

<div class="stat-card">

<div class="stat-icon expense-icon">
    <i class="fa-solid fa-arrow-up"></i>
</div>

<div class="stat-title">
    Расходы
</div>

<div class="stat-value">
    {total_expenses} ₽
</div>

</div>

</div>

<div class="section">

<div class="section-title">
    Новая операция
</div>

<div class="form-card">

<form
    method="post"
    action="/add_operation"
>

<input
    class="input"
    type="number"
    step="0.01"
    name="amount"
    placeholder="Введите сумму"
    required
>

<select
    class="select"
    name="type"
>

<option value="income">
    Доход
</option>

<option value="expense">
    Расход
</option>

</select>

<input
    class="input"
    type="text"
    name="category"
    placeholder="Категория"
>

<button
    class="button"
    type="submit"
>
    + Добавить операцию
</button>

</form>

</div>

</div>

<div class="section">

<div class="section-title">
    Аналитика
</div>

<div class="chart-card">

<canvas id="expenseChart"></canvas>

</div>

</div>

<div class="tip-card">

💡 Основные расходы распределены по категориям.
Следите за балансом и старайтесь
держать расходы ниже доходов.

</div>

</div>

<div class="bottom-nav">

<div class="nav-item active">
    <i class="fa-solid fa-house"></i>
    Главная
</div>

<div class="nav-item">
    <i class="fa-solid fa-chart-pie"></i>
    Аналитика
</div>

<div class="nav-item">
    <i class="fa-solid fa-wallet"></i>
    Финансы
</div>

<div class="nav-item">
    <i class="fa-solid fa-gear"></i>
    Настройки
</div>

</div>

<script>

const ctx = document
.getElementById('expenseChart');

new Chart(ctx, {{

type: 'doughnut',

data: {{

labels: {chart_labels},

datasets: [{{
    data: {chart_data},
    backgroundColor: [
        '#1f8bff',
        '#34c759',
        '#ff9f0a',
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

</script>

</body>

</html>

"""


# ====== ДОБАВЛЕНИЕ ОПЕРАЦИИ ======
@app.route("/add_operation", methods=["POST"])
def add_operation():

    amount = float(
        request.form.get(
            "amount",
            0
        )
    )

    type_op = request.form.get(
        "type",
        "income"
    )

    category = request.form.get(
        "category"
    ) or "Другое"

    data = load_data()

    entry = {{
        "amount": amount,
        "category": category,
        "date": str(datetime.now())
    }}

    if type_op == "income":

        data["income"].append(entry)

    else:

        data["expenses"].append(entry)

    save_data(data)

    return redirect("/")


# ====== TELEGRAM ======
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


# ====== ЗАПУСК ======
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
