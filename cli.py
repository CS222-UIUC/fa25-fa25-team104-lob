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
