"""Firebase client for persisting orders to Firestore."""

from typing import Dict, Any, Optional


class FirebaseClient:
    """Abstract interface for Firebase/Firestore operations.
    
    This class defines the interface for order persistence.
    Implementations should handle actual database operations.
    """

    def create_order(self, order_data: Dict[str, Any]) -> str:
        """Create an order in the database.
        
        Args:
            order_data: Dictionary containing order fields
            
        Returns:
            The generated order ID
        """
        raise NotImplementedError

    def delete_order(self, order_id: str) -> bool:
        """Delete an order from the database.
        
        Args:
            order_id: The ID of the order to delete
            
        Returns:
            True if deleted, False if not found
        """
        raise NotImplementedError

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an order from the database.
        
        Args:
            order_id: The ID of the order to retrieve
            
        Returns:
            Order data dict if found, None otherwise
        """
        raise NotImplementedError

