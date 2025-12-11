# Limit Order Book

A Python implementation of a limit order book matching engine with Firebase persistence.

## Overview

This project implements a basic limit order book system that supports:
- Buy and sell limit orders
- Price-time priority matching
- Order cancellation
- Trade execution tracking
- Firebase/Firestore persistence

## Features

- **Order Book Engine**: Efficient matching using heap-based priority queues
- **Price-Time Priority**: Orders matched by best price, then by arrival time
- **Firebase Integration**: Persist orders to Firestore database
- **Mock Client**: In-memory mock for testing without Firebase
- **CLI Interface**: Interactive command-line interface
- **Order Status Tracking**: Track orders through OPEN, PARTIAL, FILLED, CANCELLED states

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the CLI:
```bash
python cli.py
```

### Commands

- `1` - Add a new order (buy or sell)
- `2` - Cancel an existing order
- `3` - Show top of book (best bid/ask)
- `4` - Show trade history
- `5` - Show all orders
- `h` - Help
- `q` - Quit

## Architecture

```
┌─────────────────────────────────────────────────┐
│                    CLI (cli.py)                 │
│         User Interface & Command Handler        │
└─────────────────────┬───────────────────────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
         ▼            ▼            ▼
┌─────────────┐ ┌───────────┐ ┌─────────────────┐
│ OrderBook   │ │  Models   │ │ FirebaseClient  │
│ (Matching)  │ │  (Data)   │ │ (Persistence)   │
└─────────────┘ └───────────┘ └─────────────────┘
```

## Project Structure

- `models.py` - Data models (Order, Trade, Side, OrderStatus)
- `order_book.py` - Order book matching engine
- `firebase_client.py` - Firebase client implementations
- `cli.py` - Command-line interface
- `utils.py` - Validation and formatting utilities

## Order Matching

The order book uses a price-time priority algorithm:

1. **Price Priority**: Best price orders are matched first
   - Highest bid price for buy orders
   - Lowest ask price for sell orders

2. **Time Priority**: At the same price level, earlier orders are matched first

3. **Trade Price**: Uses the passive order's price (the order already in the book)

## Team Members

- Julian Castaneda
- Allan Luo
- Hamza Patel
- Haonan Wang

## Course

CS 222 - Software Design Lab
