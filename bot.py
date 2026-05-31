import telebot
from telebot import types
import json
import os

TOKEN = "8921235792:AAGYIAMNnIuKoPv3RsmRpOn-28bx0BqpaK4"

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "finance.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "card": 105.98,
        "cash": 57.93,
        "transactions": [],
        "debts": {
            "Красная карта": 2000,
            "Овердрафт": 600,
            "МТС Деньги": 360
        }
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

@bot.message_handler(commands=["start"])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add("💸 Расход")
    markup.add("💰 Баланс")
    markup.add("📋 Долги")

    bot.send_message(
        message.chat.id,
        "Sage Finance Bot запущен",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "💰 Баланс")
def balance(message):

    text = f"""
Карта: {data["card"]:.2f} р
Наличные: {data["cash"]:.2f} р
"""

    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "📋 Долги")
def debts(message):

    txt = "Долги:\\n\\n"

    for name, amount in data["debts"].items():
        txt += f"{name}: {amount} р\\n"

    bot.send_message(message.chat.id, txt)

@bot.message_handler(func=lambda m: m.text == "💸 Расход")
def ask_expense(message):

    bot.send_message(
        message.chat.id,
        "Введи расход так:\\nПродукты 12.5 карта"
    )

@bot.message_handler(func=lambda m: True)
def parse_expense(message):

    try:

        parts = message.text.split()

        if len(parts) < 3:
            return

        title = parts[0]
        amount = float(parts[1])
        method = parts[2].lower()

        tx = {
            "title": title,
            "amount": amount,
            "method": method
        }

        data["transactions"].insert(0, tx)

        if "карт" in method:
            data["card"] -= amount
        else:
            data["cash"] -= amount

        save_data(data)

        bot.send_message(
            message.chat.id,
            f"Добавлено: {title} {amount} р"
        )

    except:
        pass

bot.infinity_polling()
