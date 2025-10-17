import heapq
from typing import List, Dict, Optional, Tuple
from models import Order, Trade, Side


class OrderBook:
    def __init__(self):
        """Initialize min/max heaps, active order map, trade list, and sequence counter."""
        # self._bids = max heap (use negative price)
        # self._asks = min heap
        # self._orders = {order_id: Order}
        # self._seq = 0
        # self.trades = []
        pass

    def _next_seq(self) -> int:
        """Return next sequence number for FIFO ordering."""
        # increment internal counter and return
        pass

    def add_order(self, order: Order) -> List[Trade]:
        """Add order to book and attempt matching."""
        # assign seq number
        # add to correct heap depending on buy/sell
        # call private _try_match() to see if trade occurs
        # return list of trades generated
        pass

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order if it exists."""
        # remove from self._orders (lazy cancel)
        # return True if found, False otherwise
        pass

    def top_of_book(self) -> Tuple[Optional[Order], Optional[Order]]:
        """Return best bid and best ask orders."""
        # peek at top of bid/ask heaps (skip canceled or filled)
        # return (best_bid_order, best_ask_order)
        pass

    def _try_match(self) -> List[Trade]:
        """Attempt to match best bid and ask while prices cross."""
        # while best_bid.price >= best_ask.price:
        #   pop top orders
        #   compute trade qty = min(bid.qty, ask.qty)
        #   choose trade price (typically passive side)
        #   call _execute_trade(bid, ask, price, qty)
        #   push back remaining qty if partial fill
        # return list of executed trades
        pass

    def _execute_trade(self, buy: Order, sell: Order, price: float, qty: int) -> Trade:
        """Apply fills, reduce qty, remove if fully filled, and return a Trade object."""
        # update quantities
        # remove from self._orders if qty = 0
        # return new Trade(buy_id, sell_id, price, qty)
        pass