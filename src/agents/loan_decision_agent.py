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

        # Convert employment risk to score for synthesis
        employment_risk_score_map = {"Low": 0.1, "Medium": 0.4, "High": 0.65, "Critical": 0.95}
        employment_risk_score = employment_risk_score_map.get(profile_analysis.employment_risk, 0.5)

        # Convert credit risk level to score
        credit_risk_score_map = {"Low": 0.15, "Medium": 0.5, "High": 0.8}
        credit_risk_score = credit_risk_score_map.get(risk_analysis.credit_risk_level, 0.5)

        # Calculate anomaly risk score from anomalies
        anomaly_risk_score = len(risk_analysis.anomalies_detected) * 0.15
        anomaly_risk_score = min(anomaly_risk_score, 0.9)

        user_message = f"""Decide: {application.applicant_id} | Stability: {profile_analysis.income_stability_score} | Emp: {profile_analysis.employment_risk} | DTI: {risk_analysis.debt_to_income_ratio:.1%} | Credit: {risk_analysis.credit_risk_level} | Risk: {risk_analysis.risk_score}
Decision: APPROVED/REJECTED/REQUIRES MANUAL REVIEW. Provide confidence, factors."""

        result = self.run(user_message)

        if not result.get("success"):
            logger.error(f"Agent failed: {result.get('error')}")
            return LoanDecision(
                applicant_id=application.applicant_id,
                classification=DecisionType.REQUIRES_REVIEW,
                risk_score=0.7,
                confidence=0.5,
                key_factors=["Decision agent failed"],
                explanation="Decision analysis failed",
                case_id=f"CASE-{application.applicant_id}-ERROR",
            )

        return self._parse_response(application.applicant_id, result.get("response", ""))

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
