from flask import Flask, request, redirect
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

# ====== ИНИЦИАЛИЗАЦИЯ ======
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"income": [], "expenses": [], "salary": 0}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ====== АНАЛИТИКА ======
def get_expense_stats(expenses):
    stats = {}
    for item in expenses:
        category = item["category"]
        stats[category] = stats.get(category, 0) + item["amount"]
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    return sorted_stats[:5]

def get_tips(expenses):
    total = sum(item["amount"] for item in expenses)
    if total == 0:
        return "💡 Добавьте первую операцию для анализа расходов"
    top = get_expense_stats(expenses)
    if not top:
        return "💡 Пока недостаточно данных"
    category, amount = top[0]
    percent = round((amount / total) * 100)
    if percent >= 50:
        return f"⚠️ Категория '{category}' занимает {percent}% всех расходов! Попробуйте сократить"
    if percent >= 30:
        return f"💡 Вы много тратите на '{category}' — подумайте, как уменьшить расходы"
    return "✅ Расходы распределены равномерно"

# ====== WEBAPP ======
@app.route("/", methods=["GET", "HEAD"])
def home():
    data = load_data()
    total_income = sum(i["amount"] for i in data["income"]) + data["salary"]
    total_expenses = sum(i["amount"] for i in data["expenses"])
    balance_amount = total_income - total_expenses
    top_expenses = get_expense_stats(data["expenses"])
    tips = get_tips(data["expenses"])

    # Формируем данные для графика
    chart_labels = [item[0] for item in top_expenses]
    chart_data = [item[1] for item in top_expenses]

    return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sage Finance</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body{{margin:0;background:#0f1115;color:white;font-family:sans-serif;}}
.container{{padding:20px;max-width:600px;margin:auto;}}
.card{{background:#1a1d24;border-radius:24px;padding:24px;margin-top:20px;}}
.title{{font-size:32px;font-weight:bold;}}
.balance-card{{background:linear-gradient(135deg,#1f8bff,#6c63ff);border-radius:24px;padding:24px;margin-top:20px;}}
.balance-label{{opacity:0.8;font-size:14px;}}
.balance{{font-size:42px;font-weight:bold;margin-top:10px;}}
.button{{width:100%;border:none;padding:16px;border-radius:18px;background:#4caf50;color:white;font-size:16px;font-weight:bold;margin-top:14px;}}
input,select{{width:100%;padding:14px;border:none;border-radius:14px;margin-top:12px;background:#2a2e38;color:white;box-sizing:border-box;}}
.tip{{margin-top:14px;background:#2a2e38;padding:16px;border-radius:16px;line-height:1.5;}}
.chart-container{{margin-top:20px;background:#1a1d24;padding:20px;border-radius:24px;}}
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
<h2>➕ Добавить операцию</h2>
<form method="post" action="/add_operation">
<input type="number" step="0.01" name="amount" placeholder="Сумма" required>
<select name="type">
<option value="income">Доход</option>
<option value="expense">Расход</option>
</select>
<input type="text" name="category" placeholder="Категория">
<button class="button" type="submit">Сохранить</button>
</form>
</div>
<div class="card chart-container">
<h2>📊 Топ расходов</h2>
<canvas id="expenseChart"></canvas>
</div>
<div class="card">
<h2>💡 Подсказка</h2>
<div class="tip">{tips}</div>
</div>
</div>
<script>
const ctx = document.getElementById('expenseChart').getContext('2d');
const expenseChart = new Chart(ctx, {{
    type: 'pie',
    data: {{
        labels: {chart_labels},
        datasets: [{{
            label: 'Расходы',
            data: {chart_data},
            backgroundColor: [
                '#ff6384',
                '#36a2eb',
                '#ffcd56',
                '#4bc0c0',
                '#9966ff'
            ]
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{
            legend: {{
                position: 'bottom',
                labels: {{
                    color: 'white'
                }}
            }}
        }}
    }}
}});
</script>
</body>
</html>
"""

# ====== ДОБАВЛЕНИЕ ОПЕРАЦИИ ======
@app.route("/add_operation", methods=["POST"])
def add_operation():
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

# ====== TELEGRAM ======
@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = types.WebAppInfo("https://sage-finance.onrender.com/")
    button = types.KeyboardButton(text="📱 Открыть Sage Finance", web_app=web_app)
    markup.add(button)
    bot.send_message(message.chat.id, "🚀 Sage Finance готов", reply_markup=markup)

# ====== ЗАПУСК ======
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
