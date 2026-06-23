# Capstone Evaluation Guide

## System Overview for Evaluators

This document provides guidance for evaluating the Intelligent Loan Approval System during the technical evaluation session.

## What to Look For

### 1. Agentic AI Architecture Understanding

**Key Demonstration Points:**

- **Agent Independence** - Agents are located in `src/agents/` with clear names
  - ApplicantProfileAgent (analyzes profiles)
  - FinancialRiskAgent (assesses risk)
  - LoanDecisionAgent (makes decisions)
  - ComplianceAgent (handles notifications)
  - Each agent has ONE responsibility

- **No Direct Coupling** - Agents don't call each other directly
  - All communication through MCP servers
  - Orchestrated by LangGraph workflow
  - Open `src/orchestration/workflow.py` to show the coordination

- **Tool Use Pattern** - Agents use Claude SDK tool_use
  - See `src/agents/agent_base.py` for BaseAgent implementation
  - Show how agents invoke MCP tools
  - Demonstrate agentic loop in `agent_base.run()`

### 2. LangGraph Orchestration

**Code to Show:**

1. **State Definition** (`src/orchestration/state.py`)
   - Shows ApplicationState TypedDict
   - Clear field definitions for each stage

2. **Workflow Graph** (`src/orchestration/workflow.py`)
   - Sequential node execution: validate → profile → risk → decision → compliance → finalize
   - Each node updates state
   - Shows state flow through pipeline
   - `build_workflow()` creates StateGraph

3. **Execution Flow**
   ```python
   workflow.add_edge(START, "validate_input")
   workflow.add_edge("validate_input", "applicant_profile_agent")
   # ... sequential edges showing control flow
   workflow.add_edge("finalize", END)
   ```

### 3. MCP Server Usage

**Key Files:**

- `src/mcp_servers/applicant_db_server.py` - Profile queries
- `src/mcp_servers/risk_rules_server.py` - Risk calculations
- `src/mcp_servers/decision_synthesis_server.py` - Decision logic
- `src/mcp_servers/notification_server.py` - Compliance actions

**Evaluation Points:**

- Each server has clear tool definitions
- Tools are simple, focused functions
- No inter-server dependencies
- Agents call servers through tool_use

**Example to Show:**
```python
# In agent_base.py:
# 1. Tools are defined as Pydantic schemas
# 2. Agent calls tool via Claude SDK
# 3. MCP server function executes
# 4. Result returned to agent
```

### 4. Explainable AI / Auditable Decisions

**Where to Find:**

1. **Decision Outputs** (`src/schemas.py`)
   - LoanDecision class has:
     - `classification` - Clear decision
     - `risk_score` - Quantified risk
     - `key_factors` - Ranked factors
     - `explanation` - Full reasoning
     - `case_id` - Audit trail reference

2. **Audit Trail** (`src/mcp_servers/notification_server.py`)
   - Every action logged with timestamp
   - Full chain of reasoning preserved

3. **Example Response** (from API)
   ```json
   {
     "decision": "Approved",
     "risk_score": 0.25,
     "key_factors": [
       "Strong income stability (0.85)",
       "Excellent credit score (750)",
       "Low DTI ratio (0.35)"
     ],
     "explanation": "Detailed reasoning...",
     "case_id": "CASE-APP001-ABC123"
   }
   ```

### 5. Live Code Modifications

**Easy Changes to Demonstrate:**

1. **Decision Thresholds**
   - Location: `src/mcp_servers/decision_synthesis_server.py`
   - Change: Modify `DECISION_THRESHOLDS` dict
   - Shows: How decisions are controlled

2. **Risk Weights**
   - Location: `src/mcp_servers/decision_synthesis_server.py`
   - Change: Adjust `weights` in `synthesize_decision()`
   - Shows: How factors are prioritized

3. **New Risk Rule**
   - Location: `src/mcp_servers/risk_rules_server.py`
   - Change: Add new condition in `detect_anomalies()`
   - Shows: How to extend decision logic

4. **Agent Prompt**
   - Location: `src/agents/financial_risk_agent.py`
   - Change: Modify `SYSTEM_PROMPT`
   - Shows: How agent behavior can be adjusted

## Testing the System

### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment
cp .env.template .env
# Edit .env with ANTHROPIC_API_KEY

# 3. Run the system
python main.py
```

### Test Scenarios

**Scenario 1: Quick Approval**
- Applicant ID: APP001 (pre-loaded in ApplicantDB)
- Income: $150,000 (High)
- Credit Score: 780 (Excellent)
- DTI: Low
- **Expected:** Approved

**Scenario 2: Likely Rejection**
- Income: $30,000 (Low)
- Loan: $100,000 (Excessive)
- Credit Score: 580 (Poor)
- **Expected:** Rejected or Review

**Scenario 3: Manual Review**
- Income: $80,000 (Medium)
- Employment: Self-employed (Higher risk)
- Credit Score: 680 (Fair)
- **Expected:** Requires Manual Review

### Manual API Testing

```bash
# Via curl (FastAPI running on :8000)
curl -X POST http://localhost:8000/api/loan/apply \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "EVAL001",
    "age": 35,
    "income": 100000,
    "employment_type": "salaried",
    "credit_score": 750,
    "loan_amount": 50000,
    "loan_tenure_months": 60,
    "existing_liabilities": 0,
    "location": "CA"
  }'
