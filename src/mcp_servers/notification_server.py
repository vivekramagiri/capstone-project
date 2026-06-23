"""
NotificationSystem Server
Handles compliance actions, audit logging, and notifications
"""

from datetime import datetime
from typing import Dict, Any
import uuid

# Audit log storage
AUDIT_LOG = []


def send_notification(applicant_id: str, decision: str, case_id: str, reason: str = "") -> Dict[str, Any]:
    """
    Send notification to applicant about loan decision

    Args:
        applicant_id: Unique applicant identifier
        decision: Decision result (Approved, Rejected, Requires Manual Review)
        case_id: Case reference ID
        reason: Reason for the decision

    Returns:
        Notification status
    """

    notification_id = f"NOTIF-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.utcnow().isoformat()

    # In real system, this would send email/SMS
    notification_record = {
        "notification_id": notification_id,
        "applicant_id": applicant_id,
        "decision": decision,
        "case_id": case_id,
        "reason": reason,
        "channel": "email",
        "status": "sent",
        "timestamp": timestamp,
    }

    AUDIT_LOG.append(
        {
            "event": "notification_sent",
            "record": notification_record,
            "timestamp": timestamp,
        }
    )

    return {
        "applicant_id": applicant_id,
        "notification_id": notification_id,
        "notification_sent": True,
        "channel": "email",
        "status": "sent",
        "timestamp": timestamp,
    }


def log_case_action(applicant_id: str, case_id: str, action: str, details: str = "") -> Dict[str, Any]:
    """
    Log a case action to the audit trail

    Args:
        applicant_id: Unique applicant identifier
        case_id: Case reference ID
        action: Action taken (e.g., "Application Submitted", "Decision Made")
        details: Additional details about the action

    Returns:
        Log confirmation
    """

    log_entry = {
        "applicant_id": applicant_id,
        "case_id": case_id,
        "action": action,
        "details": details,
        "timestamp": datetime.utcnow().isoformat(),
        "log_id": f"LOG-{uuid.uuid4().hex[:8].upper()}",
    }

    AUDIT_LOG.append(log_entry)

    return {
        "applicant_id": applicant_id,
        "case_id": case_id,
        "log_id": log_entry["log_id"],
        "action": action,
        "status": "logged",
        "timestamp": log_entry["timestamp"],
    }


def get_audit_trail(applicant_id: str) -> Dict[str, Any]:
    """
    Retrieve complete audit trail for an applicant

    Args:
        applicant_id: Unique applicant identifier

    Returns:
        List of all logged actions for this applicant
    """
    applicant_logs = [log for log in AUDIT_LOG if log.get("applicant_id") == applicant_id]

    return {
        "applicant_id": applicant_id,
        "total_entries": len(applicant_logs),
        "audit_trail": applicant_logs,
        "retrieved_at": datetime.utcnow().isoformat(),
    }


def generate_compliance_summary(applicant_id: str, case_id: str, final_decision: str) -> Dict[str, Any]:
    """
    Generate a compliance summary for a loan application

    Args:
        applicant_id: Unique applicant identifier
        case_id: Case reference ID
        final_decision: Final decision (Approved, Rejected, Requires Manual Review)

    Returns:
        Compliance summary
    """

    summary_id = f"SUMMARY-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.utcnow().isoformat()

    # Get related audit entries
    related_logs = [log for log in AUDIT_LOG if log.get("case_id") == case_id]

    summary = {
        "summary_id": summary_id,
        "applicant_id": applicant_id,
        "case_id": case_id,
        "final_decision": final_decision,
        "audit_trail_length": len(related_logs),
        "created_at": timestamp,
        "compliance_status": "verified",
        "actions_taken": [log.get("action") for log in related_logs if "action" in log],
    }

    # Log the summary creation
    AUDIT_LOG.append(
        {
            "event": "compliance_summary_created",
            "applicant_id": applicant_id,
            "case_id": case_id,
            "summary_id": summary_id,
            "timestamp": timestamp,
        }
    )

    return summary


if __name__ == "__main__":
    print("Starting NotificationSystem MCP Server...")
    print("Available tools: send_notification, log_case_action, get_audit_trail, generate_compliance_summary")

    # Test examples
    print("\n--- Test: log_case_action ---")
    log_result = log_case_action("APP001", "CASE-001", "Application Submitted", "Submitted via web form")
    import json

    print(json.dumps(log_result, indent=2))

    print("\n--- Test: send_notification ---")
    notif_result = send_notification("APP001", "Approved", "CASE-001", "Application approved successfully")
    print(json.dumps(notif_result, indent=2))

    print("\n--- Test: get_audit_trail ---")
    trail = get_audit_trail("APP001")
    print(json.dumps(trail, indent=2))
