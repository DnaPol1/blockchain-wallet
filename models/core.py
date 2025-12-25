import hashlib
import json
import time
from typing import List
from models.api import BlockHeader
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
from node.config import BLOCK_REWARD
from persistence import save_chain, load_chain
from models.transaction import SignedTransaction
from models.block import Block

def sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def tx_payload(tx: SignedTransaction) -> bytes:
    """
    Данные, которые реально подписываются
    """
    payload = {
        "sender": tx.sender,
        "receiver": tx.receiver,
        "amount": tx.amount,
    }
    return json.dumps(payload, sort_keys=True).encode()

def verify_signature(tx: SignedTransaction) -> bool:
    if tx.sender in ("0" * 64, "NETWORK"):
        return True  # coinbase

    try:
        public_key = ec.EllipticCurvePublicKey.from_encoded_point(
            ec.SECP256K1(),
            bytes.fromhex(tx.sender)
        )

        public_key.verify(
            bytes.fromhex(tx.signature),
            tx_payload(tx),
            ec.ECDSA(hashes.SHA256())
        )
        return True

    except (ValueError, InvalidSignature):
        return False

def calculate_merkle_root(transactions: List[SignedTransaction]) -> str:
    if not transactions:
        return sha256("")

    hashes = [sha256(json.dumps(tx.dict(), sort_keys=True)) for tx in transactions]

    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])

        hashes = [
            sha256(hashes[i] + hashes[i + 1])
            for i in range(0, len(hashes), 2)
        ]

    return hashes[0]

class Blockchain:
    def __init__(self, difficulty: int = 2):
        self.difficulty = difficulty
        self.mempool: List[SignedTransaction] = []

        loaded = load_chain()
        if loaded:
            self.chain: list[Block] = loaded
        else:
            self.chain: List[Block] = []
            self.create_genesis_block()
            save_chain(self.chain)

    # -------------------------
    # БАЗОВЫЕ МЕТОДЫ
    # -------------------------

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, block: Block):
        if not block.is_block_valid(self.get_last_block()):
            raise ValueError("Invalid block")

        self.chain.append(block)
        self.mempool.clear()
        save_chain(self.chain)

    def replace_chain(self, new_chain: List[Block]):
        if len(new_chain) <= len(self.chain):
            return False

        if not self.is_chain_valid(new_chain):
            return False

        self.chain = new_chain
        save_chain(self.chain)
        return True

    def is_chain_valid(self, chain: List[Block]) -> bool:
        for i in range(1, len(chain)):
            if not chain[i].is_valid(chain[i - 1]):
                return False
        return True

    # -------------------------
    # БАЛАНС
    # -------------------------

    def get_balance(self, address: str) -> float:
        balance = 0.0

        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.receiver == address:
                    balance += tx.amount

        # for tx in self.mempool:
        #     if tx.sender == address:
        #        balance -= tx.amount

        return balance

        # -------------------------
        # ТРАНЗАКЦИИ
        # -------------------------

    def add_transaction(self, tx: SignedTransaction):
        #тестовый режим
        if tx.sender in ("0" * 64, "NETWORK"):
            self.mempool.append(tx)
            return

        if self.get_balance(tx.sender) < tx.amount:
            raise ValueError("Insufficient balance")
        # if not verify_signature(tx):
        #     raise ValueError("Invalid signature")
        #
        # if tx.sender != "0" * 64:
        #     if self.get_balance(tx.sender) < tx.amount:
        #         raise ValueError("Insufficient balance")

        self.mempool.append(tx)
        return

    # -------------------------
    # БЛОКИ
    # -------------------------
    def create_genesis_block(self):
        genesis = Block.create_genesis_block(self.difficulty)
        self.chain.append(genesis)


    def mine_block(self, miner_address: str) -> Block:
        coinbase_tx = SignedTransaction(
            sender="0" * 64,
            receiver=miner_address,
            amount=BLOCK_REWARD,
            signature="COINBASE"
        )

        transactions = [coinbase_tx] + self.mempool
        merkle_root = calculate_merkle_root(transactions)

        previous_block = self.chain[-1]
        index = len(self.chain)
        nonce = 0

        while True:
            header = BlockHeader(
                index=index,
                previous_hash=previous_block.header.hash,
                merkle_root=merkle_root,
                timestamp=time.time(),
                nonce=nonce,
                difficulty=self.difficulty,
                hash=""
            )

            block_hash = sha256(json.dumps(header.dict(), sort_keys=True))
            header.hash = block_hash

            if block_hash.startswith("0" * self.difficulty):
                break

            nonce += 1

        block = Block(
            header=header,
            transactions=transactions,
        )

        self.chain.append(block)
        self.mempool.clear()
        return block

    # -------------------------
    # ВАЛИДАЦИЯ
    # -------------------------



    # -------------------------
    # HASH
    # -------------------------

    def calculate_block_hash(self, index, header, transactions) -> str:
        payload = {
            "header": header.dict(),
            "transactions": [tx.dict() for tx in transactions]
        }

        return sha256(json.dumps(payload, sort_keys=True))

# ДОБАВИТЬ В КОНЕЦ Blockchain

    def get_headers(self):
        headers = []
        for block in self.chain:
            headers.append({
                "index": block.header.index,
                "previous_hash": block.header.previous_hash,
                "hash": block.header.hash,
                "nonce": block.header.nonce,
                "difficulty": block.header.difficulty
            })
        return headers
