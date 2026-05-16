# AstroBob WxO Integration Examples

This directory contains example configurations and tools for integrating AstroBob with IBM WxO (Watsonx Orchestrate) multi-agent systems.

## Overview

AstroBob provides persistent memory capabilities for WxO agents, enabling:
- **Shared Knowledge Base**: All agents access the same memory store
- **Cross-Agent Learning**: Agents learn from each other's experiences
- **Procedural Memory**: Reusable patterns extracted from episodes
- **Memory Coordination**: Supervisor agents manage memory quality

## Directory Structure

```
examples/wxo/
├── agents/
│   ├── code-memory.agent.yaml    # Specialized coding agent
│   └── supervisor.agent.yaml     # Multi-agent coordinator
├── tools/
│   └── memory_tool.py            # Python wrapper for AstroBob
└── README.md                     # This file
```

## Quick Start

### 1. Setup AstroBob

```bash
# Install AstroBob
pip install astrobob

# Initialize in your project
cd your-wxo-project
astrobob init
astrobob astra setup

# Start MCP server (for agent access)
astrobob mcp
```

### 2. Configure WxO Agents

Copy the agent YAML files to your WxO agents directory:

```bash
cp examples/wxo/agents/*.yaml /path/to/wxo/agents/
```

### 3. Use Memory Tool in Agents

```python
from examples.wxo.tools.memory_tool import AstroBobMemoryTool

# Initialize tool
tool = AstroBobMemoryTool(use_direct_api=True)

# Store a memory
memory_id = tool.remember(
    content="How to add MCP tool: 1) Define schema...",
    memory_type="procedural",
    project="my-project",
    tags=["mcp", "development"],
    importance=4,
    agent_name="code-memory"
)

# Retrieve memories
results = tool.recall(
    query="how to add MCP tool",
    project="my-project"
)
```

## Agent Configurations

### Code Memory Agent

**Purpose**: Manages coding knowledge and patterns

**Capabilities**:
- Stores coding patterns as procedural memories
- Retrieves relevant past solutions
- Reflects on bug fixes to extract patterns
- Tags memories by language/framework

**Usage**:
```yaml
# In your WxO workflow
- agent: code-memory
  task: "Implement user authentication"
  memory_actions:
    - recall: "query='auth patterns', tags=['fastapi']"
    - remember: "type='procedural', content='Auth implementation steps...'"
```

### Supervisor Agent

**Purpose**: Coordinates multiple agents and manages shared memory

**Capabilities**:
- Decomposes tasks for specialized agents
- Coordinates memory access across agents
- Triggers cross-agent reflections
- Monitors memory quality

**Usage**:
```yaml
# In your WxO workflow
- agent: supervisor
  task: "Build new feature"
  sub_agents:
    - code-memory: "Implement feature"
    - test-agent: "Write tests"
    - doc-agent: "Update docs"
  coordination:
    - "Share design decisions via memory"
    - "Reflect on full implementation pattern"
```

## Memory Coordination Patterns

### Sequential Workflow

Agents work in sequence, passing knowledge through memory:

```
code-memory → test-agent → doc-agent
     ↓            ↓            ↓
  [stores]    [recalls]    [recalls]
  design      design       design+tests
```

**Example**:
```python
# Agent 1: Code Memory
tool.remember(
    content="Auth uses JWT with 1h expiry",
    memory_type="semantic",
    project="api",
    tags=["auth", "jwt", "design"]
)

# Agent 2: Test Agent (later)
design = tool.recall(
    query="auth design decisions",
    tags=["auth", "design"]
)
# Uses design info to write tests
```

### Parallel Workflow

Agents work independently on separate subtasks:

```
code-memory (feature A) ─┐
                         ├─→ supervisor reflects
test-agent (feature B) ──┘
```

**Example**:
```python
# Both agents store episodes
code_memory_id = tool.remember(
    content="Implemented feature A",
    memory_type="episodic",
    tags=["feature-a"]
)

test_agent_id = tool.remember(
    content="Tested feature B",
    memory_type="episodic",
    tags=["feature-b"]
)

# Supervisor reflects on both
tool.reflect(
    project="api",
    episode_ids=[code_memory_id, test_agent_id],
    lesson="Feature implementation pattern: code first, test second",
    agent_name="supervisor"
)
```

### Collaborative Workflow

Agents work together on same subtask:

```
code-memory + debug-agent → shared episode
```

**Example**:
```python
# Both agents contribute to same memory
tool.remember(
    content="Fixed memory leak by...",
    memory_type="episodic",
    project="api",
    tags=["agent:code-memory", "agent:debug-agent", "memory-leak"],
    importance=4
)
```

