# wallet/balance.py
import json
import os
from pathlib import Path
from typing import Dict

# Путь к файлу с балансами (всегда в корне проекта)
BALANCE_FILE = Path(__file__).parent.parent / "balances.json"

def load_balances() -> Dict[str, float]:
    """Загружает балансы из JSON-файла. Если файла нет — создаёт с нулём."""
    if not BALANCE_FILE.exists():
        save_balances({})
    try:
        with open(BALANCE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Приводим всё к float, на всякий случай
            return {str(k): float(v) for k, v in data.items()}
    except:
        save_balances({})
        return {}

def save_balances(balances: Dict[str, float]):
    """Сохраняет балансы в файл с красивым отступом"""
    with open(BALANCE_FILE, "w", encoding="utf-8") as f:
        json.dump(balances, f, indent=2, ensure_ascii=False)

def get_balance(address: str) -> float:
    """Возвращает баланс адреса (0.0 если нет)"""
    return load_balances().get(address, 0.0)

if BALANCE_FILE.exists():
    temp_balances = load_balances()
    if not temp_balances:  # если файл пустой
        # from wallet.keys import generate_wallet
        # wallet = generate_wallet()
        pass
else:
    # from wallet.keys import generate_wallet
    # wallet = generate_wallet()
    pass