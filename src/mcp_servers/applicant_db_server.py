"""
ApplicantDB Server
Provides tools for querying applicant profile information and credit history
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel


# Simulated applicant database
APPLICANT_DB = {
    "APP001": {
        "name": "John Doe",
        "age": 35,
        "employment_type": "salaried",
        "employment_years": 8,
        "income_history": [85000, 87000, 90000, 95000],
        "credit_defaults": 0,
        "recent_inquiries": 1,
        "account_age_months": 120,
        "missing_fields": [],
    },
    "APP002": {
        "name": "Jane Smith",
        "age": 28,
        "employment_type": "self_employed",
        "employment_years": 3,
        "income_history": [45000, 52000, 58000],
        "credit_defaults": 1,
        "recent_inquiries": 4,
        "account_age_months": 60,
        "missing_fields": ["employment_verification"],
    },
    "APP003": {
        "name": "Bob Johnson",
        "age": 52,
        "employment_type": "salaried",
        "employment_years": 20,
        "income_history": [120000, 125000, 130000, 135000],
        "credit_defaults": 0,
        "recent_inquiries": 0,
        "account_age_months": 240,
        "missing_fields": [],
    },
}


def get_applicant_profile(applicant_id: str) -> Dict[str, Any]:
    """
    Retrieve applicant profile information including employment and credit history

    Args:
        applicant_id: Unique applicant identifier

    Returns:
        Dictionary containing applicant profile data
    """
    if applicant_id not in APPLICANT_DB:
        return {"error": f"Applicant {applicant_id} not found in database"}

    profile = APPLICANT_DB[applicant_id]

    # Calculate stability score based on employment history
    employment_years = profile["employment_years"]
    income_growth = (
        (profile["income_history"][-1] - profile["income_history"][0])
        / profile["income_history"][0]
        if profile["income_history"]
        else 0
    )

    # Income stability: higher score = more stable
    if employment_years >= 5 and income_growth >= 0:
        stability_score = min(0.9, 0.5 + employment_years / 50 + income_growth / 5)
    else:
        stability_score = 0.3 + (employment_years / 20)

    # Employment risk mapping
    employment_risk_map = {
        "salaried": "Low",
        "self_employed": "High",
        "freelance": "High",
        "unemployed": "Critical",
    }
    employment_risk = employment_risk_map.get(profile["employment_type"], "Medium")

    # Credit history summary
    default_flag = "Yes" if profile["credit_defaults"] > 0 else "No"
    inquiry_flag = "Multiple recent inquiries" if profile["recent_inquiries"] >= 3 else "Normal inquiry activity"

    credit_history_summary = f"Defaults: {default_flag}. {inquiry_flag}. Account age: {profile['account_age_months']} months."

    return {
        "applicant_id": applicant_id,
        "name": profile["name"],
        "age": profile["age"],
        "employment_type": profile["employment_type"],
        "employment_years": employment_years,
        "income_history": profile["income_history"],
        "income_stability_score": round(stability_score, 2),
        "employment_risk": employment_risk,
        "credit_history_summary": credit_history_summary,
        "credit_defaults": profile["credit_defaults"],
        "recent_inquiries": profile["recent_inquiries"],
        "account_age_months": profile["account_age_months"],
    }


def validate_application_completeness(applicant_id: str) -> Dict[str, Any]:
    """
    Check for missing or incomplete fields in application

    Args:
        applicant_id: Unique applicant identifier

    Returns:
        Dictionary with completeness status and any missing fields
    """
    if applicant_id not in APPLICANT_DB:
        return {"error": f"Applicant {applicant_id} not found in database"}

    profile = APPLICANT_DB[applicant_id]
    missing_fields = profile.get("missing_fields", [])

    is_complete = len(missing_fields) == 0

    return {
        "applicant_id": applicant_id,
        "is_complete": is_complete,
        "missing_fields": missing_fields,
        "completion_flags": [f"Missing: {field}" for field in missing_fields],
    }


if __name__ == "__main__":
    import uvicorn

    print("Starting ApplicantDB MCP Server...")
    print("Available tools: get_applicant_profile, validate_application_completeness")

    # For testing purposes
    print("\nTest: get_applicant_profile('APP001')")
    print(get_applicant_profile("APP001"))
    print("\nTest: validate_application_completeness('APP002')")
    print(validate_application_completeness("APP002"))
