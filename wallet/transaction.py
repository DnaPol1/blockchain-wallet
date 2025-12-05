import hashlib
import json
import time
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from ecdsa.util import sigencode_der, sigdecode_der

class Transaction:
    def __init__(self, sender: str, receiver : str, amount: float, timestamp: float = None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp or time.time()
        self.signature: str = None #hex-строка подписи

    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp
        }

    def calculate_hash(self) -> str:
        tx_string = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(tx_string.encode()).hexdigest()

    def sign(self, private_key_hex: str) -> None:
        """Подписываем ХЕШ транзакции (именно то, что делает calculate_hash, но в bytes)"""
        sk = SigningKey.from_string(bytes.fromhex(private_key_hex), curve=SECP256k1)

        # Важно: подписываем ТОЧНО ТЕ ЖЕ ДАННЫЕ, что и в calculate_hash
        message = json.dumps(self.to_dict(), sort_keys=True).encode()
        hash_bytes = hashlib.sha256(message).digest()

        signature_bytes = sk.sign_deterministic(
            hash_bytes,
            hashfunc=hashlib.sha256,
            sigencode=sigencode_der
        )
        self.signature = signature_bytes.hex()

    def verify_signature(self) -> bool:
        """Проверяем, что подпись валидна и соответствует sender (публичному ключу)"""
        if not self.signature:
            return False

        try:
            # Предполагаем, что sender — это hex несжатого публичного ключа (начинается с 04)
            pubkey_bytes = bytes.fromhex(self.sender)
            vk = VerifyingKey.from_string(pubkey_bytes, curve=SECP256k1)

            sig_bytes = bytes.fromhex(self.signature)
            message = json.dumps(self.to_dict(), sort_keys=True).encode()
            hash_bytes = hashlib.sha256(message).digest()

            return vk.verify(sig_bytes, hash_bytes, hashfunc=hashlib.sha256, sigdecode=sigdecode_der)
        except Exception as e:
            print(f"Ошибка проверки подписи: {e}")
            return False

    def to_dict_with_signature(self) -> dict:
        """Для отправки в сеть — с подписью"""
        data = self.to_dict()
        data["signature"] = self.signature or ""
        return data

    def __repr__(self):
        return f"<Tx {self.sender[:8]}... → {self.receiver[:8]}... {self.amount}>"