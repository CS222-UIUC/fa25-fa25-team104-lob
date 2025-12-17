from models import Order, Side, new_order_id
from order_book import OrderBook
from firebase_client import FirestoreClient
from rich.console import Console
from rich.table import Table

console = Console()

def prompt_side() -> Side:
    """Ask user for side input."""
    while True:
        side_input = input("Enter side (b for buy, s for sell): ").strip().lower()
        if side_input == "b":
            return Side.BUY
        elif side_input == "s":
            return Side.SELL
        else:
            print("Invalid input. Please enter 'b' or 's'.")


def prompt_int(msg: str) -> int:
    """Ask for a positive integer input."""
    while True:
        try:
            value = int(input(msg))
            return value
        except ValueError:
            print("Invalid number. Please enter an integer.")


def show_book(order_book: OrderBook, levels: int = 10):
    """Display aggregated book with asks above bids and a mid-price marker."""
    bids = getattr(order_book, "bids", []) or []
    asks = getattr(order_book, "asks", []) or []

    table = Table(title="Order Book (cents)", show_lines=False)
    table.add_column("Side", justify="center")
    table.add_column("Qty", justify="right")
    table.add_column("Px (c)", justify="right")

    ask_slice = asks[:levels]
    for level in reversed(ask_slice):
        qty = level.get("quantity")
        price = level.get("price")
        table.add_row("ASK", str(qty) if qty is not None else "", str(price) if price is not None else "", style="red")

    best_bid = bids[0]["price"] if bids else None
    best_ask = asks[0]["price"] if asks else None
    if best_bid is not None and best_ask is not None:
        mid = (int(best_bid) + int(best_ask)) / 2
        mid_text = f"Mid: {mid:.1f}c"
    elif best_bid is not None:
        mid_text = f"Best Bid: {best_bid}c"
    elif best_ask is not None:
        mid_text = f"Best Ask: {best_ask}c"
    else:
        mid_text = "No market"
    table.add_row("", "", mid_text, style="bold")

    bid_slice = bids[:levels]
    for level in bid_slice:
        qty = level.get("quantity")
        price = level.get("price")
        table.add_row("BID", str(qty) if qty is not None else "", str(price) if price is not None else "", style="green")

    console.print("\n")
    console.print(table)
    # show cached trader info if available
    ct = getattr(order_book, "current_trader", None)
    if ct:
        print(f"Current trader: {ct}{(' - '+order_book.current_name) if order_book.current_name else ''}")
        print(f"  balanceUSD (cents): {order_book.current_trader_balance_usd if order_book.current_trader_balance_usd is not None else 'N/A'}")
        print(f"  reservedUSD (cents): {order_book.current_trader_reserved_usd if order_book.current_trader_reserved_usd is not None else 'N/A'}")
        print(f"  balanceInstrument (units): {order_book.current_trader_balance_instrument if order_book.current_trader_balance_instrument is not None else 'N/A'}")
        print(f"  reservedInstrument (units): {order_book.current_trader_reserved_instrument if order_book.current_trader_reserved_instrument is not None else 'N/A'}")
    print("")


def add_trader_cli(firebase) -> tuple:
    """Prompt for trader details and create trader via firebase if available.
    Returns (trader_id, name).
    """
    name = input("Trader name to add?: ").strip()
    balance_usd = prompt_int("Starting USD balance in cents: ")
    balance_instrument = prompt_int("Starting instrument balance (integer units): ")
    try:
        trader_id = firebase.create_trader(name, balance_usd, balance_instrument)
        print(f"Created trader {trader_id}")
        return trader_id, name
    except Exception as e:
        print(f"Firebase create_trader failed: {e}")
    trader_id = input("Enter an ID to assign to this trader (or leave blank to generate): ").strip()
    if not trader_id:
        trader_id = f"local-{name}-{new_order_id()}"
    print(f"Using trader id: {trader_id}")
    return trader_id, name


