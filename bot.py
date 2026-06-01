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

MONTH_LIMIT = 1500


AUTO_CATEGORIES = {
    "продукты": "Продукты",
    "магазин": "Продукты",
    "евроопт": "Продукты",
    "такси": "Транспорт",
    "автобус": "Транспорт",
    "проезд": "Транспорт",
    "кафе": "Кафе",
    "кофе": "Кафе",
    "дом": "Для дома",
    "ремонт": "Для дома",
    "игры": "Игры",
    "steam": "Игры",
    "связь": "Связь",
    "мтс": "Связь"
}


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

    with open(DATA_FILE, "w", encoding="utf-8") as f:
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
    markup.add("🔄 Перевод", "📤 Backup")
    markup.add("🔍 Поиск", "🗑 Удалить")

    return markup


def financial_health():

    total = data["card"] + data["cash"]

    debts = sum(data["debts"].values())

    if total <= 0:
        return "🔴 Критично"

    if debts > total * 5:
        return "🟠 Риск"

    if debts > total * 2:
        return "🟡 Нормально"

    return "🟢 Хорошо"


def add_transaction(category, amount, method, tx_type):

    transaction = {
        "category": category,
        "amount": amount,
        "method": method,
        "type": tx_type,
        "date": datetime.now().strftime("%d.%m.%Y %H:%M")
    }

    data["transactions"].insert(0, transaction)

    if tx_type == "expense":

        if method == "card":
            data["card"] -= amount
        else:
            data["cash"] -= amount

    else:

        if method == "card":
            data["card"] += amount
        else:
            data["cash"] += amount

    save_data(data)


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
        "Категория расхода:",
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
        "Категория дохода:",
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

    markup.add("✍️ Своя сумма")
    markup.add("⬅️ Назад")

    bot.send_message(
        message.chat.id,
        "Введите сумму:",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "✍️ Своя сумма")
def custom_amount(message):

    bot.send_message(
        message.chat.id,
        "Введите сумму:"
    )


@bot.message_handler(func=lambda m: m.text == "🗑 Удалить")
def delete_last(message):

    if len(data["transactions"]) == 0:

        bot.send_message(
            message.chat.id,
            "❌ История пуста"
        )

        return

    tx = data["transactions"].pop(0)

    if tx["type"] == "expense":

        if tx["method"] == "card":
            data["card"] += tx["amount"]
        else:
            data["cash"] += tx["amount"]

    else:

        if tx["method"] == "card":
            data["card"] -= tx["amount"]
        else:
            data["cash"] -= tx["amount"]

    save_data(data)

    bot.send_message(
        message.chat.id,
        f"🗑 Удалено:\n"
        f"{tx['category']} {tx['amount']} р"
    )


