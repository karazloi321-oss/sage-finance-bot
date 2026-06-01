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
return
<html>
<head>

    <title>Sage Finance</title>

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >

    <style>

        body{
            background:
            font-family:sans-serif;
            padding:20 px;
            text-align:center;
        }

        .card{
            background:white;
            padding:25 px;
            border-radius:20 px;
            max-width:400 px;
            margin:auto;
            box-shadow:0 4 pz 10 px rgba(0,0,0,0.1);
        }

        h1{
            color:#1f2a1f;
        }

        .balance{
            font-size:40 px;
            margin:20 px 0;
            font-weight:bold;
        }

        button{
            width:100%;
            padding:18 px;
            border:none;
            border-radius:16 px;
            background:#7c9b76;
            color:white;
            font-size:20 px;
            margin-top:12 px;
        }

    </style>

</head>

<body>

    <div class="card">

        <h1>Sage Finance</h1>

        <div class="balance">
            0 P
        </div>

        <button onclick="minus(10)">
            -10 P
        </button>

        <button onclick="minus(50)">
            -50 P
        </button>

        <button onclick="minus(100)">
            -100 P
        </button>

    </div>

    <script>

        let balance = 0

        function minus(amount){

            balance -= amount

            document.querySelector(
                ".balance"
            ).innerHTML =
                balance + " P"
        }

    </script>

</body>
</html>
@bot.message_handler(commands=["start"])
def start(message):

markup = types.ReplyKeyboardMarkup(
    resize_keyboard=True
)

webapp = types.WebAppInfo(
    "https://sage-finance.onrender.com"
)

button = types.KeyboardButton(
    "📱 Открыть Sage Finance"
    web_app=webapp
)

markup.add(button)

bot.send_message(
    message.chat.id,
    "🚀 Sage Finance готов"
    reply_markup=markup
)

def run_bot():

try:

    bot.remove_webhook()

    bot.infinity_polling(
        skip_pending=True
    )

except Exception as e:

    print(e)

if __name__ == "**main**":

threading.Thread(
    target=run_bot
).start()

app.run(
    host="0.0.0.0"
    port=int(
        os.environ.get(
            "PORT"
            10000
        )
    )
)
