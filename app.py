# app.py — это ЕДИНСТВЕННЫЙ файл, который мы будем запускать
from flask import Flask, render_template, request
from pathlib import Path

# Абсолютный путь — работает ОТКУДА УГОДНО
BASE_DIR = Path(__file__).parent
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))

# Импортируем наш кошелёк
from wallet.wallet import MY_ADDRESS, get_balance, create_signed_transaction

@app.route("/")
def index():
    return render_template("send.html",
                           my_address=MY_ADDRESS,
                           balance=get_balance(MY_ADDRESS))

@app.route("/wallet/send", methods=["POST"])
def send():
    try:
        tx = create_signed_transaction(
            request.form["to"].strip(),
            float(request.form["amount"])
        )
        message = "Транзакция успешно создана и подписана!"
    except Exception as e:
        message = f"Ошибка: {e}"

    return render_template("send.html",
                           my_address=MY_ADDRESS,
                           balance=get_balance(MY_ADDRESS),
                           message=message)

if __name__ == "__main__":
    print("Кошелёк запущен → http://127.0.0.1:5000")
    app.run(debug=True, port=5000)