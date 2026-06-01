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

LOW_BALANCE = 50


EXPENSE_CATEGORIES = {
    "🍔 Продукты": "Продукты",
    "🚌 Транспорт": "Транспорт",
    "☕ Кафе": "Кафе",
    "🏠 Дом": "Для дома",
    "🎮 Игры": "Игры",
    "📱 Связь": "Связь"
}


INCOME_CATEGORIES = {
    "💼 Зарплата": "Зарплата",
    "💰 Доход": "Доход",
    "🎁 Подарок": "Подарок"
}


FAST_AMOUNTS = [
    "5",
    "10",
    "20",
    "50",
    "100"
]


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

    backup = f"backup_{datetime.now().strftime('%d_%m_%Y')}.json"

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(backup, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


data = load_data()

authorized_users = set()

user_states = {}


def main_keyboard():

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add("💸 Расход", "💰 Доход")
    markup.add("💳 Баланс", "📊 Аналитика")
    markup.add("🧾 История", "📋 Долги")
    markup.add("📅 Месяц", "📈 Сегодня")

    return markup


@bot.message_handler(commands=["start"])
def start(message):

    bot.send_message(
        message.chat.id,
        "🔐 Введите PIN"
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


@bot.message_handler(func=lambda m: m.text == "💸 Расход")
def expense_menu(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for cat in EXPENSE_CATEGORIES.keys():
        markup.add(cat)

    markup.add("⬅️ Назад")

    user_states[message.chat.id] = {
        "type": "expense"
    }

    bot.send_message(
        message.chat.id,
        "Выберите категорию расхода:",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "💰 Доход")
def income_menu(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for cat in INCOME_CATEGORIES.keys():
        markup.add(cat)

    markup.add("⬅️ Назад")

    user_states[message.chat.id] = {
        "type": "income"
    }

    bot.send_message(
        message.chat.id,
        "Выберите категорию дохода:",
        reply_markup=markup
    )


@bot.message_handler(
    func=lambda m:
    m.text in EXPENSE_CATEGORIES.keys()
    or m.text in INCOME_CATEGORIES.keys()
)
def choose_method(message):

    category = (
        EXPENSE_CATEGORIES.get(message.text)
        or INCOME_CATEGORIES.get(message.text)
    )

    user_states[message.chat.id]["category"] = category

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add("💳 Карта", "💵 Наличные")
    markup.add("⬅️ Назад")

    bot.send_message(
        message.chat.id,
        "Выберите счет:",
        reply_markup=markup
    )


@bot.message_handler(
    func=lambda m:
    m.text in ["💳 Карта", "💵 Наличные"]
)
def choose_amount(message):

    method = (
        "card"
        if "Карта" in message.text
        else "cash"
    )

    user_states[message.chat.id]["method"] = method

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for amount in FAST_AMOUNTS:
        markup.add(f"{amount} р")

    markup.add("⬅️ Назад")

    bot.send_message(
        message.chat.id,
        "Введите сумму:",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: "р" in m.text)
def save_transaction(message):

    if message.chat.id not in user_states:
        return

    try:

        amount = float(
            message.text.replace("р", "").strip()
        )

        state = user_states[message.chat.id]

        transaction = {
            "category": state["category"],
            "amount": amount,
            "method": state["method"],
            "type": state["type"],
            "date": datetime.now().strftime("%d.%m.%Y")
        }

        data["transactions"].insert(0, transaction)

        if state["type"] == "expense":

            if state["method"] == "card":
                data["card"] -= amount
            else:
                data["cash"] -= amount

        else:

            if state["method"] == "card":
                data["card"] += amount
            else:
                data["cash"] += amount

        save_data(data)

        del user_states[message.chat.id]

        total = data["card"] + data["cash"]

        text = (
            f"✅ Операция добавлена\n\n"
            f"📂 {transaction['category']}\n"
            f"💵 {amount} р"
        )

        if total <= LOW_BALANCE:

            text += (
                f"\n\n⚠️ Низкий баланс!"
                f"\nОсталось: {total:.2f} р"
            )

        bot.send_message(
            message.chat.id,
            text,
            reply_markup=main_keyboard()
        )

    except:

        bot.send_message(
            message.chat.id,
            "⚠️ Ошибка суммы"
        )


@bot.message_handler(func=lambda m: m.text == "💳 Баланс")
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

    total = sum(data["debts"].values())

    text = "📋 Долги:\n\n"

    for name, amount in data["debts"].items():

        text += f"{name}: {amount} р\n"

    text += f"\n💸 Всего долгов: {total} р"

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "🧾 История")
def history(message):

    text = "🧾 Последние операции:\n\n"

    for tx in data["transactions"][:20]:

        emoji = "💸"

        if tx["type"] == "income":
            emoji = "💰"

        text += (
            f"{emoji} {tx['date']} | "
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
        f"📅 Статистика месяца\n\n"
        f"💰 Доходы: {income:.2f} р\n"
        f"💸 Расходы: {expense:.2f} р\n"
        f"📉 Итог: {(income-expense):.2f} р"
    )

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "📈 Сегодня")
def today_stats(message):

    today = datetime.now().strftime("%d.%m.%Y")

    income = 0
    expense = 0

    for tx in data["transactions"]:

        if tx["date"] == today:

            if tx["type"] == "income":
                income += tx["amount"]
            else:
                expense += tx["amount"]

    text = (
        f"📈 Сегодня\n\n"
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
