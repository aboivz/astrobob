---
name: agent-reflector
description: Convert episodic experiences into reusable procedural knowledge through systematic reflection
---

Use this skill when you need to:
- Convert episodic experiences into reusable procedural knowledge
- Identify patterns across multiple tasks or sessions
- Distill lessons learned from problem-solving
- Create actionable procedures from trial-and-error
- Build a knowledge base of best practices

## Core Philosophy

**Reflection transforms experience into expertise.**

The goal is not to remember everything, but to extract reusable patterns that make future work more efficient. Good reflection creates procedural memories that:
- Save time on similar future tasks
- Prevent repeating mistakes
- Codify best practices
- Build institutional knowledge

## When to Reflect

### Strong Signals (Always Reflect)
- ✅ Solved a problem after 3+ attempts
- ✅ Discovered a non-obvious solution
- ✅ Found a pattern that applies to multiple scenarios
- ✅ Learned a best practice the hard way
- ✅ Created a reusable multi-step procedure

### Weak Signals (Consider Reflecting)
- ⚠️ Completed a complex task successfully
- ⚠️ Fixed a bug with interesting root cause
- ⚠️ Learned a new tool or technique
- ⚠️ Made an architectural decision

### Don't Reflect On
- ❌ Routine tasks with no new insights
- ❌ One-off fixes with no reusable pattern
- ❌ Trivial completions
- ❌ Tasks where you just followed existing procedures

## Reflection Process

### Step 1: Identify Episodes
Look for related episodic memories that share:
- Common problem domain
- Similar solution approaches
- Recurring patterns
- Connected decisions

```python
# Find related episodes
recall(
    query="authentication bug fixes",
    memory_type="episodic",
    project="myproject",
    limit=10
)
```

### Step 2: Extract the Pattern
Ask yourself:
- What was the underlying problem?
- What approach worked?
- What didn't work and why?
- What would I do differently next time?
- What's the reusable pattern here?

### Step 3: Formulate the Lesson
Good procedural memories are:
- **Actionable**: Steps you can follow
- **Specific**: Concrete, not abstract
- **Contextualized**: When to apply it
- **Concise**: Core insight, not full story

### Step 4: Create Procedural Memory
```python
reflect(
    project="myproject",
    episode_ids=["01ABC...", "01DEF...", "01GHI..."],
    lesson="Auth debugging checklist: 1) Check token expiry 2) Verify refresh logic 3) Test edge cases (expired, invalid, missing) 4) Add logging at each step",
    tags=["auth", "debugging", "checklist"],
    importance=5
)
```

## Reflection Templates

### Template 1: Debugging Procedure
```
[Problem Type] debugging checklist:
1. [First diagnostic step]
2. [Second diagnostic step]
3. [Common root causes to check]
4. [Verification steps]
5. [Prevention measures]
```

**Example:**
```
API timeout debugging checklist:
1. Check network connectivity and DNS
2. Verify endpoint URL and authentication
3. Test with curl to isolate client issues
4. Check server logs for errors
5. Add retry logic with exponential backoff
```

### Template 2: Implementation Pattern
```
To [accomplish goal]:
1. [Setup/preparation step]
2. [Core implementation steps]
3. [Testing approach]
4. [Common pitfalls to avoid]
```

**Example:**
```
To add a new MCP tool:
1. Define tool schema in mcp_server/schemas.py
2. Implement handler in mcp_server/tools.py
3. Add to server.py tool list
4. Test with MCP Inspector
5. Avoid: Don't forget to handle errors and return proper JSON
```

### Template 3: Decision Framework
```
When deciding [decision type]:
- Consider: [key factors]
- If [condition], then [approach A]
- If [condition], then [approach B]
- Red flags: [warning signs]
```

**Example:**
```
When deciding memory importance level:
- Consider: Reusability, specificity, project scope
- If used daily: importance 5
- If project-specific best practice: importance 4
- If useful but not critical: importance 3
- Red flags: Generic advice, one-off solutions
```

### Template 4: Troubleshooting Guide
```
If [symptom]:
1. Check [most common cause]
2. If not, check [second most common]
3. If still failing, [diagnostic approach]
4. Last resort: [escalation path]
```

**Example:**
```
If recall() returns no results:
1. Check query phrasing (use natural language)
2. If not, verify project name matches stored memories
3. If still empty, check memory report for existence
4. Last resort: Check AstraDB connection and collections
```

## Quality Guidelines

### Excellent Procedural Memories

