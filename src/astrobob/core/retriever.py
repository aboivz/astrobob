"""
Memory retrieval system with query-intent routing.

Intelligently searches across semantic, episodic, and procedural memory
collections based on query intent, then ranks and merges results.
"""

from datetime import datetime, timezone
from typing import Literal, Optional

from astrobob.astra.client import AstraClient
from astrobob.core.ranking import rank_memories
from astrobob.core.store import MemoryStore
from astrobob.models import MemoryDocument


MemoryType = Literal["semantic", "episodic", "procedural"]


def infer_collection_priority(query: str) -> list[MemoryType]:
    """
    Infer which memory collections to prioritize based on query intent.
    
    Uses keyword matching to determine if the user is asking:
    - "How to" questions → procedural first
    - "What is" questions → semantic first
    - "Last time" questions → episodic first
    
    Args:
        query: The search query
        
    Returns:
        Ordered list of memory types to search, highest priority first
    """
    query_lower = query.lower()
    
    # Procedural indicators (how-to, should I, when to)
    procedural_keywords = [
        "how to", "how do i", "how can i", "how should",
        "should i", "when to", "when should", "steps to",
        "procedure", "process", "workflow", "best way",
    ]
    
    # Semantic indicators (what is, does it, is there)
    semantic_keywords = [
        "what is", "what are", "what does", "is there",
        "does it", "can it", "define", "explain",
        "meaning", "definition", "about",
    ]
    
    # Episodic indicators (last time, why did, when did)
    episodic_keywords = [
        "last time", "previous", "history", "when did",
        "why did", "what happened", "remember when",
        "ago", "before", "earlier",
    ]
    
    # Check for matches
    has_procedural = any(kw in query_lower for kw in procedural_keywords)
    has_semantic = any(kw in query_lower for kw in semantic_keywords)
    has_episodic = any(kw in query_lower for kw in episodic_keywords)
    
    # Determine priority order
    if has_procedural:
        return ["procedural", "semantic", "episodic"]
    elif has_semantic:
        return ["semantic", "procedural", "episodic"]
    elif has_episodic:
        return ["episodic", "semantic", "procedural"]
    else:
        # Default: procedural is most useful for agents
        return ["procedural", "semantic", "episodic"]


