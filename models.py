"""Data models for the limit order book system."""

from enum import Enum
from dataclasses import dataclass, field
import time


class Side(Enum):
    """Represents the side of an order - buy or sell."""
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Order:
    """Represents a limit order in the order book.
    
    Attributes:
        id: Unique identifier for the order
        user_id: ID of the user who placed the order
        side: BUY or SELL
        price: Limit price for the order
        qty: Quantity of shares/units
        ts: Timestamp when order was created
        seq: Sequence number for FIFO ordering at same price
    """
    id: str
    user_id: str
    side: Side
    price: float
    qty: int
    ts: float = field(default_factory=lambda: time.time())
    seq: int = 0
