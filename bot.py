from flask import Flask, render_template
import telebot
from telebot import types
import threading
import os

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@bot.message_handler(commands=["start"])
def start(message):

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    webapp = types.WebAppInfo(
        "https://ТВОЙ-RENDER-URL.onrender.com"
    )

    button = types.KeyboardButton(
        "📱 Открыть Sage Finance",
        web_app=webapp
    )

    markup.add(button)

    bot.send_message(
        message.chat.id,
        "🚀 Sage Finance",
        reply_markup=markup
    )
def run_bot():

    try:

        bot.remove_webhook()

        bot.infinity_polling(
            skip_pending=True
        )

    except Exception as e:

        print(e)


if __name__ == "__main__":

    threading.Thread(
        target=run_bot
    ).start()
