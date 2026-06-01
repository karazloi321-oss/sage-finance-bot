from flask import Flask
import telebot
from telebot import types
import threading
import os

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route("/")
def home():

```
return """
<html>
<head>

    <title>Sage Finance</title>

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >

    <style>

        body{
            background:#d9e5d6;
            font-family:sans-serif;
            padding:20px;
            text-align:center;
        }

        .card{
            background:white;
            padding:25px;
            border-radius:20px;
            max-width:400px;
            margin:auto;
            box-shadow:0 4px 10px rgba(0,0,0,0.1);
        }

        h1{
            color:#1f2a1f;
        }

        .balance{
            font-size:40px;
            margin:20px 0;
            font-weight:bold;
        }

        button{
            width:100%;
            padding:18px;
            border:none;
            border-radius:16px;
            background:#7c9b76;
            color:white;
            font-size:20px;
            margin-top:12px;
        }

    </style>

</head>

<body>

    <div class="card">

        <h1>Sage Finance</h1>

        <div class="balance">
            0 ₽
        </div>

        <button onclick="minus(10)">
            -10 ₽
        </button>

        <button onclick="minus(50)">
            -50 ₽
        </button>

        <button onclick="minus(100)">
            -100 ₽
        </button>

    </div>

    <script>

        let balance = 0

        function minus(amount){

            balance -= amount

            document.querySelector(
                ".balance"
            ).innerHTML =
                balance + " ₽"
        }

    </script>

</body>
</html>
"""
```

@bot.message_handler(commands=["start"])
def start(message):

```
markup = types.ReplyKeyboardMarkup(
    resize_keyboard=True
)

webapp = types.WebAppInfo(
    "https://sage-finance.onrender.com"
)

button = types.KeyboardButton(
    "📱 Открыть Sage Finance",
    web_app=webapp
)

markup.add(button)

bot.send_message(
    message.chat.id,
    "🚀 Sage Finance готов",
    reply_markup=markup
)
```

def run_bot():

```
try:

    bot.remove_webhook()

    bot.infinity_polling(
        skip_pending=True
    )

except Exception as e:

    print(e)
```

if **name** == "**main**":

```
threading.Thread(
    target=run_bot
).start()

app.run(
    host="0.0.0.0",
    port=int(
        os.environ.get(
            "PORT",
            10000
        )
    )
)
