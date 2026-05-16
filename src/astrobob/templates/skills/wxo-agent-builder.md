# WxO Agent Builder

## When to use this skill

Use this skill when building multi-agent systems with IBM watsonx Orchestrate (WxO), including:
- Designing agent architectures
- Integrating AstroBob memory with WxO agents
- Creating agent workflows and orchestration
- Implementing agent communication patterns
- Building memory-aware agent teams

## Core Concepts

### Agent Types in WxO
1. **Supervisor Agent**: Orchestrates other agents, delegates tasks
2. **Specialist Agent**: Focused on specific domain (e.g., code, memory, testing)
3. **Tool Agent**: Wraps external tools and APIs
4. **Memory Agent**: Manages persistent knowledge (powered by AstroBob)

### Memory-Aware Agents

Agents enhanced with AstroBob gain:
- **Persistent knowledge** across sessions
- **Learning from experience** via reflection
- **Shared memory** across agent team
- **Provenance tracking** for decisions
- **Continuous improvement** over time

## Integration Patterns

### Pattern 1: Memory-Enhanced Specialist
```yaml
# Agent with AstroBob memory access
agent:
  name: code-specialist
  role: "Python code expert with persistent memory"
  tools:
    - mcp: astrobob
  system_prompt: |
    Before coding tasks, recall relevant patterns.
    After completing tasks, store reusable knowledge.
```

**Use when:**
- Agent needs to learn from past work
- Patterns should persist across sessions
- Knowledge should be shared with team

### Pattern 2: Supervisor with Memory Coordination
```yaml
# Supervisor that coordinates memory across agents
supervisor:
  name: team-lead
  agents:
    - code-specialist
    - test-specialist
    - memory-coordinator
  workflow:
    - recall: Check team knowledge base
    - delegate: Assign to specialist
    - reflect: Store lessons learned
```

**Use when:**
- Multiple agents need shared context
- Team learning is important
- Coordination requires memory

### Pattern 3: Memory-First Agent
```yaml
# Agent that primarily manages memory
memory-agent:
  name: knowledge-keeper
  role: "Manages team knowledge and learning"
  tools:
    - mcp: astrobob
  responsibilities:
    - Curate procedural memories
    - Suggest reflections
    - Maintain knowledge quality
```

**Use when:**
- Memory management is critical
- Knowledge curation is needed
- Team has many agents

## AstroBob + WxO Integration

### Setup
1. Install AstroBob: `pip install astrobob`
2. Initialize: `astrobob init`
3. Configure WxO agents to use MCP server
4. Add memory-aware prompts to agents

### Agent Configuration
```yaml
# In WxO agent config
tools:
  mcp:
    - name: astrobob
      command: python
      args: ["-m", "astrobob.mcp_server.server"]
      env:
        ASTRA_DB_API_ENDPOINT: "${ASTRA_ENDPOINT}"
        ASTRA_DB_APPLICATION_TOKEN: "${ASTRA_TOKEN}"
```

### Memory-Aware Prompts
```
System Prompt Template:

You are [agent role] with access to persistent memory via AstroBob.

Before starting tasks:
1. recall() relevant procedural knowledge
2. recall() project conventions and patterns

During tasks:
- Note important discoveries
- Track decision rationale

After completing tasks:
1. remember() key learnings (semantic/episodic)
2. Consider reflect() for reusable patterns

Memory Guidelines:
- Be specific and actionable
- Tag appropriately for retrieval
- Set importance based on reusability
- Link related memories via provenance
```

## Agent Workflows

### Workflow 1: Code Generation with Memory
```
1. User Request → Supervisor
2. Supervisor → recall("similar code patterns")
3. Supervisor → Delegate to Code Agent
4. Code Agent → recall("project conventions")
5. Code Agent → Generate code
6. Code Agent → remember(episodic: "generated X feature")
7. Test Agent → Validate
8. Supervisor → reflect("code generation pattern")
```

### Workflow 2: Debugging with Team Memory
```
1. Bug Report → Supervisor
2. Supervisor → recall("similar bugs")
3. Supervisor → Check if known issue
4. If new → Delegate to Debug Agent
5. Debug Agent → recall("debugging procedures")
6. Debug Agent → Investigate and fix
7. Debug Agent → remember(episodic: "fixed bug X")
8. Memory Agent → reflect("debugging pattern")
```

### Workflow 3: Knowledge Curation
```
1. End of Sprint → Memory Agent
2. Memory Agent → Review episodic memories
3. Memory Agent → Identify patterns
4. Memory Agent → reflect() to create procedures
5. Memory Agent → Update importance scores
6. Memory Agent → Archive outdated knowledge
```

## Best Practices

### Agent Design
- **Single Responsibility**: Each agent has clear role
- **Memory Scope**: Define what each agent should remember
- **Shared Context**: Use project tags for team memory
- **Provenance**: Link agent decisions to memories

### Memory Management
- **Distributed Storage**: All agents write to same AstroBob
- **Centralized Curation**: One agent manages quality
- **Scoped Retrieval**: Agents query relevant memories
- **Regular Reflection**: Scheduled knowledge distillation

### Orchestration
- **Memory-First**: Check knowledge before acting
- **Learn Continuously**: Store insights after tasks
- **Share Knowledge**: Tag for team-wide access
- **Improve Over Time**: Reflect on agent performance

## Example: Multi-Agent Code Team

### Architecture
```
Supervisor (Team Lead)
├── Code Agent (Implementation)
├── Test Agent (Quality)
├── Review Agent (Standards)
└── Memory Agent (Knowledge)
```

### Memory Flow
1. **Supervisor** recalls project patterns
2. **Code Agent** recalls coding conventions
3. **Test Agent** recalls test strategies
4. **Review Agent** recalls quality standards
5. **Memory Agent** curates and reflects

### Shared Memory
- **Project**: "myproject"
- **Tags**: ["architecture", "patterns", "standards"]
- **Importance**: Team-wide procedures = 5
- **Provenance**: Link to agent decisions

## Integration with Bob

### Bob as Supervisor
Bob can orchestrate WxO agents while using AstroBob:
```
Bob → recall("agent orchestration patterns")
Bob → Delegate to WxO agents
Bob → Monitor agent outputs
Bob → reflect("orchestration lessons")
```

### Bob as Specialist
Bob can be a specialist agent in WxO team:
```
WxO Supervisor → Delegate to Bob
Bob → recall("relevant knowledge")
Bob → Complete task
Bob → remember("task completion")
```

## Troubleshooting

### Agents not sharing memory
- Check project tags match
- Verify all agents use same AstroBob instance
- Review memory scope settings

### Memory retrieval slow
- Optimize query phrasing
- Use specific tags
- Limit result count
- Check AstraDB performance

### Knowledge quality issues
- Assign Memory Agent for curation
- Regular reflection sessions
- Review and update importance
- Archive outdated memories

## Future Enhancements

- Agent-specific memory scopes
- Automatic reflection triggers
- Memory conflict resolution
- Agent learning metrics
- Knowledge graph visualization

## Resources

- WxO Documentation: [IBM watsonx Orchestrate docs]
- AstroBob MCP Tools: See `astra-memory-engineer.md`
- Reflection Guide: See `agent-reflector.md`

---

*This skill is part of the AstroBob memory system. Use it to build memory-aware multi-agent systems with WxO.*