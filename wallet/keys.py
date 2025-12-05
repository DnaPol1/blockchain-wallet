from ecdsa import SigningKey, SECP256k1
import hashlib


def generate_wallet():
    """
    Генерирует новый кошелёк.
    Возвращает словарь с приватным ключом и адресом (несжатый публичный ключ в hex).
    Именно такой адрес использует большинство групп в ЮУрГУ.
    """
    sk = SigningKey.generate(curve=SECP256k1)
    private_key = sk.to_string().hex()  # 64 символа hex

    # Несжатый публичный ключ: 04 + 32 байта X + 32 байта Y
    vk = sk.verifying_key
    public_key_bytes = b'\x04' + vk.to_string()
    address = public_key_bytes.hex()  # 130 символов, начинается с 04

    return {
        "private_key": private_key,
        "address": address
    }