"""
AstraDB client wrapper for AstroBob.

Provides connection management and common operations for AstraDB Serverless.
"""

from typing import Optional
from astrapy import DataAPIClient, Database
from astrapy.exceptions import DataAPIException

from astrobob.config import AstroBobConfig
from astrobob.errors import AstraConnectionError


class AstraClient:
    """
    Wrapper around astrapy client for AstroBob operations.
    
    Handles connection management, error handling, and common operations
    like hybrid search with reranking.
    """
    
    def __init__(self, config: AstroBobConfig):
        """
        Initialize AstraDB client.
        
        Args:
            config: AstroBob configuration with Astra credentials
            
        Raises:
            AstraConnectionError: If connection cannot be established
        """
        self.config = config
        self._client: Optional[DataAPIClient] = None
        self._database: Optional[Database] = None
        
    def _ensure_connected(self) -> None:
        """Ensure client and database are initialized."""
        if self._client is None:
            try:
                self._client = DataAPIClient(token=self.config.astra_db_application_token)
            except Exception as e:
                raise AstraConnectionError(
                    f"Failed to initialize AstraDB client: {e}"
                ) from e
                
        if self._database is None:
            try:
                self._database = self._client.get_database(
                    api_endpoint=self.config.astra_db_api_endpoint
                )
            except Exception as e:
                raise AstraConnectionError(
                    f"Failed to connect to AstraDB: {e}"
                ) from e
    
    def get_database(self) -> Database:
        """
        Get the AstraDB database instance.
        
        Returns:
            astrapy Database instance
            
        Raises:
            AstraConnectionError: If connection fails
        """
        self._ensure_connected()
        assert self._database is not None  # for type checker
        return self._database
    
    def test_connection(self) -> bool:
        """
        Test connection to AstraDB.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            db = self.get_database()
            # Try to list collections as a connection test
            db.list_collection_names()
            return True
        except Exception:
            return False
    
    def find_and_rerank(
        self,
        collection_name: str,
        query: str,
        limit: int = 10,
        filter_dict: Optional[dict] = None,
        include_similarity: bool = True,
    ) -> list[dict]:
        """
        Perform vector search with automatic embedding generation.
        
        Uses AstraDB's $vectorize to automatically generate embeddings
        from the query string using the NVIDIA integration.
        
        Args:
            collection_name: Name of the collection to search
            query: Search query string (will be vectorized automatically)
            limit: Maximum number of results to return
            filter_dict: Optional filter criteria (e.g., {"deleted_at": None})
            include_similarity: Whether to include similarity scores
            
        Returns:
            List of documents with similarity scores
            
        Raises:
            AstraConnectionError: If search fails
        """
        try:
            db = self.get_database()
            collection = db.get_collection(collection_name)
            
            # Use $vectorize for automatic embedding generation
            sort_criteria = {"$vectorize": query}
            
            # Perform vector search with automatic embedding
            cursor = collection.find(
                filter=filter_dict or {},
                sort=sort_criteria,
                limit=limit,
                include_similarity=include_similarity,
            )
            
            # Convert cursor to list
            results = list(cursor)
            
            return results
            
        except DataAPIException as e:
            raise AstraConnectionError(
                f"Vector search failed on collection '{collection_name}': {e}"
            ) from e
        except Exception as e:
            raise AstraConnectionError(
                f"Unexpected error during search: {e}"
            ) from e
    
    def close(self) -> None:
        """Close the client connection."""
        # astrapy doesn't require explicit closing, but we provide this
        # for consistency and future-proofing
        self._client = None
        self._database = None


def create_astra_client(config: Optional[AstroBobConfig] = None) -> AstraClient:
    """
    Factory function to create an AstraClient instance.
    
    Args:
        config: Optional configuration. If None, loads from environment.
        
    Returns:
        Configured AstraClient instance
        
    Raises:
        ConfigError: If configuration is invalid
        AstraConnectionError: If connection fails
    """
    from astrobob.config import get_config
    
    if config is None:
        config = get_config()
    
    return AstraClient(config)

# Made with Bob
