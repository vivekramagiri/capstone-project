"""
Applicant Profile Agent
Analyzes applicant profile, income stability, and employment history
"""

import json
from src.agents.agent_base import BaseAgent
from src.schemas import LoanApplication, ApplicantProfileAnalysis
from src.mcp_servers import applicant_db_server
from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_applicant_profile_tool(applicant_id: str) -> dict:
    """Wrapper to call ApplicantDB MCP server"""
    return applicant_db_server.get_applicant_profile(applicant_id)


def validate_completeness_tool(applicant_id: str) -> dict:
    """Wrapper to call ApplicantDB MCP server"""
    return applicant_db_server.validate_application_completeness(applicant_id)


SYSTEM_PROMPT = """Analyze applicant profile: employment type, income stability, and data completeness.
Use tools to fetch profile data. Return income_stability_score (0-1) and employment_risk (Low/Medium/High)."""

TOOLS_DEFINITION = [
    {
        "name": "get_applicant_profile",
        "description": "Retrieve applicant profile information including employment history and credit history from the database",
        "input_schema": {
            "type": "object",
            "properties": {
                "applicant_id": {
                    "type": "string",
                    "description": "The unique applicant identifier",
                }
            },
            "required": ["applicant_id"],
        },
    },
    {
        "name": "validate_application_completeness",
        "description": "Check for missing or incomplete fields in the applicant's application",
        "input_schema": {
            "type": "object",
            "properties": {
                "applicant_id": {
                    "type": "string",
                    "description": "The unique applicant identifier",
                }
            },
            "required": ["applicant_id"],
        },
    },
]


class ApplicantProfileAgent(BaseAgent):
    def __init__(self, use_fast_model: bool = True):
        super().__init__("ApplicantProfileAgent", SYSTEM_PROMPT, use_fast_model=use_fast_model)
        self.add_tool(TOOLS_DEFINITION[0], get_applicant_profile_tool)
        self.add_tool(TOOLS_DEFINITION[1], validate_completeness_tool)

    def analyze(self, application: LoanApplication) -> ApplicantProfileAnalysis:
        """
        Analyze applicant profile using the agent

        Args:
            application: Loan application with applicant data

        Returns:
            ApplicantProfileAnalysis with assessment results
        """
        # Fast synchronous analysis (no tool use)
        income_stability_score = 0.7
        employment_risk = "Medium"

        # Score based on employment type
        if application.employment_type.value == "salaried":
            income_stability_score = 0.85
            employment_risk = "Low"
        elif application.employment_type.value == "self_employed":
            income_stability_score = 0.65
            employment_risk = "Medium"
        elif application.employment_type.value == "freelance":
            income_stability_score = 0.5
            employment_risk = "High"
        elif application.employment_type.value == "unemployed":
            income_stability_score = 0.2
            employment_risk = "Critical"

        # Adjust for age
        if application.age < 22:
            income_stability_score -= 0.1
        elif application.age > 65:
            income_stability_score -= 0.05

        return ApplicantProfileAnalysis(
            applicant_id=application.applicant_id,
            income_stability_score=income_stability_score,
            employment_risk=employment_risk,
            credit_history_summary=f"{application.employment_type.value} employment, {application.age} years old",
            completeness_flags=[],
            details={"employment_type": application.employment_type.value, "age": application.age},
        )

    def _parse_response(self, applicant_id: str, response_text: str) -> ApplicantProfileAnalysis:
        """Parse agent's text response into structured format"""

        # Try to extract scores from the response
        import re

        income_stability = 0.7  # Default
        employment_risk = "Medium"  # Default
        completeness_flags = []

        # Simple regex patterns to find scores in response
        stability_match = re.search(r"stability[^0-9]*(\d+\.?\d*)", response_text, re.IGNORECASE)
        if stability_match:
            stability_val = float(stability_match.group(1))
            income_stability = min(max(stability_val / 100 if stability_val > 1 else stability_val, 0), 1)

        if "Low" in response_text and "employment" in response_text:
            employment_risk = "Low"
        elif "High" in response_text and ("employment" in response_text or "risky" in response_text):
            employment_risk = "High"

        if "missing" in response_text.lower() or "incomplete" in response_text.lower():
            completeness_flags.append("Missing or incomplete fields detected")

        return ApplicantProfileAnalysis(
            applicant_id=applicant_id,
            income_stability_score=income_stability,
            employment_risk=employment_risk,
            credit_history_summary=response_text[:500],
            completeness_flags=completeness_flags,
            details={"agent_response": response_text},
        )


# Singleton instance
_agent_instance = None


def get_agent() -> ApplicantProfileAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ApplicantProfileAgent()
    return _agent_instance
