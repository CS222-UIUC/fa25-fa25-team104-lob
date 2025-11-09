"""Firebase client for persisting orders to Firestore."""

from typing import Dict, Any, Optional, List
import uuid
import time

import firebase_admin
from firebase_admin import credentials, firestore


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

    def list_orders(self) -> List[Dict[str, Any]]:
        """List all orders in the database.
        
        Returns:
            List of all order data dicts
        """
        raise NotImplementedError


class RealFirebaseClient(FirebaseClient):
    """Real Firebase/Firestore implementation for production use.
    
    Connects to Firestore using service account credentials.
    """

    def __init__(self, credentials_path: str = "serviceAccount.json"):
        """Initialize Firebase connection.
        
        Args:
            credentials_path: Path to service account JSON file
        """
        # Initialize Firebase if not already done
        if not firebase_admin._apps:
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred)
        
        self._db = firestore.client()
        self._collection = self._db.collection('orders')

    def create_order(self, order_data: Dict[str, Any]) -> str:
        """Create an order in Firestore.
        
        Args:
            order_data: Dictionary containing order fields
            
        Returns:
            The generated order ID
        """
        order_id = order_data.get('id') or uuid.uuid4().hex
        order_data['id'] = order_id
        # Add timestamp if not present
        if 'created_at' not in order_data:
            order_data['created_at'] = time.time()
        self._collection.document(order_id).set(order_data)
        return order_id

    def delete_order(self, order_id: str) -> bool:
        """Delete an order from Firestore.
        
        Args:
            order_id: The ID of the order to delete
            
        Returns:
            True if deleted, False if not found
        """
        doc_ref = self._collection.document(order_id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
            return True
        return False

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an order from Firestore.
        
        Args:
            order_id: The ID of the order to retrieve
            
        Returns:
            Order data dict if found, None otherwise
        """
        doc = self._collection.document(order_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def list_orders(self) -> List[Dict[str, Any]]:
        """List all orders from Firestore.
        
        Returns:
            List of all order data dicts
        """
        docs = self._collection.stream()
        return [doc.to_dict() for doc in docs]


class MockFirebaseClient(FirebaseClient):
    """In-memory mock implementation for testing without Firebase.
    
    Stores orders in a dictionary, simulating database operations.
    Useful for local development and unit testing.
    """

    def __init__(self):
        """Initialize the mock client with empty storage."""
        self._store: Dict[str, Dict[str, Any]] = {}

    def create_order(self, order_data: Dict[str, Any]) -> str:
        """Create an order in memory.
        
        Args:
            order_data: Dictionary containing order fields
            
        Returns:
            The generated order ID
        """
        # Generate ID if not provided
        order_id = order_data.get('id') or uuid.uuid4().hex
        order_data['id'] = order_id
        # Add timestamp if not present
        if 'created_at' not in order_data:
            order_data['created_at'] = time.time()
        self._store[order_id] = order_data.copy()
        return order_id

    def delete_order(self, order_id: str) -> bool:
        """Delete an order from memory.
        
        Args:
            order_id: The ID of the order to delete
            
        Returns:
            True if deleted, False if not found
        """
        if order_id in self._store:
            del self._store[order_id]
            return True
        return False

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an order from memory.
        
        Args:
            order_id: The ID of the order to retrieve
            
        Returns:
            Order data dict if found, None otherwise
        """
        return self._store.get(order_id)

    def list_orders(self) -> List[Dict[str, Any]]:
        """List all orders in memory.
        
        Returns:
            List of all order data dicts
        """
        return list(self._store.values())
