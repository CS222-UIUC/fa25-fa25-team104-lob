from enum import Enum
from dataclasses import dataclass, field
import time
import uuid


class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Order:
    id: str
    user_id: str
    side: Side
    price: float
    qty: int
    ts: float = field(default_factory=lambda: time.time())
    seq: int = 0  # assigned by order book for FIFO at same price


@dataclass
class Trade:
    buy_order_id: str
    sell_order_id: str
    price: float
    qty: int
    ts: float = field(default_factory=lambda: time.time())


def new_order_id() -> str:
    """Generate a unique order ID."""
    # return a UUID hex string
    pass