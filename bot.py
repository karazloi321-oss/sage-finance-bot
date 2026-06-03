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
            },

            "debts": [],

            "goals": [],

            "budgets": {
                "Продукты": 10000,
                "Кафе": 5000,
                "Транспорт": 4000
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

    return stats


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

    expense_stats = get_expense_stats(
        data["personal"]["expenses"]
    )

    labels = list(
        expense_stats.keys()
    )

    values = list(
        expense_stats.values()
    )

    # ================= HISTORY =================

    history_html = ""

    for item in reversed(
        data["personal"]["history"][-15:]
    ):

        icon = "📈" if item["type"] == "income" else "📉"

        color = "#7db1d4" if item["type"] == "income" else "#ff7d7d"

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
                        {item["wallet"]}
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

    # ================= DEBTS =================

    debts_html = ""

    for debt in reversed(
        data["debts"]
    ):

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
                        {debt["date"]}
                    </div>

                </div>

            </div>

            <div class="history-amount">
                {debt["amount"]} ₽
            </div>

        </div>

        """

    # ================= GOALS =================

    goals_html = ""

    for goal in data["goals"]:

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

    # ================= BUDGETS =================

    budgets_html = ""

    for category, limit in data["budgets"].items():

        spent = expense_stats.get(
            category,
            0
        )

        progress = min(
            int(
                (spent / limit) * 100
            ),
            100
        )

        budgets_html += f"""

        <div class="goal-card">

            <div class="goal-top">

                <div>
                    💳 {category}
                </div>

                <div>
                    {spent} / {limit} ₽
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
letter-spacing:-1px;
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

.quick-actions{{
display:flex;
gap:12px;
overflow-x:auto;
margin-bottom:18px;
}}

.quick-btn{{
min-width:95px;
background:#1a2230;
padding:18px 14px;
border-radius:24px;
text-align:center;
}}

.quick-btn i{{
font-size:24px;
display:block;
margin-bottom:10px;
color:#9bb6c9;
}}

.quick-btn span{{
font-size:13px;
font-weight:800;
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

.tabs{{
display:flex;
gap:10px;
margin-bottom:14px;
}}

.tab{{
flex:1;
padding:16px;
border:none;
border-radius:20px;
background:#222d40;
color:white;
font-size:15px;
font-weight:900;
}}

.active-tab{{
background:linear-gradient(
135deg,
#6d8ea6,
#9bb6c9
);
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

.amount-input{{
font-size:34px;
font-weight:900;
text-align:center;
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
}}

.nav-item{{
display:flex;
flex-direction:column;
align-items:center;
font-size:11px;
opacity:0.55;
cursor:pointer;
}}

.nav-item i{{
font-size:22px;
margin-bottom:6px;
}}

.active{{
opacity:1;
color:#9bb6c9;
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

<div class="quick-actions">

<div class="quick-btn">
<i class="fa-solid fa-plus"></i>
<span>Доход</span>
</div>

<div class="quick-btn">
<i class="fa-solid fa-minus"></i>
<span>Расход</span>
</div>

<div class="quick-btn">
<i class="fa-solid fa-building"></i>
<span>Бизнес</span>
</div>

<div class="quick-btn">
<i class="fa-solid fa-wallet"></i>
<span>Бюджет</span>
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

<canvas id="expenseChart"></canvas>

{budgets_html}

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
method="post"
action="/add_goal"
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
method="post"
action="/add_debt"
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
data-target="business-section"
>
<i class="fa-solid fa-building"></i>
Бизнес
</div>

<div
class="nav-item"
data-target="debts-section"
>
<i class="fa-solid fa-money-bill-wave"></i>
Долги
</div>

</div>

<script>

function selectType(type) {

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

if(type === "income") {

incomeBtn.classList.add(
"active-tab"
);

expenseBtn.classList.remove(
"active-tab"
);

typeInput.value = "income";

} else {

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
'#6d8ea6',
'#9bb6c9',
'#7db1d4',
'#5d738a',
'#bfd3e2'
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

}

);

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


# ================= ADD DEBT =================

@app.route("/add_debt", methods=["POST"])
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


# ================= ADD GOAL =================

@app.route("/add_goal", methods=["POST"])
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