```

### Web UI Testing

1. Go to http://localhost:8501
2. Fill out form with test data
3. Click "Submit Application"
4. Observe decision, factors, reasoning

## Architecture Walkthrough

### Code Tour Structure

**Start here for high-level understanding:**
1. `src/orchestration/workflow.py` - Shows the orchestration pattern
2. `src/agents/applicant_profile_agent.py` - Example of one agent
3. `src/mcp_servers/risk_rules_server.py` - Example of MCP server
4. `src/schemas.py` - Data structures

**Then drill into details:**
1. `src/agents/agent_base.py` - Tool use implementation
2. `src/api/main.py` and `src/api/routes.py` - API layer
3. `src/ui/app.py` - Streamlit interface

**For evaluation context:**
1. `README.md` - Full system documentation
2. `.github/` or project structure diagrams

### Key Code Snippets to Show

**1. Agent Tool Use Loop**
```python
# In agent_base.py - run() method
# Shows how agents execute tools in a loop
while iteration < max_iterations:
    response = client.messages.create(...)  # Call Claude
    if response.stop_reason == "tool_use":
        # Execute the tool
        result = self.execute_tool(tool_name, tool_input)
```

**2. Workflow State Flow**
```python
# In workflow.py - each node updates state
def run_applicant_profile_agent(state: ApplicationState):
    # Input: state with application
    agent = applicant_profile_agent.get_agent()
    profile_analysis = agent.analyze(state["application"])
    state["applicant_analysis"] = profile_analysis  # Update state
    return state  # Return for next node
```

**3. MCP Server Tool Definition**
```python
# In risk_rules_server.py
@server.call_tool()
def calculate_debt_to_income(income, existing_liabilities, loan_amount):
    # Simple, focused function
    # No dependencies on other servers
```

## Performance Metrics

### What to Expect

- **Latency:** 30-60 seconds per application
  - Due to Claude API calls (3-4 per application)
  - Can be improved with caching or parallel agents

- **Throughput:** 1 application at a time (sequential)
  - Current design is intentionally simple for clarity
  - Can be scaled with async/queue system

- **Error Rate:** Should be <5% (mostly due to API)
  - System handles failures gracefully
  - Auto-escalates to manual review on errors

## Evaluation Scoring Rubric

### Architecture Understanding (25%)
- [ ] Agents are clearly independent with one responsibility each
- [ ] MCP servers are used for all data access
- [ ] No direct agent-to-agent communication
- [ ] Clear separation of concerns

### LangGraph Implementation (25%)
- [ ] StateGraph correctly defines workflow
- [ ] Sequential execution clear in code
- [ ] State management working properly
- [ ] Node transitions are logical

### Agent Responsibilities (20%)
- [ ] Each agent has clear role
- [ ] Tool definitions are appropriate
- [ ] Agents make meaningful decisions
- [ ] Tool results properly interpreted

### Explainability (20%)
- [ ] Decisions have clear reasoning
- [ ] Factors are ranked/weighted
- [ ] Audit trail is complete
- [ ] Output is human-readable

### Code Quality & Walkthrough (10%)
- [ ] Code is well-organized
- [ ] Logic is easy to modify
- [ ] Can explain all components
- [ ] No major technical debt

## Questions You Might Be Asked

### "Why did the agent make this decision?"
- Point to `decision.key_factors` in API response
- Show the `decision.explanation` field
- Trace through MCP server outputs
- Show risk scores for each component

### "How would you add a new rule?"
- Show `src/mcp_servers/risk_rules_server.py`
- Point to where to add a new tool or condition
- Explain how agents would use it

### "What if an agent fails?"
- Show error handling in `workflow.py`
- Demonstrate cascading to manual review
- Explain state tracking

### "Can you explain the MCP pattern?"
- Show the tool definitions
- Explain how agents invoke tools
- Point out no inter-server coupling
- Mention scalability benefits

### "How does the UI work?"
- Show `src/ui/app.py`
- Explain it calls API endpoints
- Demo the form submission flow

## Files for Quick Reference

| File | Purpose | Show For |
|------|---------|----------|
| `README.md` | Full documentation | Overall context |
| `src/orchestration/workflow.py` | LangGraph workflow | Architecture, orchestration |
| `src/agents/agent_base.py` | Base agent class | Tool use, agentic loop |
| `src/mcp_servers/risk_rules_server.py` | Example MCP server | Tool definition, logic |
| `src/schemas.py` | Data models | Decision structure |
| `src/api/routes.py` | API endpoint | Request/response format |
| `src/ui/app.py` | Streamlit UI | User interface |

## Preparation Checklist

Before evaluation session:

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create `.env` with ANTHROPIC_API_KEY
- [ ] Test basic import: `python -c "from src.config import settings; settings.validate()"`
- [ ] Run system: `python main.py` (keep terminal available)
- [ ] Test one loan application via API or UI
- [ ] Review README.md
- [ ] Prepare test cases (3 scenarios above)
- [ ] Know which files to open for quick reference
- [ ] Practice one code modification (e.g., threshold change)

## Troubleshooting During Evaluation

| Issue | Fix |
|-------|-----|
| API not responding | Verify running: `curl http://localhost:8000/health` |
| Streamlit won't connect | Check API_BASE_URL in src/ui/app.py |
| Import errors | Run: `pip install --upgrade langgraph` |
| Agent slow/timeout | This is normal (~30-60s per application) |
| Missing ANTHROPIC_API_KEY | Set in .env file and restart |

---

**Evaluation Date:** [To be filled by evaluator]  
**Evaluator:** [To be filled by evaluator]  
**System Status:** ✅ Ready for Evaluation
