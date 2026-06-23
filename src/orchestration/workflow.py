"""
LangGraph-based orchestration workflow for loan approval
"""

from datetime import datetime
from typing import Optional
from langgraph.graph import StateGraph, START, END
from src.orchestration.state import ApplicationState
from src.agents import applicant_profile_agent, financial_risk_agent, loan_decision_agent, compliance_agent
from src.utils.logger import get_logger
from src.utils.validators import validate_loan_application
import hashlib
import json

logger = get_logger(__name__)

# Simple cache for agent responses
_response_cache = {}


def _get_cache_key(agent_name: str, application_data: dict) -> str:
    """Generate cache key for agent response"""
    data_str = json.dumps(application_data, sort_keys=True, default=str)
    return f"{agent_name}:{hashlib.md5(data_str.encode()).hexdigest()}"


def validate_input(state: ApplicationState) -> ApplicationState:
    """Validate loan application input"""
    logger.info(f"Validating input for applicant {state['application'].applicant_id}")

    application = state["application"]
    is_valid, errors = validate_loan_application(application)

    state["step_history"].append("validate_input")

    if not is_valid:
        state["errors"].extend(errors)
        state["status"] = "failed"
        logger.error(f"Validation failed with errors: {errors}")
        return state

    logger.info("Input validation passed")
    return state


def run_applicant_profile_agent(state: ApplicationState) -> ApplicationState:
    """Run applicant profile analysis agent"""
    logger.info(f"Running applicant profile analysis for {state['application'].applicant_id}")

    if state["status"] == "failed":
        logger.warning("Skipping profile agent due to prior errors")
        return state

    try:
        app_dict = state["application"].model_dump()
        cache_key = _get_cache_key("profile", app_dict)

        if cache_key in _response_cache:
            logger.info("✓ Profile analysis retrieved from cache")
            state["applicant_analysis"] = _response_cache[cache_key]
        else:
            agent = applicant_profile_agent.get_agent()
            profile_analysis = agent.analyze(state["application"])
            _response_cache[cache_key] = profile_analysis
            state["applicant_analysis"] = profile_analysis
            logger.info(f"Profile analysis completed: {profile_analysis.employment_risk}")

        state["step_history"].append("applicant_profile_agent")
    except Exception as e:
        logger.error(f"Profile agent failed: {str(e)}")
        state["errors"].append(f"Profile analysis failed: {str(e)}")
        state["status"] = "failed"

    return state


def run_financial_risk_agent(state: ApplicationState) -> ApplicationState:
    """Run financial risk analysis agent"""
    logger.info(f"Running financial risk analysis for {state['application'].applicant_id}")

    if state["status"] == "failed" or state["applicant_analysis"] is None:
        logger.warning("Skipping risk agent due to prior errors")
        return state

    try:
        app_dict = state["application"].model_dump()
        cache_key = _get_cache_key("risk", app_dict)

        if cache_key in _response_cache:
            logger.info("✓ Risk analysis retrieved from cache")
            state["risk_analysis"] = _response_cache[cache_key]
        else:
            agent = financial_risk_agent.get_agent()
            risk_analysis = agent.analyze(state["application"], state["applicant_analysis"])
            _response_cache[cache_key] = risk_analysis
            state["risk_analysis"] = risk_analysis
            logger.info(f"Risk analysis completed: risk_score={risk_analysis.risk_score}")

        state["step_history"].append("financial_risk_agent")
    except Exception as e:
        logger.error(f"Risk agent failed: {str(e)}")
        state["errors"].append(f"Risk analysis failed: {str(e)}")
        state["status"] = "failed"

    return state


