"""Command-line interface for the limit order book."""

from models import Order, Side, new_order_id
from order_book import OrderBook
from firebase_client import MockFirebaseClient


def prompt_side() -> Side:
    """Prompt user to enter order side (buy/sell).
    
    Returns:
        Side.BUY or Side.SELL based on user input
    """
    while True:
        choice = input("Side (b)uy or (s)ell: ").strip().lower()
        if choice == 'b':
            return Side.BUY
        elif choice == 's':
            return Side.SELL
        else:
            print("Invalid input. Please enter 'b' for buy or 's' for sell.")


def prompt_float(msg: str) -> float:
    """Prompt user to enter a positive float value.
    
    Args:
        msg: The prompt message to display
        
    Returns:
        A positive float value entered by user
    """
    while True:
        try:
            value = float(input(msg).strip())
            if value > 0:
                return value
            print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def prompt_int(msg: str) -> int:
    """Prompt user to enter a positive integer value.
    
    Args:
        msg: The prompt message to display
        
    Returns:
        A positive integer value entered by user
    """
    while True:
        try:
            value = int(input(msg).strip())
            if value > 0:
                return value
            print("Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")


def show_book(order_book: OrderBook):
    """Display the current top of book (best bid and ask).
    
    Args:
        order_book: The OrderBook instance to display
    """
    best_bid, best_ask = order_book.top_of_book()
    
    print("\n--- Top of Book ---")
    if best_bid:
        print(f"Best Bid: ${best_bid.price:.2f} x {best_bid.qty}")
    else:
        print("Best Bid: None")
    
    if best_ask:
        print(f"Best Ask: ${best_ask.price:.2f} x {best_ask.qty}")
    else:
        print("Best Ask: None")
    print("-------------------\n")


def show_trades(order_book: OrderBook):
    """Display all executed trades.
    
    Args:
        order_book: The OrderBook instance containing trades
    """
    trades = order_book.trades
    
    print("\n--- Trade History ---")
    if not trades:
        print("No trades executed yet.")
    else:
        for i, trade in enumerate(trades, 1):
            print(f"{i}. {trade.qty} @ ${trade.price:.2f}")
            print(f"   Buy: {trade.buy_order_id[:8]}...")
            print(f"   Sell: {trade.sell_order_id[:8]}...")
    print("---------------------\n")


def main():
    """Main entry point for the CLI application."""
    print("Limit Order Book CLI")
    print("====================")
    print()
    print("Commands:")
    print("  1) Add order")
    print("  2) Cancel order")
    print("  3) Show top of book")
    print("  4) Show trades")
    print("  q) Quit")
    print()


if __name__ == "__main__":
    main()
