"""Unit tests for ranking system."""

import pytest
from datetime import datetime, timezone, timedelta
from astrobob.core.ranking import calculate_score, rank_memories, explain_score
from astrobob.models import MemoryDocument, Provenance


def create_test_memory(
    importance: int = 3,
    success_count: int = 0,
    created_days_ago: int = 0,
    last_accessed_days_ago: int | None = None,
) -> MemoryDocument:
    """Helper to create test memory documents."""
    now = datetime.now(timezone.utc)
    created_at = now - timedelta(days=created_days_ago)
    last_accessed_at = None
    if last_accessed_days_ago is not None:
        last_accessed_at = now - timedelta(days=last_accessed_days_ago)
    
    return MemoryDocument(
        id="test_id",
        memory_type="semantic",
        project="test",
        content="Test memory",
        importance=importance,
        created_at=created_at,
        updated_at=created_at,
        success_count=success_count,
        last_accessed_at=last_accessed_at,
        access_count=0 if last_accessed_at is None else 1,
        provenance=Provenance(),
    )


def test_calculate_score_basic():
    """Test basic score calculation."""
    memory = create_test_memory(importance=4, created_days_ago=10)
    score = calculate_score(memory, rerank_score=0.8)
    
    # Score should be between 0 and 1
    assert 0 <= score <= 1
    # With high rerank score and importance, should be relatively high
    assert score > 0.5


def test_calculate_score_perfect():
    """Test perfect score scenario."""
    memory = create_test_memory(
        importance=5,
        success_count=20,
        created_days_ago=0
    )
    score = calculate_score(memory, rerank_score=1.0)
    
    # Should be very high score
    assert score > 0.9


def test_calculate_score_poor():
    """Test poor score scenario."""
    memory = create_test_memory(
        importance=1,
        success_count=0,
        created_days_ago=365,
        last_accessed_days_ago=180
    )
    score = calculate_score(memory, rerank_score=0.1)
    
    # Should be low score
    assert score < 0.3


def test_calculate_score_importance_impact():
    """Test that importance affects score."""
    current_time = datetime.now(timezone.utc)
    
    mem_low = create_test_memory(importance=1, created_days_ago=10)
    mem_mid = create_test_memory(importance=3, created_days_ago=10)
    mem_high = create_test_memory(importance=5, created_days_ago=10)
    
    score_low = calculate_score(mem_low, 0.5, current_time)
    score_mid = calculate_score(mem_mid, 0.5, current_time)
    score_high = calculate_score(mem_high, 0.5, current_time)
    
    # Higher importance should yield higher score
    assert score_low < score_mid < score_high


def test_calculate_score_recency_impact():
    """Test that recency affects score."""
    current_time = datetime.now(timezone.utc)
    
    mem_new = create_test_memory(importance=3, created_days_ago=1)
    mem_old = create_test_memory(importance=3, created_days_ago=100)
    
    score_new = calculate_score(mem_new, 0.5, current_time)
    score_old = calculate_score(mem_old, 0.5, current_time)
    
    # Newer memories should score higher
    assert score_new > score_old


def test_calculate_score_success_impact():
    """Test that success count affects score."""
    current_time = datetime.now(timezone.utc)
    
    mem_no_success = create_test_memory(importance=3, success_count=0)
    mem_some_success = create_test_memory(importance=3, success_count=10)
    
    score_no = calculate_score(mem_no_success, 0.5, current_time)
    score_some = calculate_score(mem_some_success, 0.5, current_time)
    
    # More successes should yield higher score
    assert score_some > score_no


def test_calculate_score_staleness_penalty():
    """Test staleness penalty for unaccessed memories."""
    current_time = datetime.now(timezone.utc)
    
    # Memory never accessed - no penalty
    mem_never = create_test_memory(importance=3, created_days_ago=100)
    
    # Memory accessed recently - no penalty
    mem_recent = create_test_memory(
        importance=3,
        created_days_ago=100,
        last_accessed_days_ago=10
    )
    
    # Memory not accessed in 90 days - penalty
    mem_stale = create_test_memory(
        importance=3,
        created_days_ago=100,
        last_accessed_days_ago=90
    )
    
    score_never = calculate_score(mem_never, 0.5, current_time)
    score_recent = calculate_score(mem_recent, 0.5, current_time)
    score_stale = calculate_score(mem_stale, 0.5, current_time)
    
    # Never accessed should not be penalized
    # Recently accessed should score higher than stale
    assert score_recent > score_stale


