from datetime import datetime
from typing import Optional, Dict, Any, List
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import FieldFilter
from utils import price_times_qty_to_cents, validate_non_negative_int


class FirestoreClient:
    def __init__(self, cred_path: str = "serviceAccount.json"):
        # initialize firebase app only once
        try:
            firebase_admin.get_app()
        except ValueError:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    # ----------------------------
    # TRADERS
    # ----------------------------
    def create_trader(self, name: str, balance_usd: int, balance_instrument: int) -> str:
        """
        All numeric balances are integers:
          - balanceUSD and reservedUSD are integer cents
          - balanceInstrument and reservedInstrument are integer whole units
        """
        trader_data = {
            "name": name,
            "balanceUSD": int(balance_usd),
            "balanceInstrument": int(balance_instrument),
            "reservedUSD": 0,
            "reservedInstrument": 0,
            "createdAt": datetime.utcnow().isoformat(),
        }
        doc_ref = self.db.collection("traders").add(trader_data)
        trader_id = doc_ref[1].id
        return trader_id

    def get_trader(self, trader_id: str) -> Optional[Dict[str, Any]]:
        doc = self.db.collection("traders").document(trader_id).get()
        return doc.to_dict() if doc.exists else None

    def get_all_traders(self) -> List[Dict[str, Any]]:
        docs = self.db.collection("traders").stream()
        traders: List[Dict[str, Any]] = []
        for doc in docs:
            data = doc.to_dict() or {}
            data["id"] = doc.id
            traders.append(data)
        return traders

    def get_trader_open_orders(self, trader_id: str) -> List[Dict[str, Any]]:
        """Return all OPEN/PARTIAL orders for a trader ordered by timestamp."""
        query = (
            self.db.collection("orders")
            .where(filter=FieldFilter("traderId", "==", trader_id))
            .where(filter=FieldFilter("status", "in", ["OPEN", "PARTIAL"]))
            .order_by("timestamp", direction=firestore.Query.ASCENDING)
        )
        orders: List[Dict[str, Any]] = []
        for doc in query.stream():
            data = doc.to_dict() or {}
            data["id"] = doc.id
            orders.append(data)
        return orders

    def update_trader(self, trader_id: str, updates: dict) -> None:
        self.db.collection("traders").document(trader_id).update(updates)

    def delete_trader(self, trader_id: str) -> None:
        self.db.collection("traders").document(trader_id).delete()

    def get_trader_trades(self, trader_id: str) -> List[Dict[str, Any]]:
        """Return trades where trader participated as buyer or seller, newest first."""
        trades: Dict[str, Dict[str, Any]] = {}
        buy_query = self.db.collection("trades").where(filter=FieldFilter("buyTraderId", "==", trader_id))
        sell_query = self.db.collection("trades").where(filter=FieldFilter("sellTraderId", "==", trader_id))

        for doc in buy_query.stream():
            data = doc.to_dict() or {}
            data["id"] = doc.id
            trades[doc.id] = data

        for doc in sell_query.stream():
            data = doc.to_dict() or {}
            data["id"] = doc.id
            trades[doc.id] = data

        results = list(trades.values())
        results.sort(key=lambda t: t.get("timestamp", ""), reverse=True)
        return results

    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an OPEN/PARTIAL order and release its reserved balances.
        Returns True when the order was updated, False otherwise.
        """
        order_ref = self.db.collection("orders").document(order_id)

        @firestore.transactional
        def txn_cancel(transaction):
            order_snap = order_ref.get(transaction=transaction)
            if not order_snap.exists:
                return False
            order = order_snap.to_dict() or {}
            status = (order.get("status") or "").upper()
            if status in ("FILLED", "CANCELLED"):
                return False

            trader_id = order.get("traderId")
            if not trader_id:
                raise ValueError("Order missing traderId")
            trader_ref = self.db.collection("traders").document(trader_id)
            trader_snap = trader_ref.get(transaction=transaction)
            if not trader_snap.exists:
                raise ValueError("Trader not found for cancel")
            trader = trader_snap.to_dict() or {}

            side = (order.get("side") or "BUY").upper()
            reserved_usd = int(order.get("reservedUSD", 0))
            reserved_inst = int(order.get("reservedInstrument", 0))

            trader_updates: Dict[str, Any] = {}
            if side == "BUY":
                new_reserved_usd = int(trader.get("reservedUSD", 0)) - reserved_usd
                if new_reserved_usd < 0:
                    raise ValueError("cancel would make reservedUSD negative")
                trader_updates["reservedUSD"] = new_reserved_usd
                if reserved_usd:
                    trader_updates["balanceUSD"] = int(trader.get("balanceUSD", 0)) + reserved_usd
            else:
                new_reserved_inst = int(trader.get("reservedInstrument", 0)) - reserved_inst
                if new_reserved_inst < 0:
                    raise ValueError("cancel would make reservedInstrument negative")
                trader_updates["reservedInstrument"] = new_reserved_inst
                if reserved_inst:
                    trader_updates["balanceInstrument"] = int(trader.get("balanceInstrument", 0)) + reserved_inst

            transaction.update(order_ref, {
                "status": "CANCELLED",
                "remainingQuantity": 0,
                "reservedUSD": 0,
                "reservedInstrument": 0,
            })
            if trader_updates:
                transaction.update(trader_ref, trader_updates)
            return True

        try:
            return bool(txn_cancel(self.db.transaction()))
        except Exception:
            return False

    def get_order_book_depth(self, levels: int = 10, per_side_limit: int = 100) -> Dict[str, List[Dict[str, int]]]:
        """
        Aggregate top N price levels for both sides.
        Returns {"bids": [{"price": cents, "quantity": qty}, ...], "asks": [...]}
        """

        def collect(side: str, direction, limit: int) -> List[Dict[str, int]]:
            query = (
                self.db.collection("orders")
                .where(filter=FieldFilter("side", "==", side))
                .where(filter=FieldFilter("status", "in", ["OPEN", "PARTIAL"]))
                .order_by("price", direction=direction)
                .order_by("timestamp", direction=firestore.Query.ASCENDING)
                .limit(limit)
            )
            results: List[Dict[str, int]] = []
            current_price = None
            current_qty = 0

            for doc in query.stream():
                data = doc.to_dict() or {}
                price = data.get("price")
                if price is None:
                    continue
                price = int(price)
                qty = int(data.get("remainingQuantity", 0))
                if qty <= 0:
                    continue
                if current_price is None:
                    current_price = price
                    current_qty = qty
                elif price == current_price:
                    current_qty += qty
                else:
                    results.append({"price": current_price, "quantity": current_qty})
                    if len(results) >= levels:
                        return results
                    current_price = price
                    current_qty = qty

            if current_price is not None and len(results) < levels:
                results.append({"price": current_price, "quantity": current_qty})
            return results

        bids = collect("BUY", firestore.Query.DESCENDING, per_side_limit)
        asks = collect("SELL", firestore.Query.ASCENDING, per_side_limit)
        return {"bids": bids, "asks": asks}

    # ----------------------------
    # ORDERS + matching (integer arithmetic)
    # ----------------------------
    def create_order(self, trader_id: str, side: str, order_type: str, quantity: int, price: Optional[int] = None) -> str:
        """
        Create an order in integer units:
          - quantity: instrument whole units (int)
          - price: price in integer cents (int) for LIMIT orders
        Reserves funds/instrument in a transaction and writes an order doc that contains per-order reserved fields:
          - reservedUSD (int) for BUY orders (cents)
          - reservedInstrument (int) for SELL orders (whole units)
        After order creation this function attempts immediate matching by querying the opposing side.
        """
        order_ref = self.db.collection("orders").document()  # reserve id

        order_data = {
            "traderId": trader_id,
            "side": side.upper(),
            "type": order_type.upper(),
            "price": int(price) if price is not None else None,
            "quantity": int(quantity),
            "remainingQuantity": int(quantity),
            "status": "OPEN",
            "timestamp": datetime.utcnow().isoformat(),
            # per-order reserve fields (filled below in txn)
            "reservedUSD": 0,
            "reservedInstrument": 0,
        }

        @firestore.transactional
        def txn_create(txn):
            trader_ref = self.db.collection("traders").document(trader_id)
            trader_snap = trader_ref.get(transaction=txn)
            if not trader_snap.exists:
                raise ValueError("Trader not found")
            trader = trader_snap.to_dict() or {}

            if side.upper() == "BUY":
                if price is None:
                    raise ValueError("LIMIT price required for BUY")
                # exact integer hold = price_cents * qty_units
                hold = price_times_qty_to_cents(int(price), int(quantity))
                available = int(trader.get("balanceUSD", 0)) - int(trader.get("reservedUSD", 0))
                if available < hold:
                    raise ValueError("Insufficient USD to place buy order")
                txn.update(trader_ref, {
                    "balanceUSD": int(trader.get("balanceUSD", 0)) - hold,
                    "reservedUSD": int(trader.get("reservedUSD", 0)) + hold,
                })
                order_data["reservedUSD"] = hold
            else:  # SELL
                available_inst = int(trader.get("balanceInstrument", 0)) - int(trader.get("reservedInstrument", 0))
                if available_inst < int(quantity):
                    raise ValueError("Insufficient instrument to place sell order")
                txn.update(trader_ref, {
                    "balanceInstrument": int(trader.get("balanceInstrument", 0)) - int(quantity),
                    "reservedInstrument": int(trader.get("reservedInstrument", 0)) + int(quantity),
                })
                order_data["reservedInstrument"] = int(quantity)

            txn.set(order_ref, order_data)
            return order_ref.id

        order_id = txn_create(self.db.transaction())

        # Attempt to match the freshly created order
        self._match_new_order(order_id)
        return order_id

    def _match_new_order(self, order_id: str) -> None:
        """
        Match the new order against opposing side orders (price and FIFO by timestamp).
        Each execution is settled in its own transaction.
        """
        new_order_snap = self.db.collection("orders").document(order_id).get()
        if not new_order_snap.exists:
            return
        new_order = new_order_snap.to_dict() or {}
        side = new_order.get("side", "BUY").upper()
        new_remaining = int(new_order.get("remainingQuantity", 0))
        new_price = int(new_order.get("price", 0)) if new_order.get("price") is not None else None

        if side == "BUY":
            # look for asks with price <= new_price
            opp_query = (
                self.db.collection("orders")
                .where(filter=FieldFilter("side", "==", "SELL"))
                .where(filter=FieldFilter("status", "in", ["OPEN", "PARTIAL"]))
                .order_by("price", direction=firestore.Query.ASCENDING)
                .order_by("timestamp", direction=firestore.Query.ASCENDING)
            )
        else:
            opp_query = (
                self.db.collection("orders")
                .where(filter=FieldFilter("side", "==", "BUY"))
                .where(filter=FieldFilter("status", "in", ["OPEN", "PARTIAL"]))
                .order_by("price", direction=firestore.Query.DESCENDING)
                .order_by("timestamp", direction=firestore.Query.ASCENDING)
            )

        for doc in opp_query.stream():
            if new_remaining <= 0:
                break
            opp = doc.to_dict() or {}
            opp_id = doc.id
            opp_price = int(opp.get("price", 0)) if opp.get("price") is not None else None
            opp_rem = int(opp.get("remainingQuantity", 0))

            # price crossing check (None price should not match)
            if new_price is None or opp_price is None:
                break
            if side == "BUY" and opp_price > new_price:
                break
            if side == "SELL" and opp_price < new_price:
                break
            if opp_rem <= 0:
                continue

            exec_qty = min(new_remaining, opp_rem)
            trade_price = opp_price  # passive side price

            success = self._settle_trade_transaction(
                buy_order_id=(order_id if side == "BUY" else opp_id),
                sell_order_id=(opp_id if side == "BUY" else order_id),
                price=trade_price,
                quantity=exec_qty,
            )
            if success:
                new_remaining -= exec_qty
            else:
                # refresh new_remaining if contention occurred
                new_order_snap = self.db.collection("orders").document(order_id).get()
                if not new_order_snap.exists:
                    new_remaining = 0
                    break
                new_order = new_order_snap.to_dict() or {}
                new_remaining = int(new_order.get("remainingQuantity", 0))

        return

    def _settle_trade_transaction(self, buy_order_id: str, sell_order_id: str, price: int, quantity: int) -> bool:
        """
        Atomic settlement using integer arithmetic (price in cents, quantity in whole units).
        Returns True on successful commit, False otherwise.
        """
        trx = self.db.transaction()
        buy_order_ref = self.db.collection("orders").document(buy_order_id)
        sell_order_ref = self.db.collection("orders").document(sell_order_id)

        @firestore.transactional
        def txn_settle(transaction):
            b_snap = buy_order_ref.get(transaction=transaction)
            s_snap = sell_order_ref.get(transaction=transaction)
            if not b_snap.exists or not s_snap.exists:
                raise ValueError("Order not found")

            b = b_snap.to_dict() or {}
            s = s_snap.to_dict() or {}

            b_rem = int(b.get("remainingQuantity", 0))
            s_rem = int(s.get("remainingQuantity", 0))

            exec_qty = min(quantity, b_rem, s_rem)
            if exec_qty <= 0:
                return False

            buy_tr_ref = self.db.collection("traders").document(b.get("traderId"))
            sell_tr_ref = self.db.collection("traders").document(s.get("traderId"))

            buy_tr_snap = buy_tr_ref.get(transaction=transaction)
            sell_tr_snap = sell_tr_ref.get(transaction=transaction)
            if not buy_tr_snap.exists or not sell_tr_snap.exists:
                raise ValueError("Trader doc missing during settlement")

            buy_tr = buy_tr_snap.to_dict() or {}
            sell_tr = sell_tr_snap.to_dict() or {}

            # Compute executed USD cents (exact): price_cents * qty_units
            executed_cents = price_times_qty_to_cents(int(price), int(exec_qty))

            # Per-order reserved amounts
            order_b_reserved = int(b.get("reservedUSD", 0))
            order_s_reserved_inst = int(s.get("reservedInstrument", 0))

            # Update buyer global reserved and instrument balance
            new_buy_reserved_global = int(buy_tr.get("reservedUSD", 0)) - executed_cents
            new_buy_balance_inst = int(buy_tr.get("balanceInstrument", 0)) + exec_qty
            if new_buy_reserved_global < 0:
                raise ValueError("Buyer reservedUSD would go negative")

            # Update seller global reserved and USD balance
            new_sell_reserved_inst_global = int(sell_tr.get("reservedInstrument", 0)) - exec_qty
            new_sell_balance_usd = int(sell_tr.get("balanceUSD", 0)) + executed_cents
            if new_sell_reserved_inst_global < 0:
                raise ValueError("Seller reservedInstrument would go negative")

            # Update per-order reserved bookkeeping
            order_b_reserved_after = order_b_reserved - executed_cents
            order_s_reserved_after = order_s_reserved_inst - exec_qty
            if order_b_reserved_after < 0 or order_s_reserved_after < 0:
                # concurrent change - abort
                raise ValueError("Order-level reserved would go negative")

            # Update orders remaining & status
            b_new_rem = b_rem - exec_qty
            s_new_rem = s_rem - exec_qty
            b_new_status = "FILLED" if b_new_rem <= 0 else "PARTIAL"
            s_new_status = "FILLED" if s_new_rem <= 0 else "PARTIAL"

            # Apply updates to orders
            transaction.update(buy_order_ref, {
                "remainingQuantity": b_new_rem,
                "status": b_new_status,
                "reservedUSD": order_b_reserved_after,
            })
            transaction.update(sell_order_ref, {
                "remainingQuantity": s_new_rem,
                "status": s_new_status,
                "reservedInstrument": order_s_reserved_after,
            })

            # Apply updates to traders (buyer and seller global balances/reserves)
            # For buyer: decrease reserved by executed_cents, increase instrument balance
            transaction.update(buy_tr_ref, {
                "reservedUSD": new_buy_reserved_global,
                "balanceInstrument": new_buy_balance_inst,
            })
            # For seller: decrease reservedInstrument, increase USD balance
            transaction.update(sell_tr_ref, {
                "reservedInstrument": new_sell_reserved_inst_global,
                "balanceUSD": new_sell_balance_usd,
            })

            # If buy order is now FILLED and had leftover per-order reserved (due to higher limit than execution price),
            # release leftover back to buyer balanceUSD
            if b_new_status == "FILLED" and order_b_reserved_after > 0:
                leftover = order_b_reserved_after
                transaction.update(buy_tr_ref, {
                    "reservedUSD": int(new_buy_reserved_global) - leftover,
                    "balanceUSD": int(buy_tr.get("balanceUSD", 0)) + leftover,
                })
                transaction.update(buy_order_ref, {"reservedUSD": 0})

            # Create trade doc
            trade_ref = self.db.collection("trades").document()
            trade_data = {
                "buyOrderId": buy_order_id,
                "sellOrderId": sell_order_id,
                "buyTraderId": b.get("traderId"),
                "sellTraderId": s.get("traderId"),
                "price": int(price),
                "quantity": int(exec_qty),
                "timestamp": datetime.utcnow().isoformat(),
            }
            transaction.set(trade_ref, trade_data)
            return True

        try:
            result = txn_settle(trx)
            return bool(result)
        except Exception:
            return False

    # ----------------------------
    # ORDERS
    # ----------------------------
    def create_order_old(self, trader_id: str, side: str, order_type: str, quantity: float, price: float = None) -> str:
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
        doc_ref = self.db.collection("orders").add(order_data)
        return doc_ref[1].id

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        doc = self.db.collection("orders").document(order_id).get()
        return doc.to_dict() if doc.exists else None

    def update_order(self, order_id: str, updates: dict) -> None:
        self.db.collection("orders").document(order_id).update(updates)

    def delete_order(self, order_id: str) -> None:
        self.db.collection("orders").document(order_id).delete()

    # ----------------------------
    # TRADES
    # ----------------------------
    def create_trade(self, buy_order_id: str, sell_order_id: str,
                     buy_trader_id: str, sell_trader_id: str,
                     price: float, quantity: float) -> str:
        trade_data = {
            "buyOrderId": buy_order_id,
            "sellOrderId": sell_order_id,
            "buyTraderId": buy_trader_id,
            "sellTraderId": sell_trader_id,
            "price": price,
            "quantity": quantity,
            "timestamp": datetime.utcnow().isoformat(),
        }
        doc_ref = self.db.collection("trades").add(trade_data)
        return doc_ref[1].id

    def get_trade(self, trade_id: str) -> Optional[Dict[str, Any]]:
        doc = self.db.collection("trades").document(trade_id).get()
        return doc.to_dict() if doc.exists else None

    def update_trade(self, trade_id: str, updates: dict) -> None:
        self.db.collection("trades").document(trade_id).update(updates)

    def delete_trade(self, trade_id: str) -> None:
        self.db.collection("trades").document(trade_id).delete()
