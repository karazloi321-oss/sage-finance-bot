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

    history_html = ""

    for item in reversed(
        data.get(
            "transactions",
            []
        )[-10:]
    ):

        history_html += f"""

        <div class="item">

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
                max-width:450px;
                margin:auto;
            }}

            h1{{
                text-align:center;
            }}

            .balance{{
                font-size:42px;
                font-weight:bold;
                text-align:center;
                margin:25px 0;
            }}

            form{{
                margin-top:15px;
            }}

            input{{
                width:100%;
                padding:18px;
                border:none;
                border-radius:18px;
                box-sizing:border-box;
                font-size:18px;
            }}

            button{{
                width:100%;
                padding:18px;
                border:none;
                border-radius:18px;
                background:#7c9b76;
                color:white;
                font-size:18px;
                margin-top:10px;
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

            <h1>
                Sage Finance
            </h1>

            <div class="balance">

                {balance} ₽

            </div>

            <form action="/income">

                <input
                    type="number"
                    name="amount"
                    placeholder="Сумма дохода"
                    required
                >

                <button type="submit">

                    ➕ Добавить доход

                </button>

            </form>

            <form action="/expense">

                <input
                    type="number"
                    name="amount"
                    placeholder="Сумма расхода"
                    required
                >

                <button type="submit">

                    ➖ Добавить расход

                </button>

            </form>

            <h2>
                История
            </h2>

            {history_html}

        </div>

    </body>

    </html>
    """


@app.route("/income")
def income():

    global data

    amount = int(
        request.args.get(
            "amount",
            0
        )
    )

    data["balance"] += amount

    data["transactions"].append(
        f"➕ Доход: {amount} ₽"
    )

    save_data(data)

    return """
    <meta http-equiv="refresh" content="0; url=/">
    """


@app.route("/expense")
def expense():

    global data

    amount = int(
        request.args.get(
            "amount",
            0
        )
    )

    data["balance"] -= amount

    data["transactions"].append(
        f"➖ Расход: {amount} ₽"
    )

    save_data(data)

    return """
    <meta http-equiv="refresh" content="0; url=/">
    """


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
