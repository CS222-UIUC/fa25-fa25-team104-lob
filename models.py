"""Data models for the limit order book system."""

from enum import Enum


class Side(Enum):
    """Represents the side of an order - buy or sell."""
    BUY = "BUY"
    SELL = "SELL"

