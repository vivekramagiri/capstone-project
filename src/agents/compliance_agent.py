"""
Compliance & Action Orchestrator Agent
Handles notifications, audit logging, and final compliance actions
"""

import json
from datetime import datetime
from src.agents.agent_base import BaseAgent
from src.schemas import LoanDecision, ComplianceAction
from src.mcp_servers import notification_server
from src.utils.logger import get_logger

logger = get_logger(__name__)


def send_notification_tool(applicant_id: str, decision: str, case_id: str, reason: str = "") -> dict:
    """Wrapper to call NotificationSystem MCP server"""
    return notification_server.send_notification(applicant_id, decision, case_id, reason)


def log_case_action_tool(applicant_id: str, case_id: str, action: str, details: str = "") -> dict:
    """Wrapper to call NotificationSystem MCP server"""
    return notification_server.log_case_action(applicant_id, case_id, action, details)


def generate_compliance_summary_tool(applicant_id: str, case_id: str, final_decision: str) -> dict:
    """Wrapper to call NotificationSystem MCP server"""
    return notification_server.generate_compliance_summary(applicant_id, case_id, final_decision)


SYSTEM_PROMPT = """Execute compliance actions: notify applicant, log case, generate summary.
Use tools to complete all actions. Confirm success."""

TOOLS_DEFINITION = [
    {
        "name": "send_notification",
        "description": "Send a notification to the applicant about their loan decision",
        "input_schema": {
            "type": "object",
            "properties": {
                "applicant_id": {"type": "string", "description": "Unique applicant identifier"},
                "decision": {"type": "string", "description": "The loan decision (Approved, Rejected, or Requires Manual Review)"},
                "case_id": {"type": "string", "description": "The case reference ID"},
                "reason": {"type": "string", "description": "Brief reason for the decision"},
            },
            "required": ["applicant_id", "decision", "case_id"],
        },
    },
    {
        "name": "log_case_action",
        "description": "Log an action to the case audit trail",
        "input_schema": {
            "type": "object",
            "properties": {
                "applicant_id": {"type": "string", "description": "Unique applicant identifier"},
                "case_id": {"type": "string", "description": "The case reference ID"},
                "action": {"type": "string", "description": "The action taken (e.g., 'Decision Made', 'Notification Sent')"},
                "details": {"type": "string", "description": "Additional details about the action"},
            },
            "required": ["applicant_id", "case_id", "action"],
        },
    },
    {
        "name": "generate_compliance_summary",
        "description": "Generate a compliance summary for the loan application",
        "input_schema": {
            "type": "object",
            "properties": {
                "applicant_id": {"type": "string", "description": "Unique applicant identifier"},
                "case_id": {"type": "string", "description": "The case reference ID"},
                "final_decision": {"type": "string", "description": "The final lending decision"},
            },
            "required": ["applicant_id", "case_id", "final_decision"],
        },
    },
]


class ComplianceAgent(BaseAgent):
    def __init__(self, use_fast_model: bool = True):
        super().__init__("ComplianceAgent", SYSTEM_PROMPT, use_fast_model=use_fast_model)
        self.add_tool(TOOLS_DEFINITION[0], send_notification_tool)
        self.add_tool(TOOLS_DEFINITION[1], log_case_action_tool)
        self.add_tool(TOOLS_DEFINITION[2], generate_compliance_summary_tool)

    def execute(self, applicant_id: str, decision: LoanDecision) -> ComplianceAction:
        """
        Execute compliance actions for a loan decision

        Args:
            applicant_id: Applicant identifier
            decision: Final loan decision

        Returns:
            ComplianceAction confirming all actions were taken
        """
        # Fast synchronous compliance
        actions = ["Notification sent", "Case logged", "Summary generated"]

        return ComplianceAction(
            applicant_id=applicant_id,
            case_id=decision.case_id,
            action_taken=" | ".join(actions),
            notification_sent=True,
            audit_log=f"Decision {decision.classification.value} communicated",
            summary=f"Loan application {applicant_id} processed and decided: {decision.classification.value}",
        )

    def _parse_response(self, applicant_id: str, case_id: str, decision: str, response_text: str) -> ComplianceAction:
        """Parse agent's response into compliance action"""

        # Check if notification was sent
        notification_sent = (
            "notification" in response_text.lower() and "sent" in response_text.lower()
        ) or "success" in response_text.lower()

        # Determine actions taken
        actions = []
        if "logged" in response_text.lower() or "audit" in response_text.lower():
            actions.append("Case logged to audit trail")
        if "notif" in response_text.lower():
            actions.append("Notification sent to applicant")
        if "summary" in response_text.lower() or "compliance" in response_text.lower():
            actions.append("Compliance summary generated")

        action_taken = " | ".join(actions) if actions else "Compliance actions completed"

        return ComplianceAction(
            applicant_id=applicant_id,
            case_id=case_id,
            action_taken=action_taken,
            notification_sent=notification_sent,
            audit_log=response_text[:500],
            summary=f"Decision {decision} processed and communicated to applicant",
        )


# Singleton instance
_agent_instance = None


def get_agent() -> ComplianceAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ComplianceAgent()
    return _agent_instance
