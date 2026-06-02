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


data = load_data()


@app.route("/", methods=["GET", "HEAD"])
def home():

    if request.method == "HEAD":
        return "", 200

    balance = data.get("balance", 0)

    return f"""

    <html>

    <head>

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1"
        >

        <style>

            body{{
                background:#d9e5d6;
                font-family:sans-serif;
                padding:20px;
            }}

            .card{{
                background:white;
                border-radius:24px;
                padding:25px;
                max-width:450px;
                margin:auto;
            }}

            .balance{{
                font-size:42px;
                font-weight:bold;
                text-align:center;
                margin:20px 0;
            }}

            button{{
                width:100%;
                padding:18px;
                border:none;
                border-radius:18px;
                background:#7c9b76;
                color:white;
                font-size:18px;
                margin-top:12px;
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

            <button onclick="addIncome()">
                ➕ Доход +100
            </button>

            <button onclick="addExpense()">
                ➖ Расход -100
            </button>

        </div>

        <a href="/income">
    <button>
        ➕ Доход +100
    </button>
</a>

<a href="/expense">
    <button>
        ➖ Расход -100
    </button>
</a>

    </body>

    </html>
    """


@app.route("/income")
def income():

    global data

    data["balance"] += 100

    save_data(data)

    return "ok"


@app.route("/expense")
def expense():

    global data

    data["balance"] -= 100

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
            )
        )
    )
