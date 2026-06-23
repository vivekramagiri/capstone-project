"""
API endpoints for loan application processing
"""

from fastapi import APIRouter, HTTPException, status
from src.schemas import LoanApplication, LoanApplicationResponse
from src.orchestration.workflow import run_application_workflow
from src.decision_engine import QuickDecisionEngine
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Loan Applications"])


@router.post("/loan/apply", response_model=LoanApplicationResponse, status_code=status.HTTP_200_OK)
async def apply_for_loan(application: LoanApplication) -> LoanApplicationResponse:
    """
    Submit a loan application and receive an immediate decision (fast path)

    Args:
        application: LoanApplication with applicant and loan details

    Returns:
        LoanApplicationResponse with decision and reasoning
    """
    try:
        logger.info(f"Processing loan application for applicant {application.applicant_id}")

        # Use fast rule-based decision engine
        decision = QuickDecisionEngine.make_decision(application)

        # Build response
        response = LoanApplicationResponse(
            application_id=application.applicant_id,
            decision=decision.classification.value,
            risk_score=decision.risk_score,
            confidence=decision.confidence,
            key_factors=decision.key_factors,
            reasoning=decision.explanation,
            case_id=decision.case_id,
            timestamp=decision.decision_timestamp.isoformat(),
            status="completed",
        )

        logger.info(
            f"Application {application.applicant_id} processed: {decision.classification.value}"
        )
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.post("/loan/apply-detailed", response_model=LoanApplicationResponse, status_code=status.HTTP_200_OK)
async def apply_for_loan_detailed(application: LoanApplication) -> LoanApplicationResponse:
    """
    Submit a loan application with full multi-agent analysis (slower but more comprehensive)

    Args:
        application: LoanApplication with applicant and loan details

    Returns:
        LoanApplicationResponse with AI-powered decision and detailed reasoning
    """
    try:
        logger.info(f"Processing detailed loan application for applicant {application.applicant_id}")

        # Convert to dict for workflow
        app_dict = application.model_dump()

        # Execute full workflow with agents
        final_state = run_application_workflow(app_dict)

        # Check for errors
        if final_state.get("status") == "failed":
            errors = final_state.get("errors", [])
            logger.error(f"Application processing failed: {errors}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Application processing failed: {', '.join(errors)}",
            )

        # Extract results
        decision = final_state.get("decision")
        if not decision:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No decision generated",
            )

        # Build response
        response = LoanApplicationResponse(
            application_id=application.applicant_id,
            decision=decision.classification.value,
            risk_score=decision.risk_score,
            confidence=decision.confidence,
            key_factors=decision.key_factors,
            reasoning=decision.explanation,
            case_id=decision.case_id,
            timestamp=decision.decision_timestamp.isoformat(),
            status="completed",
        )

        logger.info(
            f"Detailed application {application.applicant_id} processed: {decision.classification.value}"
        )
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/loan/{application_id}/status")
async def get_application_status(application_id: str):
    """
    Get the status of a previously submitted application

    Note: This is a placeholder. In a production system, this would query a database.

    Args:
        application_id: The application ID to look up

    Returns:
        Application status information
    """
    return {
        "application_id": application_id,
        "status": "completed",
        "note": "Full status lookup would require persistent storage",
    }


@router.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "service": "Loan Approval AI System",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "apply": "POST /api/loan/apply",
            "status": "GET /api/loan/{application_id}/status",
        },
    }
