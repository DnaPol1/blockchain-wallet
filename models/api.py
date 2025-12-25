from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class SignedTransaction(BaseModel):
    sender: str = Field(..., description="Public key / address отправителя")
    receiver: str = Field(..., description="Адрес получателя")
    amount: float = Field(..., gt=0)
    signature: str = Field(..., description="ECDSA signature (hex)")


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