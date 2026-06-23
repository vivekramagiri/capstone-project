"""
Loan Decision Agent
Synthesizes all analyses into a final loan decision with clear reasoning
"""

import json
import re
from src.agents.agent_base import BaseAgent
from src.schemas import (
    LoanApplication,
    ApplicantProfileAnalysis,
    FinancialRiskAnalysis,
    LoanDecision,
    DecisionType,
)
from src.mcp_servers import decision_synthesis_server
from src.utils.logger import get_logger

logger = get_logger(__name__)


def synthesize_decision_tool(
    applicant_id: str,
    income_stability_score: float,
    employment_risk: str,
    dti_ratio: float,
    credit_risk_score: float,
    loan_to_income_ratio: float,
    anomaly_risk_score: float,
    anomalies_detected: list,
) -> dict:
    """Wrapper to call DecisionSynthesis MCP server"""
    return decision_synthesis_server.synthesize_decision(
        applicant_id,
        income_stability_score,
        employment_risk,
        dti_ratio,
        credit_risk_score,
        loan_to_income_ratio,
        anomaly_risk_score,
        anomalies_detected,
    )


SYSTEM_PROMPT = """Synthesize all analyses into a loan decision: APPROVED/REJECTED/REQUIRES MANUAL REVIEW.
Provide: decision, confidence (0-1), risk_score, key_factors."""

TOOLS_DEFINITION = [
    {
        "name": "synthesize_decision",
        "description": "Synthesize individual risk assessments into a final loan decision",
        "input_schema": {
            "type": "object",
            "properties": {
                "applicant_id": {"type": "string", "description": "Unique applicant identifier"},
                "income_stability_score": {"type": "number", "description": "Income stability score (0-1)"},
                "employment_risk": {"type": "string", "description": "Employment risk level"},
                "dti_ratio": {"type": "number", "description": "Debt-to-income ratio"},
                "credit_risk_score": {"type": "number", "description": "Credit risk score (0-1)"},
                "loan_to_income_ratio": {"type": "number", "description": "Loan-to-income ratio"},
                "anomaly_risk_score": {"type": "number", "description": "Anomaly risk score (0-1)"},
                "anomalies_detected": {"type": "array", "items": {"type": "string"}, "description": "List of detected anomalies"},
            },
            "required": [
                "applicant_id",
                "income_stability_score",
                "employment_risk",
                "dti_ratio",
                "credit_risk_score",
                "loan_to_income_ratio",
                "anomaly_risk_score",
                "anomalies_detected",
            ],
        },
    },
]


class LoanDecisionAgent(BaseAgent):
    def __init__(self, use_fast_model: bool = True):
        super().__init__("LoanDecisionAgent", SYSTEM_PROMPT, use_fast_model=use_fast_model)
        self.add_tool(TOOLS_DEFINITION[0], synthesize_decision_tool)

    def decide(
        self,
        application: LoanApplication,
        profile_analysis: ApplicantProfileAnalysis,
        risk_analysis: FinancialRiskAnalysis,
    ) -> LoanDecision:
        """
        Make final loan decision based on all analyses

        Args:
            application: Loan application details
            profile_analysis: Applicant profile analysis
            risk_analysis: Financial risk analysis

        Returns:
            LoanDecision with classification and reasoning
        """
        # Fast synchronous decision logic
        risk_score = risk_analysis.risk_score
        employment_risk = profile_analysis.employment_risk

        # Decision logic
        classification = DecisionType.APPROVED
        if employment_risk == "Critical" or risk_score > 0.7:
            classification = DecisionType.REQUIRES_REVIEW
        elif employment_risk == "High" or risk_score > 0.6:
            classification = DecisionType.REQUIRES_REVIEW
        elif risk_analysis.loan_amount_risk == "High" and risk_analysis.credit_risk_level == "High":
            classification = DecisionType.REJECTED

        # Confidence
        confidence = 1.0 - (risk_score * 0.3)

        # Key factors
        key_factors = [
            f"Income Stability: {profile_analysis.income_stability_score:.0%}",
            f"Employment: {profile_analysis.employment_risk}",
            f"DTI Ratio: {risk_analysis.debt_to_income_ratio:.1%}",
            f"Credit Risk: {risk_analysis.credit_risk_level}",
        ]

        from datetime import datetime
        import uuid

        return LoanDecision(
            applicant_id=application.applicant_id,
            classification=classification,
            risk_score=risk_score,
            confidence=confidence,
            key_factors=key_factors,
            explanation=f"Decision: {classification.value}. Risk factors: {', '.join(key_factors[:2])}",
            case_id=f"CASE-{uuid.uuid4().hex[:8].upper()}",
            decision_timestamp=datetime.utcnow(),
        )

    def _parse_response(self, applicant_id: str, response_text: str) -> LoanDecision:
        """Parse agent's text response into structured decision"""

        # Determine decision
        classification = DecisionType.REQUIRES_REVIEW
        if "APPROVED" in response_text.upper() and "NOT APPROVED" not in response_text.upper():
            classification = DecisionType.APPROVED
        elif "REJECTED" in response_text.upper():
            classification = DecisionType.REJECTED
        elif "MANUAL REVIEW" in response_text.upper() or "REVIEW" in response_text.upper():
            classification = DecisionType.REQUIRES_REVIEW

        # Extract confidence
        confidence_pattern = r"confidence[:\s]+(\d+\.?\d*)"
        confidence_match = re.search(confidence_pattern, response_text, re.IGNORECASE)
        confidence = float(confidence_match.group(1)) / 100 if confidence_match else 0.7
        confidence = min(max(confidence, 0), 1)

        # Extract risk score
        risk_score_pattern = r"risk[^0-9]*(\d+\.?\d*)"
        risk_match = re.search(risk_score_pattern, response_text, re.IGNORECASE)
        risk_score = float(risk_match.group(1)) / 100 if risk_match else 0.5
        risk_score = min(max(risk_score, 0), 1)

        # Extract key factors (look for numbered list)
        key_factors = []
        lines = response_text.split("\n")
        for line in lines:
            if re.match(r"^\d+\.", line) or line.strip().startswith("-"):
                factor = re.sub(r"^\d+\.\s*|-\s*", "", line).strip()
                if factor and len(factor) > 5:
                    key_factors.append(factor[:100])
        if not key_factors:
            key_factors = ["Decision based on comprehensive analysis"]

        # Generate case ID using MCP server
        from src.mcp_servers import decision_synthesis_server as ds

        case_id = f"CASE-{applicant_id}-{abs(hash(response_text)) % 100000:05d}"

        return LoanDecision(
            applicant_id=applicant_id,
            classification=classification,
            risk_score=risk_score,
            confidence=confidence,
            key_factors=key_factors[:5],
            explanation=response_text[:800],
            case_id=case_id,
        )


# Singleton instance
_agent_instance = None


def get_agent() -> LoanDecisionAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = LoanDecisionAgent()
    return _agent_instance
