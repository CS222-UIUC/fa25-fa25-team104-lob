"""Firebase client for persisting orders to Firestore.

This module provides both real Firebase operations and a mock client for testing.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid

# Try to import Firebase, but don't fail if not installed
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    firebase_admin = None
    credentials = None
    firestore = None

# Global database reference (initialized lazily)
_db = None


def _get_db():
    """Get or initialize the Firestore database client."""
    global _db
    if _db is None and FIREBASE_AVAILABLE:
        if not firebase_admin._apps:
            cred = credentials.Certificate("serviceAccount.json")
            firebase_admin.initialize_app(cred)
        _db = firestore.client()
    return _db


# =============================
# MOCK CLIENT FOR TESTING
# =============================

class MockFirebaseClient:
    """In-memory mock implementation for testing without Firebase.
    
    Stores orders in a dictionary, simulating database operations.
    Useful for local development and unit testing.
    """

    def __init__(self):
        """Initialize the mock client with empty storage."""
        self._store: Dict[str, Dict[str, Any]] = {}

    def create_order(self, order_data: Dict[str, Any]) -> str:
        """Create an order in memory.
        
        Args:
            order_data: Dictionary containing order fields
            
        Returns:
            The generated order ID
        """
        order_id = order_data.get('id') or order_data.get('order_id') or uuid.uuid4().hex
        order_data['id'] = order_id
        self._store[order_id] = order_data.copy()
        return order_id

    def delete_order(self, order_id: str) -> bool:
        """Delete an order from memory.
        
        Args:
            order_id: The ID of the order to delete
            
        Returns:
            True if deleted, False if not found
        """
        if order_id in self._store:
            del self._store[order_id]
            return True
        return False

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an order from memory.
        
        Args:
            order_id: The ID of the order to retrieve
            
        Returns:
            Order data dict if found, None otherwise
        """
        return self._store.get(order_id)

    def list_orders(self) -> List[Dict[str, Any]]:
        """List all orders in memory.
        
        Returns:
            List of all order data dicts
        """
        return list(self._store.values())


# =============================
# TRADERS (Real Firebase)
# =============================

def create_trader(name: str, balance_usd: float, balance_instrument: float):
    """Create a trader in /traders"""
    db = _get_db()
    if not db:
        print("Firebase not available")
        return None
    trader_data = {
        "name": name,
        "balanceUSD": balance_usd,
        "balanceInstrument": balance_instrument,
        "createdAt": datetime.utcnow().isoformat(),
    }
    doc_ref = db.collection("traders").add(trader_data)
    trader_id = doc_ref[1].id
    print(f"Trader created: {trader_id}")
    return trader_id


def get_trader(trader_id: str):
    """Fetch a trader by document ID"""
    db = _get_db()
    if not db:
        return None
    doc = db.collection("traders").document(trader_id).get()
    if doc.exists:
        print(f"Trader {trader_id}: {doc.to_dict()}")
        return doc.to_dict()
    else:
        print(f"Trader {trader_id} not found.")
        return None


def update_trader(trader_id: str, updates: dict):
    """Update one or more fields for a trader"""
    db = _get_db()
    if not db:
        return
    db.collection("traders").document(trader_id).update(updates)
    print(f"Trader {trader_id} updated with {updates}")


def delete_trader(trader_id: str):
    """Delete a trader"""
    db = _get_db()
    if not db:
        return
    db.collection("traders").document(trader_id).delete()
    print(f"Trader {trader_id} deleted.")


# =============================
# ORDERS (Real Firebase)
# =============================

def create_order(trader_id: str, side: str, order_type: str, quantity: float, price: float = None):
    """Create an order in /orders"""
    db = _get_db()
    if not db:
        print("Firebase not available")
        return None
    order_data = {
        "traderId": trader_id,
        "side": side.upper(),
        "type": order_type.upper(),
        "price": price,
        "quantity": quantity,
        "remainingQuantity": quantity,
        "status": "OPEN",
        "timestamp": datetime.utcnow().isoformat(),
    }
    doc_ref = db.collection("orders").add(order_data)
    order_id = doc_ref[1].id
    print(f"Order created: {order_id}")
    return order_id


def get_order(order_id: str):
    """Fetch a specific order"""
    db = _get_db()
    if not db:
        return None
    doc = db.collection("orders").document(order_id).get()
    if doc.exists:
        print(f"Order {order_id}: {doc.to_dict()}")
        return doc.to_dict()
    else:
        print(f"Order {order_id} not found.")
        return None


def update_order(order_id: str, updates: dict):
    """Update fields of an order"""
    db = _get_db()
    if not db:
        return
    db.collection("orders").document(order_id).update(updates)
    print(f"Order {order_id} updated with {updates}")


def delete_order(order_id: str):
    """Delete an order"""
    db = _get_db()
    if not db:
        return
    db.collection("orders").document(order_id).delete()
    print(f"Order {order_id} deleted.")


# =============================
# TRADES (Real Firebase)
# =============================

def create_trade(buy_order_id: str, sell_order_id: str,
                 buy_trader_id: str, sell_trader_id: str,
                 price: float, quantity: float):
    """Create a trade in /trades"""
    db = _get_db()
    if not db:
        print("Firebase not available")
        return None
    trade_data = {
        "buyOrderId": buy_order_id,
        "sellOrderId": sell_order_id,
        "buyTraderId": buy_trader_id,
        "sellTraderId": sell_trader_id,
        "price": price,
        "quantity": quantity,
        "timestamp": datetime.utcnow().isoformat(),
    }
    doc_ref = db.collection("trades").add(trade_data)
    trade_id = doc_ref[1].id
    print(f"Trade created: {trade_id}")
    return trade_id


def get_trade(trade_id: str):
    """Fetch a trade"""
    db = _get_db()
    if not db:
        return None
    doc = db.collection("trades").document(trade_id).get()
    if doc.exists:
        print(f"Trade {trade_id}: {doc.to_dict()}")
        return doc.to_dict()
    else:
        print(f"Trade {trade_id} not found.")
        return None


def update_trade(trade_id: str, updates: dict):
    """Update a trade (usually rare, but allowed)"""
    db = _get_db()
    if not db:
        return
    db.collection("trades").document(trade_id).update(updates)
    print(f"Trade {trade_id} updated with {updates}")


def delete_trade(trade_id: str):
    """Delete a trade"""
    db = _get_db()
    if not db:
        return
    db.collection("trades").document(trade_id).delete()
    print(f"Trade {trade_id} deleted.")
