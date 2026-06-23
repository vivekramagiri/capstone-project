"""
Fast rule-based decision engine for quick loan approval decisions
"""

import uuid
from datetime import datetime
from src.schemas import LoanApplication, LoanDecision, DecisionType


class QuickDecisionEngine:
    """Rule-based decision engine for fast loan decisions"""

    @staticmethod
    def make_decision(application: LoanApplication) -> LoanDecision:
        """
        Make a quick loan decision based on rules

        Args:
            application: Loan application

        Returns:
            LoanDecision with classification and reasoning
        """
        # Calculate key metrics
        dti_ratio = (application.loan_amount / 12) / (application.income / 12)
        credit_score = application.credit_score
        income = application.income
        loan_to_income = application.loan_amount / income

        # Initialize decision parameters
        risk_score = 0.0
        key_factors = []
        classification = DecisionType.APPROVED

        # Credit score evaluation
        if credit_score < 580:
            classification = DecisionType.REJECTED
            risk_score += 0.4
            key_factors.append("Credit score too low (< 580)")
        elif credit_score < 620:
            risk_score += 0.3
            key_factors.append("Fair credit score (620-579)")
        elif credit_score < 700:
            risk_score += 0.15
            key_factors.append("Good credit score (620-700)")
        else:
            risk_score += 0.05
            key_factors.append("Excellent credit score (700+)")

        # DTI ratio evaluation
        if dti_ratio > 0.50:
            classification = DecisionType.REJECTED
            risk_score += 0.4
            key_factors.append(f"Debt-to-income ratio too high ({dti_ratio:.2%})")
        elif dti_ratio > 0.43:
            risk_score += 0.25
            key_factors.append(f"Debt-to-income ratio concerning ({dti_ratio:.2%})")
        elif dti_ratio > 0.35:
            risk_score += 0.15
            key_factors.append(f"Debt-to-income ratio acceptable ({dti_ratio:.2%})")
        else:
            risk_score += 0.05
            key_factors.append(f"Debt-to-income ratio excellent ({dti_ratio:.2%})")

        # Loan to income ratio
        if loan_to_income > 5:
            classification = DecisionType.REJECTED
            risk_score += 0.3
            key_factors.append("Loan amount too high relative to income")
        elif loan_to_income > 3:
            risk_score += 0.15
            key_factors.append("Loan amount moderately high relative to income")
        else:
            key_factors.append("Loan amount reasonable relative to income")

        # Income evaluation
        if income < 30000:
            risk_score += 0.2
            key_factors.append("Lower income level")
        elif income > 150000:
            risk_score -= 0.1
            key_factors.append("Strong income level")

        # Employment type evaluation
        employment_risk_map = {
            "salaried": 0.0,
            "self_employed": 0.15,
            "freelance": 0.2,
            "unemployed": 0.5
        }
        emp_risk = employment_risk_map.get(application.employment_type.value, 0.1)
        risk_score += emp_risk
        key_factors.append(f"Employment type: {application.employment_type.value}")

        # Existing liabilities
        if application.existing_liabilities > application.income * 0.5:
            risk_score += 0.15
            key_factors.append("High existing liabilities")
        elif application.existing_liabilities > 0:
            risk_score += 0.05
            key_factors.append("Moderate existing liabilities")

        # Age evaluation
        if application.age < 22:
            risk_score += 0.1
            key_factors.append("Applicant age relatively young")
        elif application.age > 65:
            risk_score += 0.1
            key_factors.append("Applicant age near retirement")

        # Normalize risk score to 0-1
        risk_score = min(max(risk_score, 0), 1)

        # Final decision based on risk score
        if classification == DecisionType.REJECTED:
            explanation = f"Application rejected due to {', '.join(key_factors[:2])}"
        elif risk_score > 0.70:
            classification = DecisionType.REQUIRES_REVIEW
            explanation = f"High risk factors detected. Manual review recommended: {', '.join(key_factors[:3])}"
        elif risk_score > 0.50:
            classification = DecisionType.APPROVED
            explanation = f"Application approved with moderate risk. Factors: {', '.join(key_factors[:3])}"
        else:
            classification = DecisionType.APPROVED
            explanation = f"Application approved. Favorable risk profile. Key factors: {', '.join(key_factors[:3])}"

        # Calculate confidence
        confidence = 1.0 - (risk_score * 0.3)  # Inverse relationship

        return LoanDecision(
            applicant_id=application.applicant_id,
            classification=classification,
            risk_score=risk_score,
            confidence=confidence,
            key_factors=key_factors[:5],  # Top 5 factors
            explanation=explanation,
            case_id=f"CASE-{uuid.uuid4().hex[:8].upper()}",
            decision_timestamp=datetime.utcnow()
        )
