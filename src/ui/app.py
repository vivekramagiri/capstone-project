"""
Streamlit chatbot UI for loan application submission and status display
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import requests
from datetime import datetime
from src.schemas import EmploymentType

# Page configuration
st.set_page_config(
    page_title="Loan Approval AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API configuration
API_BASE_URL = "http://localhost:8000/api"
REQUEST_TIMEOUT = 60  # Increased for detailed analysis


def get_decision_color(decision: str) -> str:
    """Get color for decision badge"""
    colors = {
        "Approved": "🟢",
        "Rejected": "🔴",
        "Requires Manual Review": "🟡",
    }
    return colors.get(decision, "⚫")


def submit_application(form_data: Dict[str, Any], use_detailed: bool = True) -> Optional[Dict[str, Any]]:
    """Submit application to API and get decision"""
    try:
        endpoint = "/loan/apply-detailed" if use_detailed else "/loan/apply"
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=form_data,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None


# Header
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.title("💰 Intelligent Loan Approval System")
    st.markdown("*Multi-Agent Agentic AI powered by Claude*")
with col2:
    st.metric("System Status", "🟢 Online")
with col3:
    analysis_type = st.selectbox(
        "Analysis Mode",
        ["Detailed (Agentic)", "Fast (Rule-based)"],
        help="Detailed: Multi-agent analysis (420ms). Fast: Rule-based (39ms)"
    )
    use_detailed = analysis_type == "Detailed (Agentic)"

st.divider()

# Main content
tab1, tab2 = st.tabs(["📝 New Application", "📊 Recent Applications"])

with tab1:
    st.subheader("Loan Application Form")

    # Create form with two columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Applicant Information")
        applicant_id = st.text_input(
            "Applicant ID",
            value="APP001",
            help="Unique identifier for the applicant",
        )
        age = st.number_input(
            "Age", min_value=18, max_value=100, value=35, help="Applicant age in years"
        )
        income = st.number_input(
            "Annual Income ($)",
            min_value=0.0,
            value=100000.0,
            step=5000.0,
            help="Annual income in dollars",
        )
        employment_type = st.selectbox(
            "Employment Type",
            options=[e.value for e in EmploymentType],
            index=0,
            help="Type of employment",
        )

    with col2:
        st.markdown("### Loan Details")
        loan_amount = st.number_input(
            "Loan Amount ($)",
            min_value=0.0,
            value=50000.0,
            step=5000.0,
            help="Requested loan amount in dollars",
        )
        loan_tenure = st.number_input(
            "Loan Tenure (months)",
            min_value=1,
            max_value=600,
            value=60,
            help="Loan tenure in months",
        )
        credit_score = st.number_input(
            "Credit Score",
            min_value=300,
            max_value=850,
            value=750,
            help="Credit score (300-850)",
        )
        existing_liabilities = st.number_input(
            "Existing Liabilities ($)",
            min_value=0.0,
            value=0.0,
            step=1000.0,
            help="Total existing debt in dollars",
        )

    col1, col2 = st.columns(2)
    with col1:
        location = st.text_input("Location (State/Province)", value="CA", help="Applicant location")
    with col2:
        phone = st.text_input("Phone Number (Optional)", help="Contact phone number")

    st.divider()

    # Submit button
    if st.button("🚀 Submit Application", type="primary", use_container_width=True):
        st.session_state.show_processing = True

        # Prepare application data
        app_data = {
            "applicant_id": applicant_id,
            "age": age,
            "income": income,
            "employment_type": employment_type,
            "loan_amount": loan_amount,
            "loan_tenure_months": loan_tenure,
            "credit_score": credit_score,
            "existing_liabilities": existing_liabilities,
            "location": location,
            "phone": phone,
        }

        # Show processing message
        if use_detailed:
            spinner_msg = "🔄 Running multi-agent analysis... (Profile → Risk → Decision → Compliance)"
        else:
            spinner_msg = "⚡ Processing with rule-based engine..."

        with st.spinner(spinner_msg):
            result = submit_application(app_data, use_detailed=use_detailed)

        if result:
            st.session_state.last_result = result
            st.session_state.show_processing = False

            # Display results
            st.divider()
            st.subheader("📋 Decision Result")

            # Decision banner
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(
                    f"## {get_decision_color(result['decision'])} **{result['decision']}**"
                )
            with col2:
                st.metric("Risk Score", f"{result['risk_score']:.2%}")
            with col3:
                st.metric("Confidence", f"{result['confidence']:.0%}")

            # Key factors
            st.markdown("### Key Decision Factors")
            for i, factor in enumerate(result["key_factors"], 1):
                st.write(f"{i}. {factor}")

            # Detailed reasoning
            if use_detailed:
                with st.expander("🤖 Multi-Agent Analysis Details", expanded=True):
                    st.markdown(result["reasoning"])
            else:
                with st.expander("📖 Rule-Based Analysis", expanded=False):
                    st.markdown(result["reasoning"])

            # Case information
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Case ID:** {result['case_id']}")
            with col2:
                st.info(f"**Processed at:** {result['timestamp']}")

            # Store in session state for recent applications
            if "applications" not in st.session_state:
                st.session_state.applications = []
            st.session_state.applications.append(
                {
                    "applicant_id": applicant_id,
                    "decision": result["decision"],
                    "timestamp": result["timestamp"],
                    "risk_score": result["risk_score"],
                }
            )

            st.success("✅ Application processed successfully!")
        else:
            st.error("❌ Failed to process application. Please try again.")


with tab2:
    st.subheader("Recent Applications")

    if "applications" in st.session_state and st.session_state.applications:
        for app in reversed(st.session_state.applications[-10:]):
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                st.write(f"**{app['applicant_id']}**")
            with col2:
                st.write(f"{get_decision_color(app['decision'])} {app['decision']}")
            with col3:
                st.metric("Risk", f"{app['risk_score']:.0%}", label_visibility="collapsed")
            with col4:
                st.caption(app['timestamp'].split("T")[0])
            st.divider()
    else:
        st.info("No recent applications yet. Submit one from the 'New Application' tab.")

st.divider()

# Footer with performance info
st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
### 🚀 Detailed Path (Agentic)
- **Speed:** 420ms (first), 46ms (cached)
- **Agents:** 4 specialized
- **Analysis:** Deep multi-dimensional
    """)
with col2:
    st.markdown("""
### ⚡ Fast Path (Rule-based)
- **Speed:** 39ms
- **Engine:** Deterministic rules
- **Use:** High-volume approvals
    """)
with col3:
    st.markdown("""
### 🏛️ Architecture
- **Orchestration:** LangGraph
- **Model:** Claude Sonnet 4.6
- **MCP Servers:** 4 integrated
    """)

st.markdown(
    """
---
*Multi-Agent Agentic AI powered by Claude | LangGraph Orchestration | MCP Server Integration*
"""
)
