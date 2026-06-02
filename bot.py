from flask import Flask
import telebot
from telebot import types
import threading
import time
import os

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)

bot = telebot.TeleBot(TOKEN)


@app.route("/", methods=["GET", "HEAD"])
def home():

    return """

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

            body{
                margin:0;
                background:#0f1115;
                color:white;
                font-family:sans-serif;
            }

            .container{
                padding:20px;
                max-width:500px;
                margin:auto;
            }

            .card{
                background:#1a1d24;
                border-radius:24px;
                padding:24px;
                margin-top:20px;
            }

            .title{
                font-size:32px;
                font-weight:bold;
            }

            .balance-card{
                background:linear-gradient(
                    135deg,
                    #1f8bff,
                    #6c63ff
                );

                border-radius:24px;
                padding:24px;
                margin-top:20px;
            }

            .balance-label{
                opacity:0.8;
                font-size:14px;
            }

            .balance{
                font-size:42px;
                font-weight:bold;
                margin-top:10px;
            }

            .button{
                width:100%;
                border:none;
                padding:16px;
                border-radius:18px;
                background:#4caf50;
                color:white;
                font-size:16px;
                font-weight:bold;
                margin-top:14px;
            }

        </style>

    </head>

    <body>

        <div class="container">

            <div class="title">
                Sage Finance
            </div>

            <div class="balance-card">

                <div class="balance-label">
                    Общий баланс
                </div>

                <div class="balance">
                    0 ₽
                </div>

            </div>

            <div class="card">

                <h2>
                    🚀 Финансовый ассистент
                </h2>

                <p>
                    Добавляй доходы,
                    расходы и следи
                    за балансом.
                </p>

                <button class="button">
                    ➕ Добавить операцию
                </button>

            </div>

        </div>

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
