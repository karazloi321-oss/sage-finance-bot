from flask import Flask, request, redirect
import telebot
from telebot import types
import threading
import time
import os
import json
from datetime import datetime

TOKEN = os.getenv("TOKEN")

if not TOKEN:

    raise Exception(
        "TOKEN environment variable not found"
    )

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "data.json"

# =====================================================
# DEFAULT DATA
# =====================================================

DEFAULT_DATA = {

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

    "goals": [],

    "settings": {
        "currency": "₽"
    },

    "income_categories": [
        "💼 Зарплата",
        "🚀 Бизнес",
        "🎁 Подарок",
        "💸 Возврат",
        "📈 Инвестиции"
    ],

    "expense_categories": [
        "🛒 Продукты",
        "🍔 Кафе",
        "🚕 Транспорт",
        "🎮 Развлечения",
        "💊 Здоровье",
        "📱 Подписки",
        "🏠 Дом",
        "📦 Другое"
    ]

}

# =====================================================
# INIT
# =====================================================

if not os.path.exists(DATA_FILE):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            DEFAULT_DATA,
            f,
            ensure_ascii=False,
            indent=4
        )

# =====================================================
# HELPERS
# =====================================================

def save_data(data):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


def load_data():

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

    except:

        save_data(DEFAULT_DATA)

        return DEFAULT_DATA

    if "settings" not in data:

        data["settings"] = {
            "currency": "₽"
        }

    if "income_categories" not in data:

        data["income_categories"] = []

    if "expense_categories" not in data:

        data["expense_categories"] = []

    return data


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


def calculate_income(history):

    total = 0

    for item in history:

        if item["type"] == "income":

            total += item["amount"]

    return total


def calculate_expense(history):

    total = 0

    for item in history:

        if item["type"] == "expense":

            total += item["amount"]

    return total


def monthly_stats(history):

    months = {}

    for item in history:

        try:

            month = item["date"][:7]

            if month not in months:

                months[month] = 0

            if item["type"] == "expense":

                months[month] += item["amount"]

        except:

            pass

    return months


def get_ai_advice(
    income,
    expense,
    savings
):

    if expense > income:

        return "Расходы превышают доходы"

    if savings < income * 0.1:

        return "Увеличь накопления"

    return "Финансы стабильны"

# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    data = load_data()

    currency = data["settings"]["currency"]

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

    all_history = sorted(

        all_history,

        key=lambda x: x.get(
            "timestamp",
            0
        ),

        reverse=True

    )

    income_total = calculate_income(
        all_history
    )

    expense_total = calculate_expense(
        all_history
    )

    debt_total = 0

    for debt in data["debts"]:

        debt_total += debt["amount"]

    ai_text = get_ai_advice(

        income_total,
        expense_total,
        savings_total

    )

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

    monthly = monthly_stats(
        all_history
    )

    month_labels = list(
        monthly.keys()
    )

    month_values = list(
        monthly.values()
    )

    top_category = "Нет данных"

    if personal_stats:

        top_category = max(

            personal_stats,

            key=personal_stats.get

        )

    finance_score = 100

    if expense_total > income_total:

        finance_score -= 35

    if savings_total < income_total * 0.1:

        finance_score -= 20

    if debt_total > total_all * 0.5:

        finance_score -= 25

    if finance_score < 0:

        finance_score = 0

    history_html = ""

    for item in all_history[:30]:

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
                        {item["date"]}
                    </div>

                </div>

            </div>

            <div style="text-align:right;">

                <div
                class="history-amount"
                style="color:{color};"
                >
                    {item["amount"]} {currency}
                </div>

                <a
                href="/delete_operation/{item['id']}"
                class="delete-btn"
                >
                    Удалить
                </a>

            </div>

        </div>

        """

    debts_html = ""

    for index, debt in enumerate(
        reversed(data["debts"])
    ):

        real_index = (
            len(data["debts"]) - 1
        ) - index

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

            <div style="text-align:right;">

                <div class="history-amount">
                    {debt["amount"]} {currency}
                </div>

                <a
                href="/delete_debt/{real_index}"
                class="delete-btn"
                >
                    Вернуть
                </a>

            </div>

        </div>

        """
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
                    {goal["saved"]} / {goal["target"]} {currency}
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

<title>Sage Finance</title>

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
min-height:100vh;
-webkit-overflow-scrolling:touch;
}}

.container{{
max-width:760px;
margin:auto;
padding:20px;
padding-bottom:120px;
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
font-size:26px;
font-weight:900;
}}