class MemoryRetriever:
    """
    Retrieves and ranks memories from AstraDB collections.
    
    Combines hybrid search (vector + lexical + rerank) with
    custom ranking formula to find the most relevant memories.
    """
    
    def __init__(self, client: AstraClient, store: MemoryStore):
        """
        Initialize retriever.
        
        Args:
            client: AstraDB client for hybrid search
            store: Memory store for access tracking
        """
        self.client = client
        self.store = store
    
    def recall(
        self,
        query: str,
        *,
        project: str,
        memory_types: Optional[list[MemoryType]] = None,
        tags: Optional[list[str]] = None,
        limit: int = 10,
        min_importance: Optional[int] = None,
    ) -> list[tuple[MemoryDocument, float]]:
        """
        Recall memories matching the query.
        
        Args:
            query: Search query (natural language)
            project: Project to search within
            memory_types: Specific memory types to search (None = infer from query)
            tags: Optional tag filter
            limit: Maximum number of results to return
            min_importance: Minimum importance level (1-5)
            
        Returns:
            List of (memory, score) tuples, sorted by score descending
        """
        # Infer collection priority if not specified
        if memory_types is None:
            memory_types = infer_collection_priority(query)
        
        # Search each collection
        all_results: list[tuple[MemoryDocument, float]] = []
        seen_ids: set[str] = set()
        
        for memory_type in memory_types:
            results = self._search_collection(
                memory_type=memory_type,
                query=query,
                project=project,
                tags=tags,
                limit=limit * 2,  # Get more to account for filtering
                min_importance=min_importance,
            )
            
            # Deduplicate by ID (in case of cross-collection matches)
            for memory, rerank_score in results:
                if memory.id not in seen_ids:
                    all_results.append((memory, rerank_score))
                    seen_ids.add(memory.id)
        
        # Rank all results using our custom formula
        current_time = datetime.now(timezone.utc)
        ranked_results = rank_memories(all_results, current_time)
        
        # Update access tracking for returned memories
        for memory, _ in ranked_results[:limit]:
            self.store.update_access(memory.memory_type, memory.id)
        
        return ranked_results[:limit]
    
    def _search_collection(
        self,
        memory_type: MemoryType,
        query: str,
        project: str,
        tags: Optional[list[str]],
        limit: int,
        min_importance: Optional[int],
    ) -> list[tuple[MemoryDocument, float]]:
        """
        Search a single collection using hybrid search.
        
        Args:
            memory_type: Which collection to search
            query: Search query
            project: Project filter
            tags: Optional tag filter
            limit: Max results
            min_importance: Minimum importance filter
            
        Returns:
            List of (memory, rerank_score) tuples
        """
        # Build filter
        filter_dict: dict = {
            "project": project,
            "deleted_at": None,  # Exclude soft-deleted
        }
        
        if tags:
            filter_dict["tags"] = {"$in": tags}
        
        if min_importance is not None:
            filter_dict["importance"] = {"$gte": min_importance}
        
        # Execute hybrid search with reranking
        try:
            results = self.client.find_and_rerank(
                collection_name=f"astrobob_{memory_type}_memory",
                query=query,
                filter_dict=filter_dict,
                limit=limit,
            )
            
            # Convert to MemoryDocument objects
            memories: list[tuple[MemoryDocument, float]] = []
            for doc in results:
                # Extract rerank score (stored in $similarity by AstraDB)
                rerank_score = doc.get("$similarity", 0.0)
                
                # Remove AstraDB metadata fields
                doc_data = {k: v for k, v in doc.items() if not k.startswith("$")}
                
                # Map _id to id for Pydantic
                if "_id" in doc_data:
                    doc_data["id"] = doc_data.pop("_id")
                
                # Create MemoryDocument
                memory = MemoryDocument(**doc_data)
                memories.append((memory, rerank_score))
            
            return memories
            
        except Exception as e:
            # Log error but don't fail entire recall
            print(f"Warning: Search failed for {memory_type}: {e}")
            return []
    
    def recall_by_id(
        self,
        memory_type: MemoryType,
        memory_id: str,
    ) -> Optional[MemoryDocument]:
        """
        Recall a specific memory by ID.
        
        Args:
            memory_type: Type of memory
            memory_id: Memory ID
            
        Returns:
            Memory document or None if not found
        """
        try:
            memory = self.store.get(memory_type, memory_id)
            self.store.update_access(memory_type, memory_id)
            return memory
        except Exception:
            return None
    
    def recall_recent_episodes(
        self,
        project: str,
        limit: int = 10,
        days: int = 7,
    ) -> list[MemoryDocument]:
        """
        Recall recent episodic memories for reflection.
        
        Args:
            project: Project to search
            limit: Max results
            days: How many days back to search
            
        Returns:
            List of recent episodic memories
        """
        cutoff_time = datetime.now(timezone.utc)
        # Note: We'll implement time-based filtering in the store
        # For now, just get recent episodes
        
        try:
            db = self.client.get_database()
            collection = db.get_collection("astrobob_episodic_memory")
            
            results = collection.find(
                filter={
                    "project": project,
                    "deleted_at": None,
                },
                sort={"created_at": -1},
                limit=limit,
            )
            
            memories = []
            for doc in results:
                doc_data = {k: v for k, v in doc.items() if not k.startswith("$")}
                if "_id" in doc_data:
                    doc_data["id"] = doc_data.pop("_id")
                memories.append(MemoryDocument(**doc_data))
            
            return memories
            
        except Exception as e:
            print(f"Warning: Failed to recall recent episodes: {e}")
            return []

# Made with Bob
