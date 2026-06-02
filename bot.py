from flask import Flask
import telebot
from telebot import types
import threading
import time
import os
import json
from datetime import datetime

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "data.json"

# ====== Инициализация данных ======
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"income": [], "expenses": [], "salary": 0}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ====== Flask WebApp ======
@app.route("/", methods=["GET", "HEAD"])
def home():
    data = load_data()
    total_income = sum(item["amount"] for item in data["income"]) + data["salary"]
    total_expenses = sum(item["amount"] for item in data["expenses"])
    balance_amount = total_income - total_expenses

    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Sage Finance</title>
        <style>
            body{{margin:0;background:#0f1115;color:white;font-family:sans-serif;}}
            .container{{padding:20px;max-width:500px;margin:auto;}}
            .card{{background:#1a1d24;border-radius:24px;padding:24px;margin-top:20px;}}
            .title{{font-size:32px;font-weight:bold;}}
            .balance-card{{background:linear-gradient(135deg,#1f8bff,#6c63ff);border-radius:24px;padding:24px;margin-top:20px;}}
            .balance-label{{opacity:0.8;font-size:14px;}}
            .balance{{font-size:42px;font-weight:bold;margin-top:10px;}}
            .button{{width:100%;border:none;padding:16px;border-radius:18px;background:#4caf50;color:white;font-size:16px;font-weight:bold;margin-top:14px;}}
            input, select{{width:100%;padding:12px;margin-top:8px;border-radius:8px;border:none;}}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="title">Sage Finance</div>
            <div class="balance-card">
                <div class="balance-label">Общий баланс</div>
                <div class="balance">{balance_amount} ₽</div>
            </div>
            <div class="card">
                <h2>🚀 Финансовый ассистент</h2>
                <p>Добавляй доходы, расходы и следи за балансом.</p>
                <form method="post" action="/add_operation">
                    <input type="number" name="amount" placeholder="Сумма" required>
                    <select name="type">
                        <option value="income">Доход</option>
                        <option value="expense">Расход</option>
                    </select>
                    <input type="text" name="category" placeholder="Категория">
                    <button class="button" type="submit">➕ Добавить операцию</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

# ====== Обработка формы WebApp ======
@app.route("/add_operation", methods=["POST"])
def add_operation():
    from flask import request, redirect
    amount = float(request.form.get("amount", 0))
    type_op = request.form.get("type", "income")
    category = request.form.get("category") or "Другое"

    data = load_data()
    entry = {"amount": amount, "category": category, "date": str(datetime.now())}
    if type_op == "income":
        data["income"].append(entry)
    else:
        data["expenses"].append(entry)
    save_data(data)
    return redirect("/")

# ====== Telegram бот ======
@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = types.WebAppInfo("https://sage-finance.onrender.com/")
    button = types.KeyboardButton(text="📱 Открыть Sage Finance", web_app=web_app)
    markup.add(button)
    bot.send_message(message.chat.id, "🚀 Sage Finance готов", reply_markup=markup)

@bot.message_handler(commands=["add_income"])
def add_income(message):
    try:
        parts = message.text.split()
        amount = float(parts[1])
        category = parts[2] if len(parts) > 2 else "Другое"
        data = load_data()
        data["income"].append({"amount": amount, "category": category, "date": str(datetime.now())})
        save_data(data)
        bot.reply_to(message, f"Доход {amount}₽ в категории '{category}' добавлен.")
    except:
        bot.reply_to(message, "Использование: /add_income сумма категория")

@bot.message_handler(commands=["add_expense"])
def add_expense(message):
    try:
        parts = message.text.split()
        amount = float(parts[1])
        category = parts[2] if len(parts) > 2 else "Другое"
        data = load_data()
        data["expenses"].append({"amount": amount, "category": category, "date": str(datetime.now())})
        save_data(data)
        bot.reply_to(message, f"Расход {amount}₽ в категории '{category}' добавлен.")
    except:
        bot.reply_to(message, "Использование: /add_expense сумма категория")

@bot.message_handler(commands=["set_salary"])
def set_salary(message):
    try:
        parts = message.text.split()
        amount = float(parts[1])
        data = load_data()
        data["salary"] = amount
        save_data(data)
        bot.reply_to(message, f"Зарплата установлена: {amount}₽")
    except:
        bot.reply_to(message, "Использование: /set_salary сумма")

@bot.message_handler(commands=["balance"])
def balance(message):
    data = load_data()
    total_income = sum(item["amount"] for item in data["income"]) + data["salary"]
    total_expenses = sum(item["amount"] for item in data["expenses"])
    balance_amount = total_income - total_expenses
    bot.reply_to(message,
        f"Баланс: {balance_amount}₽\nДоходы: {total_income}₽\nРасходы: {total_expenses}₽\nЗарплата: {data['salary']}₽")

@bot.message_handler(commands=["report"])
def report(message):
    data = load_data()
    income_report = {}
    expense_report = {}
    for item in data["income"]:
        income_report[item["category"]] = income_report.get(item["category"], 0) + item["amount"]
    for item in data["expenses"]:
        expense_report[item["category"]] = expense_report.get(item["category"], 0) + item["amount"]
    income_text = "\n".join([f"{k}: {v}₽" for k, v in income_report.items()]) or "Нет доходов"
    expense_text = "\n".join([f"{k}: {v}₽" for k, v in expense_report.items()]) or "Нет расходов"
    bot.reply_to(message, f"💰 Доходы по категориям:\n{income_text}\n\n💸 Расходы по категориям:\n{expense_text}")

# ====== Запуск бота ======
def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=30, skip_pending=True)
        except Exception as e:
            print(e)
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
