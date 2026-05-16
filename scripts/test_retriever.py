"""
Test script for memory retriever with query-intent routing.

Tests that queries are routed to the correct collections based on intent.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from astrobob.core.retriever import infer_collection_priority


def test_query_routing():
    """Test that query intent routing works correctly."""
    print("Testing Query-Intent Routing\n")
    print("=" * 80)
    
    test_cases = [
        # Procedural queries
        ("How to add a new MCP tool?", ["procedural", "semantic", "episodic"]),
        ("What's the best way to handle errors?", ["procedural", "semantic", "episodic"]),
        ("Should I use async or sync?", ["procedural", "semantic", "episodic"]),
        ("When should I call reflect()?", ["procedural", "semantic", "episodic"]),
        
        # Semantic queries
        ("What is AstraDB?", ["semantic", "procedural", "episodic"]),
        ("What does the ranking formula do?", ["semantic", "procedural", "episodic"]),
        ("Is there a memory limit?", ["semantic", "procedural", "episodic"]),
        ("Define episodic memory", ["semantic", "procedural", "episodic"]),
        
        # Episodic queries
        ("What happened last time I deployed?", ["episodic", "semantic", "procedural"]),
        ("Why did the test fail yesterday?", ["episodic", "semantic", "procedural"]),
        ("When did I add the ranking system?", ["episodic", "semantic", "procedural"]),
        ("Remember when we fixed the auth bug?", ["episodic", "semantic", "procedural"]),
        
        # Ambiguous queries
        ("Tell me about memory", ["semantic", "procedural", "episodic"]),  # "about" is semantic
        ("Search for ranking", ["procedural", "semantic", "episodic"]),  # default to procedural
    ]
    
    passed = 0
    failed = 0
    
    for query, expected_priority in test_cases:
        actual_priority = infer_collection_priority(query)
        
        if actual_priority == expected_priority:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1
        
        print(f"\n[{status}] Query: \"{query}\"")
        print(f"  Expected: {expected_priority}")
        print(f"  Actual:   {actual_priority}")
    
    print("\n" + "=" * 80)
    print(f"\nResults: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("\nSome tests failed!")
        sys.exit(1)
    else:
        print("\nAll query routing tests passed!")


def test_keyword_detection():
    """Test specific keyword detection."""
    print("\n\nTesting Keyword Detection\n")
    print("=" * 80)
    
    # Test procedural keywords
    procedural_queries = [
        "how to do something",
        "how do i configure this",
        "how can i improve performance",
        "should i use this approach",
        "when to call this function",
        "steps to deploy",
        "what's the procedure for",
        "best way to handle",
    ]
    
    print("\nProcedural Keywords:")
    for query in procedural_queries:
        priority = infer_collection_priority(query)
        if priority[0] == "procedural":
            print(f"  PASS: \"{query}\" -> {priority[0]}")
        else:
            print(f"  FAIL: \"{query}\" -> {priority[0]} (expected procedural)")
    
    # Test semantic keywords
    semantic_queries = [
        "what is this thing",
        "what are the options",
        "what does this do",
        "is there a limit",
        "does it support async",
        "can it handle errors",
        "define this term",
        "explain how it works",
    ]
    
    print("\nSemantic Keywords:")
    for query in semantic_queries:
        priority = infer_collection_priority(query)
        if priority[0] == "semantic":
            print(f"  PASS: \"{query}\" -> {priority[0]}")
        else:
            print(f"  FAIL: \"{query}\" -> {priority[0]} (expected semantic)")
    
    # Test episodic keywords
    episodic_queries = [
        "last time we deployed",
        "previous attempt failed",
        "history of changes",
        "when did this happen",
        "why did we do that",
        "what happened yesterday",
        "remember when we fixed",
        "two days ago",
    ]
    
    print("\nEpisodic Keywords:")
    for query in episodic_queries:
        priority = infer_collection_priority(query)
        if priority[0] == "episodic":
            print(f"  PASS: \"{query}\" -> {priority[0]}")
        else:
            print(f"  FAIL: \"{query}\" -> {priority[0]} (expected episodic)")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        test_query_routing()
        test_keyword_detection()
        print("\n\nAll retriever tests completed successfully!")
        
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
