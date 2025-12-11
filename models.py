"""Data models for the limit order book system."""

from enum import Enum
from dataclasses import dataclass, field
import time
import uuid


class Side(Enum):
    """Represents the side of an order - buy or sell."""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    """Represents the status of an order."""
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


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
        original_qty: Original quantity when order was placed
        status: Current status of the order
    """
    id: str
    user_id: str
    side: Side
    price: float
    qty: int
    ts: float = field(default_factory=lambda: time.time())
    seq: int = 0
    original_qty: int = 0
    status: OrderStatus = OrderStatus.OPEN

    def __post_init__(self):
        """Set original_qty if not provided."""
        if self.original_qty == 0:
            self.original_qty = self.qty


@dataclass
class Trade:
    """Represents an executed trade between two orders.
    
    Attributes:
        buy_order_id: ID of the buy order
        sell_order_id: ID of the sell order
        price: Execution price
        qty: Quantity traded
        ts: Timestamp of trade execution
    """
    buy_order_id: str
    sell_order_id: str
    price: float
    qty: int
    ts: float = field(default_factory=lambda: time.time())


def new_order_id() -> str:
    """Generate a unique order ID using UUID4.
    
    Returns:
        A unique hex string identifier for an order.
    """
    return uuid.uuid4().hex
