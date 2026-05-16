"""
Memory ranking system for AstroBob.

Implements a weighted scoring formula that combines:
- AstraDB rerank score (55%)
- Importance level (15%)
- Recency/freshness (15%)
- Success count (10%)
- Staleness penalty (5%)
"""

import math
from datetime import datetime, timezone
from typing import Any

from astrobob.models import MemoryDocument


def calculate_score(
    memory: MemoryDocument,
    rerank_score: float,
    current_time: datetime | None = None,
) -> float:
    """
    Calculate final ranking score for a memory.
    
    Formula:
    final_score = (
        0.55 * rerank_score +
        0.15 * (importance / 5.0) +
        0.15 * exp(-age_days / 30) +
        0.10 * log1p(success_count) / log1p(20) -
        0.05 * staleness_penalty
    )
    
    Args:
        memory: The memory document to score
        rerank_score: Score from AstraDB reranker (0.0-1.0)
        current_time: Current time for age calculation (defaults to now)
        
    Returns:
        Final score (typically 0.0-1.0, but can exceed 1.0 for exceptional memories)
    """
    if current_time is None:
        current_time = datetime.now(timezone.utc)
    
    # Component 1: Rerank score (55% weight)
    rerank_component = 0.55 * rerank_score
    
    # Component 2: Importance (15% weight)
    # Normalize importance (1-5) to 0.0-1.0
    importance_component = 0.15 * (memory.importance / 5.0)
    
    # Component 3: Recency (15% weight)
    # Exponential decay with 30-day half-life
    age_days = (current_time - memory.created_at).total_seconds() / 86400
    recency_component = 0.15 * math.exp(-age_days / 30)
    
    # Component 4: Success count (10% weight)
    # Logarithmic scaling, normalized to 20 successes = 1.0
    success_component = 0.10 * (
        math.log1p(memory.success_count) / math.log1p(20)
    )
    
    # Component 5: Staleness penalty (5% weight)
    # Penalize memories that haven't been accessed recently
    staleness_penalty = _calculate_staleness_penalty(memory, current_time)
    
    final_score = (
        rerank_component +
        importance_component +
        recency_component +
        success_component -
        staleness_penalty
    )
    
    return final_score


def _calculate_staleness_penalty(
    memory: MemoryDocument,
    current_time: datetime,
) -> float:
    """
    Calculate staleness penalty based on last access time.
    
    Memories that haven't been accessed in a long time get penalized,
    but only if they've been accessed before (to avoid penalizing new memories).
    
    Args:
        memory: The memory document
        current_time: Current time
        
    Returns:
        Penalty value (0.0-0.05)
    """
    if memory.last_accessed_at is None:
        # New memory, no penalty
        return 0.0
    
    days_since_access = (
        current_time - memory.last_accessed_at
    ).total_seconds() / 86400
    
    # Apply penalty after 60 days of no access
    if days_since_access > 60:
        # Linear penalty: 0.05 at 60 days, capped at 0.05
        penalty = min(0.05, 0.05 * ((days_since_access - 60) / 60))
        return penalty
    
    return 0.0


def rank_memories(
    memories: list[tuple[MemoryDocument, float]],
    current_time: datetime | None = None,
) -> list[tuple[MemoryDocument, float]]:
    """
    Rank a list of memories with their rerank scores.
    
    Args:
        memories: List of (memory, rerank_score) tuples
        current_time: Current time for age calculation
        
    Returns:
        Sorted list of (memory, final_score) tuples, highest score first
    """
    if current_time is None:
        current_time = datetime.now(timezone.utc)
    
    # Calculate final scores
    scored_memories = [
        (memory, calculate_score(memory, rerank_score, current_time))
        for memory, rerank_score in memories
    ]
    
    # Sort by score descending
    scored_memories.sort(key=lambda x: x[1], reverse=True)
    
    return scored_memories


def explain_score(
    memory: MemoryDocument,
    rerank_score: float,
    final_score: float,
    current_time: datetime | None = None,
) -> dict[str, Any]:
    """
    Explain how a score was calculated (for debugging/transparency).
    
    Args:
        memory: The memory document
        rerank_score: Score from AstraDB reranker
        final_score: Final calculated score
        current_time: Current time used in calculation
        
    Returns:
        Dictionary with score breakdown
    """
    if current_time is None:
        current_time = datetime.now(timezone.utc)
    
    age_days = (current_time - memory.created_at).total_seconds() / 86400
    
    components = {
        "rerank": 0.55 * rerank_score,
        "importance": 0.15 * (memory.importance / 5.0),
        "recency": 0.15 * math.exp(-age_days / 30),
        "success": 0.10 * (
            math.log1p(memory.success_count) / math.log1p(20)
        ),
        "staleness_penalty": _calculate_staleness_penalty(memory, current_time),
    }
    
    return {
        "memory_id": memory.id,
        "final_score": final_score,
        "components": components,
        "metadata": {
            "age_days": age_days,
            "importance": memory.importance,
            "success_count": memory.success_count,
            "access_count": memory.access_count,
            "last_accessed": memory.last_accessed_at.isoformat() if memory.last_accessed_at else None,
        },
    }

# Made with Bob
