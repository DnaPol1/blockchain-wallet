import hashlib
import time
import json
from wallet.transaction import Transaction


class BlockHeader:
    def __init__(self, previous_hash: str, merkle_root: str,
                 timestamp: float = None, nonce: int = 0, difficulty: int = 4):
        self.previous_hash = previous_hash
        self.merkle_root = merkle_root
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.difficulty = difficulty

    def calculate_hash(self) -> str:
        header_string = f"{self.previous_hash}{self.merkle_root}{self.timestamp}{self.nonce}{self.difficulty}"
        return hashlib.sha256(header_string.encode()).hexdigest()


class Block:
    def __init__(self, index: int, transactions: list, previous_hash: str, difficulty: int = 4):
        self.index = index
        self.transactions = transactions
        self.merkle_root = self.compute_merkle_root()
        self.header = BlockHeader(previous_hash, self.merkle_root, difficulty=difficulty)
        self.hash = self.mine_block()

    def compute_merkle_root(self) -> str:
        tx_hashes = [
            tx.calculate_hash() if isinstance(tx, Transaction)
            else hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest()
            for tx in self.transactions
        ]
        if not tx_hashes:
            return hashlib.sha256(b"").hexdigest()
        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 != 0:
                tx_hashes.append(tx_hashes[-1])
            tx_hashes = [
                hashlib.sha256((tx_hashes[i] + tx_hashes[i + 1]).encode()).hexdigest()
                for i in range(0, len(tx_hashes), 2)
            ]
        return tx_hashes[0]

    def mine_block(self) -> str:
        while True:
            hash_val = self.header.calculate_hash()
            if hash_val.startswith("0" * self.header.difficulty):
                return hash_val
            self.header.nonce += 1

    def is_valid(self) -> bool:
        return (self.hash == self.header.calculate_hash() and
                self.hash.startswith("0" * self.header.difficulty))

def create_block(transactions: list, previous_hash: str = None, difficulty: int = 4) -> dict:
    """
    Создаёт блок в формате главного узла и возвращает dict для сохранения.
    """
    if previous_hash is None:
        from app import blockchain
        previous_hash = blockchain[-1]["hash"] if blockchain else "0" * 64

    block_obj = Block(
        index=(blockchain[-1]["index"] if blockchain else 0) + 1,
        transactions=transactions,
        previous_hash=previous_hash,
        difficulty=difficulty
    )

    return {
        "index": block_obj.index,
        "hash": block_obj.hash,
        "previous_hash": block_obj.header.previous_hash,
        "timestamp": block_obj.header.timestamp,
        "nonce": block_obj.header.nonce,
        "merkle_root": block_obj.merkle_root,
        "transactions": [tx.to_dict() if hasattr(tx, 'to_dict') else tx for tx in transactions]
    }