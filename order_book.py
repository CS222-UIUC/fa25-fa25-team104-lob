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

    def _clean_top_bid(self) -> Optional[Order]:
        """Remove cancelled/filled orders from top of bid heap.
        
        Returns:
            The top valid bid order, or None if heap is empty
        """
        while self._bids:
            neg_price, seq, order = self._bids[0]
            # Check if order is still active
            if order.id in self._orders and order.qty > 0:
                return order
            heapq.heappop(self._bids)
        return None

    def _clean_top_ask(self) -> Optional[Order]:
        """Remove cancelled/filled orders from top of ask heap.
        
        Returns:
            The top valid ask order, or None if heap is empty
        """
        while self._asks:
            price, seq, order = self._asks[0]
            # Check if order is still active
            if order.id in self._orders and order.qty > 0:
                return order
            heapq.heappop(self._asks)
        return None

    def add_order(self, order: Order) -> List[Trade]:
        """Add an order to the book and attempt matching.
        
        Args:
            order: The order to add
            
        Returns:
            List of trades that resulted from matching
        """
        # Assign sequence number for FIFO ordering
        order.seq = self._next_seq()
        
        # Add to order tracking
        self._orders[order.id] = order
        
        # Add to appropriate heap based on side
        if order.side == Side.BUY:
            # Use negative price for max heap behavior
            heapq.heappush(self._bids, (-order.price, order.seq, order))
        else:
            heapq.heappush(self._asks, (order.price, order.seq, order))
        
        # Try to match orders
        return self._try_match()

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order by ID using lazy deletion.
        
        The order is removed from the tracking dict but left in the heap.
        It will be cleaned up when it reaches the top of the heap.
        
        Args:
            order_id: The ID of the order to cancel
            
        Returns:
            True if order was found and cancelled, False otherwise
        """
        if order_id in self._orders:
            del self._orders[order_id]
            return True
        return False

    def top_of_book(self) -> Tuple[Optional[Order], Optional[Order]]:
        """Get the best bid and ask orders.
        
        Returns:
            Tuple of (best_bid, best_ask), either can be None if no orders
        """
        pass

    def _try_match(self) -> List[Trade]:
        """Attempt to match orders. Placeholder for now."""
        return []
