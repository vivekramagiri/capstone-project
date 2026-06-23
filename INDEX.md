# 🏦 Intelligent Loan Approval System - Complete Documentation Index

## Getting Started

**First Time Here?** Start with one of these:

1. **[QUICKSTART.md](QUICKSTART.md)** ⚡
   - 5-minute setup
   - How to run the system
   - Test scenarios
   - Common issues

2. **[README.md](README.md)** 📖
   - Full system documentation
   - Architecture overview
   - Agent descriptions
   - API examples

## For Evaluation

**Preparing for technical evaluation?**

- **[EVALUATION_GUIDE.md](EVALUATION_GUIDE.md)** 🎯
  - What evaluators will look for
  - Code tour structure
  - Live code modification examples
  - Scoring rubric
  - Troubleshooting during eval

## Project Overview

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** 📊
  - Completion status
  - What was built
  - Architecture highlights
  - Technology stack
  - Statistics

## Code Structure

```
src/
├── agents/              # 4 AI Agents (Applicant, Risk, Decision, Compliance)
├── mcp_servers/         # 4 MCP Servers (ApplicantDB, RiskRules, DecisionSynthesis, Notification)
├── orchestration/       # LangGraph Workflow (state.py, workflow.py)
├── api/                 # FastAPI (main.py, routes.py)
├── ui/                  # Streamlit (app.py)
├── utils/               # Logger, Validators
├── schemas.py           # Pydantic Models
└── config.py            # Configuration

tests/
└── test_workflow.py     # Integration Tests

main.py                  # Entry point
```

## Key Files by Purpose

### Understanding Architecture

| File | Purpose |
|------|---------|
| `src/orchestration/workflow.py` | LangGraph orchestration - **START HERE** |
| `src/agents/agent_base.py` | Base agent with tool_use pattern |
| `src/mcp_servers/risk_rules_server.py` | Example MCP server |
| `README.md` | Architecture diagrams & overview |

### Implementing Features

| File | Purpose |
|------|---------|
| `src/agents/loan_decision_agent.py` | Decision logic - easy to modify |
| `src/mcp_servers/decision_synthesis_server.py` | Decision thresholds & weights |
| `src/schemas.py` | Data structures - add new fields here |

### Running & Testing

| File | Purpose |
|------|---------|
| `main.py` | Start all services |
| `src/api/routes.py` | API endpoints - test via HTTP |
| `src/ui/app.py` | Web UI - test via browser |
| `tests/test_workflow.py` | Integration tests |

## Quick Reference

### Run Commands

```bash
# Setup
pip install -r requirements.txt
cp .env.template .env
# Edit .env with ANTHROPIC_API_KEY

# Start all services
python main.py

# Run tests
pytest tests/test_workflow.py -v
```

### Access URLs

```
Web UI:          http://localhost:8501
API:             http://localhost:8000
API Docs:        http://localhost:8000/docs
Health Check:    http://localhost:8000/health
```

### Test Scenarios

**Via cURL:**
```bash
curl -X POST http://localhost:8000/api/loan/apply \
  -H "Content-Type: application/json" \
  -d '{"applicant_id":"TEST","age":35,"income":100000,...}'
```

**Via Web UI:**
- Open http://localhost:8501
- Fill form
- Click "Submit"

## Documentation Map

```
QUICKSTART.md ──→ README.md ──→ EVALUATION_GUIDE.md
    ↓               ↓                    ↓
 5 min setup   Architecture       Live walkthrough
 First test    Deep dive         Code modification
                Tech stack        Evaluation rubric
                
                ↑
             PROJECT_SUMMARY.md
                (Overview)
```

## Architecture Summary

