from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class EmploymentType(str, Enum):
    SALARIED = "salaried"
    SELF_EMPLOYED = "self_employed"
    FREELANCE = "freelance"
    UNEMPLOYED = "unemployed"


class DecisionType(str, Enum):
    APPROVED = "Approved"
    REJECTED = "Rejected"
    REQUIRES_REVIEW = "Requires Manual Review"


class LoanApplication(BaseModel):
    applicant_id: str = Field(..., description="Unique applicant identifier")
    age: int = Field(..., ge=18, le=100, description="Applicant age")
    income: float = Field(..., gt=0, description="Annual income in dollars")
    employment_type: EmploymentType = Field(..., description="Type of employment")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score (300-850)")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount in dollars")
    loan_tenure_months: int = Field(..., gt=0, description="Loan tenure in months")
    existing_liabilities: float = Field(default=0, ge=0, description="Total existing debt")
    location: str = Field(..., description="Applicant location/state")
    application_timestamp: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="Application submission time"
    )
    phone: Optional[str] = Field(default=None, description="Applicant phone number")
    email: Optional[str] = Field(default=None, description="Applicant email")

    @validator("age")
    def validate_age(cls, v):
        if v < 18:
            raise ValueError("Applicant must be at least 18 years old")
        return v

    @validator("credit_score")
    def validate_credit_score(cls, v):
        if v < 300 or v > 850:
            raise ValueError("Credit score must be between 300 and 850")
        return v


class ApplicantProfileAnalysis(BaseModel):
    applicant_id: str
    income_stability_score: float = Field(..., ge=0, le=1, description="Income stability score (0-1)")
    employment_risk: str = Field(..., description="Risk level: Low, Medium, High")
    credit_history_summary: str = Field(..., description="Summary of credit history")
    completeness_flags: List[str] = Field(default_factory=list, description="Data quality issues")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional analysis details")


class FinancialRiskAnalysis(BaseModel):
    applicant_id: str
    debt_to_income_ratio: float = Field(..., ge=0, description="DTI ratio (e.g., 0.35 = 35%)")
    credit_risk_level: str = Field(..., description="Risk level: Low, Medium, High")
    loan_amount_risk: str = Field(..., description="Risk assessment for loan amount")
    anomalies_detected: List[str] = Field(default_factory=list, description="Suspicious patterns found")
    risk_score: float = Field(..., ge=0, le=1, description="Overall risk score (0-1)")
    reasoning: str = Field(..., description="Explanation of risk assessment")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class LoanDecision(BaseModel):
    applicant_id: str
    classification: DecisionType = Field(..., description="Decision: Approved, Rejected, or Requires Review")
    risk_score: float = Field(..., ge=0, le=1, description="Overall risk score (0-1)")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in decision (0-1)")
    key_factors: List[str] = Field(..., description="Primary factors influencing decision")
    explanation: str = Field(..., description="Detailed explanation of decision")
    case_id: str = Field(..., description="Unique case reference ID")
    decision_timestamp: datetime = Field(default_factory=datetime.utcnow)


class ComplianceAction(BaseModel):
    applicant_id: str
    case_id: str
    action_taken: str = Field(..., description="Action executed (e.g., 'Notification Sent', 'Case Logged')")
    notification_sent: bool = Field(..., description="Whether notification was sent")
    audit_log: str = Field(..., description="Audit trail entry")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    summary: str = Field(..., description="Summary of compliance action")


class LoanApplicationResponse(BaseModel):
    application_id: str
    decision: str
    risk_score: float
    confidence: float
    key_factors: List[str]
    reasoning: str
    case_id: str
    timestamp: str
    status: str = "completed"
