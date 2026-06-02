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
    <h1>Sage Finance работает 🚀</h1>
    <p>Flask работает нормально</p>
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
        text="📱 Открыть приложение",
        web_app=web_app
    )

    markup.add(button)

    bot.send_message(
        message.chat.id,
        "Sage Finance готов 🚀",
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
