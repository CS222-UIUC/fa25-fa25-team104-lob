from typing import Optional, List, Dict


class OrderBook:

    def __init__(self):
        # Depth snapshots loaded from Firestore
        self.bids: List[Dict[str, int]] = []
        self.asks: List[Dict[str, int]] = []

        # Trader metadata cached for quick display
        self.current_trader: Optional[str] = None
        self.current_name: Optional[str] = None
        self.all_traders: List[Dict[str, str]] = []
        self.current_trades: List[Dict[str, int]] = []
        self.current_trade_history: List[Dict[str, int]] = []

        # Cached balances/reserves (all integers)
        self.current_trader_balance_usd: Optional[int] = None
        self.current_trader_reserved_usd: Optional[int] = None
        self.current_trader_balance_instrument: Optional[int] = None
        self.current_trader_reserved_instrument: Optional[int] = None
