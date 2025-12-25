import os
import json

# Адрес текущего узла
MY_NETWORK_ADDRESS = os.getenv("MY_NETWORK_ADDRESS", "127.0.0.1:8000")

# Известные узлы (seed)
SEED_NODES = json.loads(os.getenv("SEED_NODES", "[]"))

NODE_ADDRESS = os.getenv("NODE_ADDRESS", "NODE_0001")
BLOCK_REWARD = 50.0