## Memory Tagging Conventions

### Required Tags

- `agent:<name>`: Which agent created this memory
- `<task-type>`: Category (feature, bug, refactor, etc.)

### Optional Tags

- `<language>`: Programming language (python, javascript, etc.)
- `<framework>`: Framework or library (fastapi, react, etc.)
- `<pattern>`: Design pattern or technique (singleton, factory, etc.)

### Example

```python
tool.remember(
    content="...",
    tags=[
        "agent:code-memory",      # Required: agent name
        "feature",                # Required: task type
        "python",                 # Optional: language
        "fastapi",                # Optional: framework
        "rest-api"                # Optional: pattern
    ]
)
```

## Memory Scoping

### Project Scope (Default)

Shared across all agents in a project:

```python
tool.remember(
    content="Project uses FastAPI 0.104",
    memory_type="semantic",
    project="my-api",
    scope="project"  # Default
)
```

### User Scope

Agent-specific preferences:

```python
tool.remember(
    content="Code-memory agent prefers pytest over unittest",
    memory_type="semantic",
    project="my-api",
    scope="user"
)
```

### Global Scope

Universal best practices:

```python
tool.remember(
    content="Always validate input before processing",
    memory_type="procedural",
    project="my-api",
    scope="global"
)
```

## Best Practices

### 1. Always Recall Before Acting

```python
# Good
results = tool.recall(query="similar task")
if results:
    # Use past knowledge
else:
    # Proceed without context

# Bad
# Just start without checking memory
```

### 2. Tag Appropriately

```python
# Good
tags=["agent:code-memory", "feature", "python", "fastapi", "auth"]

# Bad
tags=["stuff", "code"]  # Too vague
```

### 3. Set Importance Correctly

- **1-2**: Low importance, transient info
- **3**: Normal importance, useful but not critical
- **4**: High importance, reusable patterns
- **5**: Critical importance, core procedures

### 4. Reflect Regularly

```python
# After 3-5 related episodes
if len(related_episodes) >= 3:
    tool.reflect(
        project="my-api",
        episode_ids=related_episodes,
        lesson="Extracted pattern: ...",
        importance=4
    )
```

### 5. Use Correct Memory Types

- **Semantic**: Stable facts that rarely change
- **Episodic**: Specific events that happened
- **Procedural**: Reusable how-to guides

## Integration with WxO

### Option 1: MCP Integration (Recommended)

Agents communicate with AstroBob via MCP:

```yaml
# In agent config
tools:
  - type: mcp
    server: "astrobob mcp"
    tools:
      - remember
      - recall
      - reflect
      - audit_trail
```

### Option 2: Direct Python API

Agents use Python wrapper directly:

```python
from examples.wxo.tools.memory_tool import AstroBobMemoryTool

tool = AstroBobMemoryTool(use_direct_api=True)
```

### Option 3: CLI Integration

Agents call CLI commands:

```bash
astrobob memory remember \
  --type procedural \
  --content "..." \
  --project my-api \
  --tags mcp,development \
  --importance 4
```

## Troubleshooting

### Memory Not Found

```python
# Check if memory exists
try:
    memory = tool.audit_trail("procedural", memory_id)
except MemoryNotFoundError:
    print("Memory was deleted or doesn't exist")
```

### Poor Recall Results

```python
# Try different query formulations
results1 = tool.recall(query="add MCP tool")
results2 = tool.recall(query="implement MCP tool")
results3 = tool.recall(query="MCP tool scaffolding")

# Or use tags
results = tool.recall(
    query="MCP",
    tags=["mcp", "development"]
)
```

### Memory Quality Issues

```python
# Use audit trail to check provenance
audit = tool.audit_trail("procedural", memory_id)
print(f"Created by: {audit['provenance']['bob_skill_used']}")
print(f"Derived from: {audit['provenance']['derived_from']}")
print(f"Access count: {audit['access_count']}")
```

## Example Workflows

See the agent YAML files for complete workflow examples:
- `agents/code-memory.agent.yaml` - Coding workflows
- `agents/supervisor.agent.yaml` - Multi-agent coordination

## Further Reading

- [AstroBob Documentation](../../README.md)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [IBM WxO Documentation](https://www.ibm.com/products/watsonx-orchestrate)

## Support

For issues or questions:
- GitHub Issues: https://github.com/aboivz/astrobob/issues
- Documentation: See main README.md
- Examples: See `examples/` directory