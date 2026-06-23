"""
DecisionSynthesis Server
Synthesizes risk analyses and profile data into loan decisions
"""

from datetime import datetime
from typing import Dict, Any, List
import uuid

# Decision rules
DECISION_THRESHOLDS = {
    "auto_approve": {"risk_score_max": 0.30, "confidence_min": 0.85},
    "auto_reject": {"risk_score_min": 0.75, "confidence_min": 0.70},
    "manual_review": {},  # Everything else
}


def synthesize_decision(
    applicant_id: str,
    income_stability_score: float,
    employment_risk: str,
    dti_ratio: float,
    credit_risk_score: float,
    loan_to_income_ratio: float,
    anomaly_risk_score: float,
    anomalies_detected: List[str],
) -> Dict[str, Any]:
    """
    Synthesize individual risk assessments into a final decision

    Args:
        applicant_id: Unique applicant identifier
        income_stability_score: Income stability (0-1)
        employment_risk: Employment risk level (Low, Medium, High, Critical)
        dti_ratio: Debt-to-income ratio
        credit_risk_score: Credit risk score (0-1)
        loan_to_income_ratio: Loan-to-income ratio
        anomaly_risk_score: Anomaly risk score (0-1)
        anomalies_detected: List of detected anomalies

    Returns:
        Decision dict with classification, risk score, and reasoning
    """

    # Map employment risk to score
    employment_risk_score = {
        "Low": 0.1,
        "Medium": 0.4,
        "High": 0.65,
        "Critical": 0.95,
    }.get(employment_risk, 0.5)

    # Calculate component scores (each 0-1)
    income_score = income_stability_score  # Higher is better, invert for risk
    income_risk_component = 1 - income_score if income_score > 0 else 0.5

    dti_component = min(dti_ratio / 0.60, 1.0)  # Cap at 0.60 DTI = risk of 1.0

    lti_component = min(loan_to_income_ratio / 5.0, 1.0)  # Cap at 5.0 LTI = risk of 1.0

    # Weighted risk score
    weights = {
        "employment": 0.15,
        "income_stability": 0.10,
        "dti": 0.25,
        "credit": 0.25,
        "lti": 0.15,
        "anomaly": 0.10,
    }

    overall_risk_score = (
        employment_risk_score * weights["employment"]
        + income_risk_component * weights["income_stability"]
        + dti_component * weights["dti"]
        + credit_risk_score * weights["credit"]
        + lti_component * weights["lti"]
        + anomaly_risk_score * weights["anomaly"]
    )

    overall_risk_score = min(overall_risk_score, 1.0)

    # Determine decision
    if overall_risk_score <= 0.30 and dti_ratio <= 0.40 and credit_risk_score <= 0.25:
        classification = "Approved"
        confidence = 0.90
    elif overall_risk_score >= 0.70 or dti_ratio >= 0.55 or credit_risk_score >= 0.75:
        classification = "Rejected"
        confidence = 0.85
    else:
        classification = "Requires Manual Review"
        confidence = 0.70

    # Determine key factors (ranked by importance)
    key_factors = []

    if dti_ratio > 0.45:
        key_factors.append(f"High DTI ratio ({dti_ratio:.2%})")
    if credit_risk_score > 0.60:
        key_factors.append(f"High credit risk ({credit_risk_score:.2f})")
    if employment_risk_score > 0.60:
        key_factors.append(f"High employment risk ({employment_risk})")
    if len(anomalies_detected) > 0:
        key_factors.append(f"Anomalies detected: {', '.join(anomalies_detected[:2])}")
    if loan_to_income_ratio > 4.0:
        key_factors.append(f"High loan-to-income ratio ({loan_to_income_ratio:.2f})")

    # Add positive factors if approving
    if classification == "Approved":
        if income_stability_score > 0.80:
            key_factors.append(f"Strong income stability ({income_stability_score:.2f})")
        if dti_ratio < 0.30:
            key_factors.append(f"Low DTI ratio ({dti_ratio:.2%})")

    # Ensure we have at least one factor
    if not key_factors:
        key_factors.append(f"Overall risk score: {overall_risk_score:.2f}")

    # Generate case ID
    case_id = f"CASE-{applicant_id}-{uuid.uuid4().hex[:8].upper()}"

    return {
        "applicant_id": applicant_id,
        "classification": classification,
        "risk_score": round(overall_risk_score, 2),
        "confidence": round(confidence, 2),
        "key_factors": key_factors,
        "case_id": case_id,
        "component_scores": {
            "employment_risk": round(employment_risk_score, 2),
            "income_stability": round(income_risk_component, 2),
            "dti_risk": round(dti_component, 2),
            "credit_risk": round(credit_risk_score, 2),
            "lti_risk": round(lti_component, 2),
            "anomaly_risk": round(anomaly_risk_score, 2),
        },
        "synthesis_timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    print("Starting DecisionSynthesis MCP Server...")
    print("Available tool: synthesize_decision")

    # Test example
    print("\n--- Test: synthesize_decision ---")
    result = synthesize_decision(
        applicant_id="APP001",
        income_stability_score=0.85,
        employment_risk="Low",
        dti_ratio=0.35,
        credit_risk_score=0.15,
        loan_to_income_ratio=2.5,
        anomaly_risk_score=0.05,
        anomalies_detected=[],
    )
    import json

    print(json.dumps(result, indent=2))
