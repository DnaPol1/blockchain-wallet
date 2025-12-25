import json
import os
from models.block import Block
from models.transaction import SignedTransaction

DATA_DIR = "data"
CHAIN_FILE = os.path.join(DATA_DIR, "blockchain.json")


def save_chain(chain):
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(CHAIN_FILE, "w", encoding="utf-8") as f:
        json.dump(
            [block.model_dump() for block in chain],
            f,
            indent=2
        )


def load_chain():
    if not os.path.exists(CHAIN_FILE):
        return None

    with open(CHAIN_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)

    return [Block.model_validate(b) for b in raw]
