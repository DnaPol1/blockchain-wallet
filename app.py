# app.py — основной и единственный файл запуска
from flask import Flask, render_template, request
from pathlib import Path
import json
import time
import os

# === Путь к папкам ===
BASE_DIR = Path(__file__).parent
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))

# === Импорты из наших модулей ===
from wallet.wallet import MY_ADDRESS, get_balance, create_signed_transaction
from wallet.validation import validate_transaction
from wallet.balance import load_balances, save_balances
from wallet.transaction import Transaction
from node.blockchain import create_block
from node.blockchain import Block
# === Мемпул и блокчейн (с сохранением в файлы) ===
mempool = []
blockchain = []

MEMPOOL_FILE = BASE_DIR / "mempool.json"
BLOCKCHAIN_FILE = BASE_DIR / "blockchain.json"

if MEMPOOL_FILE.exists():
    try:
        mempool = json.load(open(MEMPOOL_FILE, encoding="utf-8"))
    except:
        mempool = []

if BLOCKCHAIN_FILE.exists():
    try:
        blockchain = json.load(open(BLOCKCHAIN_FILE, encoding="utf-8"))
    except:
        blockchain = []

# === Генезис-блок (если цепочка пустая) ===
if not blockchain:
    genesis = create_block([])
    blockchain.append(genesis)
    json.dump(blockchain, open(BLOCKCHAIN_FILE, "w", encoding="utf-8"), indent=2)
    print("Создан генезис-блок")

# === Главная страница ===
@app.route("/")
def wallet():
    return render_template("wallet.html",
                           my_address=MY_ADDRESS,
                           balance=get_balance(MY_ADDRESS),
                           mempool=mempool,
                           blockchain=blockchain)

# === Отправка транзакции ===
@app.route("/wallet/send", methods=["POST"])
def send():
    try:
        recipient = request.form["to"].strip()
        amount = float(request.form["amount"])

        tx = create_signed_transaction(recipient, amount)

        # Добавляем в мемпул как словарь
        tx_dict = {
            "sender": tx.sender,
            "receiver": tx.receiver,
            "amount": tx.amount,
            "timestamp": tx.timestamp,
            "signature": tx.signature
        }
        mempool.append(tx_dict)
        json.dump(mempool, open(MEMPOOL_FILE, "w", encoding="utf-8"), indent=2)

        message = "Транзакция отправлена в мемпул!"
    except Exception as e:
        message = f"Ошибка: {e}"

    return render_template("wallet.html",
                           my_address=MY_ADDRESS,
                           balance=get_balance(MY_ADDRESS),
                           mempool=mempool,
                           blockchain=blockchain,
                           message=message)

# === Приём транзакций от других узлов ===
@app.route("/transaction", methods=["POST"])
def receive_tx():
    tx_data = request.get_json()
    if tx_data:
        mempool.append(tx_data)
        json.dump(mempool, open(MEMPOOL_FILE, "w", encoding="utf-8"), indent=2)
    return {"status": "ok"}

# === Майнинг блока (PoW + Merkle root + совместимый хеш) ===
@app.route("/mine")
def mine_block():
    if not mempool:
        message = "Мемпул пуст"
    else:
        tx_objects = []
        for tx_data in mempool:
            tx = Transaction(
                sender=tx_data["sender"],
                receiver=tx_data["receiver"],
                amount=tx_data["amount"],
                timestamp=tx_data["timestamp"]
            )
            tx_objects.append(tx)

        previous_hash = blockchain[-1]["hash"] if blockchain else "0" * 64
        new_block = Block(
            index=len(blockchain) + 1,
            transactions=tx_objects,
            previous_hash=previous_hash
        )

        # Обновляем балансы
        for tx in tx_objects:
            balances = load_balances()
            balances[tx.sender] = balances.get(tx.sender, 0.0) - tx.amount
            balances[tx.receiver] = balances.get(tx.receiver, 0.0) + tx.amount
            save_balances(balances)

        # Сохраняем как у главного узла
        os.makedirs("blockchain_data", exist_ok=True)
        block_data = {
            "index": new_block.index,
            "hash": new_block.hash,
            "previous_hash": new_block.header.previous_hash,
            "timestamp": new_block.header.timestamp,
            "nonce": new_block.header.nonce
        }
        tx_data = [tx.to_dict() for tx in tx_objects]

        with open(f"blockchain_data/block_{new_block.index}.json", "w", encoding="utf-8") as f:
            json.dump(block_data, f, indent=2)
        with open(f"blockchain_data/transactions_{new_block.index}.json", "w", encoding="utf-8") as f:
            json.dump(tx_data, f, indent=2)

        blockchain.append(block_data)
        mempool.clear()
        json.dump(mempool, open(MEMPOOL_FILE, "w"), indent=2)

        message = f"Блок #{new_block.index} замейнён и сохранён в blockchain_data/"

    return render_template("wallet.html", my_address=MY_ADDRESS, balance=get_balance(MY_ADDRESS),
                           mempool=mempool, blockchain=blockchain, message=message)
# === Запуск ===
if __name__ == "__main__":
    print("="*60)
    print("БЛОКЧЕЙН-УЗЕЛ ЗАПУЩЕН")
    print(f"Адрес: {MY_ADDRESS}")
    print(f"Баланс: {get_balance(MY_ADDRESS)} монет")
    print(f"http://127.0.0.1:5000")
    print("="*60)
    app.run(debug=True, port=5000)