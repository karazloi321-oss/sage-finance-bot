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


# ================= WEB =================

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

        

    return f"""
        """

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
margin-bottom:20px;
}}

.logo{{
font-size:32px;
font-weight:900;
}}

.profile{{
width:52px;
height:52px;
border-radius:50%;
background:#1b2339;
display:flex;
align-items:center;
justify-content:center;
font-size:20px;
}}

.card{{
border-radius:30px;
padding:24px;
margin-top:20px;
background:#121a2b;
}}

.balance-card{{
background:linear-gradient(
135deg,
#1f8bff,
#6c63ff
);
}}

.balance{{
font-size:42px;
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
border-radius:20px;
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

.tabs{{
display:flex;
gap:10px;
margin-bottom:14px;
}}

.tab{{
flex:1;
padding:15px;
border:none;
border-radius:18px;
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
border-radius:18px;
margin-top:12px;
background:#1b2339;
color:white;
font-size:16px;
outline:none;
}}

.amount-input{{
font-size:30px;
font-weight:900;
text-align:center;
}}

.button{{
width:100%;
border:none;
padding:18px;
border-radius:20px;
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
gap:10px;
margin-top:16px;
}}

.fast-category{{
padding:14px;
background:#1b2339;
border-radius:16px;
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
border-radius:18px;
margin-top:14px;
}}

.history-left{{
display:flex;
align-items:center;
gap:14px;
}}

.history-icon{{
width:46px;
height:46px;
border-radius:14px;
background:#25304b;
display:flex;
align-items:center;
justify-content:center;
font-size:18px;
}}

.history-title{{
font-size:16px;
font-weight:800;
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
bottom:0;
left:0;
width:100%;
background:#111827;
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
opacity:0.6;
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

<div class="card balance-card">

<div>
💼 Бизнес баланс
</div>

<div class="balance">
{business_total} ₽
</div>

<div class="sub-balance">

<div class="sub-box">

<div class="sub-title">
💵 Наличные
</div>

<div class="sub-value">
{data["business"]["cash"]} ₽
</div>

</div>

<div class="sub-box">

<div class="sub-title">
💳 Карта
</div>

<div class="sub-value">
{data["business"]["card"]} ₽
</div>

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

<option value="Подписки">
📱 Подписки
</option>

<option value="Инвестиции">
📈 Инвестиции
</option>

<option value="Бизнес">
🏢 Бизнес
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

if(ctx){

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

}

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
