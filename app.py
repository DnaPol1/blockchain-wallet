from fastapi import FastAPI, HTTPException
import requests

from storage import blockchain
from node.config import SEED_NODES, MY_NETWORK_ADDRESS, NODE_ADDRESS
from models.api import SignedTransaction

app = FastAPI(
    title="Polinas Node",
    version="0.3.0"
)


# -------------------------
# TRANSACTIONS
# -------------------------

@app.post("/transactions")
def create_transaction(tx: SignedTransaction):
    try:
        blockchain.add_transaction(tx)
        return {"status": "ok", "message": "Transaction accepted"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/transactions/pending")
def pending_transactions():
    return blockchain.mempool


# -------------------------
# BLOCKS
# -------------------------

@app.post("/blocks/mine")
def mine_block():
    return blockchain.mine_block(NODE_ADDRESS)


@app.get("/chain")
def get_chain():
    return blockchain.chain


@app.get("/chain/headers")
def get_chain_headers():
    return blockchain.get_headers()


# -------------------------
# BALANCE
# -------------------------

@app.get("/balance/{address}")
def get_balance(address: str):
    return {
        "address": address,
        "balance": blockchain.get_balance(address)
    }


# -------------------------
# CONSENSUS
# -------------------------

@app.post("/nodes/resolve")
def resolve_nodes():
    max_length = len(blockchain.chain)
    new_chain = None

    for node in SEED_NODES:
        if node == MY_NETWORK_ADDRESS:
            continue

        try:
            headers_resp = requests.get(
                f"http://{node}/chain/headers",
                timeout=3
            )
            if headers_resp.status_code != 200:
                continue

            foreign_headers = headers_resp.json()
            foreign_length = len(foreign_headers)

            if foreign_length > max_length:
                chain_resp = requests.get(
                    f"http://{node}/chain",
                    timeout=5
                )
                if chain_resp.status_code != 200:
                    continue

                candidate_chain = chain_resp.json()

                if blockchain.is_chain_valid(candidate_chain):
                    max_length = foreign_length
                    new_chain = candidate_chain

        except Exception:
            continue

    if new_chain:
        blockchain.replace_chain(new_chain)
        return {
            "replaced": True,
            "new_length": len(blockchain.chain)
        }

    return {
        "replaced": False,
        "length": len(blockchain.chain)
    }
