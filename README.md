# Central Limit Order Book

## 1. Project Introduction
- A central limit order book (CLOB) is the matching engine behind stock and financial derivative exchanges.  Traders can post "Buy" and "Sell" orders that specify price and quantity, and these will persist on the book.  All traders can see all these order, promoting liquidity and price discovery.  The CLOB supports trade execution, which occurs when a buy or sell price crosses into the other side, triggering a match.  Orders are consumed by price level, and within the same price level, earlier orders are matched first.  Our project is a sandbox CLOB which allows users to add/switch traders, place/cancel/view orders (which automatically execute trades when applicable), and view matched order history.  The goal is to enable students to play around with placing orders, and possibly even enacting more advanced study of advanced trading strategies and algorithms.

## 2. Technical Architecture
<img width="846" height="170" alt="image" src="https://github.com/user-attachments/assets/9652b795-63a8-4b49-82e4-0c43099ce2ae" />

- **CLI Frontend:** Looping menu that takes user input and calls backend routes, renders orderbook snapshot using Rich tables
- **LOB Cache:** Class that stores data from database fetches for frontend use, minimizes unnecessary re-fetches
- **Backend Python Endpoints:** Firestore routes to facilitate database actions, transactions enable atomic logic (order creation, trade execution, order cancellation)
- **Database:** Firestore collections (`traders`, `orders`, `trades`) with integer balances/reserves.


## 3. Installation & Setup
1. Clone the repository.
2. Create/activate a Python virtual environment.
3. Install dependencies: `pip install -r requirements.txt`.
4. IMPORTANT: Provide `serviceAccount.json` (Firebase credentials) in the project root (We did not include our database's private key. We can be contacted for it, or a new one can be generated to replace it)
5. Run the CLI: `python main.py`.

## 4. Team Members & Roles
- **Allan Luo – backend Firestore routes, trade execution transaction logic**
- **Hamza Patel – financial utility functions, database schemas**
- **Haonan Wang – Command line frontend logic**
- **Julian Castaneda – Main frontend user menu**







