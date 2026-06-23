from typing import Tuple, List
from src.schemas import LoanApplication, EmploymentType


def validate_loan_application(app: LoanApplication) -> Tuple[bool, List[str]]:
    """Validate loan application and return (is_valid, list_of_errors)"""
    errors = []

    # Age validation
    if app.age < 18:
        errors.append("Applicant must be at least 18 years old")
    if app.age > 100:
        errors.append("Age must be reasonable (≤100)")

    # Income validation
    if app.income <= 0:
        errors.append("Income must be positive")
    if app.income > 10_000_000:
        errors.append("Income seems unusually high; please verify")

    # Credit score validation
    if app.credit_score < 300 or app.credit_score > 850:
        errors.append("Credit score must be between 300 and 850")

    # Loan amount validation
    if app.loan_amount <= 0:
        errors.append("Loan amount must be positive")
    if app.loan_amount > app.income * 50:
        errors.append("Loan amount exceeds 50x annual income")

    # Tenure validation
    if app.loan_tenure_months <= 0:
        errors.append("Loan tenure must be positive")
    if app.loan_tenure_months > 600:
        errors.append("Loan tenure exceeds maximum (600 months/50 years)")

    # Liabilities validation
    if app.existing_liabilities < 0:
        errors.append("Existing liabilities cannot be negative")

    # Location validation
    if not app.location or len(app.location.strip()) == 0:
        errors.append("Location is required")

    return len(errors) == 0, errors


def get_employment_risk_level(employment_type: EmploymentType) -> str:
    """Map employment type to base risk level"""
    risk_map = {
        EmploymentType.SALARIED: "Low",
        EmploymentType.SELF_EMPLOYED: "High",
        EmploymentType.FREELANCE: "High",
        EmploymentType.UNEMPLOYED: "Critical",
    }
    return risk_map.get(employment_type, "Medium")