.section-title{{
font-size:24px;
font-weight:900;
margin-bottom:18px;
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

.delete-btn{{
display:inline-block;
margin-top:6px;
font-size:12px;
color:#ff7d7d;
text-decoration:none;
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

.score-circle{{
width:180px;
height:180px;
margin:30px auto;
border-radius:50%;
background:linear-gradient(
135deg,
#6d8ea6,
#9bb6c9
);
display:flex;
flex-direction:column;
align-items:center;
justify-content:center;
}}

.score-number{{
font-size:52px;
font-weight:900;
}}

.score-label{{
margin-top:6px;
opacity:0.8;
}}

.search-input{{
width:100%;
padding:18px;
border:none;
border-radius:22px;
background:#222d40;
color:white;
margin-bottom:14px;
font-size:16px;
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
{total_all} {currency}
</div>

</div>

<div class="stats-grid">

<div class="stat-box">

<div class="stat-title">
📈 Доходы
</div>

<div class="stat-value">
{income_total} {currency}
</div>

</div>

<div class="stat-box">

<div class="stat-title">
📉 Расходы
</div>

<div class="stat-value">
{expense_total} {currency}
</div>

</div>

<div class="stat-box">

<div class="stat-title">
💎 Накопления
</div>

<div class="stat-value">
{savings_total} {currency}
</div>

</div>

<div class="stat-box">

<div class="stat-title">
🔥 Топ расход
</div>

<div class="stat-value" style="font-size:18px;">
{top_category}
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

<div class="card">

<div class="section-title">
🧠 AI Финансовый рейтинг
</div>

<div class="score-circle">

<div class="score-number">
{finance_score}
</div>

<div class="score-label">
из 100
</div>

</div>

</div>

<div class="card">

<div class="section-title">
💸 Операции
</div>

<form
action="/add_operation"
method="POST"
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

<option>🛒 Продукты</option>
<option>🍔 Кафе</option>
<option>🚕 Транспорт</option>
<option>🎮 Развлечения</option>
<option>💊 Здоровье</option>
<option>📱 Подписки</option>
<option>🏠 Дом</option>
<option>📦 Другое</option>

</select>

<button
class="button"
type="submit"
>
Сохранить
</button>

</form>

</div>

<div class="card">

<div class="section-title">
🕓 История
</div>

<input
type="text"
class="search-input"
placeholder="Поиск операций..."
onkeyup="searchHistory(this.value)"
>

{history_html}

</div>

<div class="card">

<div class="section-title">
💸 Долги
</div>

{debts_html}

</div>

<div class="card">

<div class="section-title">
🎯 Цели
</div>

{goals_html}

</div>

</div>

<script>

function searchHistory(value){{

const items =
document.querySelectorAll(
'.history-item'
);

items.forEach(item => {{

if(
item.innerText
.toLowerCase()
.includes(
value.toLowerCase()
)
){{

item.style.display = 'flex';

}}else{{

item.style.display = 'none';

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

    try:

        amount = float(
            request.form.get(
                "amount",
                0
            )
        )

    except:

        amount = 0

    if amount <= 0:

        return redirect("/")

    category = request.form.get(
        "category"
    )

    if op_type == "expense":

        if data[account][wallet] < amount:

            return redirect("/")

    operation_id = str(
        int(time.time() * 1000)
    )

    if op_type == "income":

        data[account][wallet] += amount

    else:

        data[account][wallet] -= amount

        data[account]["expenses"].append({

            "id": operation_id,
            "amount": amount,
            "category": category,
            "wallet": wallet,
            "date": datetime.now().strftime(
                "%d.%m.%Y %H:%M"
            )

        })

    data[account]["history"].append({

        "id": operation_id,
        "type": op_type,
        "amount": amount,
        "category": category,
        "wallet": wallet,
        "date": datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        ),
        "timestamp": time.time()

    })

    save_data(data)

    return redirect("/")
  # =====================================================
# DELETE OPERATION
# =====================================================

@app.route(
    "/delete_operation/<operation_id>"
)
def delete_operation(operation_id):

    data = load_data()

    for section in ["personal", "business"]:

        new_history = []

        for item in data[section]["history"]:

            if item["id"] == operation_id:

                amount = item["amount"]
                wallet = item["wallet"]

                if item["type"] == "income":

                    data[section][wallet] -= amount

                elif item["type"] == "expense":

                    data[section][wallet] += amount

            else:

                new_history.append(item)

        data[section]["history"] = new_history

        data[section]["expenses"] = [

            item for item in
            data[section]["expenses"]

            if item["id"] != operation_id

        ]

    save_data(data)

    return redirect("/")

# =====================================================
# TRANSFER SAVINGS
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

    try:

        amount = float(
            request.form.get(
                "amount",
                0
            )
        )

    except:

        amount = 0

    if amount <= 0:

        return redirect("/")

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

    try:

        amount = float(
            request.form.get(
                "amount",
                0
            )
        )

    except:

        amount = 0

    if amount <= 0:

        return redirect("/")

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
# DELETE DEBT
# =====================================================

@app.route("/delete_debt/<int:index>")
def delete_debt(index):

    data = load_data()

    try:

        del data["debts"][index]

        save_data(data)

    except:

        pass

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

    try:

        target = float(
            request.form.get(
                "target",
                0
            )
        )

    except:

        target = 0

    if target <= 0:

        return redirect("/")

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
