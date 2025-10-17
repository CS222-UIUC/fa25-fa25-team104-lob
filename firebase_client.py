from typing import Dict, Any, Optional


class FirebaseClient:
    """Abstract interface for Firebase operations."""

    def create_order(self, order_data: Dict[str, Any]) -> str:
        """Write order to Firebase and return generated ID."""
        # implement using Firebase SDK
        pass

    def delete_order(self, order_id: str) -> bool:
        """Delete order document from Firebase."""
        # return True if deleted, False if not found
        pass

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Fetch order document."""
        pass


class MockFirebaseClient(FirebaseClient):
    """Local in-memory Firebase replacement for testing."""

    def __init__(self):
        # self._store = {}
        pass

    def create_order(self, order_data: Dict[str, Any]) -> str:
        # simulate adding doc to _store
        # generate ID if missing
        # return order_id
        pass

    def delete_order(self, order_id: str) -> bool:
        # simulate deletion in _store
        pass

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        # return _store[order_id] if exists else None
        pass