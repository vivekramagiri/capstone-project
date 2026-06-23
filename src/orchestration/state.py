"""
Application workflow state management
"""

from typing import Optional, List, Dict, Any
from typing_extensions import TypedDict
from src.schemas import (
    LoanApplication,
    ApplicantProfileAnalysis,
    FinancialRiskAnalysis,
    LoanDecision,
    ComplianceAction,
)


class ApplicationState(TypedDict, total=False):
    """Workflow state that gets passed through the orchestration"""

    # Primary data
    application: LoanApplication

    # Analysis results
    applicant_analysis: Optional[ApplicantProfileAnalysis]
    risk_analysis: Optional[FinancialRiskAnalysis]
    decision: Optional[LoanDecision]
    compliance_action: Optional[ComplianceAction]

    # Tracking
    step_history: List[str]
    errors: List[str]

    # Execution info
    execution_id: str
    started_at: str
    completed_at: Optional[str]
    status: str  # pending, processing, completed, failed
