"""Command-line interface for the limit order book."""

from models import Order, Side, new_order_id
from order_book import OrderBook
from firebase_client import MockFirebaseClient
from utils import validate_price, validate_quantity, format_price, format_quantity


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
            if validate_price(value):
                return value
            print("Please enter a valid price (0 < price <= 1,000,000).")
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
            if validate_quantity(value):
                return value
            print("Please enter a valid quantity (0 < qty <= 1,000,000).")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")


def show_book(order_book: OrderBook):
    """Display the current top of book (best bid and ask).
    
    Args:
        order_book: The OrderBook instance to display
    """
    best_bid, best_ask = order_book.top_of_book()
    
    print("\n--- Top of Book ---")
    print(f"Active orders: {order_book.order_count()}")
    print()
    
    if best_bid:
        print(f"Best Bid: {format_price(best_bid.price)} x {format_quantity(best_bid.qty)}")
    else:
        print("Best Bid: None")
    
    if best_ask:
        print(f"Best Ask: {format_price(best_ask.price)} x {format_quantity(best_ask.qty)}")
    else:
        print("Best Ask: None")
    
    # Calculate and display spread
    if best_bid and best_ask:
        spread = best_ask.price - best_bid.price
        mid_price = (best_bid.price + best_ask.price) / 2
        spread_pct = (spread / mid_price) * 100 if mid_price > 0 else 0
        print(f"Spread: {format_price(spread)} ({spread_pct:.2f}%)")
    
    print("-------------------\n")


def show_trades(order_book: OrderBook):
    """Display all executed trades with statistics.
    
    Args:
        order_book: The OrderBook instance containing trades
    """
    trades = order_book.trades
    
    print("\n--- Trade History ---")
    if not trades:
        print("No trades executed yet.")
    else:
        total_volume = 0
        total_value = 0
        
        for i, trade in enumerate(trades, 1):
            print(f"{i}. {format_quantity(trade.qty)} @ {format_price(trade.price)}")
            print(f"   Buy: {trade.buy_order_id[:8]}...")
            print(f"   Sell: {trade.sell_order_id[:8]}...")
            total_volume += trade.qty
            total_value += trade.qty * trade.price
        
        print("\n--- Statistics ---")
        print(f"Total trades: {len(trades)}")
        print(f"Total volume: {format_quantity(total_volume)}")
        print(f"Total value: {format_price(total_value)}")
        if trades:
            avg_price = total_value / total_volume
            print(f"Average price: {format_price(avg_price)}")
    
    print("---------------------\n")


def show_orders(firebase_client: MockFirebaseClient):
    """Display all orders stored in Firebase.
    
    Args:
        firebase_client: Firebase client containing orders
    """
    orders = firebase_client.list_orders()
    
    print("\n--- All Orders ---")
    if not orders:
        print("No orders in the system.")
    else:
        for order in orders:
            side = order.get('side', 'UNKNOWN')
            price = order.get('price', 0)
            qty = order.get('qty', 0)
            order_id = order.get('id', 'unknown')[:8]
            user_id = order.get('user_id', 'unknown')
            print(f"  {order_id}... [{user_id}] {side} {format_quantity(qty)} @ {format_price(price)}")
    print("------------------\n")


def print_menu():
    """Print the command menu."""
    print("\nCommands:")
    print("  1) Add order")
    print("  2) Cancel order")
    print("  3) Show top of book")
    print("  4) Show trades")
    print("  5) Show all orders")
    print("  h) Help")
    print("  q) Quit")


def show_help():
    """Display detailed help information."""
    print("\n" + "=" * 50)
    print("LIMIT ORDER BOOK - HELP")
    print("=" * 50)
    print()
    print("This is a simple limit order book implementation.")
    print()
    print("COMMANDS:")
    print("---------")
    print("1) Add order    - Create a new buy or sell order")
    print("2) Cancel order - Cancel an existing order by ID")
    print("3) Top of book  - Show best bid and ask prices")
    print("4) Show trades  - Display executed trades history")
    print("5) All orders   - List all active orders")
    print("h) Help         - Show this help message")
    print("q) Quit         - Exit the application")
    print()
    print("ORDER MATCHING:")
    print("---------------")
    print("Orders are matched when a buy price >= sell price.")
    print("Matching uses price-time priority (best price first,")
    print("then earliest order at same price).")
    print()
    print("=" * 50 + "\n")


def add_order(firebase_client: MockFirebaseClient, order_book: OrderBook):
    """Handle adding a new order.
    
    Args:
        firebase_client: Firebase client for persistence
        order_book: OrderBook for matching
    """
    print("\n--- Add New Order ---")
    
    try:
        user_id = input("User ID: ").strip() or "default_user"
        side = prompt_side()
        price = prompt_float("Price: $")
        qty = prompt_int("Quantity: ")
        
        # Create order
        order_id = new_order_id()
        order = Order(
            id=order_id,
            user_id=user_id,
            side=side,
            price=price,
            qty=qty
        )
        
        # Save to Firebase
        order_data = {
            'id': order_id,
            'user_id': user_id,
            'side': side.value,
            'price': price,
            'qty': qty
        }
        firebase_client.create_order(order_data)
        
        # Add to order book and get any trades
        trades = order_book.add_order(order)
        
        print(f"\nOrder created: {order_id[:8]}...")
        print(f"  {side.value} {format_quantity(qty)} @ {format_price(price)}")
        
        if trades:
            print(f"\n{len(trades)} trade(s) executed!")
            for trade in trades:
                print(f"  Matched: {format_quantity(trade.qty)} @ {format_price(trade.price)}")
    except KeyboardInterrupt:
        print("\nOrder cancelled.")
    except Exception as e:
        print(f"\nError creating order: {e}")


def cancel_order(firebase_client: MockFirebaseClient, order_book: OrderBook):
    """Handle cancelling an existing order.
    
    Args:
        firebase_client: Firebase client for persistence
        order_book: OrderBook containing the order
    """
    print("\n--- Cancel Order ---")
    
    try:
        order_id = input("Order ID: ").strip()
        
        if not order_id:
            print("Error: Order ID is required.")
            return
        
        # Try to cancel in order book
        if order_book.cancel_order(order_id):
            # Also remove from Firebase
            firebase_client.delete_order(order_id)
            print(f"Order {order_id[:8]}... cancelled successfully.")
        else:
            print(f"Error: Order {order_id[:8]}... not found.")
    except KeyboardInterrupt:
        print("\nCancellation aborted.")
    except Exception as e:
        print(f"\nError cancelling order: {e}")


def main():
    """Main entry point for the CLI application."""
    print("Limit Order Book CLI")
    print("====================")
    
    # Initialize components
    firebase_client = MockFirebaseClient()
    order_book = OrderBook()
    
    print_menu()
    
    while True:
        try:
            choice = input("\nEnter command: ").strip().lower()
            
            if choice == 'q':
                print("Goodbye!")
                break
            elif choice == '1':
                add_order(firebase_client, order_book)
            elif choice == '2':
                cancel_order(firebase_client, order_book)
            elif choice == '3':
                show_book(order_book)
            elif choice == '4':
                show_trades(order_book)
            elif choice == '5':
                show_orders(firebase_client)
            elif choice == 'h':
                show_help()
            else:
                print("Invalid command. Please try again.")
                print_menu()
        except KeyboardInterrupt:
            print("\n\nUse 'q' to quit.")
        except EOFError:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
