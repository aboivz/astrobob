<div align="center">

<img src="astrobob_logomascot.PNG" alt="AstroBob Logo" width="200"/>

# AstroBob

**Memory-Powered Agent Toolkit for IBM Bob**  
Give your AI agents persistent semantic, episodic, and procedural memory via AstraDB

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

**[📖 Full Documentation](https://aboivz.github.io/astrobob/index.html)** | [Quick Start](#-quick-start) | [MCP Tools](#-mcp-tools) | [Examples](examples/)

</div>

---

## 🎯 What is AstroBob?

AstroBob gives IBM Bob (and other AI agents) the ability to **remember, learn, and improve** across sessions:

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

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install AstroBob
uv tool install astrobob

# Or from source
git clone https://github.com/aboivz/astrobob.git
cd astrobob
uv sync
```

### Configuration

1. **Get AstraDB Credentials**
   - Sign up at [astra.datastax.com](https://astra.datastax.com)
   - Create a Serverless (vector) database in **AWS `us-east-2`** or **GCP `us-east1`**
   - Copy your API Endpoint and Application Token
   - Create .env file accordingly:

```bash
# AstraDB Configuration (Required)
ASTRA_DB_API_ENDPOINT=https://YOUR_DATABASE_ID-YOUR_REGION.apps.astra.datastax.com
ASTRA_DB_APPLICATION_TOKEN=AstraCS:YOUR_TOKEN_HERE
```

2. **Initialize AstroBob**

```bash
# Navigate to your project directory
cd ~/projects/my-project

# Initialize AstroBob (creates .bob/ directory and configs)
astrobob init

# Set up AstraDB collections
astrobob astra setup

# Verify installation
astrobob doctor
```

You should see all checks passing! ✅

---

## 📖 Basic Usage

### Store Memories

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

### Recall Memories

```bash
# Search across all memory types (uses natural language with automatic embedding)
astrobob memory recall "how to add MCP tool" --project my-project

# Search specific memory type
astrobob memory recall "authentication" --project my-project --type episodic

# Filter by tags and importance
astrobob memory recall "bug fixes" --project my-project --tag auth --min-importance 4
```

### Reflect on Experiences

```bash
# Create procedural memory from episodic memories
astrobob memory reflect \
  --project my-project \
  --episode-id <episode-id-1> \
  --episode-id <episode-id-2> \
  --lesson "Always add tests when implementing new features" \
  --importance 4
```

---

## 🤖 MCP Tools

AstroBob integrates with IBM Bob via MCP (Model Context Protocol). Start the server:

```bash
astrobob mcp serve
```

### Available Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `remember` | Store new memory | `remember(type="semantic", content="...")` |
| `recall` | Search memories | `recall(query="how to deploy")` |
| `reflect` | Create procedural from episodic | `reflect(episode_ids=[...], lesson="...")` |
| `forget` | Soft-delete memory | `forget(type="episodic", memory_id="...")` |
| `audit_trail` | View memory history | `audit_trail(type="procedural", memory_id="...")` |

### Export Learned Skills

```bash
# Export high-importance procedural memories as Bob skills
astrobob skills sync

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
│  NVIDIA nvidia/nv-embedqa-e5-v5     │
│  Automatic $vectorize embeddings    │
└─────────────────────────────────────┘
```

### Memory Types

| Type | Purpose | Example |
|------|---------|---------|
| **Semantic** | Stable facts | "Project uses FastAPI 0.104" |
| **Episodic** | Events that happened | "Fixed auth bug on 2026-05-15" |
| **Procedural** | Reusable playbooks | "How to add MCP tool: 5 steps" |

**Key Insight**: Reflections convert episodic → procedural via the `reflect()` tool.

---

## 📚 Documentation

**[📖 Full Documentation](https://aboivz.github.io/astrobob/index.html)**

- [Installation Guide](https://aboivz.github.io/astrobob/installation.html)
- [Quick Start](https://aboivz.github.io/astrobob/quickstart.html)
- [MCP Tools Reference](https://aboivz.github.io/astrobob/mcp-tools.html)
- [CLI Reference](https://aboivz.github.io/astrobob/cli-reference.html)
- [Troubleshooting](https://aboivz.github.io/astrobob/troubleshooting.html)
- [FAQ](https://aboivz.github.io/astrobob/faq.html)

---

## 🧪 Development

```bash
# Unit tests
uv run pytest tests/unit/ -v

# Integration tests (requires live AstraDB)
RUN_INTEGRATION=1 uv run pytest tests/integration/ -v

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
│   └── templates/        # Jinja2 templates for init command
├── tests/                # Unit and integration tests
├── examples/wxo/         # WxO integration examples
└── docs/                 # Documentation site
```

---

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/aboivz/astrobob/issues)
- **Discussions**: [GitHub Discussions](https://github.com/aboivz/astrobob/discussions)

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

**Made with ❤️ and Bob**
