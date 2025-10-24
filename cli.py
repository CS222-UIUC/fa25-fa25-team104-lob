from models import Order, Side, new_order_id
from order_book import OrderBook
from firebase_client import MockFirebaseClient


def prompt_side() -> Side:
    """Ask user for side input."""
    # prompt until 'b' or 's' entered
    pass


def prompt_float(msg: str) -> float:
    """Ask for a float input."""
    pass


def prompt_int(msg: str) -> int:
    """Ask for a positive integer input."""
    pass


def show_book(order_book: OrderBook):
    """Display current best bid/ask."""
    # call order_book.top_of_book()
    # print results nicely
    pass


def main():
    """Main command-line loop."""
    # initialize firebase client and order book
    # print menu options:
    #   1) Add order
    #   2) Cancel order
    #   3) Show top of book
    #   4) Show trades
    #   q) Quit

    # loop until user quits:
    #   if add order:
    #       gather user_id, side, price, qty
    #       call firebase.create_order(payload)
    #       if success, call order_book.add_order(Order(...))
    #       display any trades
    #   if cancel order:
    #       prompt for id
    #       firebase.delete_order(id)
    #       order_book.cancel_order(id)
    #   if show book:
    #       call show_book()
    #   if show trades:
    #       print order_book.trades
    pass


if __name__ == "__main__":
    main()