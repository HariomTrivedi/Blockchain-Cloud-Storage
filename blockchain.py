import hashlib
import json
import time
import os

BLOCKCHAIN_FILE = "blockchain.json"

class Block:
    def __init__(self, index, transactions, prev_hash, nonce=0):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions  
        self.prev_hash = prev_hash
        self.nonce = nonce
        self.hash = self.generate_hash()

    def generate_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True, default=str)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "prev_hash": self.prev_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }

    @staticmethod
    def from_dict(block_dict):
        return Block(
            block_dict["index"],
            block_dict["transactions"],
            block_dict["prev_hash"],
            block_dict["nonce"]
        )

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.block_size_limit = 1 * 1024 * 1024  # 1MB per block
        self.load_chain()

    def create_genesis_block(self):
        genesis_block = Block(0, [], "0")
        self.chain.append(genesis_block)
        self.save_chain()

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)
        total_size = sum(len(tx['chunk']) for tx in self.pending_transactions)

        if total_size >= self.block_size_limit:
            self.mine_block()

    def mine_block(self):
        if not self.pending_transactions:
            return False

        last_block = self.chain[-1]
        new_block = Block(len(self.chain), self.pending_transactions, last_block.hash)
        self.chain.append(new_block)
        self.pending_transactions = []
        self.save_chain()

    def save_chain(self):
        with open(BLOCKCHAIN_FILE, "w") as f:
            json.dump([block.to_dict() for block in self.chain], f, indent=4)

    def load_chain(self):
        if os.path.exists(BLOCKCHAIN_FILE):
            with open(BLOCKCHAIN_FILE, "r") as f:
                data = json.load(f)
                self.chain = [Block.from_dict(block) for block in data]
        else:
            self.create_genesis_block()