@bot.message_handler(func=lambda m: True)
def universal_handler(message):

    text = (
        message.text
        .lower()
        .replace(",", ".")
        .strip()
    )

    if text == "⬅️ назад":

        if message.chat.id in user_states:
            del user_states[message.chat.id]

        bot.send_message(
            message.chat.id,
            "Главное меню",
            reply_markup=main_keyboard()
        )

        return

    if text == "📤 backup":

        with open(DATA_FILE, "rb") as f:

            bot.send_document(
                message.chat.id,
                f
            )

        return

    if text.startswith("поиск"):

        query = text.replace("поиск", "").strip()

        results = []

        for tx in data["transactions"]:

            if (
                query in tx["category"].lower()
                or query in str(tx["amount"])
            ):

                results.append(tx)

        if len(results) == 0:

            bot.send_message(
                message.chat.id,
                "❌ Ничего не найдено"
            )

            return

        reply = "🔍 Результаты:\n\n"

        for tx in results[:15]:

            reply += (
                f"{tx['date']} | "
                f"{tx['category']} | "
                f"{tx['amount']} р\n"
            )

        bot.send_message(
            message.chat.id,
            reply
        )

        return

    if text.startswith("перевод"):

        try:

            words = text.split()

            amount = float(words[1])

            if "нал" in text:

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

        except:

            bot.send_message(
                message.chat.id,
                "⚠️ Ошибка перевода"
            )

        return

    if message.chat.id in user_states:

        try:

            amount = float(
                text.replace("р", "")
            )

            state = user_states[message.chat.id]

            add_transaction(
                state["category"],
                amount,
                state["method"],
                state["type"]
            )

            del user_states[message.chat.id]

            total = data["card"] + data["cash"]

            reply = (
                f"✅ Добавлено\n\n"
                f"{state['category']}: "
                f"{amount:.2f} р"
            )

            if total <= LOW_BALANCE:

                reply += (
                    f"\n\n⚠️ Низкий баланс:"
                    f"\n{total:.2f} р"
                )

            bot.send_message(
                message.chat.id,
                reply,
                reply_markup=main_keyboard()
            )

        except:

            bot.send_message(
                message.chat.id,
                "⚠️ Введите сумму"
            )

        return

    words = text.split()

    if len(words) >= 2:

        try:

            title = words[0]

            amount = float(words[1])

            category = "Прочее"

            tx_type = "expense"

            method = "card"

            for key, value in AUTO_CATEGORIES.items():

                if key in title:
                    category = value

            if (
                "зарплата" in title
                or "доход" in title
                or "аванс" in title
            ):

                tx_type = "income"

                category = "Доход"

            add_transaction(
                category,
                amount,
                method,
                tx_type
            )

            bot.send_message(
                message.chat.id,
                f"✅ Быстро добавлено\n"
                f"{category}: {amount:.2f} р",
                reply_markup=main_keyboard()
            )

            return

        except:
            pass


@bot.message_handler(func=lambda m: m.text == "💳 Баланс")
def balance(message):

    total = data["card"] + data["cash"]

    health = financial_health()

    text = (
        f"💳 Карта: {data['card']:.2f} р\n"
        f"💵 Наличные: {data['cash']:.2f} р\n\n"
        f"💰 Всего: {total:.2f} р\n"
        f"🏦 Состояние: {health}"
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

    if len(data["transactions"]) == 0:

        bot.send_message(
            message.chat.id,
            "История пуста"
        )

        return

    text = "🧾 Последние операции:\n\n"

    for tx in data["transactions"][:20]:

        emoji = "💸"

        if tx["type"] == "income":
            emoji = "💰"

        method = "💳"

        if tx["method"] == "cash":
            method = "💵"

        text += (
            f"{emoji} "
            f"{tx['date']} | "
            f"{method} "
            f"{tx['category']} | "
            f"{tx['amount']} р\n"
        )

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "📊 Аналитика")
def analytics(message):

    stats = {}

    total_expense = 0

    biggest = 0
    biggest_category = ""

    for tx in data["transactions"]:

        if tx["type"] == "expense":

            category = tx["category"]

            stats[category] = (
                stats.get(category, 0)
                + tx["amount"]
            )

            total_expense += tx["amount"]

            if tx["amount"] > biggest:

                biggest = tx["amount"]
                biggest_category = category

    sorted_stats = sorted(
        stats.items(),
        key=lambda x: x[1],
        reverse=True
    )

    text = "📊 Аналитика:\n\n"

    for cat, amount in sorted_stats:

        percent = 0

        if total_expense > 0:

            percent = (
                amount / total_expense
            ) * 100

        text += (
            f"{cat}: "
            f"{amount:.2f} р "
            f"({percent:.0f}%)\n"
        )

    text += (
        f"\n🔥 Самая большая трата:\n"
        f"{biggest_category}: {biggest:.2f} р"
    )

    if total_expense >= MONTH_LIMIT:

        text += (
            f"\n\n⚠️ Лимит превышен!"
        )

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


@bot.message_handler(func=lambda m: m.text == "📈 Сегодня")
def today_stats(message):

    today = datetime.now().strftime("%d.%m.%Y")

    income = 0
    expense = 0

    for tx in data["transactions"]:

        if today in tx["date"]:

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


bot.remove_webhook()

time.sleep(3)

bot.infinity_polling(
    timeout=30,
    long_polling_timeout=30,
    skip_pending=True
)
