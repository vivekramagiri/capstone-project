# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
# Navigate to project directory
cd capstone-project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy template
cp .env.template .env

# Edit .env and add your Anthropic API key
# Get one at: https://console.anthropic.com/account/keys
```

### 3. Run System
```bash
# Start all services
python main.py
```

Wait for output:
```
✓ All services started successfully!
📡 API Server: http://0.0.0.0:8000
🌐 Web UI:    http://localhost:8501
```

## Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Web UI** | http://localhost:8501 | Loan application form + results |
| **API** | http://localhost:8000/api | REST endpoints |
| **API Docs** | http://localhost:8000/docs | Interactive Swagger UI |
| **Health** | http://localhost:8000/health | Service status |

## Try It Out

### Via Web UI (Easiest)
1. Open http://localhost:8501
2. Fill in the form with test data
3. Click "Submit Application"
4. See decision + reasoning

### Via API (Terminal)
```bash
curl -X POST http://localhost:8000/api/loan/apply \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "TEST001",
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

### Via Python
```python
import requests

response = requests.post(
    "http://localhost:8000/api/loan/apply",
    json={
        "applicant_id": "TEST001",
        "age": 35,
        "income": 100000,
        "employment_type": "salaried",
        "credit_score": 750,
        "loan_amount": 50000,
        "loan_tenure_months": 60,
        "existing_liabilities": 0,
        "location": "CA"
    }
)

print(response.json())
```

## Test Scenarios

### 1. Auto-Approve (High Income, Excellent Credit)
```json
{
  "applicant_id": "APPROVAL_TEST",
  "age": 35,
  "income": 150000,
  "employment_type": "salaried",
  "credit_score": 780,
  "loan_amount": 50000,
  "loan_tenure_months": 60,
  "existing_liabilities": 0,
  "location": "CA"
}
```

### 2. Auto-Reject (Low Income, Large Loan)
```json
{
  "applicant_id": "REJECTION_TEST",
  "age": 28,
  "income": 30000,
  "employment_type": "freelance",
  "credit_score": 580,
  "loan_amount": 100000,
  "loan_tenure_months": 60,
  "existing_liabilities": 25000,
  "location": "NY"
}
```

### 3. Manual Review (Borderline)
```json
{
  "applicant_id": "REVIEW_TEST",
  "age": 42,
  "income": 80000,
  "employment_type": "self_employed",
  "credit_score": 680,
  "loan_amount": 75000,
  "loan_tenure_months": 72,
  "existing_liabilities": 20000,
  "location": "TX"
}
```

## Example Response

```json
{
  "application_id": "TEST001",
  "decision": "Approved",
  "risk_score": 0.25,
  "confidence": 0.90,
  "key_factors": [
    "Strong income stability (0.85)",
    "Excellent credit score (750)",
    "Low DTI ratio (0.35)"
  ],
  "reasoning": "Application approved based on strong financial profile...",
  "case_id": "CASE-TEST001-ABC12345",
  "timestamp": "2026-06-21T20:30:45.123456",
  "status": "completed"
}
```

## Architecture Overview

```
Streamlit UI (Port 8501)
    ↓
FastAPI API (Port 8000)
    ↓
LangGraph Orchestrator
    ↓
4 Agents with Tool Use
    ↓
4 MCP Servers (Simulated Data)
    ↓
Final Decision with Explanation
```

## Code Tour

**For quick understanding, read in this order:**

1. **README.md** - Full system documentation
2. **src/orchestration/workflow.py** - How agents are orchestrated
3. **src/agents/agent_base.py** - How agents work
4. **src/mcp_servers/risk_rules_server.py** - Example MCP server
5. **src/api/routes.py** - API endpoint implementation

## Troubleshooting

### API Not Starting
```bash
# Check if port 8000 is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Or use different port
export API_PORT=8001
python main.py
```

### Missing API Key
```bash
# Error: ANTHROPIC_API_KEY environment variable not set

# Solution: Add to .env file
echo "ANTHROPIC_API_KEY=sk-..." >> .env
python main.py
```

### Streamlit Can't Connect to API
```bash
# Edit src/ui/app.py and change:
API_BASE_URL = "http://localhost:8001/api"  # If using different port
```

### Slow Responses
- First request may take 1-2 minutes
- Subsequent requests typically 30-60 seconds
- This is normal due to Claude API latency

## Key Features to Explore

1. **Explainable Decisions**
   - Every decision includes key factors
   - See detailed reasoning in API response

2. **Risk Scoring**
   - Debt-to-income ratio calculated
   - Credit risk assessed
   - Anomalies detected

3. **Audit Trail**
   - Case ID generated for each application
   - Decision timestamp recorded
   - Compliance actions logged

4. **Live Modifications**
   - Open `src/mcp_servers/decision_synthesis_server.py`
   - Change `DECISION_THRESHOLDS` to modify approval criteria
   - Restart `python main.py` to test

## Next Steps

- **Read Full Documentation**: `README.md`
- **View Evaluation Guide**: `EVALUATION_GUIDE.md`
- **Run Tests**: `pytest tests/test_workflow.py -v`
- **Explore API Docs**: http://localhost:8000/docs
- **Modify Decision Logic**: See code walkthroughs in README

## Support

- **API Documentation**: http://localhost:8000/docs
- **System Architecture**: README.md section "Architecture"
- **Evaluation Guide**: EVALUATION_GUIDE.md
- **Troubleshooting**: README.md section "Troubleshooting"

---

**System Ready?** ✅ You're all set! Start with the Web UI or API tests above.
