# wallet/client_wallet.py
from wallet.transaction import Transaction

def create_signed_transaction(sender, private_key, receiver, amount):
    tx = Transaction(sender, receiver, amount)
    tx.sign(private_key)
    return  tx