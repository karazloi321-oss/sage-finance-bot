from flask import Flask
import telebot
from telebot import types
import threading
import os

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)

bot = telebot.TeleBot(TOKEN)


@app.route("/")
def home():

    return """
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

            body{

                margin:0;
                padding:20px;

                background:#d9e5d6;

                font-family:sans-serif;
            }

            .card{

                background:white;

                border-radius:24px;

                padding:25px;

                max-width:400px;

                margin:auto;

                box-shadow:0 4px 12px rgba(0,0,0,0.1);
            }

            h1{

                text-align:center;
            }

            .balance{

                font-size:42px;

                font-weight:bold;

                text-align:center;

                margin:25px 0;
            }

            button{

                width:100%;

                border:none;

                border-radius:18px;

                padding:18px;

                margin-top:12px;

                background:#7c9b76;

                color:white;

                font-size:20px;
            }

        </style>

    </head>

    <body>

        <div class="card">

            <h1>Sage Finance</h1>

            <div
                class="balance"
                id="balance"
            >
                0 ₽
            </div>

            <button onclick="minus(10)">
                -10 ₽
            </button>

            <button onclick="minus(50)">
                -50 ₽
            </button>

            <button onclick="minus(100)">
                -100 ₽
            </button>

        </div>

        <script>

            let balance = 0

            const balanceElement =
                document.getElementById(
                    "balance"
                )

            function updateBalance(){

                balanceElement.innerHTML =
                    balance + " ₽"
            }

            function minus(amount){

                balance -= amount

                updateBalance()
            }

        </script>

    </body>

    </html>
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

    bot.remove_webhook()

    bot.infinity_polling(
        skip_pending=True
    )


if __name__ == "__main__":

    threading.Thread(
        target=run_bot
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
