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
        pass

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

