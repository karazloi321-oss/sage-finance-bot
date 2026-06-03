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

# ================= INIT =================

if not os.path.exists(DATA_FILE):

    with open(DATA_FILE, "w") as f:

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
                "income": [],
                "expenses": [],
                "history": []
            }

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


def get_total_balance(section):

    return (
        section["cash"]
        + section["card"]
    )


def get_expense_stats(expenses):

    stats = {}

    for item in expenses:

        category = item["category"]

        if category not in stats:

            stats[category] = 0

        stats[category] += item["amount"]

    return sorted(
        stats.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]


# ================= WEBAPP =================

@app.route("/", methods=["GET"])
def home():

    data = load_data()

    personal_total = get_total_balance(
        data["personal"]
    )

    business_total = get_total_balance(
        data["business"]
    )

    personal_chart = get_expense_stats(
        data["personal"]["expenses"]
    )

    labels = [
        item[0]
        for item in personal_chart
    ]

    values = [
        item[1]
        for item in personal_chart
    ]

    history_html = ""

    for item in reversed(
        data["personal"]["history"][-10:]
    ):

        icon = "📈" if item["type"] == "income" else "📉"

        history_html += f"""

        <div class="history-item">

            <div class="history-left">

                <div class="history-icon">
                    {icon}
                </div>

                <div>

                    <div class="history-title">
                        {item["category"]}
                    </div>

                    <div class="history-date">
                        {item["wallet"]}
                    </div>

                </div>

            </div>

            <div class="history-amount">

                {item["amount"]} ₽

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
background:#070b14;
color:white;
font-family:-apple-system,BlinkMacSystemFont,sans-serif;
overflow-x:hidden;
}}

body::before{{
content:'';
position:fixed;
width:500px;
height:500px;
background:#1f8bff30;
filter:blur(120px);
top:-200px;
right:-200px;
z-index:-1;
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
margin-bottom:18px;
}}

.logo{{
font-size:32px;
font-weight:900;
}}

.profile{{
width:52px;
height:52px;
border-radius:50%;
background:rgba(255,255,255,0.08);
backdrop-filter:blur(20px);
display:flex;
align-items:center;
justify-content:center;
font-size:20px;
border:1px solid rgba(255,255,255,0.08);
}}

.card{{
border-radius:34px;
padding:24px;
margin-top:20px;
background:rgba(255,255,255,0.06);
backdrop-filter:blur(25px);
border:1px solid rgba(255,255,255,0.08);
box-shadow:0 10px 40px rgba(0,0,0,0.35);
}}

.balance-card{{
background:
linear-gradient(
135deg,
rgba(31,139,255,0.95),
rgba(108,99,255,0.95)
);
position:relative;
overflow:hidden;
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
padding:14px;
border-radius:22px;
}}

.sub-title{{
opacity:0.8;
font-size:13px;
}}

.sub-value{{
margin-top:8px;
font-size:20px;
font-weight:800;
}}

.section-title{{
font-size:24px;
font-weight:900;
margin-bottom:18px;
}}

.quick-actions{{
display:grid;
grid-template-columns:1fr 1fr;
gap:14px;
margin-top:20px;
}}

.action-btn{{
padding:18px;
border-radius:24px;
background:rgba(255,255,255,0.06);
text-align:center;
font-weight:700;
font-size:15px;
}}

.action-btn i{{
font-size:22px;
margin-bottom:10px;
display:block;
}}

.tabs{{
display:flex;
gap:10px;
margin-bottom:14px;
}}

.tab{{
flex:1;
padding:15px;
border:none;
border-radius:20px;
background:#1b2339;
color:white;
font-size:15px;
font-weight:800;
}}

.active-tab{{
background:linear-gradient(
135deg,
#1f8bff,
#6c63ff
);
}}

.input{{
width:100%;
padding:18px;
border:none;
border-radius:20px;
margin-top:12px;
background:#1b2339;
color:white;
font-size:16px;
outline:none;
}}

.amount-input{{
font-size:32px;
font-weight:900;
text-align:center;
padding:24px;
}}

.button{{
width:100%;
border:none;
padding:20px;
border-radius:22px;
margin-top:16px;
font-size:17px;
font-weight:800;
color:white;
background:linear-gradient(
135deg,
#34c759,
#30d158
);
}}

.fast-categories{{
display:grid;
grid-template-columns:1fr 1fr 1fr;
gap:12px;
margin-top:16px;
}}

.fast-category{{
padding:14px;
background:#1b2339;
border-radius:18px;
text-align:center;
font-size:14px;
font-weight:700;
}}

.history-item{{
display:flex;
justify-content:space-between;
align-items:center;
padding:16px;
background:#1b2339;
border-radius:22px;
margin-top:14px;
}}

.history-left{{
display:flex;
align-items:center;
gap:14px;
}}

.history-icon{{
width:48px;
height:48px;
border-radius:16px;
background:rgba(255,255,255,0.08);
display:flex;
align-items:center;
justify-content:center;
font-size:20px;
}}

.history-title{{
font-size:16px;
font-weight:800;
}}

.history-date{{
opacity:0.55;
font-size:13px;
margin-top:4px;
}}

.history-amount{{
font-size:18px;
font-weight:900;
}}

.ai-card{{
background:
linear-gradient(
135deg,
rgba(255,149,0,0.18),
rgba(255,59,48,0.15)
);
}}

.goal-bar{{
height:16px;
background:#1b2339;
border-radius:30px;
overflow:hidden;
margin-top:16px;
}}

.goal-progress{{
height:100%;
width:42%;
background:linear-gradient(
135deg,
#34c759,
#30d158
);
}}

.navbar{{
position:fixed;
bottom:0;
left:0;
width:100%;
background:rgba(10,14,24,0.9);
backdrop-filter:blur(25px);
display:flex;
justify-content:space-around;
padding:14px 0;
border-top:1px solid rgba(255,255,255,0.06);
}}

.nav-item{{
display:flex;
flex-direction:column;
align-items:center;
font-size:11px;
opacity:0.55;
transition:0.2s;
}}

.nav-item i{{
font-size:22px;
margin-bottom:6px;
}}

.active{{
opacity:1;
color:#1f8bff;
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
{data["personal"]["cash"]} ₽
</div>

</div>

<div class="sub-box">

<div class="sub-title">
💳 Карта
</div>

<div class="sub-value">
{data["personal"]["card"]} ₽
</div>

</div>

</div>

</div>

<div class="card">

<div class="section-title">
⚡ Быстрые действия
</div>

<div class="quick-actions">

<div class="action-btn">
<i class="fa-solid fa-plus"></i>
Доход
</div>

<div class="action-btn">
<i class="fa-solid fa-minus"></i>
Расход
</div>

<div class="action-btn">
<i class="fa-solid fa-arrow-right-arrow-left"></i>
Перевод
</div>

<div class="action-btn">
<i class="fa-solid fa-chart-pie"></i>
Аналитика
</div>

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

<div class="tabs">

<button
type="button"
class="tab active-tab"
onclick="selectType('income')"
id="incomeBtn"
>
📈 Доход
</button>

<button
type="button"
class="tab"
onclick="selectType('expense')"
id="expenseBtn"
>
📉 Расход
</button>

</div>

<input
type="hidden"
name="type"
id="typeInput"
value="income"
>

<select
class="input"
name="account"
>

<option value="personal">
👤 Личный счет
</option>

<option value="business">
💼 Бизнес счет
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
class="input amount-input"
type="number"
step="0.01"
name="amount"
placeholder="0 ₽"
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

<option value="Бизнес">
🏢 Бизнес
</option>

<option value="Подписки">
📱 Подписки
</option>

<option value="Инвестиции">
📈 Инвестиции
</option>

<option value="Другое">
📦 Другое
</option>

</select>

<div class="fast-categories">

<div class="fast-category">
🍔 Еда
</div>

<div class="fast-category">
🚕 Такси
</div>

<div class="fast-category">
🛒 Магазин
</div>

<div class="fast-category">
🎮 Игры
</div>

<div class="fast-category">
💊 Аптека
</div>

<div class="fast-category">
📱 Подписки
</div>

</div>

<button
class="button"
type="submit"
>
Сохранить операцию
</button>

</form>

</div>

<div class="card ai-card">

<div class="section-title">
🤖 AI Анализ
</div>

<div>
• Расходы на кафе выросли<br>
• Ты сохранил 18% дохода<br>
• Самая большая категория — Продукты
</div>

</div>

<div class="card">

<div class="section-title">
🎯 Финансовая цель
</div>

<div>
MacBook Pro
<br><br>
12 500 / 30 000 ₽
</div>

<div class="goal-bar">

<div class="goal-progress"></div>

</div>

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

<canvas id="expenseChart"></canvas>

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
data-target="history-section"
>

<i class="fa-solid fa-clock"></i>
История

</div>

<div
class="nav-item"
data-target="business-section"
>

<i class="fa-solid fa-building"></i>
Бизнес

</div>

</div>

<script>

function selectType(type){

const incomeBtn =
document.getElementById(
"incomeBtn"
);

const expenseBtn =
document.getElementById(
"expenseBtn"
);

const typeInput =
document.getElementById(
"typeInput"
);

if(type === "income"){

incomeBtn.classList.add(
"active-tab"
);

expenseBtn.classList.remove(
"active-tab"
);

typeInput.value = "income";

}else{

expenseBtn.classList.add(
"active-tab"
);

incomeBtn.classList.remove(
"active-tab"
);

typeInput.value = "expense";

}

}

const ctx =
document.getElementById(
'expenseChart'
);

new Chart(ctx, {

type:'doughnut',

data: {

labels: {labels},

datasets:[{

data:{values},

backgroundColor:[
'#1f8bff',
'#34c759',
'#ff9500',
'#ff3b30',
'#6c63ff'
],

borderWidth:0

}]

}

});

const navItems =
document.querySelectorAll(
'.nav-item'
);

const sections =
document.querySelectorAll(
'.section'
);

navItems.forEach(item => {

item.addEventListener(
'click',
() => {

navItems.forEach(nav => {
nav.classList.remove(
'active'
);
});

item.classList.add(
'active'
);

sections.forEach(section => {
section.classList.remove(
'active-section'
);
});

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

});

});

</script>

</body>

</html>

"""


# ================= ADD OPERATION =================

@app.route("/add_operation", methods=["POST"])
def add_operation():

    data = load_data()

    account = request.form.get(
        "account"
    )

    type_op = request.form.get(
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
    ) or "Другое"

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

    data[account]["history"].append({

        "type": type_op,
        "amount": amount,
        "category": category,
        "wallet": wallet,
        "date": str(datetime.now())

    })

    save_data(data)

    return redirect("/")


# ================= TELEGRAM =================

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
