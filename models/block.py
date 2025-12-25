from pydantic import BaseModel, Field
from typing import List
from models.transaction import SignedTransaction
import hashlib
import time

class BlockHeader(BaseModel):
    index: int
    previous_hash: str
    merkle_root: str
    timestamp: float
    nonce: int
    difficulty: int
    hash: str

class Block(BaseModel):
    header: BlockHeader
    transactions: List[SignedTransaction]

    @staticmethod
    def create_genesis_block(self, difficulty: int = 2):
        header = BlockHeader(
            index=0,
            previous_hash="0" * 64,
            timestamp=time.time(),
            merkle_root="0" * 64,
            nonce=0,
            difficulty=difficulty, #было self.difficulty
            hash="0" * 64
        )
        # genesis_block = Block(
        #     header=header,
        #     transactions=[]
        # )
        # self.chain.append(genesis_block)
        return Block(header=header, transactions=[])

    def compute_hash(self):
        block_string = f"{self.header.index}{self.header.previous_hash}{self.header.merkle_root}{self.header.timestamp}{self.header.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def is_block_valid(self, previous_block):
        if self.header.previous_hash != previous_block.header.hash:
            return False

        if not self.header.hash.startswith("0" * self.header.difficulty):
            return False

        if self.compute_hash() != self.header.hash:
            return False

        # #PoW
        # if not block.hash.startswith("0" * block.header.difficulty):
        #     return False
        # # merkle_root
        # if block.header.merkle_root != calculate_merkle_root(block.transactions):
        #     return False
        # # hash корректен
        # recalculated_hash = self.calculate_block_hash(
        #     block.index, block.header, block.transactions
        # )
        # if recalculated_hash != block.hash:
        #     return False

        return True