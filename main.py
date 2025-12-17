import random

from firebase_client import FirestoreClient
from order_book import OrderBook
from cli import (
    add_trader_cli,
    switch_trader_cli,
    refresh_trader_cache,
    prompt_side,
    prompt_int,
    show_book,
)


def main():
    firebase = FirestoreClient()
    order_book = OrderBook()

    try:
        order_book.all_traders = firebase.get_all_traders()
    except Exception as e:
        print(f"Warning: could not fetch traders: {e}")

    if order_book.all_traders:
        chosen = random.choice(order_book.all_traders)
        tid = chosen.get("id") or chosen.get("traderId")
        name = chosen.get("name")
        order_book.current_trader = tid
        order_book.current_name = name if name else None
        try:
            tdoc = firebase.get_trader(tid)
            if tdoc:
                order_book.current_trader_balance_usd = int(tdoc.get("balanceUSD", 0))
                order_book.current_trader_reserved_usd = int(tdoc.get("reservedUSD", 0))
                order_book.current_trader_balance_instrument = int(tdoc.get("balanceInstrument", 0))
                order_book.current_trader_reserved_instrument = int(tdoc.get("reservedInstrument", 0))
        except Exception:
            order_book.current_trader_balance_usd = None
            order_book.current_trader_reserved_usd = None
            order_book.current_trader_balance_instrument = None
            order_book.current_trader_reserved_instrument = None

        print(f"Auto-selected current trader: {tid}{(' - '+order_book.current_name) if order_book.current_name else ''}")
    else:
        print("No traders found to auto-select.")

    while True:
        print("\nOptions:")
        print("1) Add trader")
        print("2) Switch trader")
        print("3) Add order")
        print("4) View/Cancel orders")
        print("5) Show top of book")
        print("6) Show trades")
        print("q) Quit\n")

        cur_id = getattr(order_book, "current_trader", None)
        cur_name = getattr(order_book, "current_name", None)
        header = f"(current trader: {cur_id}" + (f" - {cur_name}" if cur_name else "") + ")"
        print(header)

        if cur_id:
            bal_usd = order_book.current_trader_balance_usd
            res_usd = order_book.current_trader_reserved_usd
            bal_inst = order_book.current_trader_balance_instrument
            res_inst = order_book.current_trader_reserved_instrument
            print(f"  balanceUSD (cents): {bal_usd if bal_usd is not None else 'N/A'}")
            print(f"  reservedUSD (cents): {res_usd if res_usd is not None else 'N/A'}")
            print(f"  balanceInstrument (units): {bal_inst if bal_inst is not None else 'N/A'}")
            print(f"  reservedInstrument (units): {res_inst if res_inst is not None else 'N/A'}")

        choice = input("\nChoose an option: ").strip()
        if choice == "1":
            tid, name = add_trader_cli(firebase)
            order_book.current_trader = tid
            order_book.current_name = name
            refresh_trader_cache(firebase, order_book)
            print(f"Current trader set to {tid} - {name}")

        elif choice == "2":
            switch_trader_cli(firebase, order_book)

        elif choice == "3":
            user_id = getattr(order_book, "current_trader", None)
            if not user_id:
                user_id = input("No current trader set. Enter user ID: ").strip()
                order_book.current_trader = user_id
                try:
                    t = firebase.get_trader(user_id)
                    order_book.current_name = t.get("name") if t else None
                    if t:
                        order_book.current_trader_balance_usd = int(t.get("balanceUSD", 0))
                        order_book.current_trader_reserved_usd = int(t.get("reservedUSD", 0))
                        order_book.current_trader_balance_instrument = int(t.get("balanceInstrument", 0))
                        order_book.current_trader_reserved_instrument = int(t.get("reservedInstrument", 0))
                except Exception:
                    order_book.current_name = None
                    order_book.current_trader_balance_usd = None
                    order_book.current_trader_reserved_usd = None
                    order_book.current_trader_balance_instrument = None
                    order_book.current_trader_reserved_instrument = None

            side = prompt_side()
            price_cents = prompt_int("Enter order price in cents (integer): ")
            qty_micro = prompt_int("Enter order quantity (integer): ")

            try:
                created_order_id = firebase.create_order(user_id, side.name, "LIMIT", qty_micro, price_cents)
            except Exception as e:
                print(
                    "[create_order] Failed to create order in Firestore "
                    f"(user={user_id}, side={side.name}, qty={qty_micro}, price={price_cents}): {e}"
                )
                created_order_id = None

            if created_order_id:
                refresh_trader_cache(firebase, order_book)
                print("Order submitted. Matching handled server-side; check trades (option 6).")
            else:
                print("Failed to create order in Firestore.")

        elif choice == "4":
            cur_id = getattr(order_book, "current_trader", None)
            if not cur_id:
                print("No current trader selected. Choose option 2 first.")
                continue
            try:
                order_book.current_trades = firebase.get_trader_open_orders(cur_id)
            except Exception as e:
                print(f"Failed to load open orders: {e}")
                order_book.current_trades = []

            if not order_book.current_trades:
                print("No OPEN/PARTIAL orders found for current trader.")
                continue

            print("Open orders:")
            for idx, o in enumerate(order_book.current_trades, start=1):
                oid = o.get("id")
                side = o.get("side")
                price = o.get("price")
                rem = int(o.get("remainingQuantity", 0))
                status = o.get("status")
                price_display = price if price is not None else "MKT"
                print(f"{idx}) {oid} | {side} {rem} @ {price_display} | {status}")

            sel = input("Choose order number to cancel (or blank to abort): ").strip()
            if not sel:
                print("Cancel aborted.")
                continue

            chosen_order = None
            if sel.isdigit():
                idx = int(sel) - 1
                if 0 <= idx < len(order_book.current_trades):
                    chosen_order = order_book.current_trades[idx]
                else:
                    print("Invalid selection.")
                    continue
            else:
                for o in order_book.current_trades:
                    if o.get("id") == sel:
                        chosen_order = o
                        break
                if not chosen_order:
                    print("Order not found in current trader list.")
                    continue

            oid = chosen_order.get("id")
            try:
                ok = firebase.cancel_order(oid)
            except Exception as e:
                print(f"Cancel failed: {e}")
                ok = False
            if ok:
                refresh_trader_cache(firebase, order_book)
                print(f"Order {oid} cancelled.")
            else:
                print("Cancel failed or order not found.")

        elif choice == "5":
            try:
                depth = firebase.get_order_book_depth()
                order_book.bids = depth.get("bids", [])
                order_book.asks = depth.get("asks", [])
            except Exception as e:
                print(f"Failed to load order book: {e}")
                continue
            show_book(order_book)

        elif choice == "6":
            cur_id = getattr(order_book, "current_trader", None)
            if not cur_id:
                print("No current trader selected. Choose option 2 first.")
                continue
            try:
                order_book.current_trade_history = firebase.get_trader_trades(cur_id)
            except Exception as e:
                print(f"Failed to load trades: {e}")
                order_book.current_trade_history = []

            if not order_book.current_trade_history:
                print("No trades found for current trader.")
                continue

            print("\n--- Trades ---")
            for idx, trade in enumerate(order_book.current_trade_history, start=1):
                side = "BUY" if trade.get("buyTraderId") == cur_id else "SELL"
                qty = trade.get("quantity", 0)
                price = trade.get("price")
                price_display = price if price is not None else "N/A"
                ts = trade.get("timestamp", "")
                counterparty = trade.get("sellTraderId") if side == "BUY" else trade.get("buyTraderId")
                print(f"{idx}) {side} {qty} @ {price_display} | against {counterparty} | {ts}")
            print("--------------\n")

        elif choice == "q":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