def switch_trader_cli(firebase, order_book: OrderBook):
    """Prompt to switch current trader; list all traders (if available) for selection."""
    try:
        order_book.all_traders = firebase.get_all_traders()
    except Exception as e:
        print(f"Warning: could not fetch traders: {e}")
        order_book.all_traders = []

    if order_book.all_traders:
        print("Available traders:")
        for i, t in enumerate(order_book.all_traders, start=1):
            tid = t.get("id") or t.get("traderId")
            name = t.get("name", "")
            print(f"{i}) {tid} {'- '+name if name else ''}")
        sel = input("Choose trader number to switch to (or enter ID, blank to cancel): ").strip()
        if not sel:
            print("Switch cancelled.")
            return
        # numeric selection
        if sel.isdigit():
            idx = int(sel) - 1
            if 0 <= idx < len(order_book.all_traders):
                chosen = order_book.all_traders[idx]
                tid = chosen.get("id") or chosen.get("traderId")
                name = chosen.get("name")
            else:
                print("Invalid selection.")
                return
        else:
            # treat as id
            tid = sel
            name = None
            try:
                t = firebase.get_trader(tid)
                name = t.get("name") if t else None
            except Exception:
                name = None
    else:
        # fallback to prompting for id (previous behavior)
        current_id = getattr(order_book, "current_trader", None)
        current_name = getattr(order_book, "current_name", None)
        print(f"Current trader: {current_id if current_id else 'None'}{(' - '+current_name) if current_name else ''}")
        tid = input("Enter trader ID to switch to (or blank to cancel): ").strip()
        if not tid:
            print("Switch cancelled.")
            return
        name = None
        if hasattr(firebase, "get_trader"):
            try:
                t = firebase.get_trader(tid)
                if t is None:
                    print("Trader not found in Firebase. Switch aborted.")
                    return
                name = t.get("name")
            except Exception as e:
                print(f"Firebase get_trader failed: {e} -- proceeding to set trader anyway.")

    # set cached fields on order_book
    order_book.current_trader = tid
    order_book.current_name = name if name else None

    # try to fetch and cache balances/reserves
    try:
        tdoc = firebase.get_trader(tid)
        if tdoc:
            order_book.current_trader_balance_usd = int(tdoc.get("balanceUSD", 0))
            order_book.current_trader_reserved_usd = int(tdoc.get("reservedUSD", 0))
            order_book.current_trader_balance_instrument = int(tdoc.get("balanceInstrument", 0))
            order_book.current_trader_reserved_instrument = int(tdoc.get("reservedInstrument", 0))
        else:
            order_book.current_trader_balance_usd = None
            order_book.current_trader_reserved_usd = None
            order_book.current_trader_balance_instrument = None
            order_book.current_trader_reserved_instrument = None
    except Exception:
        order_book.current_trader_balance_usd = None
        order_book.current_trader_reserved_usd = None
        order_book.current_trader_balance_instrument = None
        order_book.current_trader_reserved_instrument = None

    print(f"Switched current trader to: {tid}{(' - '+order_book.current_name) if order_book.current_name else ''}")


def refresh_trader_cache(firebase: FirestoreClient, order_book: OrderBook) -> None:
    """Fetch current trader doc and update cached balances/reserves on order_book."""
    tid = getattr(order_book, "current_trader", None)
    if not tid:
        order_book.current_trader_balance_usd = None
        order_book.current_trader_reserved_usd = None
        order_book.current_trader_balance_instrument = None
        order_book.current_trader_reserved_instrument = None
        return
    try:
        print(f"[refresh_trader_cache] fetching trader {tid}...")
        tdoc = firebase.get_trader(tid)
        if tdoc:
            order_book.current_trader_balance_usd = int(tdoc.get("balanceUSD", 0))
            order_book.current_trader_reserved_usd = int(tdoc.get("reservedUSD", 0))
            order_book.current_trader_balance_instrument = int(tdoc.get("balanceInstrument", 0))
            order_book.current_trader_reserved_instrument = int(tdoc.get("reservedInstrument", 0))
            order_book.current_name = tdoc.get("name", order_book.current_name)
            print(
                "[refresh_trader_cache] updated balances: "
                f"balanceUSD={order_book.current_trader_balance_usd}, "
                f"reservedUSD={order_book.current_trader_reserved_usd}, "
                f"balanceInstrument={order_book.current_trader_balance_instrument}, "
                f"reservedInstrument={order_book.current_trader_reserved_instrument}"
            )
        else:
            order_book.current_trader_balance_usd = None
            order_book.current_trader_reserved_usd = None
            order_book.current_trader_balance_instrument = None
            order_book.current_trader_reserved_instrument = None
            print(f"[refresh_trader_cache] trader {tid} not found.")
    except Exception as e:
        print(f"[refresh_trader_cache] failed to fetch trader {tid}: {e}")
        order_book.current_trader_balance_usd = None
        order_book.current_trader_reserved_usd = None
        order_book.current_trader_balance_instrument = None
        order_book.current_trader_reserved_instrument = None