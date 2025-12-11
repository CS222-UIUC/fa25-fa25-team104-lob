from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore


# -----------------------------
# 1. Initialize Firestore
# -----------------------------
cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


# =============================
# TRADERS
# =============================

def create_trader(name: str, balance_usd: float, balance_instrument: float):
    """Create a trader in /traders"""
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
    doc = db.collection("traders").document(trader_id).get()
    if doc.exists:
        print(f"Trader {trader_id}: {doc.to_dict()}")
        return doc.to_dict()
    else:
        print(f"Trader {trader_id} not found.")
        return None


def update_trader(trader_id: str, updates: dict):
    """Update one or more fields for a trader"""
    db.collection("traders").document(trader_id).update(updates)
    print(f"Trader {trader_id} updated with {updates}")


def delete_trader(trader_id: str):
    """Delete a trader"""
    db.collection("traders").document(trader_id).delete()
    print(f"Trader {trader_id} deleted.")


# =============================
# ORDERS
# =============================

def create_order(trader_id: str, side: str, order_type: str, quantity: float, price: float = None):
    """Create an order in /orders"""
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
    doc = db.collection("orders").document(order_id).get()
    if doc.exists:
        print(f"Order {order_id}: {doc.to_dict()}")
        return doc.to_dict()
    else:
        print(f"Order {order_id} not found.")
        return None


def update_order(order_id: str, updates: dict):
    """Update fields of an order"""
    db.collection("orders").document(order_id).update(updates)
    print(f"Order {order_id} updated with {updates}")


def delete_order(order_id: str):
    """Delete an order"""
    db.collection("orders").document(order_id).delete()
    print(f"Order {order_id} deleted.")


# =============================
# TRADES
# =============================

def create_trade(buy_order_id: str, sell_order_id: str,
                 buy_trader_id: str, sell_trader_id: str,
                 price: float, quantity: float):
    """Create a trade in /trades"""
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
    doc = db.collection("trades").document(trade_id).get()
    if doc.exists:
        print(f"Trade {trade_id}: {doc.to_dict()}")
        return doc.to_dict()
    else:
        print(f"Trade {trade_id} not found.")
        return None


def update_trade(trade_id: str, updates: dict):
    """Update a trade (usually rare, but allowed)"""
    db.collection("trades").document(trade_id).update(updates)
    print(f"Trade {trade_id} updated with {updates}")


def delete_trade(trade_id: str):
    """Delete a trade"""
    db.collection("trades").document(trade_id).delete()
    print(f"Trade {trade_id} deleted.")




if __name__ == "__main__":
    print(" Firestore CRUD test starting...\n")

    # Create traders
    t1 = create_trader("Alice", 50000, 2.5)
    # t2 = create_trader("Bob", 20000, 5)

    # # Create orders
    # o1 = create_order(t1, "BUY", "LIMIT", 10, 101.5)
    # o2 = create_order(t2, "SELL", "LIMIT", 10, 101.5)

    # # Create trade
    # tr = create_trade(o1, o2, t1, t2, price=101.5, quantity=5)

    # print("\n--- Reading back ---")
    # get_trader(t1)
    # get_order(o1)
    # get_trade(tr)

    # print("\n--- Updating values ---")
    # update_trader(t1, {"balanceUSD": 48000})
    # update_order(o1, {"status": "FILLED", "remainingQuantity": 0})
    # update_trade(tr, {"price": 101.6})

    # print("\n--- Deleting everything ---")
    # delete_trade(tr)
    # delete_order(o1)
    # delete_order(o2)
    # delete_trader(t1)
    # delete_trader(t2)

    print("\n Done! Check your Firestore console for confirmation.")