def test_calculate_score_rerank_dominance():
    """Test that rerank score is the dominant factor (55% weight)."""
    memory = create_test_memory(importance=3, created_days_ago=10)
    current_time = datetime.now(timezone.utc)
    
    score_low_rerank = calculate_score(memory, 0.2, current_time)
    score_high_rerank = calculate_score(memory, 0.9, current_time)
    
    # Difference should be significant (roughly 0.55 * 0.7 = 0.385)
    assert score_high_rerank - score_low_rerank > 0.3


def test_rank_memories():
    """Test ranking multiple memories."""
    current_time = datetime.now(timezone.utc)
    
    # Create memories with different characteristics
    mem1 = create_test_memory(importance=5, created_days_ago=1)
    mem2 = create_test_memory(importance=3, created_days_ago=30)
    mem3 = create_test_memory(importance=1, created_days_ago=100)
    
    memories = [
        (mem1, 0.9),  # High rerank, high importance, recent
        (mem2, 0.5),  # Medium everything
        (mem3, 0.3),  # Low everything
    ]
    
    ranked = rank_memories(memories, current_time)
    
    # Should return 3 memories
    assert len(ranked) == 3
    
    # First should be mem1 (highest score)
    assert ranked[0][0].id == mem1.id
    
    # Scores should be descending
    assert ranked[0][1] >= ranked[1][1] >= ranked[2][1]


def test_rank_memories_empty():
    """Test ranking empty list."""
    ranked = rank_memories([])
    assert ranked == []


def test_explain_score():
    """Test score explanation."""
    memory = create_test_memory(
        importance=4,
        success_count=10,
        created_days_ago=15,
        last_accessed_days_ago=5
    )
    current_time = datetime.now(timezone.utc)
    
    score = calculate_score(memory, 0.8, current_time)
    explanation = explain_score(memory, 0.8, score, current_time)
    
    # Check structure
    assert "memory_id" in explanation
    assert "final_score" in explanation
    assert "components" in explanation
    assert "metadata" in explanation
    
    # Check components
    components = explanation["components"]
    assert "rerank" in components
    assert "importance" in components
    assert "recency" in components
    assert "success" in components
    assert "staleness_penalty" in components
    
    # Check metadata
    metadata = explanation["metadata"]
    assert "age_days" in metadata
    assert "importance" in metadata
    assert "success_count" in metadata
    assert "access_count" in metadata
    
    # Verify component values are reasonable
    assert 0 <= components["rerank"] <= 0.55
    assert 0 <= components["importance"] <= 0.15
    assert 0 <= components["recency"] <= 0.15
    assert 0 <= components["success"] <= 0.10
    assert 0 <= components["staleness_penalty"] <= 0.05


def test_calculate_score_consistency():
    """Test that same inputs produce same outputs."""
    memory = create_test_memory(importance=4, created_days_ago=15)
    current_time = datetime.now(timezone.utc)
    
    score1 = calculate_score(memory, 0.75, current_time)
    score2 = calculate_score(memory, 0.75, current_time)
    
    assert score1 == score2


def test_calculate_score_boundary_values():
    """Test boundary values for all parameters."""
    current_time = datetime.now(timezone.utc)
    
    # Minimum values
    mem_min = create_test_memory(importance=1, success_count=0, created_days_ago=0)
    score_min = calculate_score(mem_min, 0.0, current_time)
    assert 0 <= score_min <= 1
    
    # Maximum values (can exceed 1.0 for exceptional memories)
    mem_max = create_test_memory(importance=5, success_count=1000, created_days_ago=0)
    score_max = calculate_score(mem_max, 1.0, current_time)
    assert score_max >= 0  # Score should be non-negative
    assert score_max > score_min  # Max should be higher than min
    assert score_max > 1.0  # With perfect inputs, should exceed 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
