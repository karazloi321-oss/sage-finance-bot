```python id="9g3kfm"
import telebot
from telebot import types
import json
import os
import time
from datetime import datetime

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "finance.json"

PIN_CODE = "1111"


FAST_AMOUNTS = [
    "5",
    "10",
    "20",
    "50"
]


CATEGORIES = {
    "🍔 Продукты": "Продукты",
    "🚌 Транспорт": "Транспорт",
    "☕ Кафе": "Кафе",
    "🏠 Дом": "Для дома",
    "🎮 Игры": "Игры",
    "📱 Связь": "Связь"
}


def load_data():

    if os.path.exists(DATA_FILE):

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "card": 0,
        "cash": 0,
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

authorized_users = set()

user_states = {}


def main_keyboard():

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add("➕ Добавить расход")
    markup.add("💰 Баланс", "📊 Аналитика")
    markup.add("🧾 История", "📋 Долги")
    markup.add("📅 Месяц")

    return markup


@bot.message_handler(commands=["start"])
def start(message):

    bot.send_message(
        message.chat.id,
        "🔐 Введите PIN-код"
    )


@bot.message_handler(func=lambda m: str(m.chat.id) not in authorized_users)
def auth(message):

    if message.text == PIN_CODE:

        authorized_users.add(str(message.chat.id))

        bot.send_message(
            message.chat.id,
            "✅ Sage Finance активирован",
            reply_markup=main_keyboard()
        )

    else:

        bot.send_message(
            message.chat.id,
            "❌ Неверный PIN"
        )


@bot.message_handler(func=lambda m: m.text == "➕ Добавить расход")
def choose_category(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for cat in CATEGORIES.keys():
        markup.add(cat)

    markup.add("⬅️ Назад")

    bot.send_message(
        message.chat.id,
        "Выберите категорию:",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text in CATEGORIES.keys())
def choose_amount(message):

    category = CATEGORIES[message.text]

    user_states[message.chat.id] = {
        "category": category
    }

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for amount in FAST_AMOUNTS:
        markup.add(f"{amount} р")

    markup.add("⬅️ Назад")

    bot.send_message(
        message.chat.id,
        f"Категория: {category}\nВведите сумму:",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: "р" in m.text)
def save_fast_expense(message):

    if message.chat.id not in user_states:
        return

    try:

        amount = float(
            message.text.replace("р", "").strip()
        )

        category = user_states[message.chat.id]["category"]

        transaction = {
            "title": category,
            "amount": amount,
            "method": "карта",
            "category": category,
            "type": "expense",
            "date": datetime.now().strftime("%d.%m.%Y")
        }

        data["transactions"].insert(0, transaction)

        data["card"] -= amount

        save_data(data)

        del user_states[message.chat.id]

        bot.send_message(
            message.chat.id,
            f"✅ Добавлено\n\n"
            f"{category}: {amount} р",
            reply_markup=main_keyboard()
        )

    except:

        bot.send_message(
            message.chat.id,
            "⚠️ Ошибка суммы"
        )


@bot.message_handler(func=lambda m: m.text == "💰 Баланс")
def balance(message):

    total = data["card"] + data["cash"]

    text = (
        f"💳 Карта: {data['card']:.2f} р\n"
        f"💵 Наличные: {data['cash']:.2f} р\n\n"
        f"💰 Всего: {total:.2f} р"
    )

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "📋 Долги")
def debts(message):

    text = "📋 Долги:\n\n"

    total = 0

    for name, amount in data["debts"].items():

        text += f"{name}: {amount} р\n"

        total += amount

    text += f"\nОбщий долг: {total} р"

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "🧾 История")
def history(message):

    text = "🧾 Последние операции:\n\n"

    for tx in data["transactions"][:15]:

        text += (
            f"{tx['date']} | "
            f"{tx['category']} | "
            f"{tx['amount']} р\n"
        )

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "📊 Аналитика")
def analytics(message):

    stats = {}

    for tx in data["transactions"]:

        if tx["type"] == "expense":

            category = tx["category"]

            stats[category] = (
                stats.get(category, 0)
                + tx["amount"]
            )

    sorted_stats = sorted(
        stats.items(),
        key=lambda x: x[1],
        reverse=True
    )

    text = "📊 Топ расходов:\n\n"

    for cat, amount in sorted_stats:

        text += f"{cat}: {round(amount, 2)} р\n"

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "📅 Месяц")
def month_stats(message):

    income = 0
    expense = 0

    current_month = datetime.now().strftime("%m.%Y")

    for tx in data["transactions"]:

        if current_month in tx["date"]:

            if tx["type"] == "income":
                income += tx["amount"]
            else:
                expense += tx["amount"]

    text = (
        f"📅 Месяц\n\n"
        f"💰 Доходы: {income:.2f} р\n"
        f"💸 Расходы: {expense:.2f} р\n"
        f"📉 Итог: {(income-expense):.2f} р"
    )

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "⬅️ Назад")
def back(message):

    bot.send_message(
        message.chat.id,
        "Главное меню",
        reply_markup=main_keyboard()
    )


bot.remove_webhook()

time.sleep(3)

bot.infinity_polling(
    timeout=30,
    long_polling_timeout=30,
    skip_pending=True
)
```
