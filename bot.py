from flask import Flask, request
import telebot
from telebot import types
import os
import threading
import time
import json

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "finance.json"


def load_data():

    if not os.path.exists(DATA_FILE):

        default_data = {
            "balance": 0,
            "transactions": []
        }

        with open(DATA_FILE, "w") as f:

            json.dump(default_data, f)

        return default_data

    try:

        with open(DATA_FILE, "r") as f:

            return json.load(f)

    except:

        return {
            "balance": 0,
            "transactions": []
        }


def save_data(data):

    with open(DATA_FILE, "w") as f:

        json.dump(data, f)

    return default_data

try:

    with open(DATA_FILE, "r") as f:

        return json.load(f)

except:

    return {
        "balance": 0,
        "transactions": []
    }

def save_data(data):

with open(DATA_FILE, "w") as f:

    json.dump(data, f)

data = load_data()

@app.route("/", methods=["GET", "HEAD"])def home():

if request.method == "HEAD":

    return "", 200

balance = data.get("balance", 0)

transactions = data.get(
    "transactions",
    []
)

income_total = 0
expense_total = 0

history_html = ""

for item in reversed(transactions[-15:]):

    if item["type"] == "income":

        income_total += item["amount"]

        color = "#2e7d32"
        emoji = "➕"

    else:

        expense_total += item["amount"]

        color = "#c62828"
        emoji = "➖"

    history_html += f"""

    <div class="item">

        <div>
            {emoji}
            {item["category"]}
        </div>

        <div style="
            color:{color};
            font-weight:bold;
        ">
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

    <style>

        body{{
            margin:0;
            padding:20px;
            background:#d9e5d6;
            font-family:sans-serif;
        }}

        .card{{
            background:white;
            border-radius:24px;
            padding:25px;
            max-width:480px;
            margin:auto;
            box-shadow:0 4px 12px rgba(0,0,0,0.1);
        }}

        h1{{
            text-align:center;
            margin-top:0;
        }}

        .balance{{
            font-size:42px;
            font-weight:bold;
            text-align:center;
            margin:25px 0;
        }}

        .stats{{
            display:flex;
            gap:10px;
            margin-bottom:20px;
        }}

        .stat{{
            flex:1;
            padding:14px;
            border-radius:16px;
            color:white;
            text-align:center;
            font-weight:bold;
        }}

        .income{{
            background:#2e7d32;
        }}

        .expense{{
            background:#c62828;
        }}

        input, select{{
            width:100%;
            padding:18px;
            border:none;
            border-radius:18px;
            margin-top:12px;
            box-sizing:border-box;
            font-size:18px;
        }}

        button{{
            width:100%;
            padding:18px;
            border:none;
            border-radius:18px;
            margin-top:12px;
            background:#7c9b76;
            color:white;
            font-size:18px;
        }}

        .item{{
            background:#f2f2f2;
            padding:14px;
            border-radius:14px;
            margin-top:10px;
            display:flex;
            justify-content:space-between;
            align-items:center;
        }}

    </style>

</head>

<body>

    <div class="card">

        <h1>
            Sage Finance
        </h1>

        <div class="balance">

            {balance} ₽

        </div>

        <div class="stats">

            <div class="stat income">

                Доход<br>
                {income_total} ₽

            </div>

            <div class="stat expense">

                Расход<br>
                {expense_total} ₽

            </div>

        </div>

        <input
            type="number"
            id="amount"
            placeholder="Сумма"
        >

        <select id="category">

            <option>
                🍔 Еда
            </option>

            <option>
                🚕 Транспорт
            </option>

            <option>
                🛍 Покупки
            </option>

            <option>
                🎮 Развлечения
            </option>

            <option>
                💼 Зарплата
            </option>

            <option>
                📦 Другое
            </option>

        </select>

        <button onclick="addIncome()">

            ➕ Добавить доход

        </button>

        <button onclick="addExpense()">

            ➖ Добавить расход

        </button>

        <h2>
            История
        </h2>

        {history_html}

    </div>

    <script>

        async function addIncome(){{

            const amount =
                document.getElementById(
                    "amount"
                ).value

            const category =
                document.getElementById(
                    "category"
                ).value

            if(!amount) return

            await fetch(
                `/income/${{amount}}/${{category}}`
            )

            location.reload()
        }}

        async function addExpense(){{

            const amount =
                document.getElementById(
                    "amount"
                ).value

            const category =
                document.getElementById(
                    "category"
                ).value

            if(!amount) return

            await fetch(
                `/expense/${{amount}}/${{category}}`
            )

            location.reload()
        }}

    </script>

</body>

</html>
"""

@app.route("/income//")def income(amount, category):

global data

amount = int(amount)

data["balance"] += amount

data["transactions"].append({
    "type": "income",
    "amount": amount,
    "category": category
})

save_data(data)

return "ok"

@app.route("/expense//")def expense(amount, category):

global data

amount = int(amount)

data["balance"] -= amount

data["transactions"].append({
    "type": "expense",
    "amount": amount,
    "category": category
})

save_data(data)

return "ok"

@bot.message_handler(commands=["start"])def start(message):

markup = types.ReplyKeyboardMarkup(
    resize_keyboard=True
)

web_app = types.WebAppInfo(
    "https://sage-finance.onrender.com/"
)

button = types.KeyboardButton(
    text="📱 Открыть Sage Finance",
    web_app=web_app
)

markup.add(button)

bot.send_message(
    message.chat.id,
    "🚀 Sage Finance готов",
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

if name == "main":

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
