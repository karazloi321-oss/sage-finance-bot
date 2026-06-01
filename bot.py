
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


def get_main_keyboard():

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add("💸 Расход", "💰 Баланс")
    markup.add("📋 Долги", "📊 Аналитика")
    markup.add("🧾 История", "📅 Месяц")
    markup.add("🔄 Перевод")

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
            "✅ Доступ разрешен",
            reply_markup=get_main_keyboard()
        )

    else:

        bot.send_message(
            message.chat.id,
            "❌ Неверный PIN"
        )


@bot.message_handler(func=lambda m: m.text == "💰 Баланс")
def balance(message):

    text = (
        f"💳 Карта: {data['card']:.2f} р\n"
        f"💵 Наличные: {data['cash']:.2f} р"
    )

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "📋 Долги")
def debts(message):

    txt = "📋 Долги:\n\n"

    total = 0

    for name, amount in data["debts"].items():

        txt += f"{name}: {amount} р\n"

        total += amount

    txt += f"\nОбщий долг: {total} р"

    bot.send_message(message.chat.id, txt)


@bot.message_handler(func=lambda m: m.text == "🧾 История")
def history(message):

    text = "🧾 Последние операции:\n\n"

    for tx in data["transactions"][:15]:

        category = tx.get("category", "Прочее")

        text += (
            f"{tx['date']} | "
            f"{tx['title']} — "
            f"{tx['amount']} р "
            f"({category})\n"
        )

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "📊 Аналитика")
def analytics(message):

    stats = {}

    for tx in data["transactions"]:

        if tx["type"] == "expense":

            category = tx.get("category", "Прочее")

            stats[category] = (
                stats.get(category, 0)
                + tx["amount"]
            )

    text = "📊 Расходы по категориям:\n\n"

    for cat, amount in stats.items():

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

    profit = income - expense

    text = (
        f"📅 Статистика месяца\n\n"
        f"💰 Доходы: {income:.2f} р\n"
        f"💸 Расходы: {expense:.2f} р\n"
        f"📈 Разница: {profit:.2f} р"
    )

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "🔄 Перевод")
def transfer_help(message):

    bot.send_message(
        message.chat.id,
        "Пример:\nперевод 50 в наличные"
    )


CATEGORIES = {
    "продукты": "Продукты",
    "автобус": "Транспорт",
    "проезд": "Транспорт",
    "кафе": "Кафе",
    "кофе": "Кафе",
    "игры": "Игры",
    "дом": "Для дома",
    "связь": "Связь",
    "сын": "Сын",
    "зарплата": "Доход",
    "аванс": "Доход"
}


@bot.message_handler(func=lambda m: True)
def parse_message(message):

    try:

        text = message.text.lower()

        if text.startswith("перевод"):

            words = text.split()

            amount = float(words[1])

            if "наличные" in text:

                data["card"] -= amount
                data["cash"] += amount

            else:

                data["cash"] -= amount
                data["card"] += amount

            save_data(data)

            bot.send_message(
                message.chat.id,
                "✅ Перевод выполнен"
            )

            return

        words = text.split()

        if len(words) < 2:
            return

        title = words[0]

        amount = float(words[1])

        method = "карта"

        if len(words) >= 3:
            method = words[2]

        category = "Прочее"

        for key, value in CATEGORIES.items():

            if key in title:
                category = value

        tx_type = "expense"

        if (
            "зарплата" in title
            or "доход" in title
            or "аванс" in title
        ):
            tx_type = "income"

        transaction = {
            "title": title,
            "amount": amount,
            "method": method,
            "category": category,
            "type": tx_type,
            "date": datetime.now().strftime("%d.%m.%Y")
        }

        data["transactions"].insert(0, transaction)

        if tx_type == "income":

            if "карт" in method:
                data["card"] += amount
            else:
                data["cash"] += amount

            bot.send_message(
                message.chat.id,
                f"✅ Доход: {amount} р"
            )

        else:

            if "карт" in method:
                data["card"] -= amount
            else:
                data["cash"] -= amount

            bot.send_message(
                message.chat.id,
                f"💸 Расход: {amount} р\n"
                f"📂 Категория: {category}"
            )

        save_data(data)

    except Exception as e:

        print(e)

        bot.send_message(
            message.chat.id,
            "⚠️ Ошибка ввода"
        )


while True:

    try:

        bot.infinity_polling(
            timeout=10,
            long_polling_timeout=5,
            skip_pending=True
        )

    except Exception as e:

        print(e)

        time.sleep(5)

