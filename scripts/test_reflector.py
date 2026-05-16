"""
Test script for memory reflector.

Tests that reflection suggestions trigger correctly based on heuristics.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from astrobob.models import create_memory
from astrobob.core.reflector import MemoryReflector


def test_single_episode_suggestions():
    """Test reflection suggestions for single episodes."""
    print("Testing Single Episode Reflection Suggestions\n")
    print("=" * 80)
    
    reflector = MemoryReflector()
    
    # Test 1: High-importance episode (should suggest)
    print("\n1. High-importance episode (importance=4)")
    high_imp_episode = create_memory(
        memory_type="episodic",
        project="test",
        content="Fixed critical auth bug by adding token refresh",
        importance=4,
    )
    
    suggestion = reflector.should_suggest_reflection(high_imp_episode, recent_episode_count=1)
    if suggestion:
        print(f"   PASS: Suggested - {suggestion.reason}")
        print(f"   Suggested importance: {suggestion.suggested_importance}")
    else:
        print("   FAIL: No suggestion (expected one)")
    
    # Test 2: Medium-importance with multiple recent episodes
    print("\n2. Medium-importance with 3 recent episodes")
    medium_episode = create_memory(
        memory_type="episodic",
        project="test",
        content="Deployed to staging successfully",
        importance=3,
    )
    
    suggestion = reflector.should_suggest_reflection(medium_episode, recent_episode_count=3)
    if suggestion:
        print(f"   PASS: Suggested - {suggestion.reason}")
    else:
        print("   FAIL: No suggestion (expected one)")
    
    # Test 3: Episode with success count
    print("\n3. Episode with success_count > 0")
    success_episode = create_memory(
        memory_type="episodic",
        project="test",
        content="Used new deployment procedure",
        importance=3,
    )
    success_episode.success_count = 2
    
    suggestion = reflector.should_suggest_reflection(success_episode, recent_episode_count=1)
    if suggestion:
        print(f"   PASS: Suggested - {suggestion.reason}")
        print(f"   Suggested importance: {suggestion.suggested_importance}")
    else:
        print("   FAIL: No suggestion (expected one)")
    
    # Test 4: Low-importance, no pattern (should NOT suggest)
    print("\n4. Low-importance, no pattern (should NOT suggest)")
    low_episode = create_memory(
        memory_type="episodic",
        project="test",
        content="Minor code cleanup",
        importance=2,
    )
    
    suggestion = reflector.should_suggest_reflection(low_episode, recent_episode_count=1)
    if suggestion is None:
        print("   PASS: No suggestion (as expected)")
    else:
        print(f"   FAIL: Unexpected suggestion - {suggestion.reason}")
    
    # Test 5: Non-episodic memory (should NOT suggest)
    print("\n5. Semantic memory (should NOT suggest)")
    semantic = create_memory(
        memory_type="semantic",
        project="test",
        content="Project uses FastAPI",
        importance=4,
    )
    
    suggestion = reflector.should_suggest_reflection(semantic, recent_episode_count=5)
    if suggestion is None:
        print("   PASS: No suggestion (as expected)")
    else:
        print(f"   FAIL: Unexpected suggestion - {suggestion.reason}")
    
    print("\n" + "=" * 80)


def test_episode_cluster_analysis():
    """Test analysis of multiple related episodes."""
    print("\n\nTesting Episode Cluster Analysis\n")
    print("=" * 80)
    
    reflector = MemoryReflector()
    current_time = datetime.now(timezone.utc)
    
    # Test 1: Episodes with common tags
    print("\n1. Episodes with common tags")
    episodes = [
        create_memory(
            memory_type="episodic",
            project="test",
            content="Added MCP tool for memory recall",
            importance=3,
            tags=["mcp", "tools"],
        ),
        create_memory(
            memory_type="episodic",
            project="test",
            content="Added MCP tool for memory storage",
            importance=3,
            tags=["mcp", "tools"],
        ),
        create_memory(
            memory_type="episodic",
            project="test",
            content="Tested MCP tools with Bob",
            importance=4,
            tags=["mcp", "testing"],
        ),
    ]
    
    suggestion = reflector.analyze_episode_cluster(episodes)
    if suggestion:
        print(f"   PASS: Suggested - {suggestion.reason}")
        print(f"   Episode count: {len(suggestion.episode_ids)}")
        print(f"   Suggested importance: {suggestion.suggested_importance}")
    else:
        print("   FAIL: No suggestion (expected one)")
    
    # Test 2: High average importance
    print("\n2. High average importance (no common tags)")
    high_imp_episodes = [
        create_memory(
            memory_type="episodic",
            project="test",
            content="Critical bug fix",
            importance=4,
        ),
        create_memory(
            memory_type="episodic",
            project="test",
            content="Major feature implementation",
            importance=5,
        ),
    ]
    
    suggestion = reflector.analyze_episode_cluster(high_imp_episodes)
    if suggestion:
        print(f"   PASS: Suggested - {suggestion.reason}")
        print(f"   Suggested importance: {suggestion.suggested_importance}")
    else:
        print("   FAIL: No suggestion (expected one)")
    
    # Test 3: Old episodes (outside time window)
    print("\n3. Old episodes (outside 7-day window)")
    old_episodes = [
        create_memory(
            memory_type="episodic",
            project="test",
            content="Old task 1",
            importance=4,
        ),
        create_memory(
            memory_type="episodic",
            project="test",
            content="Old task 2",
            importance=4,
        ),
    ]
    # Make them old
    for ep in old_episodes:
        ep.created_at = current_time - timedelta(days=10)
    
    suggestion = reflector.analyze_episode_cluster(old_episodes)
    if suggestion is None:
        print("   PASS: No suggestion (episodes too old)")
    else:
        print(f"   FAIL: Unexpected suggestion - {suggestion.reason}")
    
    # Test 4: Single episode (should NOT suggest)
    print("\n4. Single episode (need at least 2)")
    single = [
        create_memory(
            memory_type="episodic",
            project="test",
            content="Solo task",
            importance=4,
        ),
    ]
    
    suggestion = reflector.analyze_episode_cluster(single)
    if suggestion is None:
        print("   PASS: No suggestion (need multiple episodes)")
    else:
        print(f"   FAIL: Unexpected suggestion - {suggestion.reason}")
    
    print("\n" + "=" * 80)


def test_reflection_prompts():
    """Test reflection prompt generation."""
    print("\n\nTesting Reflection Prompt Generation\n")
    print("=" * 80)
    
    reflector = MemoryReflector()
    
    # Test 1: Single episode
    print("\n1. Single episode prompt")
    episode = create_memory(
        memory_type="episodic",
        project="test",
        content="Fixed auth bug by implementing token refresh logic",
        importance=4,
    )
    
    prompt = reflector.suggest_reflection_prompt([episode])
    print(f"   Prompt length: {len(prompt)} chars")
    if "Reflect on this episode" in prompt and "lesson" in prompt.lower():
        print("   PASS: Prompt contains expected elements")
    else:
        print("   FAIL: Prompt missing expected elements")
    
    # Test 2: Multiple episodes
    print("\n2. Multiple episodes prompt")
    episodes = [
        create_memory(
            memory_type="episodic",
            project="test",
            content="Added MCP tool for recall",
            importance=3,
        ),
        create_memory(
            memory_type="episodic",
            project="test",
            content="Added MCP tool for storage",
            importance=3,
        ),
    ]
    
    prompt = reflector.suggest_reflection_prompt(episodes)
    print(f"   Prompt length: {len(prompt)} chars")
    if "2 related episodes" in prompt and "pattern" in prompt.lower():
        print("   PASS: Prompt contains expected elements")
    else:
        print("   FAIL: Prompt missing expected elements")
    
    # Test 3: Empty list
    print("\n3. Empty episode list")
    prompt = reflector.suggest_reflection_prompt([])
    if "No episodes" in prompt:
        print("   PASS: Handles empty list")
    else:
        print("   FAIL: Doesn't handle empty list")
    
    print("\n" + "=" * 80)


def test_keyword_extraction():
    """Test keyword extraction from episodes."""
    print("\n\nTesting Keyword Extraction\n")
    print("=" * 80)
    
    reflector = MemoryReflector()
    
    episodes = [
        create_memory(
            memory_type="episodic",
            project="test",
            content="Task 1",
            tags=["mcp", "tools"],
        ),
        create_memory(
            memory_type="episodic",
            project="test",
            content="Task 2",
            tags=["mcp", "testing"],
        ),
    ]
    
    keywords = reflector.extract_lesson_keywords(episodes)
    
    print(f"\n   Extracted keywords: {keywords}")
    
    # Check for episode tags
    if "mcp" in keywords and "tools" in keywords:
        print("   PASS: Contains episode tags")
    else:
        print("   FAIL: Missing episode tags")
    
    # Check for procedural keywords
    if "procedure" in keywords or "lesson" in keywords:
        print("   PASS: Contains procedural keywords")
    else:
        print("   FAIL: Missing procedural keywords")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        test_single_episode_suggestions()
        test_episode_cluster_analysis()
        test_reflection_prompts()
        test_keyword_extraction()
        print("\n\nAll reflector tests completed successfully!")
        
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