✅ **Specific and Actionable**
```
"To fix CORS errors: 1) Add CORS middleware to FastAPI app 2) Set allow_origins=['*'] for dev 3) Restrict to specific domains in prod 4) Test with browser DevTools"
```

✅ **Includes Context**
```
"When adding new database models: 1) Define Pydantic model first 2) Create Alembic migration 3) Update API schemas 4) Add tests for CRUD operations. Note: Always test migrations on staging first."
```

✅ **Captures Lessons Learned**
```
"Auth token refresh pattern: Store expiry time with token, check before each request, refresh if <5min remaining. Learned: Don't wait until expired - race conditions cause 401s."
```

### Poor Procedural Memories

❌ **Too Generic**
```
"Always write tests" (not actionable)
```

❌ **Missing Context**
```
"Run pytest -v" (when? why? what to check?)
```

❌ **Just a Log Entry**
```
"Fixed bug in auth.py line 42" (no reusable pattern)
```

## Reflection Workflow

### Daily Reflection (End of Session)
1. Review episodic memories from today
2. Identify 1-2 patterns worth capturing
3. Create procedural memories for reusable insights
4. Tag appropriately for future retrieval

### Weekly Reflection (Maintenance)
1. Review procedural memories created this week
2. Consolidate duplicates
3. Update importance based on actual usage
4. Archive outdated procedures

### Project Reflection (Milestones)
1. Review all project memories
2. Identify cross-cutting patterns
3. Create high-level procedural guides
4. Document architectural decisions

## Integration with Memory System

### Before Reflection
```python
# 1. Find related episodes
episodes = recall(
    query="recent authentication work",
    memory_type="episodic",
    project="myproject",
    limit=10
)

# 2. Review episode details
for ep in episodes:
    audit_trail(memory_type="episodic", memory_id=ep.id)
```

### During Reflection
```python
# 3. Create procedural memory
reflect(
    project="myproject",
    episode_ids=[ep.id for ep in episodes],
    lesson="[Extracted pattern]",
    tags=["domain", "type"],
    importance=4
)
```

### After Reflection
```python
# 4. Verify procedural memory
recall(
    query="authentication procedures",
    memory_type="procedural",
    project="myproject"
)

# 5. Check provenance
audit_trail(memory_type="procedural", memory_id="[new_id]")
```

## Common Reflection Scenarios

### Scenario 1: Bug Fix Pattern
**Episodes:** Fixed 3 similar auth bugs
**Pattern:** All involved token expiry edge cases
**Lesson:** "Auth token edge case checklist: expired, missing, malformed, wrong scope, revoked"
**Importance:** 5 (will use constantly)

### Scenario 2: Tool Usage
**Episodes:** Used pytest multiple times with different flags
**Pattern:** Specific flag combinations for different scenarios
**Lesson:** "Pytest usage: -v for verbose, -x for fail-fast, -k for pattern matching, --cov for coverage"
**Importance:** 3 (useful reference)

### Scenario 3: Architecture Decision
**Episodes:** Evaluated 3 approaches for API design
**Pattern:** Trade-offs between REST and GraphQL
**Lesson:** "API design decision: Use REST for simple CRUD, GraphQL for complex queries with nested data. Consider: team expertise, client needs, caching strategy"
**Importance:** 4 (project-specific but reusable)

## Anti-Patterns

### Over-Reflection
❌ Creating procedural memory for every single task
✅ Only reflect when there's a reusable pattern

### Under-Reflection
❌ Never creating procedural memories, just episodic
✅ Regular reflection sessions to extract patterns

### Premature Reflection
❌ Reflecting after first attempt at something
✅ Wait for pattern to emerge across multiple episodes

### Vague Reflection
❌ "Remember to be careful with auth"
✅ "Auth checklist: 1) Validate token 2) Check expiry 3) Verify scope"

## Success Metrics

- Procedural memories are actually used in future sessions
- Time to complete similar tasks decreases
- Fewer repeated mistakes
- Growing library of reusable procedures
- Improved code quality and consistency

## Tips for Effective Reflection

1. **Reflect regularly**: End of day, end of week, end of project
2. **Be specific**: Concrete steps, not abstract principles
3. **Include context**: When to apply, when not to apply
4. **Link episodes**: Maintain provenance for traceability
5. **Update over time**: Refine procedures as you learn more
6. **Tag thoughtfully**: Make procedures discoverable
7. **Set importance**: Prioritize what you'll actually use

---

*This skill is part of the AstroBob memory system. Use it to transform your experiences into reusable expertise.*