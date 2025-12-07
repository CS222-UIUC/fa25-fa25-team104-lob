"""Utility functions for the limit order book system.

This module provides validation and formatting utilities used throughout
the application for consistent input validation and output formatting.
"""


def validate_price(price: float) -> bool:
    """Validate that a price is positive and reasonable.
    
    Prices must be greater than 0 and less than or equal to 1,000,000
    to prevent overflow issues and unrealistic values.
    
    Args:
        price: The price to validate
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> validate_price(100.50)
        True
        >>> validate_price(-10)
        False
        >>> validate_price(0)
        False
    """
    if price <= 0:
        return False
    if price > 1_000_000:  # Max price limit
        return False
    return True


def validate_quantity(qty: int) -> bool:
    """Validate that a quantity is positive and reasonable.
    
    Quantities must be greater than 0 and less than or equal to 1,000,000
    to prevent overflow issues and unrealistic values.
    
    Args:
        qty: The quantity to validate
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> validate_quantity(100)
        True
        >>> validate_quantity(-5)
        False
        >>> validate_quantity(0)
        False
    """
    if qty <= 0:
        return False
    if qty > 1_000_000:  # Max quantity limit
        return False
    return True


def validate_order_id(order_id: str) -> bool:
    """Validate that an order ID is in valid format.
    
    Order IDs should be hex strings (from UUID4) with at least 8 characters.
    
    Args:
        order_id: The order ID to validate
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> validate_order_id("a1b2c3d4e5f6")
        True
        >>> validate_order_id("")
        False
        >>> validate_order_id("short")
        False
    """
    if not order_id:
        return False
    if len(order_id) < 8:
        return False
    # Should be hex string
    try:
        int(order_id, 16)
        return True
    except ValueError:
        return False


def format_price(price: float) -> str:
    """Format a price for display with dollar sign and commas.
    
    Args:
        price: The price to format
        
    Returns:
        Formatted price string (e.g., "$1,234.56")
        
    Examples:
        >>> format_price(1234.567)
        '$1,234.57'
        >>> format_price(100)
        '$100.00'
    """
    return f"${price:,.2f}"


def format_quantity(qty: int) -> str:
    """Format a quantity for display with commas.
    
    Args:
        qty: The quantity to format
        
    Returns:
        Formatted quantity string (e.g., "1,234")
        
    Examples:
        >>> format_quantity(1234567)
        '1,234,567'
        >>> format_quantity(100)
        '100'
    """
    return f"{qty:,}"
