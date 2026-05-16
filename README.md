# AstroBob

> **Memory-Powered Agent Toolkit for IBM Bob**  
> Give your AI agents persistent semantic, episodic, and procedural memory via AstraDB

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

---

## 🎯 What is AstroBob?

AstroBob is a memory system that gives IBM Bob (and other AI agents) the ability to **remember, learn, and improve** across sessions. Instead of forgetting everything between conversations, agents can:

- **Remember facts** (semantic memory) - "This project uses FastAPI 0.104"
- **Recall events** (episodic memory) - "Fixed auth bug on May 15th"
- **Apply procedures** (procedural memory) - "How to add a new MCP tool: 5 steps"

**The Magic**: Bob can reflect on its experiences and write its own skills, creating a self-improving feedback loop.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- AstraDB Serverless account ([free tier available](https://astra.datastax.com))
- IBM Bob trial or subscription

### Installation

#### Option 1: Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install AstroBob
uv tool install astrobob

# Or install from source
git clone https://github.com/aboivz/astrobob.git
cd astrobob
uv sync
```

#### Option 2: Using pip

```bash
pip install astrobob

# Or from source
git clone https://github.com/aboivz/astrobob.git
cd astrobob
pip install -e .
```

### Configuration

1. **Get AstraDB Credentials**
   - Sign up at [astra.datastax.com](https://astra.datastax.com)
   - Create a Serverless database in `us-east-2`
   - Enable "Hybrid Search" and "Rerank" features
   - Copy your API Endpoint and Application Token

2. **Set Environment Variables**

```bash
# Create .env file in your project
cat > .env << EOF
ASTRA_DB_API_ENDPOINT=https://your-db-id-us-east-2.apps.astra.datastax.com
ASTRA_DB_APPLICATION_TOKEN=AstraCS:your-token-here
EOF
```

3. **Initialize AstroBob**

```bash
# Navigate to your project directory
cd ~/projects/my-project

# Initialize AstroBob (creates .bob/ directory and configs)
astrobob init

# Set up AstraDB collections
astrobob astra setup
```

4. **Verify Installation**

```bash
# Run health check
astrobob doctor
```

You should see all checks passing! ✅

---

## 📖 Usage

### Basic Memory Operations

#### Store a Memory

```bash
# Store a semantic memory (fact)
astrobob memory remember \
  --type semantic \
  --content "Project uses FastAPI 0.104 with async routes" \
  --importance 4 \
  --tags python,fastapi,web

# Store an episodic memory (event)
astrobob memory remember \
  --type episodic \
  --content "Fixed authentication bug by adding token refresh logic" \
  --importance 3 \
  --tags bug,auth,fix

# Store a procedural memory (how-to)
astrobob memory remember \
  --type procedural \
  --content "To add MCP tool: 1) Implement in core/store.py, 2) Add to mcp_server/tools.py, 3) Update schemas.py, 4) Test with MCP Inspector, 5) Document in README" \
  --importance 5 \
  --tags mcp,development,procedure
```

#### Recall Memories

```bash
# Search across all memory types
astrobob memory recall "how to add MCP tool"

# Search specific memory type
astrobob memory recall "authentication" --type episodic

# Filter by tags
astrobob memory recall "bug fixes" --tags auth,bug

# Limit results
astrobob memory recall "python" --limit 5
```

#### Reflect on Experiences

```bash
# Create procedural memory from episodic memories
astrobob memory reflect \
  --project my-project \
  --episode-id <episode-id-1> \
  --episode-id <episode-id-2> \
  --lesson "Always add tests when implementing new features" \
  --importance 4
```

#### View Memory Report

```bash
# See memory statistics
astrobob memory report

# For specific project
astrobob memory report --project my-project
```

### Using with IBM Bob

AstroBob integrates seamlessly with IBM Bob via MCP (Model Context Protocol).

#### 1. Start MCP Server

```bash
# STDIO mode (default for Bob)
astrobob mcp

# HTTP mode (for debugging)
astrobob mcp --http
```

#### 2. Bob Configuration

The `astrobob init` command creates `.bob/mcp.json` with the correct configuration:

```json
{
  "mcpServers": {
    "astrobob": {
      "command": "astrobob",
      "args": ["mcp"],
      "env": {
        "ASTRA_DB_API_ENDPOINT": "your-endpoint",
        "ASTRA_DB_APPLICATION_TOKEN": "your-token"
      }
    }
  }
}
```

#### 3. Available MCP Tools

Bob can use these 5 tools:

| Tool | Purpose | Example |
|------|---------|---------|
| `remember` | Store new memory | `remember(type="semantic", content="...")` |
| `recall` | Search memories | `recall(query="how to deploy")` |
| `reflect` | Create procedural from episodic | `reflect(episode_ids=[...], lesson="...")` |
| `forget` | Soft-delete memory | `forget(type="episodic", memory_id="...")` |
| `audit_trail` | View memory history | `audit_trail(type="procedural", memory_id="...")` |

#### 4. Bob Skills

AstroBob includes 3 pre-built skills for Bob:

- **Astra Memory Engineer** - Manages memory operations
- **WxO Agent Builder** - Builds multi-agent systems
- **Agent Reflector** - Facilitates learning from experience

#### 5. Export Learned Skills

```bash
# Export high-importance procedural memories as Bob skills
astrobob skills sync

# Dry run to preview
astrobob skills sync --dry-run

# Filter by importance
astrobob skills sync --min-importance 4
```

This creates `.bob/skills/learned/<skill-name>/SKILL.md` files that Bob can use natively!

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│  Bob / BobShell (MCP Client)        │
└─────────────┬───────────────────────┘
              │ MCP STDIO/HTTP
┌─────────────▼───────────────────────┐
│  FastMCP Server (5 tools)           │
│  remember·recall·reflect·forget·audit│
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  Service Layer (core/)              │
│  MemoryStore·Retriever·Reflector    │
└─────────────┬───────────────────────┘
              │ astrapy
┌─────────────▼───────────────────────┐
│  AstraDB (3 collections)            │
│  semantic·episodic·procedural       │
└─────────────────────────────────────┘
```

### Memory Types

| Type | Purpose | Example | Lifecycle |
|------|---------|---------|-----------|
| **Semantic** | Stable facts | "Project uses FastAPI 0.104" | Update + supersede |
| **Episodic** | Events that happened | "Fixed auth bug on 2026-05-15" | Append-only |
| **Procedural** | Reusable playbooks | "How to add MCP tool: 5 steps" | Curate by success_count |

**Key Insight**: Reflections convert episodic → procedural via the `reflect()` tool.

### Ranking System

Memories are ranked using a weighted formula:

```
final_score = (
    0.55 * astra_rerank_score +      # AstraDB's hybrid search score
    0.15 * (importance / 5.0) +       # User-assigned importance
    0.15 * exp(-age_days / 30) +      # Recency (30-day half-life)
    0.10 * log1p(success_count) / log1p(20) -  # Success tracking
    0.05 * staleness_penalty          # Penalize unaccessed memories
)
```

This ensures the most relevant, important, and recent memories surface first.

---

## 🔧 Advanced Usage

### WxO Multi-Agent Integration

AstroBob supports Watsonx Orchestrate (WxO) multi-agent systems. See `examples/wxo/` for:

- Agent configuration templates
- Memory coordination patterns
- Python tool wrappers
- Integration examples

### Custom Memory Scopes

```bash
# Project-scoped (default) - visible to project team
astrobob memory remember --scope project --content "..."

# User-scoped - personal preferences
astrobob memory remember --scope user --content "..."

# Global-scoped - universal best practices
astrobob memory remember --scope global --content "..."
```

### Provenance Tracking

Every memory tracks its origin:

```python
{
  "provenance": {
    "derived_from": ["episode-id-1", "episode-id-2"],
    "session_id": "session-123",
    "tool_call_id": "call-456",
    "bob_skill_used": "astra-memory-engineer"
  }
}
```

### Memory Lifecycle

```bash
# View memory details
astrobob memory audit --type procedural --id <memory-id>

# Soft delete (preserves for audit)
astrobob memory forget --type episodic --id <memory-id>

# Update access tracking (automatic on recall)
# Access count and last_accessed_at are updated
```

---

## 🧪 Development

### Running Tests

```bash
# Unit tests
uv run pytest tests/unit/ -v

# Integration tests (requires live AstraDB)
RUN_INTEGRATION=1 uv run pytest tests/integration/ -v

# All tests
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=astrobob --cov-report=html
```

### Project Structure

```
astrobob/
├── src/astrobob/
│   ├── cli/              # CLI commands
│   ├── core/             # Core logic (store, retriever, ranking, reflector)
│   ├── astra/            # AstraDB client and collections
│   ├── mcp_server/       # MCP server implementation
│   ├── skills_export/    # Skill generation from procedural memories
│   ├── templates/        # Jinja2 templates for init command
│   ├── config.py         # Configuration management
│   ├── models.py         # Pydantic data models
│   └── errors.py         # Custom exceptions
├── tests/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── examples/
│   └── wxo/              # WxO integration examples
└── scripts/              # Development scripts
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`uv run pytest tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📚 Documentation

- **[Installation Guide](docs/installation.md)** - Detailed setup instructions
- **[Configuration Guide](docs/configuration.md)** - All configuration options
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[MCP Tools Reference](docs/mcp-tools.md)** - MCP tool specifications
- **[Architecture Guide](docs/architecture.md)** - System design and internals
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

---

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/aboivz/astrobob/issues)
- **Discussions**: [GitHub Discussions](https://github.com/aboivz/astrobob/discussions)
- **Discord**: [Join our community](https://discord.gg/astrobob)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [IBM Bob](https://www.ibm.com/products/watsonx-code-assistant)
- Powered by [AstraDB](https://www.datastax.com/products/datastax-astra)
- Uses [FastMCP](https://github.com/jlowin/fastmcp) for MCP protocol
- Inspired by cognitive science research on human memory systems

---

## 🎯 Roadmap

- [ ] Working memory (short-term context)
- [ ] Memory consolidation (automatic reflection)
- [ ] Multi-user collaboration
- [ ] Memory visualization dashboard
- [ ] Claude Desktop integration
- [ ] VS Code extension

---

**Made with ❤️ and Bob**