def run_decision_agent(state: ApplicationState) -> ApplicationState:
    """Run loan decision agent"""
    logger.info(f"Running loan decision for {state['application'].applicant_id}")

    if state["status"] == "failed" or state["applicant_analysis"] is None or state["risk_analysis"] is None:
        logger.warning("Skipping decision agent due to prior errors")
        return state

    try:
        app_dict = state["application"].model_dump()
        cache_key = _get_cache_key("decision", app_dict)

        if cache_key in _response_cache:
            logger.info("✓ Decision retrieved from cache")
            state["decision"] = _response_cache[cache_key]
        else:
            agent = loan_decision_agent.get_agent()
            decision = agent.decide(state["application"], state["applicant_analysis"], state["risk_analysis"])
            _response_cache[cache_key] = decision
            state["decision"] = decision
            logger.info(f"Decision made: {decision.classification.value}")

        state["step_history"].append("loan_decision_agent")
    except Exception as e:
        logger.error(f"Decision agent failed: {str(e)}")
        state["errors"].append(f"Decision analysis failed: {str(e)}")
        state["status"] = "failed"

    return state


def run_compliance_agent(state: ApplicationState) -> ApplicationState:
    """Run compliance agent to log decision and send notifications"""
    logger.info(f"Running compliance actions for {state['application'].applicant_id}")

    if state["status"] == "failed" or state["decision"] is None:
        logger.warning("Skipping compliance agent due to prior errors")
        return state

    try:
        agent = compliance_agent.get_agent()
        compliance_action = agent.execute(state["application"].applicant_id, state["decision"])
        state["compliance_action"] = compliance_action
        state["step_history"].append("compliance_agent")
        logger.info(f"Compliance actions completed: {compliance_action.action_taken}")
    except Exception as e:
        logger.error(f"Compliance agent failed: {str(e)}")
        state["errors"].append(f"Compliance actions failed: {str(e)}")

    return state


def finalize(state: ApplicationState) -> ApplicationState:
    """Finalize the workflow"""
    logger.info(f"Finalizing workflow for {state['application'].applicant_id}")

    state["completed_at"] = datetime.utcnow().isoformat()
    if state["status"] != "failed":
        state["status"] = "completed"

    state["step_history"].append("finalize")
    logger.info(f"Workflow completed with status: {state['status']}")

    return state


def build_workflow():
    """Build the LangGraph workflow with sequential execution (LangGraph state merging limitation)"""
    workflow = StateGraph(ApplicationState)

    # Add nodes
    workflow.add_node("validate_input", validate_input)
    workflow.add_node("applicant_profile_agent", run_applicant_profile_agent)
    workflow.add_node("financial_risk_agent", run_financial_risk_agent)
    workflow.add_node("loan_decision_agent", run_decision_agent)
    workflow.add_node("compliance_agent", run_compliance_agent)
    workflow.add_node("finalize", finalize)

    # Sequential workflow (LangGraph requires proper state merging for parallel)
    # Profile and Risk are optimized individually (fast model, reduced tokens)
    workflow.add_edge(START, "validate_input")
    workflow.add_edge("validate_input", "applicant_profile_agent")
    workflow.add_edge("applicant_profile_agent", "financial_risk_agent")
    workflow.add_edge("financial_risk_agent", "loan_decision_agent")
    workflow.add_edge("loan_decision_agent", "compliance_agent")
    workflow.add_edge("compliance_agent", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()


# Global workflow instance
_workflow_graph = None


def get_workflow():
    """Get or create the compiled workflow"""
    global _workflow_graph
    if _workflow_graph is None:
        _workflow_graph = build_workflow()
        logger.info("Workflow graph compiled")
    return _workflow_graph


def run_application_workflow(application_data: dict) -> ApplicationState:
    """
    Execute the loan application workflow

    Args:
        application_data: Dictionary with loan application details

    Returns:
        Final application state with all results
    """
    from src.schemas import LoanApplication

    try:
        # Parse application
        application = LoanApplication(**application_data)

        # Initialize state
        initial_state: ApplicationState = {
            "application": application,
            "applicant_analysis": None,
            "risk_analysis": None,
            "decision": None,
            "compliance_action": None,
            "step_history": [],
            "errors": [],
            "execution_id": f"EXEC-{application.applicant_id}-{datetime.utcnow().timestamp()}",
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "status": "processing",
        }

        # Run workflow
        workflow = get_workflow()
        final_state = workflow.invoke(initial_state)

        logger.info(f"Workflow execution completed for {application.applicant_id}")
        return final_state

    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        raise
