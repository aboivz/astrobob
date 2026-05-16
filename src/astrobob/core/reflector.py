"""
Reflection system for converting episodic memories into procedural knowledge.

The reflector analyzes episodic memories and suggests when they should be
distilled into reusable procedural memories (lessons learned).
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from astrobob.models import MemoryDocument


class ReflectionSuggestion:
    """Suggestion to reflect on episodic memories."""
    
    def __init__(
        self,
        reason: str,
        episode_ids: list[str],
        suggested_importance: int = 3,
    ):
        """
        Initialize reflection suggestion.
        
        Args:
            reason: Why reflection is suggested
            episode_ids: IDs of episodes to reflect on
            suggested_importance: Suggested importance for the procedural memory
        """
        self.reason = reason
        self.episode_ids = episode_ids
        self.suggested_importance = suggested_importance
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "reason": self.reason,
            "episode_ids": self.episode_ids,
            "suggested_importance": self.suggested_importance,
        }


class MemoryReflector:
    """
    Analyzes episodic memories and suggests when to create procedural memories.
    
    Uses heuristics to identify patterns that indicate reusable knowledge:
    - Multiple similar episodes in a short time
    - High-importance episodes
    - Episodes with success indicators
    """
    
    def __init__(self):
        """Initialize reflector."""
        pass
    
    def should_suggest_reflection(
        self,
        memory: MemoryDocument,
        recent_episode_count: int = 0,
    ) -> Optional[ReflectionSuggestion]:
        """
        Determine if a memory should trigger a reflection suggestion.
        
        Args:
            memory: The memory to analyze
            recent_episode_count: Number of recent episodes in same project
            
        Returns:
            ReflectionSuggestion if reflection is recommended, None otherwise
        """
        # Only suggest for episodic memories
        if memory.memory_type != "episodic":
            return None
        
        # Rule 1: High-importance episodes should be reflected
        if memory.importance >= 4:
            return ReflectionSuggestion(
                reason="High-importance episode detected",
                episode_ids=[memory.id],
                suggested_importance=memory.importance,
            )
        
        # Rule 2: Multiple recent episodes suggest a pattern
        if recent_episode_count >= 3 and memory.importance >= 3:
            return ReflectionSuggestion(
                reason=f"Multiple recent episodes ({recent_episode_count}) suggest a pattern",
                episode_ids=[memory.id],
                suggested_importance=3,
            )
        
        # Rule 3: Episodes with success indicators
        if memory.success_count > 0:
            return ReflectionSuggestion(
                reason="Episode has proven successful",
                episode_ids=[memory.id],
                suggested_importance=4,
            )
        
        return None
    
    def analyze_episode_cluster(
        self,
        episodes: list[MemoryDocument],
        time_window_days: int = 7,
    ) -> Optional[ReflectionSuggestion]:
        """
        Analyze a cluster of episodes to suggest reflection.
        
        Looks for patterns across multiple episodes that indicate
        a reusable procedure or lesson learned.
        
        Args:
            episodes: List of episodic memories to analyze
            time_window_days: Time window for clustering (days)
            
        Returns:
            ReflectionSuggestion if pattern detected, None otherwise
        """
        if not episodes:
            return None
        
        # Filter to episodic only
        episodes = [e for e in episodes if e.memory_type == "episodic"]
        
        if len(episodes) < 2:
            return None
        
        # Check if episodes are within time window
        current_time = datetime.now(timezone.utc)
        cutoff_time = current_time - timedelta(days=time_window_days)
        
        recent_episodes = [
            e for e in episodes
            if e.created_at >= cutoff_time
        ]
        
        if len(recent_episodes) < 2:
            return None
        
        # Check for common tags (indicates related activities)
        all_tags = set()
        for episode in recent_episodes:
            all_tags.update(episode.tags)
        
        common_tags = []
        for tag in all_tags:
            count = sum(1 for e in recent_episodes if tag in e.tags)
            if count >= 2:
                common_tags.append(tag)
        
        if common_tags:
            avg_importance = sum(e.importance for e in recent_episodes) / len(recent_episodes)
            suggested_importance = min(5, int(avg_importance) + 1)
            
            return ReflectionSuggestion(
                reason=f"Found {len(recent_episodes)} related episodes with common tags: {', '.join(common_tags)}",
                episode_ids=[e.id for e in recent_episodes],
                suggested_importance=suggested_importance,
            )
        
        # Check for high average importance
        avg_importance = sum(e.importance for e in recent_episodes) / len(recent_episodes)
        if avg_importance >= 3.5:
            return ReflectionSuggestion(
                reason=f"Found {len(recent_episodes)} high-importance episodes (avg: {avg_importance:.1f})",
                episode_ids=[e.id for e in recent_episodes],
                suggested_importance=4,
            )
        
        return None
    
    def suggest_reflection_prompt(
        self,
        episodes: list[MemoryDocument],
    ) -> str:
        """
        Generate a prompt to help the user reflect on episodes.
        
        Args:
            episodes: Episodes to reflect on
            
        Returns:
            Suggested reflection prompt
        """
        if not episodes:
            return "No episodes to reflect on."
        
        if len(episodes) == 1:
            episode = episodes[0]
            return (
                f"Reflect on this episode:\n\n"
                f"{episode.content}\n\n"
                f"What lesson or procedure can be extracted from this experience?"
            )
        
        # Multiple episodes
        episode_summaries = []
        for i, episode in enumerate(episodes, 1):
            summary = episode.summary or episode.content[:100]
            episode_summaries.append(f"{i}. {summary}")
        
        return (
            f"Reflect on these {len(episodes)} related episodes:\n\n"
            + "\n".join(episode_summaries) +
            "\n\nWhat common pattern or procedure emerges from these experiences?"
        )
    
    def extract_lesson_keywords(
        self,
        episodes: list[MemoryDocument],
    ) -> list[str]:
        """
        Extract potential keywords for the procedural memory.
        
        Args:
            episodes: Episodes to analyze
            
        Returns:
            List of suggested keywords/tags
        """
        # Collect all tags from episodes
        all_tags = set()
        for episode in episodes:
            all_tags.update(episode.tags)
        
        # Add common procedural keywords
        procedural_keywords = ["procedure", "lesson", "pattern"]
        
        return list(all_tags) + procedural_keywords

# Made with Bob
