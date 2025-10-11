"""Order book implementation with price-time priority matching."""

import heapq
from typing import List, Dict, Optional, Tuple
from models import Order, Trade, Side


class OrderBook:
    """A limit order book that matches buy and sell orders.
    
    Uses max heap for bids (buy orders) and min heap for asks (sell orders).
    Orders at the same price level are matched in FIFO order using sequence numbers.
    """
    
    def __init__(self):
        """Initialize the order book with empty heaps and order tracking."""
        # Max heap for bids - use negative price for max heap behavior
        self._bids: List[Tuple[float, int, Order]] = []
        # Min heap for asks
        self._asks: List[Tuple[float, int, Order]] = []
        # Map of order_id -> Order for quick lookup
        self._orders: Dict[str, Order] = {}
        # Sequence counter for FIFO ordering at same price
        self._seq = 0
        # List of all executed trades
        self.trades: List[Trade] = []

    def _next_seq(self) -> int:
        """Get the next sequence number for FIFO ordering.
        
        Returns:
            The next sequence number
        """
        self._seq += 1
        return self._seq

    def add_order(self, order: Order) -> List[Trade]:
        """Add an order to the book and attempt matching.
        
        Args:
            order: The order to add
            
        Returns:
            List of trades that resulted from matching
        """
        pass

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order by ID.
        
        Args:
            order_id: The ID of the order to cancel
            
        Returns:
            True if order was found and cancelled, False otherwise
        """
        pass

    def top_of_book(self) -> Tuple[Optional[Order], Optional[Order]]:
        """Get the best bid and ask orders.
        
        Returns:
            Tuple of (best_bid, best_ask), either can be None if no orders
        """
        pass
