# wallet/wallet.py
import os

from wallet.transaction import Transaction
from wallet.keys import generate_wallet
from wallet.balance import get_balance, add_funds  # ← из вчерашнего (или сегодняшнего) balance.py

# Наш собственный кошелёк (один на всю программу)
# Можно потом сделать загрузку из файла, но пока хватит
MY_WALLET = generate_wallet()
MY_ADDRESS = MY_WALLET["address"]
MY_PRIVATE_KEY = MY_WALLET["private_key"]

# Даём себе 1000 монет, если у нас ещё нет баланса
if get_balance(MY_ADDRESS) == 0:
    add_funds(MY_ADDRESS, 1000.0)
    print(f"Начислено 1000 монет на ваш адрес!")

def create_signed_transaction(recipient: str, amount: float) -> Transaction:
    """
    Главная функция кошелька: создаёт и подписывает транзакцию.
    """
    # 1. Проверяем баланс
    current_balance = get_balance(MY_ADDRESS)
    if current_balance < amount:
        raise ValueError(f"Недостаточно средств! Есть {current_balance}, нужно {amount}")

    # 2. Создаём транзакцию
    tx = Transaction(
        sender=MY_ADDRESS,
        receiver=recipient,
        amount=amount
    )

    # 3. Подписываем
    tx.sign(MY_PRIVATE_KEY)

    # 4. (опционально) сразу отнимаем с баланса
    # Сейчас оставим — Person B потом отнимет после майнинга
    # Или можно отнять здесь, если договоритесь

    return tx