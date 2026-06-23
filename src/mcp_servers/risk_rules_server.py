"""
RiskRulesDB Server
Provides tools for financial risk assessment and anomaly detection
"""

from typing import Dict, Any


# Risk assessment rules
DTI_THRESHOLDS = {
    "safe": (0, 0.30),
    "moderate": (0.30, 0.45),
    "high": (0.45, 0.60),
    "critical": (0.60, float("inf")),
}

CREDIT_SCORE_BRACKETS = {
    "excellent": (750, 850),
    "good": (670, 749),
    "fair": (580, 669),
    "poor": (300, 579),
}

LOAN_TO_INCOME_LIMITS = {
    "salaried": 5.0,
    "self_employed": 2.5,
    "freelance": 2.0,
    "unemployed": 0.0,
}


def calculate_debt_to_income(income: float, existing_liabilities: float, loan_amount: float) -> Dict[str, Any]:
    """
    Calculate debt-to-income ratio

    Args:
        income: Annual income in dollars
        existing_liabilities: Total existing debt in dollars
        loan_amount: Requested loan amount in dollars

    Returns:
        DTI ratio and risk classification
    """
    if income <= 0:
        return {"error": "Income must be positive"}

    # Estimate monthly loan payment (assuming 5-year tenure, 6% interest for simplification)
    monthly_loan_payment = (loan_amount * 0.06 / 12) / (1 - (1 + 0.06 / 12) ** (-60))
    monthly_income = income / 12
    monthly_liabilities = existing_liabilities / 12  # Simplified: spread over 12 months

    total_monthly_debt = monthly_loan_payment + monthly_liabilities
    dti_ratio = total_monthly_debt / monthly_income if monthly_income > 0 else 1.0

    # Classify risk level
    risk_level = "critical"
    for level, (low, high) in DTI_THRESHOLDS.items():
        if low <= dti_ratio < high:
            risk_level = level
            break

    return {
        "dti_ratio": round(dti_ratio, 3),
        "risk_level": risk_level,
        "monthly_debt_payment": round(total_monthly_debt, 2),
        "monthly_income": round(monthly_income, 2),
        "max_recommended_debt": round(monthly_income * 0.45, 2),
    }


def assess_credit_risk(credit_score: int, historical_defaults: int) -> Dict[str, Any]:
    """
    Assess credit risk based on credit score and default history

    Args:
        credit_score: Credit score (300-850)
        historical_defaults: Number of historical defaults

    Returns:
        Credit risk classification and score
    """
    if not (300 <= credit_score <= 850):
        return {"error": "Credit score must be between 300 and 850"}

    # Classify credit score
    credit_bracket = "poor"
    for bracket, (low, high) in CREDIT_SCORE_BRACKETS.items():
        if low <= credit_score <= high:
            credit_bracket = bracket
            break

    # Calculate risk based on score and defaults
    base_risk = {"excellent": 0.1, "good": 0.25, "fair": 0.50, "poor": 0.80}[credit_bracket]

    # Increase risk for each default (up to max 0.95)
    default_penalty = min(historical_defaults * 0.15, 0.40)
    credit_risk_score = min(base_risk + default_penalty, 0.95)

    # Classify final risk level
    if credit_risk_score < 0.30:
        risk_level = "Low"
    elif credit_risk_score < 0.60:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return {
        "credit_score": credit_score,
        "credit_bracket": credit_bracket,
        "historical_defaults": historical_defaults,
        "credit_risk_score": round(credit_risk_score, 2),
        "risk_level": risk_level,
    }


