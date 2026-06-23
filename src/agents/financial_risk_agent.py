"""
Financial Risk Analysis Agent
Performs comprehensive financial risk assessment including DTI, credit risk, and anomaly detection
"""

import json
import re
from src.agents.agent_base import BaseAgent
from src.schemas import LoanApplication, ApplicantProfileAnalysis, FinancialRiskAnalysis
from src.mcp_servers import risk_rules_server
from src.utils.logger import get_logger

logger = get_logger(__name__)


def calculate_dti_tool(income: float, existing_liabilities: float, loan_amount: float) -> dict:
    """Wrapper to call RiskRulesDB MCP server"""
    return risk_rules_server.calculate_debt_to_income(income, existing_liabilities, loan_amount)


def assess_credit_risk_tool(credit_score: int, historical_defaults: int) -> dict:
    """Wrapper to call RiskRulesDB MCP server"""
    return risk_rules_server.assess_credit_risk(credit_score, historical_defaults)


def evaluate_lti_tool(loan_amount: float, income: float, employment_type: str) -> dict:
    """Wrapper to call RiskRulesDB MCP server"""
    return risk_rules_server.evaluate_loan_amount_risk(loan_amount, income, employment_type)


def detect_anomalies_tool(
    applicant_id: str,
    credit_score: int,
    recent_inquiries: int,
    credit_defaults: int,
    employment_type: str,
    income_stability_score: float,
) -> dict:
    """Wrapper to call RiskRulesDB MCP server"""
    return risk_rules_server.detect_anomalies(
        applicant_id, credit_score, recent_inquiries, credit_defaults, employment_type, income_stability_score
    )


SYSTEM_PROMPT = """You are a Financial Risk Analysis Agent for a loan approval system.

Your role is to:
1. Calculate debt-to-income (DTI) ratio and assess acceptability
2. Evaluate credit risk based on credit score and payment history
3. Assess loan-to-income risk
4. Detect anomalies and suspicious patterns
5. Synthesize findings into a comprehensive risk assessment

When analyzing applications:
- Use the available tools to calculate each risk dimension
- Interpret results against industry standards
- Identify concerning patterns or red flags
- Provide a holistic risk score (0-1) and detailed reasoning
- Highlight which factors pose the highest risk

Be precise with numbers and provide specific thresholds in your analysis."""

TOOLS_DEFINITION = [
    {
        "name": "calculate_debt_to_income",
        "description": "Calculate the debt-to-income ratio based on income, existing liabilities, and requested loan amount",
        "input_schema": {
            "type": "object",
            "properties": {
                "income": {"type": "number", "description": "Annual income in dollars"},
                "existing_liabilities": {"type": "number", "description": "Total existing debt in dollars"},
                "loan_amount": {"type": "number", "description": "Requested loan amount in dollars"},
            },
            "required": ["income", "existing_liabilities", "loan_amount"],
        },
    },
    {
        "name": "assess_credit_risk",
        "description": "Assess credit risk based on credit score and historical default information",
        "input_schema": {
            "type": "object",
            "properties": {
                "credit_score": {"type": "integer", "description": "Credit score (300-850)"},
                "historical_defaults": {"type": "integer", "description": "Number of historical defaults"},
            },
            "required": ["credit_score", "historical_defaults"],
        },
    },
    {
        "name": "evaluate_loan_to_income_ratio",
        "description": "Evaluate the risk of the loan amount relative to applicant income and employment type",
        "input_schema": {
            "type": "object",
            "properties": {
                "loan_amount": {"type": "number", "description": "Requested loan amount in dollars"},
                "income": {"type": "number", "description": "Annual income in dollars"},
                "employment_type": {
                    "type": "string",
                    "description": "Employment type (salaried, self_employed, freelance, unemployed)",
                },
            },
            "required": ["loan_amount", "income", "employment_type"],
        },
    },
    {
        "name": "detect_anomalies",
        "description": "Detect suspicious patterns or anomalies in the applicant's profile",
        "input_schema": {
            "type": "object",
            "properties": {
                "applicant_id": {"type": "string", "description": "Unique applicant identifier"},
                "credit_score": {"type": "integer", "description": "Credit score"},
                "recent_inquiries": {"type": "integer", "description": "Number of recent credit inquiries"},
                "credit_defaults": {"type": "integer", "description": "Number of credit defaults"},
                "employment_type": {"type": "string", "description": "Employment type"},
                "income_stability_score": {"type": "number", "description": "Income stability score (0-1)"},
            },
            "required": [
                "applicant_id",
                "credit_score",
                "recent_inquiries",
                "credit_defaults",
                "employment_type",
                "income_stability_score",
            ],
        },
    },
]


