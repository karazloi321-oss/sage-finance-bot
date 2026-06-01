from flask import Flask, render_template
import telebot
from telebot import types
import threading
import os

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@bot.message_handler(commands=["start"])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    webapp = types.WebAppInfo(
        "https://YOUR-RAILWAY-URL.up.railway.app"
    )

    button = types.KeyboardButton(
        "📱 Открыть Sage Finance",
        web_app=webapp
    )

    markup.add(button)

    bot.send_message(
        message.chat.id,
        "🚀 Sage Finance Mini App",
        reply_markup=markup
    )


def run_bot():

    bot.remove_webhook()

    bot.infinity_polling()


threading.Thread(target=run_bot).start()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
