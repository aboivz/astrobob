# AstroBob Complete Testing & Demo Script

> **Purpose**: Comprehensive testing guide and demo recording script  
> **Duration**: 15-20 minutes for full workflow  
> **Audience**: Developers, Testers, Business Analysts, Technical Decision Makers

---

## 📋 Pre-Flight Checklist

Before starting, ensure you have:

- [ ] Python 3.12+ installed
- [ ] `uv` package manager installed (`pip install uv`)
- [ ] AstraDB account with Serverless database created
- [ ] AstraDB credentials ready (API endpoint + application token)
- [ ] IBM Bob account with active trial (30+ Bobcoins)
- [ ] Screen recording software ready (optional, for demo)
- [ ] Terminal with clean environment

---

## 🎯 Test Scenario: "E-Commerce Platform Development"

**Context**: Building an e-commerce platform where Bob needs to remember:
- Project conventions and architecture decisions
- Bug fixes and their solutions
- Reusable development procedures
- Team knowledge across sessions

**Roles Covered**: Developer, Tester, Business Analyst

---

## Phase 1: Installation & Setup (5 minutes)

### 1.1 Install AstroBob

```bash
# Using uv (recommended)
uv tool install git+https://github.com/aboivz/astrobob.git

# Verify installation
astrobob --version
```

**Expected**: `astrobob, version 0.1.0`

**✅ Checkpoint**: Command available

---

### 1.2 Initialize Project

```bash
# Navigate to project directory
cd ~/projects/ecommerce-platform

# Initialize AstroBob
astrobob init
```

**Expected Output**:
```
✓ Created .bob/mcp.json
✓ Created .bob/custom_modes.yaml
✓ Created .bob/skills/ (3 skills)
✓ Created .env.example
```

**✅ Checkpoint**: `.bob/` directory created

---

### 1.3 Configure AstraDB

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Add your credentials:
```env
ASTRA_DB_API_ENDPOINT=https://YOUR_DATABASE_ID-YOUR_REGION.apps.astra.datastax.com
ASTRA_DB_APPLICATION_TOKEN=AstraCS:YOUR_TOKEN_HERE
```

**✅ Checkpoint**: `.env` contains valid credentials

---

### 1.4 Setup Collections

```bash
# Create memory collections
astrobob astra setup
```

**Expected**:
```
✓ astrobob_semantic_memory
✓ astrobob_episodic_memory
✓ astrobob_procedural_memory
```

**✅ Checkpoint**: Collections visible in AstraDB Studio

---

### 1.5 Health Check

```bash
astrobob doctor
```

**Expected**: All checks pass (green checkmarks)

**✅ Checkpoint**: System ready

---

## Phase 2: Bob Integration & MCP Server (5 minutes)

### 2.1 Start MCP Server

```bash
# Start in STDIO mode (for Bob)
astrobob mcp
```

**Expected**: Server running, waiting for connections

**✅ Checkpoint**: No errors, server listening

---

### 2.2 Configure Bob

Open Bob and add MCP server:

1. Go to **Settings** → **Advanced** → **MCP Servers**
2. Add server from `.bob/mcp.json`
3. Restart Bob

**✅ Checkpoint**: Bob shows 5 AstroBob tools in Advanced mode

---

### 2.3 Verify MCP Tools

In Bob, check available tools:
- `remember` - Store memories
- `recall` - Retrieve memories
- `reflect` - Create procedural memories
- `forget` - Delete memories
- `audit_trail` - View memory history

**✅ Checkpoint**: All 5 tools visible

---

## Phase 3: Real-World Usage Scenarios (10 minutes)

### Scenario A: Developer - Establishing Conventions

**Session 1: Learning Project Structure**

```
User: "We're building an e-commerce platform. Our tech stack is:
- Backend: FastAPI with async routes
- Database: PostgreSQL with SQLAlchemy ORM
- Frontend: React with TypeScript
- Payment: Stripe integration
Remember this as our project architecture."

Bob: [Uses remember() tool]
✓ Stored semantic memory: "Project architecture and tech stack"
```

**Test CLI Verification**:
```bash
# View stored memory
astrobob memory report --project ecommerce-platform
```

**Expected**: Shows 1 semantic memory

---

**Session 1 Continued: Coding Convention**

```
User: "Add a new API endpoint for product search. Follow our conventions."

Bob: [Uses recall() to check conventions]
→ No conventions found yet

Bob: [Implements endpoint, then suggests]
"I've created the endpoint. Should I remember this pattern for future endpoints?"

User: "Yes, remember the pattern."

Bob: [Uses remember() with type=procedural]
✓ Stored: "How to add FastAPI endpoint: 1) Create route in routes/, 2) Add Pydantic model..."
```

**Test CLI Verification**:
```bash
# View procedural memory
astrobob memory report --project ecommerce-platform
```

**Expected**: Shows 1 semantic + 1 procedural memory

---

### Scenario B: Bug Fix Documentation

**Session 2: Encountering a Bug**

