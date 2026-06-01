from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Sage Finance работает 🚀</h1>
    <p>Mini App успешно запущен</p>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
