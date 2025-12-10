# Testing Guide for Limit Order Book CLI

This guide walks you through testing all features of the limit order book system.

## Starting the CLI

```bash
python3 cli.py
```

> **Tip:** You can press `Ctrl+C` at any time to interrupt the current operation or exit the program.

---

## Test Scenarios

### Test 1: Add a Buy Order

**Input:**
```
Press: 1
User ID: alice
Side: b
Price: 100
Quantity: 10
```

**Expected Output:**
```
Order created: xxxxxxxx...
  BUY 10 @ $100.00
```

---

### Test 2: Add Another Buy Order (Lower Price)

**Input:**
```
Press: 1
User ID: bob
Side: b
Price: 99
Quantity: 5
```

**Expected Output:**
```
Order created: xxxxxxxx...
  BUY 5 @ $99.00
```

---

### Test 3: Add a Sell Order (No Match Expected)

**Input:**
```
Press: 1
User ID: charlie
Side: s
Price: 105
Quantity: 8
```

**Expected Output:**
```
Order created: xxxxxxxx...
  SELL 8 @ $105.00
```

No trades should execute because the sell price ($105) is higher than the best bid ($100).

---

### Test 4: Check Top of Book

**Input:**
```
Press: 3
```

**Expected Output:**
```
--- Top of Book ---
Active orders: 3

Best Bid: $100.00 x 10
Best Ask: $105.00 x 8
Spread: $5.00 (4.88%)
-------------------
```

The spread shows the difference between best ask and best bid prices.

---

### Test 5: Show All Orders

**Input:**
```
Press: 5
```

**Expected Output:**
```
--- All Orders ---
  xxxxxxxx... [alice] BUY 10 @ $100.00
  xxxxxxxx... [bob] BUY 5 @ $99.00
  xxxxxxxx... [charlie] SELL 8 @ $105.00
------------------
```

---

### Test 6: Add a Crossing Order (Triggers Trades!)

This is the key test - adding a sell order at a price that crosses existing buy orders.

**Input:**
```
Press: 1
User ID: dave
Side: s
Price: 99
Quantity: 15
```

**Expected Output:**
```
Order created: xxxxxxxx...
  SELL 15 @ $99.00

2 trade(s) executed!
  Matched: 10 @ $100.00
  Matched: 5 @ $99.00
```

**What happened:**
1. Dave's sell order at $99 crossed Alice's buy at $100 → Trade 1: 10 shares at $100
2. Remaining 5 shares crossed Bob's buy at $99 → Trade 2: 5 shares at $99
3. All 15 shares were sold, both buy orders are now filled

---

### Test 7: Show Trade History

**Input:**
```
Press: 4
```

**Expected Output:**
```
--- Trade History ---
1. 10 @ $100.00
   Buy: xxxxxxxx...
   Sell: xxxxxxxx...
2. 5 @ $99.00
   Buy: xxxxxxxx...
   Sell: xxxxxxxx...

--- Statistics ---
Total trades: 2
Total volume: 15
Total value: $1,495.00
Average price: $99.67
---------------------
```

---

### Test 8: Verify Top of Book After Trades

**Input:**
```
Press: 3
```

**Expected Output:**
```
--- Top of Book ---
Active orders: 1

Best Bid: None
Best Ask: $105.00 x 8
-------------------
```

The buy orders were filled, so Best Bid is now None.

---

### Test 9: Cancel an Order

**Input:**
```
Press: 2
Order ID: [paste a full order ID from the orders list, or type first 8 characters]
```

**Expected Output:**
```
Order xxxxxxxx... cancelled successfully.
```

---

### Test 10: View Help

**Input:**
```
Press: h
```

**Expected Output:** A detailed help screen explaining all commands and how order matching works.

---

### Test 11: Quit the Program

**Input:**
```
Press: q
```

**Expected Output:**
```
Goodbye!
```

---

## Quick Reference

| Command | Action |
|---------|--------|
| `1` | Add a new order |
| `2` | Cancel an order |
| `3` | Show top of book (best bid/ask) |
| `4` | Show trade history |
| `5` | Show all active orders |
| `h` | Display help |
| `q` | Quit the program |
| `Ctrl+C` | Interrupt/stop at any time |

---

## Order Matching Rules

1. **Price Priority**: Best prices are matched first
   - Buyers: Highest price has priority
   - Sellers: Lowest price has priority

2. **Time Priority**: At the same price, earlier orders are matched first

3. **Trade Price**: The trade executes at the passive order's price (the order that was already in the book)

---

## Troubleshooting

- **"Invalid input"**: Make sure to enter valid numbers for price and quantity
- **"Order not found"**: The order ID must match an existing active order
- **No trades executing**: Check that buy price >= sell price for a match to occur

