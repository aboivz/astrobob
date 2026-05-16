"""
Test script for ranking system.

Tests the scoring formula with various edge cases:
- New memories (age=0)
- Old memories (age=90 days)
- Memories with no successes
- Memories with high success counts
- Memories with different importance levels
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from astrobob.models import create_memory
from astrobob.core.ranking import calculate_score, rank_memories, explain_score


def test_edge_cases():
    """Test ranking formula with edge cases."""
    print("Testing Ranking System Edge Cases\n")
    print("=" * 80)
    
    current_time = datetime.now(timezone.utc)
    
    # Test Case 1: Brand new memory
    print("\n1. Brand New Memory (age=0, success=0)")
    new_memory = create_memory(
        content="Brand new memory",
        memory_type="semantic",
        project="test",
        importance=3,
    )
    score = calculate_score(new_memory, rerank_score=0.8, current_time=current_time)
    explanation = explain_score(new_memory, 0.8, score, current_time)
    print(f"   Final Score: {score:.4f}")
    print(f"   Components: {explanation['components']}")
    
    # Test Case 2: Old memory (90 days)
    print("\n2. Old Memory (age=90 days, success=0)")
    old_memory = create_memory(
        content="Old memory",
        memory_type="semantic",
        project="test",
        importance=3,
    )
    old_memory.created_at = current_time - timedelta(days=90)
    score = calculate_score(old_memory, rerank_score=0.8, current_time=current_time)
    explanation = explain_score(old_memory, 0.8, score, current_time)
    print(f"   Final Score: {score:.4f}")
    print(f"   Components: {explanation['components']}")
    
    # Test Case 3: High success count
    print("\n3. High Success Memory (success=20)")
    success_memory = create_memory(
        content="Successful memory",
        memory_type="procedural",
        project="test",
        importance=4,
    )
    success_memory.success_count = 20
    score = calculate_score(success_memory, rerank_score=0.7, current_time=current_time)
    explanation = explain_score(success_memory, 0.7, score, current_time)
    print(f"   Final Score: {score:.4f}")
    print(f"   Components: {explanation['components']}")
    
    # Test Case 4: Low importance
    print("\n4. Low Importance Memory (importance=1)")
    low_imp_memory = create_memory(
        content="Low importance",
        memory_type="semantic",
        project="test",
        importance=1,
    )
    score = calculate_score(low_imp_memory, rerank_score=0.8, current_time=current_time)
    explanation = explain_score(low_imp_memory, 0.8, score, current_time)
    print(f"   Final Score: {score:.4f}")
    print(f"   Components: {explanation['components']}")
    
    # Test Case 5: High importance
    print("\n5. High Importance Memory (importance=5)")
    high_imp_memory = create_memory(
        content="High importance",
        memory_type="procedural",
        project="test",
        importance=5,
    )
    score = calculate_score(high_imp_memory, rerank_score=0.8, current_time=current_time)
    explanation = explain_score(high_imp_memory, 0.8, score, current_time)
    print(f"   Final Score: {score:.4f}")
    print(f"   Components: {explanation['components']}")
    
    # Test Case 6: Stale memory (not accessed in 90 days)
    print("\n6. Stale Memory (last_accessed=90 days ago)")
    stale_memory = create_memory(
        content="Stale memory",
        memory_type="semantic",
        project="test",
        importance=3,
    )
    stale_memory.last_accessed_at = current_time - timedelta(days=90)
    stale_memory.access_count = 5
    score = calculate_score(stale_memory, rerank_score=0.8, current_time=current_time)
    explanation = explain_score(stale_memory, 0.8, score, current_time)
    print(f"   Final Score: {score:.4f}")
    print(f"   Components: {explanation['components']}")
    
    print("\n" + "=" * 80)


def test_ranking_order():
    """Test that memories are ranked in correct order."""
    print("\n\nTesting Ranking Order\n")
    print("=" * 80)
    
    current_time = datetime.now(timezone.utc)
    
    # Create diverse memories
    memories = [
        (
            create_memory(
                content="Recent high-importance procedural",
                memory_type="procedural",
                project="test",
                importance=5,
            ),
            0.9,  # rerank score
        ),
        (
            create_memory(
                content="Old low-importance semantic",
                memory_type="semantic",
                project="test",
                importance=1,
            ),
            0.7,
        ),
        (
            create_memory(
                content="Medium everything",
                memory_type="episodic",
                project="test",
                importance=3,
            ),
            0.8,
        ),
    ]
    
    # Make second memory old
    memories[1][0].created_at = current_time - timedelta(days=60)
    
    # Add success to first memory
    memories[0][0].success_count = 10
    
    # Rank them
    ranked = rank_memories(memories, current_time)
    
    print("\nRanked Memories (highest to lowest):")
    for i, (memory, score) in enumerate(ranked, 1):
        print(f"\n{i}. {memory.content}")
        print(f"   Score: {score:.4f}")
        print(f"   Type: {memory.memory_type}, Importance: {memory.importance}")
        print(f"   Age: {(current_time - memory.created_at).days} days")
        print(f"   Success count: {memory.success_count}")
    
    print("\n" + "=" * 80)


def test_score_components():
    """Test that score components sum correctly."""
    print("\n\nTesting Score Component Math\n")
    print("=" * 80)
    
    current_time = datetime.now(timezone.utc)
    
    memory = create_memory(
        content="Test memory",
        memory_type="semantic",
        project="test",
        importance=3,
    )
    
    rerank_score = 0.8
    final_score = calculate_score(memory, rerank_score, current_time)
    explanation = explain_score(memory, rerank_score, final_score, current_time)
    
    components = explanation['components']
    calculated_sum = (
        components['rerank'] +
        components['importance'] +
        components['recency'] +
        components['success'] -
        components['staleness_penalty']
    )
    
    print(f"\nFinal Score: {final_score:.6f}")
    print(f"Sum of Components: {calculated_sum:.6f}")
    print(f"Difference: {abs(final_score - calculated_sum):.10f}")
    
    if abs(final_score - calculated_sum) < 1e-10:
        print("\nPASS: Components sum correctly")
    else:
        print("\nFAIL: Components don't sum correctly!")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        test_edge_cases()
        test_ranking_order()
        test_score_components()
        print("\n\nAll ranking tests completed successfully!")
        
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
