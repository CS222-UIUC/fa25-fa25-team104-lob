from models import Order, Side, new_order_id
from order_book import OrderBook
from firebase_client import MockFirebaseClient


def prompt_side() -> Side:
    """Ask user for side input."""
    # prompt until 'b' or 's' entered
    while True:
        side_input = input("Enter side (b for buy, s for sell): ").strip().lower()
        if side_input == "b":
            return Side.BUY
        elif side_input == "s":
            return Side.SELL
        else:
            print("Invalid input. Please enter 'b' or 's'.")


def prompt_float(msg: str) -> float:
    """Ask for a float input."""
    while True:
        try:
            return float(input(msg))
        except ValueError:
            print("Invalid number. Please enter a valid float.")


def prompt_int(msg: str) -> int:
    """Ask for a positive integer input."""
    while True:
        try:
            value = int(input(msg))
            if value > 0:
                return value
            print("Enter a positive integer.")
        except ValueError:
            print("Invalid number. Please enter an integer.")


def show_book(order_book: OrderBook):
    """Display current best bid/ask."""
    # call order_book.top_of_book()
    # print results nicely
    top_bid, top_ask = order_book.top_of_book()
    print("\n--- Top of Book ---")
    print(f"Best Bid: {top_bid if top_bid else 'None'}")
    print(f"Best Ask: {top_ask if top_ask else 'None'}")
    print("-------------------\n")


def main():
    """Main command-line loop."""
    # initialize firebase client and order book
    firebase = MockFirebaseClient()
    order_book = OrderBook()

    # print menu options:
    #   1) Add order
    #   2) Cancel order
    #   3) Show top of book
    #   4) Show trades
    #   q) Quit
    menu = """
Options:
1) Add order
2) Cancel order
3) Show top of book
4) Show trades
q) Quit
"""

    # loop until user quits:
    while True:
        print(menu)
        choice = input("Choose an option: ").strip().lower()

        #   if add order:
        #       gather user_id, side, price, qty
        #       call firebase.create_order(payload)
        #       if success, call order_book.add_order(Order(...))
        #       display any trades
        if choice == "1":
            user_id = input("Enter user ID: ").strip()
            side = prompt_side()
            price = prompt_float("Enter price: ")
            qty = prompt_int("Enter quantity: ")

            order_id = new_order_id()
            payload = {
                "order_id": order_id,
                "user_id": user_id,
                "side": side,
                "price": price,
                "qty": qty,
            }

            if firebase.create_order(payload):
                order = Order(order_id, user_id, side, price, qty)
                trades = order_book.add_order(order)
                if trades:
                    print("\nTrades executed:")
                    for trade in trades:
                        print(trade)
                else:
                    print("Order added with no trades.")
            else:
                print("Failed to create order in Firebase.")

        #   if cancel order:
        #       prompt for id
        #       firebase.delete_order(id)
        #       order_book.cancel_order(id)
        elif choice == "2":
            order_id = input("Enter order ID to cancel: ").strip()
            firebase.delete_order(order_id)
            order_book.cancel_order(order_id)
            print(f"Order {order_id} cancelled (if existed).")

        #   if show book:
        #       call show_book()
        elif choice == "3":
            show_book(order_book)

        #   if show trades:
        #       print order_book.trades
        elif choice == "4":
            print("\n--- Trades ---")
            for trade in order_book.trades:
                print(trade)
            print("--------------\n")

        elif choice == "q":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