def evaluate_loan_amount_risk(loan_amount: float, income: float, employment_type: str = "salaried") -> Dict[str, Any]:
    """
    Evaluate risk of requested loan amount relative to income

    Args:
        loan_amount: Requested loan amount in dollars
        income: Annual income in dollars
        employment_type: Type of employment (salaried, self_employed, freelance, unemployed)

    Returns:
        Loan amount risk assessment
    """
    if income <= 0 or loan_amount <= 0:
        return {"error": "Income and loan amount must be positive"}

    loan_to_income = loan_amount / income
    max_lti = LOAN_TO_INCOME_LIMITS.get(employment_type, 2.0)

    # Classify risk
    if loan_to_income <= max_lti * 0.7:
        risk_level = "Low"
        risk_score = 0.1
    elif loan_to_income <= max_lti:
        risk_level = "Medium"
        risk_score = 0.4
    elif loan_to_income <= max_lti * 1.3:
        risk_level = "High"
        risk_score = 0.7
    else:
        risk_level = "Critical"
        risk_score = 0.9

    return {
        "loan_amount": loan_amount,
        "annual_income": income,
        "loan_to_income_ratio": round(loan_to_income, 2),
        "max_recommended_lti": max_lti,
        "employment_type": employment_type,
        "risk_level": risk_level,
        "risk_score": risk_score,
    }


def detect_anomalies(
    applicant_id: str,
    credit_score: int,
    recent_inquiries: int,
    credit_defaults: int,
    employment_type: str,
    income_stability_score: float,
) -> Dict[str, Any]:
    """
    Detect suspicious patterns or anomalies in applicant profile

    Args:
        applicant_id: Unique applicant identifier
        credit_score: Credit score
        recent_inquiries: Number of recent credit inquiries
        credit_defaults: Number of historical defaults
        employment_type: Type of employment
        income_stability_score: Income stability score (0-1)

    Returns:
        List of detected anomalies and overall anomaly risk
    """
    anomalies = []
    anomaly_risk_score = 0.0

    # Check for multiple recent inquiries
    if recent_inquiries >= 3:
        anomalies.append(f"Multiple recent credit inquiries ({recent_inquiries})")
        anomaly_risk_score += 0.25

    # Check for recent defaults
    if credit_defaults > 0:
        anomalies.append(f"Recent payment defaults ({credit_defaults} defaults)")
        anomaly_risk_score += 0.30

    # Check for employment instability
    if income_stability_score < 0.4:
        anomalies.append("Unstable income history")
        anomaly_risk_score += 0.20

    # Check for low credit score with high inquiries
    if credit_score < 600 and recent_inquiries >= 2:
        anomalies.append("Low credit score combined with recent inquiries - possible credit-seeking behavior")
        anomaly_risk_score += 0.15

    # Check for self-employed/freelance with poor credit
    if employment_type in ["self_employed", "freelance"] and credit_score < 650:
        anomalies.append("Self-employed/freelance status with lower credit score")
        anomaly_risk_score += 0.10

    # Cap anomaly score at 1.0
    anomaly_risk_score = min(anomaly_risk_score, 1.0)

    return {
        "applicant_id": applicant_id,
        "anomalies_detected": anomalies,
        "anomaly_risk_score": round(anomaly_risk_score, 2),
        "requires_manual_review": anomaly_risk_score > 0.5,
    }


if __name__ == "__main__":
    print("Starting RiskRulesDB MCP Server...")
    print("Available tools: calculate_debt_to_income, assess_credit_risk, evaluate_loan_amount_risk, detect_anomalies")

    # Test examples
    print("\n--- Test: calculate_debt_to_income ---")
    print(calculate_debt_to_income(100000, 25000, 50000))

    print("\n--- Test: assess_credit_risk ---")
    print(assess_credit_risk(750, 0))

    print("\n--- Test: evaluate_loan_amount_risk ---")
    print(evaluate_loan_amount_risk(100000, 150000, "salaried"))

    print("\n--- Test: detect_anomalies ---")
    print(
        detect_anomalies(
            applicant_id="APP001",
            credit_score=650,
            recent_inquiries=4,
            credit_defaults=1,
            employment_type="self_employed",
            income_stability_score=0.35,
        )
    )