```
┌─────────────────────────────────────────────────┐
│         Streamlit Web UI (Port 8501)           │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│       FastAPI REST API (Port 8000)              │
│    POST /api/loan/apply                        │
│    GET /api/loan/{id}/status                   │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│      LangGraph Orchestration Workflow           │
│  Validate → Profile → Risk → Decision →        │
│         Compliance → Finalize                   │
└──────┬──────────┬──────────┬──────────┬─────────┘
       │          │          │          │
    ┌──▼──┐   ┌───▼──┐   ┌──▼───┐   ┌─▼────┐
    │Agent│   │Agent │   │Agent │   │Agent │
    │  1  │   │  2   │   │  3   │   │  4   │
    └──┬──┘   └───┬──┘   └──┬───┘   └─┬────┘
       │          │          │        │
  ┌────▼──┐  ┌───▼───┐  ┌───▼────┐ ┌▼─────┐
  │MCP    │  │MCP    │  │MCP     │ │MCP   │
  │Server1│  │Server2│  │Server3 │ │Server│
  │       │  │       │  │        │ │4     │
  └───────┘  └───────┘  └────────┘ └──────┘
```

## Feature Checklist

✅ Multi-Agent Architecture (4 independent agents)
✅ LangGraph Orchestration (state graph workflow)
✅ MCP Servers (4 data/logic servers)
✅ Claude Integration (Sonnet 4.6 with tool_use)
✅ REST API (FastAPI with documentation)
✅ Web UI (Streamlit application)
✅ Explainable Decisions (reasoning + factors)
✅ Audit Trail (compliance & logging)
✅ Error Handling (graceful degradation)
✅ Configuration Management (env-based)
✅ Structured Logging (JSON format)
✅ Type Safety (Pydantic models)

## Common Tasks

### "I want to modify decision logic"
1. Open `src/mcp_servers/decision_synthesis_server.py`
2. Edit `DECISION_THRESHOLDS` or `synthesize_decision()` function
3. Restart: `python main.py`
4. Test with new scenario

### "How does the workflow execute?"
1. Read `src/orchestration/workflow.py`
2. Follow the `build_workflow()` function
3. Trace through node definitions
4. Check state.py for data flow

### "What makes agents work?"
1. Read `src/agents/agent_base.py` - Base class
2. Check one agent like `financial_risk_agent.py`
3. See how tools are registered and executed
4. Notice the agentic loop in `run()` method

### "I need to add new data fields"
1. Update `src/schemas.py` - Add to Pydantic model
2. Update agent that uses it
3. Update MCP server if needed
4. Update UI form if user-facing

## Evaluation Checklist

Before your evaluation session, verify:

- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] API key set in `.env` file
- [ ] System starts without errors: `python main.py`
- [ ] Web UI accessible: http://localhost:8501
- [ ] API responding: `curl http://localhost:8000/health`
- [ ] One test application processes successfully
- [ ] Decision output includes reasoning

## Support & Help

**Issue** | **Solution**
---------|----------
API won't start | Check port 8000 isn't in use
Missing API key | Set ANTHROPIC_API_KEY in .env
Streamlit can't connect | API might be using different port
Tests fail | Ensure all dependencies installed
Slow responses | Normal (30-60s due to Claude API)

See **QUICKSTART.md** → Troubleshooting section for more help.

## What Makes This System Special

1. **Truly Distributed Agents**
   - No monolithic decision maker
   - Each agent has clear, narrow responsibility
   - Orchestrated coordination

2. **Explainable by Design**
   - Every decision can be traced
   - Factors ranked by importance
   - Full audit trail

3. **Production Architecture**
   - Clear separation of concerns
   - Scalable pattern (can be made async)
   - Error handling built in

4. **Evaluation-Ready**
   - Code is clear and modifiable
   - Architecture is visible
   - Live changes possible

5. **Well-Documented**
   - 4 documentation files
   - Code examples included
   - Setup guides provided

## Next Steps

1. **New to the system?** → Read QUICKSTART.md
2. **Want details?** → Read README.md
3. **Preparing for eval?** → Read EVALUATION_GUIDE.md
4. **Need overview?** → Read PROJECT_SUMMARY.md

---

**System Status**: ✅ Ready for Use
**Last Updated**: 2026-06-21
**Version**: 1.0.0

For questions, refer to the documentation above or check the code comments in key files.
