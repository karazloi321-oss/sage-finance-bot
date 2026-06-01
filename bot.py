from flask import Flask
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

        return {
            "balance": 0,
            "transactions": []
        }

    with open(DATA_FILE, "r") as f:

        return json.load(f)


def save_data(data):

    with open(DATA_FILE, "w") as f:

        json.dump(data, f)


data = load_data()


@app.route("/")
def home():

    history_html = ""

    for item in reversed(data["transactions"][-10:]):

        history_html += f"""
        <div class='item'>
            {item}
        </div>
        """

    return f"""
    <!DOCTYPE html>

    <html lang="ru">

    <head>

        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>Sage Finance</title>

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
                max-width:450px;
                margin:auto;
            }}

            h1{{
                text-align:center;
            }}

            .balance{{
                font-size:42px;
                text-align:center;
                font-weight:bold;
                margin:25px 0;
            }}

            button{{
                width:100%;
                border:none;
                border-radius:18px;
                padding:18px;
                margin-top:12px;
                background:#7c9b76;
                color:white;
                font-size:18px;
            }}

            input{{
                width:100%;
                border:none;
                border-radius:18px;
                padding:18px;
                margin-top:12px;
                box-sizing:border-box;
                font-size:18px;
            }}

            .history{{
                margin-top:25px;
            }}

            .item{{
                background:#f2f2f2;
                padding:12px;
                border-radius:12px;
                margin-top:10px;
            }}

        </style>

    </head>

    <body>

        <div class="card">

            <h1>Sage Finance</h1>

            <div class="balance">
                {data["balance"]} ₽
            </div>

            <input
                type="number"
                id="amount"
                placeholder="Сумма"
            >

            <button onclick="addIncome()">
                ➕ Доход
            </button>

            <button onclick="addExpense()">
                ➖ Расход
            </button>

            <div class="history">

                <h2>
                    История
                </h2>

                {history_html}

            </div>

        </div>

        <script>

            async function addIncome(){{

                const amount =
                    document.getElementById(
                        "amount"
                    ).value

                if(!amount) return

                await fetch(
                    "/income/" + amount
                )

                location.reload()
            }}

            async function addExpense(){{

                const amount =
                    document.getElementById(
                        "amount"
                    ).value

                if(!amount) return

                await fetch(
                    "/expense/" + amount
                )

                location.reload()
            }}

        </script>

    </body>

    </html>
    """


@app.route("/income/<amount>")
def income(amount):

    amount = int(amount)

    data["balance"] += amount

    data["transactions"].append(
        f"➕ Доход: {amount} ₽"
    )

    save_data(data)

    return "ok"


@app.route("/expense/<amount>")
def expense(amount):

    amount = int(amount)

    data["balance"] -= amount

    data["transactions"].append(
        f"➖ Расход: {amount} ₽"
    )

    save_data(data)

    return "ok"


@bot.message_handler(commands=["start"])
def start(message):

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
