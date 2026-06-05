from flask import Flask
import threading
import telebot
import os
import time

from core.logger import logger
from core.db import init_db

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

# =========================
# INIT DATABASE
# =========================

init_db()

# =========================
# HEALTHCHECK
# =========================

@app.route("/health")
def health():
    return {
        "status": "ok",
        "service": "sage-finance"
    }

# =========================
# HOME
# =========================

@app.route("/")
def home():
    return {
        "app": "Sage Finance",
        "status": "running"
    }

# =========================
# TELEGRAM
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    logger.info(f"START USER {message.chat.id}")

    bot.send_message(
        message.chat.id,
        "🏦 Sage Finance V9 работает"
    )

# =========================
# BOT LOOP
# =========================

def run_bot():

    while True:

        try:

            logger.info("BOT STARTED")

            bot.remove_webhook()

            bot.infinity_polling(
                timeout=30,
                long_polling_timeout=30,
                skip_pending=True
            )

        except Exception as e:

            logger.error(f"BOT ERROR: {e}")

            time.sleep(5)

# =========================
# START TELEGRAM THREAD
# =========================

telegram_thread = threading.Thread(
    target=run_bot,
    daemon=True
)

telegram_thread.start()

logger.info("APP STARTED")
