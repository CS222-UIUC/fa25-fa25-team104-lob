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
        best_bid = self._clean_top_bid()
        best_ask = self._clean_top_ask()
        return (best_bid, best_ask)

    def _execute_trade(self, buy: Order, sell: Order, price: float, qty: int) -> Trade:
        """Execute a trade between a buy and sell order.
        
        Args:
            buy: The buy order
            sell: The sell order
            price: The execution price
            qty: The quantity to trade
            
        Returns:
            The Trade object representing this execution
        """
        # Reduce quantities
        buy.qty -= qty
        sell.qty -= qty
        
        # Remove fully filled orders from tracking
        if buy.qty == 0:
            if buy.id in self._orders:
                del self._orders[buy.id]
        if sell.qty == 0:
            if sell.id in self._orders:
                del self._orders[sell.id]
        
        # Create and record the trade
        trade = Trade(
            buy_order_id=buy.id,
            sell_order_id=sell.id,
            price=price,
            qty=qty
        )
        self.trades.append(trade)
        return trade

    def _try_match(self) -> List[Trade]:
        """Attempt to match best bid and ask while prices cross.
        
        A match occurs when the best bid price >= best ask price.
        Uses price-time priority: best price first, then earliest order.
        Trade price is the passive order's price (the one already in the book).
        
        Returns:
            List of trades executed during matching
        """
        executed_trades: List[Trade] = []
        
        while True:
            best_bid = self._clean_top_bid()
            best_ask = self._clean_top_ask()
            
            # Check if we can match
            if best_bid is None or best_ask is None:
                break
            if best_bid.price < best_ask.price:
                break
            
            # Prices cross - we have a match!
            # Pop both orders from heaps
            heapq.heappop(self._bids)
            heapq.heappop(self._asks)
            
            # Calculate trade quantity and price
            trade_qty = min(best_bid.qty, best_ask.qty)
            # Use the passive order's price (earlier order)
            if best_bid.seq < best_ask.seq:
                trade_price = best_bid.price
            else:
                trade_price = best_ask.price
            
            # Execute the trade
            trade = self._execute_trade(best_bid, best_ask, trade_price, trade_qty)
            executed_trades.append(trade)
            
            # Push back orders with remaining quantity
            if best_bid.qty > 0:
                heapq.heappush(self._bids, (-best_bid.price, best_bid.seq, best_bid))
            if best_ask.qty > 0:
                heapq.heappush(self._asks, (best_ask.price, best_ask.seq, best_ask))
        
        return executed_trades
