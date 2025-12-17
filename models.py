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
    price: int   # price in integer cents
    qty: int     # quantity in whole units (integer)
    ts: float = field(default_factory=lambda: time.time())
    seq: int = 0  # assigned by order book for FIFO at same price


@dataclass
class Trade:
    buy_order_id: str
    sell_order_id: str
    price: int   # price in cents
    qty: int     # qty in whole units
    ts: float = field(default_factory=lambda: time.time())


def new_order_id() -> str:
    return uuid.uuid4().hex