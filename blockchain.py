"""
Mini Blockchain — proof of work, chain validation, transactions.
"""
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Transaction:
    sender:    str
    receiver:  str
    amount:    float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "sender":    self.sender,
            "receiver":  self.receiver,
            "amount":    self.amount,
            "timestamp": self.timestamp,
        }


@dataclass
class Block:
    index:        int
    transactions: List[Transaction]
    previous_hash: str
    timestamp:    float = field(default_factory=time.time)
    nonce:        int   = 0
    hash:         str   = ""

    def compute_hash(self) -> str:
        data = {
            "index":         self.index,
            "transactions":  [t.to_dict() for t in self.transactions],
            "previous_hash": self.previous_hash,
            "timestamp":     self.timestamp,
            "nonce":         self.nonce,
        }
        return hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()

    def mine(self, difficulty: int) -> None:
        """Proof of work — find nonce so hash starts with `difficulty` zeros."""
        target = "0" * difficulty
        while True:
            self.hash = self.compute_hash()
            if self.hash.startswith(target):
                break
            self.nonce += 1


class Blockchain:
    DIFFICULTY = 3

    def __init__(self):
        self.chain:               List[Block]       = []
        self.pending_transactions: List[Transaction] = []
        self.balances:            dict               = {}
        self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        genesis = Block(index=0, transactions=[], previous_hash="0" * 64)
        genesis.mine(self.DIFFICULTY)
        self.chain.append(genesis)

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, sender: str, receiver: str, amount: float) -> bool:
        """Add a transaction to the pending pool after validation."""
        if sender != "COINBASE" and self.get_balance(sender) < amount:
            print(f"  ❌ Insufficient funds: {sender} has {self.get_balance(sender)}")
            return False
        self.pending_transactions.append(
            Transaction(sender=sender, receiver=receiver, amount=amount)
        )
        return True

    def mine_pending(self, miner_address: str) -> Block:
        """Mine all pending transactions into a new block."""
        # Reward the miner
        self.pending_transactions.append(
            Transaction("COINBASE", miner_address, 10.0)
        )

        block = Block(
            index         = len(self.chain),
            transactions  = self.pending_transactions[:],
            previous_hash = self.last_block.hash,
        )
        print(f"  ⛏️  Mining block {block.index}...", end="", flush=True)
        start = time.perf_counter()
        block.mine(self.DIFFICULTY)
        elapsed = time.perf_counter() - start
        print(f" done in {elapsed:.3f}s  (nonce={block.nonce})")

        self.chain.append(block)
        self.pending_transactions = []

        # Update balances
        for tx in block.transactions:
            if tx.sender != "COINBASE":
                self.balances[tx.sender] = self.get_balance(tx.sender) - tx.amount
            self.balances[tx.receiver] = self.get_balance(tx.receiver) + tx.amount

        return block

    def get_balance(self, address: str) -> float:
        return self.balances.get(address, 0.0)

    def is_valid(self) -> bool:
        """Validate the entire chain."""
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]

            if curr.hash != curr.compute_hash():
                print(f"  ❌ Block {i} hash mismatch")
                return False
            if curr.previous_hash != prev.hash:
                print(f"  ❌ Block {i} broken link")
                return False
        return True

    def print_chain(self) -> None:
        print("\n" + "=" * 60)
        print("  📦 Blockchain")
        print("=" * 60)
        for block in self.chain:
            print(f"\n  Block #{block.index}")
            print(f"  Hash     : {block.hash[:20]}...")
            print(f"  Prev     : {block.previous_hash[:20]}...")
            print(f"  Nonce    : {block.nonce}")
            print(f"  Tx count : {len(block.transactions)}")
            for tx in block.transactions:
                print(f"    {tx.sender} → {tx.receiver}: {tx.amount} coins")


if __name__ == "__main__":
    bc = Blockchain()

    # Seed balances
    bc.balances["Alice"] = 100.0
    bc.balances["Bob"]   = 50.0

    print("=" * 60)
    print("  🔗 Mini Blockchain Demo")
    print("=" * 60)

    bc.add_transaction("Alice", "Bob",    30.0)
    bc.add_transaction("Bob",   "Charlie", 10.0)
    bc.mine_pending("Miner1")

    bc.add_transaction("Alice",  "Charlie", 20.0)
    bc.add_transaction("Miner1", "Alice",    5.0)
    bc.mine_pending("Miner2")

    bc.print_chain()

    print(f"\n  Balances:")
    for name in ["Alice", "Bob", "Charlie", "Miner1", "Miner2"]:
        print(f"    {name:10} : {bc.get_balance(name):.1f} coins")

    print(f"\n  Chain valid: {bc.is_valid()}")

    # Tamper and re-validate
    print("\n  Tampering with block 1...")
    bc.chain[1].transactions[0].amount = 9999
    print(f"  Chain valid: {bc.is_valid()}")
