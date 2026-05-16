---
name: astra-memory-engineer
description: Work with AstroBob's memory system including storing, retrieving, and managing memories via MCP tools
---

Use this skill when working with AstroBob's memory system, including:
- Storing and retrieving memories via MCP tools
- Designing memory schemas and data models
- Optimizing memory retrieval and ranking
- Debugging memory-related issues
- Implementing new memory features

## Core Concepts

### Memory Types
1. **Semantic**: Stable facts and knowledge (e.g., "Project uses FastAPI 0.104")
2. **Episodic**: Events that happened (e.g., "Fixed auth bug on 2026-05-15")
3. **Procedural**: Reusable how-to knowledge (e.g., "Steps to add MCP tool")

### Memory Lifecycle
- **Creation**: Use `remember()` with appropriate type, importance, and tags
- **Retrieval**: Use `recall()` with query-intent routing
- **Reflection**: Use `reflect()` to convert episodes → procedures
- **Deletion**: Use `forget()` for soft-delete (preserves audit trail)
- **Audit**: Use `audit_trail()` to view complete history

## MCP Tools Reference

### remember()
```python
remember(
    content="Project uses FastAPI 0.104 with async routes",
    memory_type="semantic",
    project="myproject",
    tags=["fastapi", "architecture"],
    importance=4
)
```

**When to use:**
- After learning project conventions
- After completing significant tasks
- When discovering reusable patterns

**Importance guidelines:**
- 5: Critical patterns you'll use constantly
- 4: Important knowledge for this project
- 3: Useful but not essential
- 2: Minor details
- 1: Rarely needed

### recall()
```python
recall(
    query="how to add MCP tool",
    memory_type="procedural",  # optional, auto-routed if omitted
    project="astrobob",
    limit=5
)
```

**Query-intent routing:**
- "how to", "should i", "when" → procedural first
- "what is", "is", "does" → semantic first
- "last time", "why did" → episodic first

### reflect()
```python
reflect(
    project="astrobob",
    episode_ids=["01ABC...", "01DEF..."],
    lesson="Always add tests when adding MCP tools",
    tags=["testing", "mcp"],
    importance=4
)
```

**When to suggest:**
- After solving complex problems
- When discovering reusable patterns
- After multiple related episodes
- When learning best practices

### forget()
```python
forget(
    memory_type="episodic",
    memory_id="01ABC..."
)
```

**Use sparingly:**
- Soft-delete preserves audit trail
- Consider updating instead of deleting
- Never delete procedural memories without reflection

### audit_trail()
```python
audit_trail(
    memory_type="procedural",
    memory_id="01ABC..."
)
```

**Use for:**
- Debugging memory issues
- Understanding provenance
- Verifying reflection links
- Checking access patterns

## Decision Tree

### Before starting a task
1. `recall()` for relevant procedural knowledge
2. `recall()` for project conventions
3. Review results and apply patterns

### During task execution
1. Note important discoveries
2. Log significant decisions
3. Track problem-solving approaches

### After completing a task
1. `remember()` semantic facts learned
2. `remember()` episodic events
3. Consider `reflect()` if reusable pattern emerged

### When to reflect
- Solved problem after multiple attempts
- Discovered reusable pattern
- Learned best practice
- Completed complex procedure

## Quality Bar

### Good memories are:
- **Specific**: "Use FastAPI 0.104" not "Use FastAPI"
- **Actionable**: "Run pytest with -v flag" not "Testing is important"
- **Contextualized**: Include project, tags, importance
- **Deduplicated**: Check existing memories first

### Bad memories are:
- Generic advice without context
- Raw chat logs or debug output
- Transient state or temporary values
- Duplicate information

## Anti-patterns

❌ **Don't dump raw logs**
```python
remember("Error: connection timeout\nStack trace: ...", ...)
```

✅ **Do extract lessons**
```python
remember("Connection timeouts resolved by adding retry logic with exponential backoff", ...)
```

❌ **Don't reflect every episode**
```python
# After every single task
reflect(episode_ids=[...], lesson="I completed a task")
```

✅ **Do reflect on patterns**
```python
# After discovering reusable knowledge
reflect(episode_ids=[...], lesson="When adding MCP tools: 1) Define schema 2) Implement handler 3) Test with MCP Inspector")
```

❌ **Don't store transient state**
```python
remember("Current user is logged in", ...)
```

✅ **Do store stable facts**
```python
remember("Auth system uses JWT tokens with 1-hour expiry", ...)
```

## Integration with Bob Workflow

1. **Start of session**: Recall relevant knowledge
2. **During work**: Note discoveries
3. **End of session**: Store memories and reflect
4. **Regular maintenance**: Review and curate procedural memories

## Troubleshooting

### Recall returns no results
- Check query phrasing (use natural language)
- Verify project name matches
- Try broader tags
- Check if memories exist with `astrobob memory report`

### Reflection not creating procedural memory
- Verify episode IDs exist
- Check importance threshold
- Ensure lesson is actionable
- Review provenance links

### Memory quality issues
- Use `audit_trail()` to review history
- Check importance and tags
- Consider updating instead of creating new
- Use `forget()` for outdated memories

## Examples

### Example 1: Learning project convention
```python
# After discovering FastAPI pattern
remember(
    content="All API routes use async def with Depends() for dependency injection",
    memory_type="semantic",
    project="myapi",
    tags=["fastapi", "patterns"],
    importance=4
)
```

### Example 2: Logging bug fix
```python
# After fixing auth bug
remember(
    content="Fixed token refresh bug by adding expiry check before API calls",
    memory_type="episodic",
    project="myapi",
    tags=["auth", "bugfix"],
    importance=3
)
```

### Example 3: Creating procedure from experience
```python
# After multiple auth fixes
reflect(
    project="myapi",
    episode_ids=["01ABC...", "01DEF..."],
    lesson="Auth bug checklist: 1) Check token expiry 2) Verify refresh logic 3) Test edge cases 4) Add logging",
    tags=["auth", "debugging"],
    importance=5
)
```

## Success Metrics

- Procedural memories are reused across sessions
- Recall finds relevant knowledge quickly
- Reflection creates actionable procedures
- Memory quality improves over time
- Bob becomes more efficient with experience

---

*This skill is part of the AstroBob memory system. For more information, see the AstroBob documentation.*