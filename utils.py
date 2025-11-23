"""Utility functions for the limit order book system."""


def validate_price(price: float) -> bool:
    """Validate that a price is positive and reasonable.
    
    Args:
        price: The price to validate
        
    Returns:
        True if valid, False otherwise
    """
    if price <= 0:
        return False
    if price > 1_000_000:  # Max price limit
        return False
    return True


def validate_quantity(qty: int) -> bool:
    """Validate that a quantity is positive and reasonable.
    
    Args:
        qty: The quantity to validate
        
    Returns:
        True if valid, False otherwise
    """
    if qty <= 0:
        return False
    if qty > 1_000_000:  # Max quantity limit
        return False
    return True


def validate_order_id(order_id: str) -> bool:
    """Validate that an order ID is in valid format.
    
    Args:
        order_id: The order ID to validate
        
    Returns:
        True if valid, False otherwise
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
    """Format a price for display.
    
    Args:
        price: The price to format
        
    Returns:
        Formatted price string
    """
    return f"${price:,.2f}"


def format_quantity(qty: int) -> str:
    """Format a quantity for display.
    
    Args:
        qty: The quantity to format
        
    Returns:
        Formatted quantity string
    """
    return f"{qty:,}"