```
User: "The payment webhook is failing with 401 errors. Help me debug."

Bob: [Investigates, finds solution]
"The issue is missing Stripe signature verification. Here's the fix..."

User: "Great! Remember this bug and solution."

Bob: [Uses remember() with type=episodic]
✓ Stored: "Fixed Stripe webhook 401 error by adding signature verification"
```

**Test CLI Verification**:
```bash
# View all memories
astrobob memory report
```

**Expected**: Shows semantic, episodic, and procedural memories

---

### Scenario C: Context Retention Across Sessions

**Session 3: New Day, Same Project**

```
User: "I need to add another payment webhook for refunds. What's our pattern?"

Bob: [Uses recall() with query="how to add webhook"]
→ Retrieves procedural memory from Session 1
→ Retrieves episodic memory about Stripe signature

Bob: "Based on previous work, here's the pattern:
1. Create route in routes/webhooks/
2. Add signature verification (remember the 401 fix?)
3. Use async handler pattern
4. Add Pydantic model for validation"
```

**Key Demonstration**: Bob remembered:
- ✅ Project structure (semantic)
- ✅ Previous bug fix (episodic)
- ✅ Coding pattern (procedural)

---

### Scenario D: Reflection & Learning

**Session 3 Continued: Creating Reusable Knowledge**

```
User: "We've now added 3 webhooks. Can you reflect on the pattern?"

Bob: [Uses reflect() tool]
→ Analyzes episodic memories
→ Creates procedural memory

✓ Stored: "Webhook Implementation Checklist:
1. Route structure: routes/webhooks/{service}/
2. Always verify signatures
3. Use async handlers
4. Log all events
5. Return 200 immediately, process async"
```

**Test CLI Verification**:
```bash
# View reflection
astrobob memory report --project ecommerce-platform
```

**Expected**: New procedural memory with high importance

---

## Phase 4: Skills Export & Self-Improvement (3 minutes)

### 4.1 Export Learned Skills

```bash
# Export procedural memories as Bob skills
astrobob skills sync --min-importance 4
```

**Expected Output**:
```
Syncing procedural memories to skills...
✓ webhook-implementation → .bob/skills/learned/webhook-implementation/SKILL.md
✓ fastapi-endpoint-pattern → .bob/skills/learned/fastapi-endpoint-pattern/SKILL.md

Synced 2 skills. Reload Bob to use them.
```

**✅ Checkpoint**: Skills created in `.bob/skills/learned/`

---

### 4.2 Verify Skills

```bash
# List learned skills
ls -la .bob/skills/learned/
```

**Expected**: 2 directories with SKILL.md files

---

### 4.3 Bob Uses Own Skills

Reload Bob, then:

```
User: "Add a new webhook for order confirmations."

Bob: [Now has native skill "webhook-implementation"]
→ Follows checklist automatically
→ Implements faster and more consistently
```

**Key Demonstration**: Bob taught itself!

---

## Phase 5: Advanced Features & Edge Cases (5 minutes)

### 5.1 Memory Management

**Test Forgetting**:
```bash
# List memories
astrobob memory report

# Forget a specific memory
astrobob memory forget --type episodic --id <memory-id>

# Verify deletion
astrobob memory report
```

**Expected**: Memory soft-deleted (not shown in reports)

---

### 5.2 Audit Trail

```bash
# View memory history
astrobob memory audit --type procedural --id <memory-id>
```

**Expected**: Shows creation, access count, last accessed

---

### 5.3 Cross-Project Memory

**Test Scope**:
```bash
# Store global memory
astrobob memory remember \
  --type semantic \
  --content "Always use async/await for I/O operations" \
  --project global \
  --importance 5

# Verify it's accessible from any project
astrobob memory report --project another-project
```

**Expected**: Global memory visible across projects

---

### 5.4 Error Handling

**Test Invalid Credentials**:
```bash
# Temporarily break .env
mv .env .env.backup
astrobob doctor
```

**Expected**: Clear error message about missing credentials

```bash
# Restore
mv .env.backup .env
```

---

### 5.5 Search & Retrieval

**Test Query Routing**:
```bash
# Semantic query
astrobob memory recall --query "what is our tech stack"

# Procedural query
astrobob memory recall --query "how to add webhook"

# Episodic query
astrobob memory recall --query "what bugs did we fix"
```

**Expected**: Different memory types returned based on query intent

---

## Phase 6: Multi-Role Scenarios (5 minutes)

### Role: Business Analyst

```
User: "Document the decision to use Stripe over PayPal."

Bob: [Uses remember() with type=semantic]
✓ Stored: "Payment provider decision: Stripe chosen for better API, lower fees, faster settlement"
```

---

### Role: Tester

```
User: "Remember this edge case: webhook fails if order total is exactly $0.00"

Bob: [Uses remember() with type=episodic]
✓ Stored: "Edge case: $0.00 orders cause webhook validation error"
```

---

### Role: Team Lead

```
User: "Reflect on all our payment-related decisions and create a guideline."

Bob: [Uses reflect() on multiple memories]
✓ Created: "Payment Integration Guidelines" (procedural memory)
```

---

## Phase 7: Performance & Scale Testing (3 minutes)

