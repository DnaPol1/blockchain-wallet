# wallet/validation.py
from wallet.transaction import Transaction
from wallet.balance import get_balance
from typing import Dict, Union

def validate_transaction(tx: Transaction) -> Dict[str, Union[bool, str]]:
    """
    Полная проверка входящей транзакции.
    Возвращает dict:
        {"valid": True}
        или
        {"valid": False, "reason": "текст ошибки"}
    """
    # 1. Проверка подписи
    if not hasattr(tx, "verify_signature") or not tx.verify_signature():
        return {"valid": False, "reason": "Неверная подпись"}

    # 2. Проверка баланса отправителя
    sender_balance = get_balance(tx.sender)
    if sender_balance < tx.amount:
        return {
            "valid": False,
            "reason": f"Недостаточно средств: есть {sender_balance}, нужно {tx.amount}"
        }

    # 3. Дополнительно: сумма должна быть положительной
    if tx.amount <= 0:
        return {"valid": False, "reason": "Сумма должна быть положительной"}

    # 4. Если всё ок
    return {"valid": True}