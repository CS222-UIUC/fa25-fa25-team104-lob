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

## Project Structure

- `models.py` - Data models (Order, Trade, Side)
- `order_book.py` - Order book matching engine
- `firebase_client.py` - Firebase client implementations
- `cli.py` - Command-line interface

## Team Members

- Julian Castaneda
- Allan

## Course

CS 222 - Software Design Lab