### 7.1 Bulk Memory Creation

```bash
# Seed demo data
python scripts/seed_demo.py
```

**Expected**: 30+ memories created across all types

---

### 7.2 Search Performance

```bash
# Test hybrid search with many memories
astrobob memory recall --query "payment" --limit 10
```

**Expected**: Results in < 2 seconds, ranked by relevance

---

### 7.3 Memory Report

```bash
# Full project report
astrobob memory report --project ecommerce-platform
```

**Expected**: Summary with counts, top procedural memories, recent episodes

---

## Phase 8: Cleanup & Reset (2 minutes)

### 8.1 Reset Demo Data

```bash
# Remove demo memories
python scripts/reset_demo.py
```

**Expected**: Demo-tagged memories deleted

---

### 8.2 Verify Clean State

```bash
astrobob memory report
```

**Expected**: Only real memories remain

---

## 📊 Success Criteria Checklist

### Installation & Setup
- [ ] AstroBob installed successfully
- [ ] Collections created in AstraDB
- [ ] Health check passes
- [ ] MCP server starts without errors

### Bob Integration
- [ ] Bob sees all 5 MCP tools
- [ ] Tools respond correctly
- [ ] Memories stored via Bob
- [ ] Memories retrieved via Bob

### Memory Operations
- [ ] Semantic memories stored/retrieved
- [ ] Episodic memories stored/retrieved
- [ ] Procedural memories stored/retrieved
- [ ] Reflection creates new procedural memories
- [ ] Forget soft-deletes memories
- [ ] Audit trail shows history

### Skills Export
- [ ] Skills sync exports SKILL.md files
- [ ] Bob loads learned skills
- [ ] Skills improve Bob's performance

### CLI Commands
- [ ] `astrobob init` works
- [ ] `astrobob astra setup` works
- [ ] `astrobob doctor` works
- [ ] `astrobob mcp` works
- [ ] `astrobob memory remember` works
- [ ] `astrobob memory recall` works
- [ ] `astrobob memory reflect` works
- [ ] `astrobob memory forget` works
- [ ] `astrobob memory audit` works
- [ ] `astrobob memory report` works
- [ ] `astrobob skills sync` works

### Real-World Value
- [ ] Context retained across sessions
- [ ] Bob learns from experience
- [ ] Procedural knowledge captured
- [ ] Team knowledge preserved
- [ ] Self-improvement loop demonstrated

---

## 🎬 Demo Recording Script (90 seconds)

### [0-15s] Hook & Install
```bash
# Show the problem
"AI agents forget everything between sessions."

# Show the solution
uv tool install git+https://github.com/aboivz/astrobob.git
astrobob init
astrobob astra setup
```

### [15-40s] Bob Learns
```
User: "Add a webhook endpoint. Check our conventions first."
Bob: recall() → empty
Bob: [Implements in 8 exploratory steps]
Bob: remember(type=procedural, content="Webhook pattern: ...")
```

**Show**: AstraDB Studio with new memory

### [40-70s] Bob Remembers
```
[New session, context cleared]
User: "Add another webhook."
Bob: recall() → retrieves pattern
Bob: [Implements in 4 directed steps]
```

**Show**: Split screen - 8 steps vs 4 steps

### [70-90s] Bob Teaches Itself
```bash
astrobob skills sync
```

**Show**: `.bob/skills/learned/webhook-pattern/SKILL.md`

```
"Bob just wrote its own skill. Now it's native knowledge."
```

---

## 🐛 Troubleshooting

### MCP Server Won't Start
```bash
# Check port availability
netstat -an | grep 8765

# Try different port
astrobob mcp --http --port 8766
```

### Bob Doesn't See Tools
1. Verify `.bob/mcp.json` has correct path
2. Restart Bob completely
3. Check Bob logs for MCP errors

### Memories Not Storing
```bash
# Test connection
astrobob doctor

# Check AstraDB Studio for collections
# Verify .env credentials
```

### Search Returns No Results
```bash
# Check memory count
astrobob memory report

# Try broader query
astrobob memory recall --query "project"
```

---

## 📚 Additional Resources

- **Full Documentation**: https://github.com/aboivz/astrobob/tree/main/docs
- **CLI Reference**: `docs/cli-reference.html`
- **MCP Tools**: `docs/mcp-tools.html`
- **Troubleshooting**: `docs/troubleshooting.html`
- **FAQ**: `docs/faq.html`

---

## 🎯 Next Steps After Testing

1. **Production Use**: Remove demo data, start real usage
2. **Team Onboarding**: Share `.bob/` configs with team
3. **Custom Skills**: Write domain-specific skills
4. **WxO Integration**: Try multi-agent templates in `examples/wxo/`
5. **Feedback**: Report issues on GitHub

---

**Testing Complete!** 🎉

You've verified:
- ✅ Installation and setup
- ✅ Bob integration via MCP
- ✅ All memory types and operations
- ✅ Skills export and self-improvement
- ✅ Real-world usage scenarios
- ✅ Error handling and edge cases

**AstroBob is ready for production use!**