class FinancialRiskAgent(BaseAgent):
    def __init__(self):
        super().__init__("FinancialRiskAgent", SYSTEM_PROMPT)
        self.add_tool(TOOLS_DEFINITION[0], calculate_dti_tool)
        self.add_tool(TOOLS_DEFINITION[1], assess_credit_risk_tool)
        self.add_tool(TOOLS_DEFINITION[2], evaluate_lti_tool)
        self.add_tool(TOOLS_DEFINITION[3], detect_anomalies_tool)

    def analyze(
        self, application: LoanApplication, profile_analysis: ApplicantProfileAnalysis
    ) -> FinancialRiskAnalysis:
        """
        Analyze financial risk of the loan application

        Args:
            application: Loan application details
            profile_analysis: Results from applicant profile analysis

        Returns:
            FinancialRiskAnalysis with assessment results
        """
        user_message = f"""Perform a comprehensive financial risk analysis for:
Applicant ID: {application.applicant_id}
Annual Income: ${application.income:,.2f}
Credit Score: {application.credit_score}
Requested Loan Amount: ${application.loan_amount:,.2f}
Existing Liabilities: ${application.existing_liabilities:,.2f}
Employment Type: {application.employment_type.value}
Income Stability Score: {profile_analysis.income_stability_score}

Please:
1. Calculate the debt-to-income ratio
2. Assess credit risk based on the credit score
3. Evaluate loan-to-income ratio appropriateness
4. Detect any anomalies or red flags
5. Provide an overall risk score and detailed reasoning

Respond with specific numbers and clear risk assessment."""

        result = self.run(user_message)

        if not result.get("success"):
            logger.error(f"Agent failed: {result.get('error')}")
            return FinancialRiskAnalysis(
                applicant_id=application.applicant_id,
                debt_to_income_ratio=0.0,
                credit_risk_level="High",
                loan_amount_risk="High",
                anomalies_detected=["Analysis failed"],
                risk_score=0.8,
                reasoning="Financial risk analysis failed",
            )

        return self._parse_response(application.applicant_id, result.get("response", ""))

    def _parse_response(self, applicant_id: str, response_text: str) -> FinancialRiskAnalysis:
        """Parse agent's text response into structured format"""

        # Extract DTI ratio
        dti_pattern = r"DTI.*?(\d+\.?\d*)"
        dti_match = re.search(dti_pattern, response_text, re.IGNORECASE)
        dti_ratio = float(dti_match.group(1)) / 100 if dti_match else 0.4

        # Determine risk levels
        credit_risk_level = "Medium"
        if "low" in response_text.lower() and "credit" in response_text.lower():
            credit_risk_level = "Low"
        elif "high" in response_text.lower() and ("credit" in response_text.lower() or "score" in response_text.lower()):
            credit_risk_level = "High"

        loan_risk = "Medium"
        if "high" in response_text.lower() and "loan" in response_text.lower():
            loan_risk = "High"
        elif "low" in response_text.lower() and "loan" in response_text.lower():
            loan_risk = "Low"

        # Extract overall risk score
        risk_score_pattern = r"risk.*?(\d+\.?\d*)"
        risk_match = re.search(risk_score_pattern, response_text, re.IGNORECASE)
        risk_score = float(risk_match.group(1)) / 100 if risk_match else 0.5

        # Identify anomalies
        anomalies = []
        if "multiple inquiries" in response_text.lower() or "inquiry" in response_text.lower():
            anomalies.append("Recent multiple credit inquiries")
        if "default" in response_text.lower():
            anomalies.append("Previous payment defaults detected")
        if "unstable" in response_text.lower():
            anomalies.append("Income instability detected")

        return FinancialRiskAnalysis(
            applicant_id=applicant_id,
            debt_to_income_ratio=min(dti_ratio, 1.0),
            credit_risk_level=credit_risk_level,
            loan_amount_risk=loan_risk,
            anomalies_detected=anomalies,
            risk_score=min(max(risk_score, 0), 1),
            reasoning=response_text[:600],
        )


# Singleton instance
_agent_instance = None


def get_agent() -> FinancialRiskAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = FinancialRiskAgent()
    return _agent_instance
