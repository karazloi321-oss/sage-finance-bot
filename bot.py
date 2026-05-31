import telebot
from telebot import types
import json
import os

TOKEN = os.getenv("TOKEN")

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

```python
CATEGORIES = {
    "продукты": "Продукты",
    "автобус": "Транспорт",
    "проезд": "Транспорт",
    "кафе": "Кафе",
    "кофе": "Кафе",
    "игры": "Игры",
    "дом": "Для дома",
    "связь": "Связь",
    "сын": "Сын"
}

@bot.message_handler(func=lambda m: True)
def parse_message(message):

    try:

        text = message.text.lower().split()

        if len(text) < 2:
            return

        title = text[0]
        amount = float(text[1])

        method = "карта"

        if len(text) >= 3:
            method = text[2]

        category = "Прочее"

        for key, value in CATEGORIES.items():

            if key in title:
                category = value

        transaction = {
            "title": title,
            "amount": amount,
            "method": method,
            "category": category
        }

        data["transactions"].insert(0, transaction)

        if "зарплата" in title or "доход" in title:

            if "карт" in method:
                data["card"] += amount
            else:
                data["cash"] += amount

            bot.send_message(
                message.chat.id,
                f"✅ Доход добавлен: {amount} р"
            )

        else:

            if "карт" in method:
                data["card"] -= amount
            else:
                data["cash"] -= amount

            bot.send_message(
                message.chat.id,
                f"💸 Расход добавлен: {amount} р\nКатегория: {category}"
            )

        save_data(data)

    except Exception as e:

        print(e)
```python
bot.infinity_polling(skip_pending=True)
```

