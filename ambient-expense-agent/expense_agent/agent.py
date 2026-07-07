import base64
import json
import re
from typing import Any

from google.adk.workflow import Workflow, node
from google.adk.agents import LlmAgent
from google.adk.agents.context import Context
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput

from .config import THRESHOLD_AMOUNT, MODEL_NAME
from .schemas import ExpenseReport, RiskAssessment, ApprovalOutcome

@node
def parse_expense(node_input: Any) -> Event:
    """Parses the incoming event payload.
    The payload contains a 'data' key which could be base64-encoded JSON or plain JSON.
    """
    if hasattr(node_input, 'parts') and node_input.parts:
        # It's a types.Content object from the playground UI
        node_input = node_input.parts[0].text

    if isinstance(node_input, str):
        try:
            node_input = json.loads(node_input)
        except json.JSONDecodeError:
            pass

    if not isinstance(node_input, dict):
        # Handle Content objects from vertexai / google.genai
        if hasattr(node_input, "parts") and node_input.parts:
            data = node_input.parts[0].text
        else:
            data = node_input
    else:
        data = node_input.get("data", node_input)

    print(f"DEBUG parse_expense: node_input={type(node_input)} {node_input}, data={type(data)} {data}")

    if isinstance(data, str):
        try:
            # Try to decode base64
            decoded = base64.b64decode(data).decode('utf-8')
            expense_dict = json.loads(decoded)
        except (ValueError, UnicodeDecodeError):
            # Not base64, assume it's already a JSON string
            try:
                expense_dict = json.loads(data)
            except json.JSONDecodeError:
                expense_dict = data
    else:
        expense_dict = data

    if not isinstance(expense_dict, dict):
        raise ValueError("Parsed data is not a dictionary")

    expense = ExpenseReport(**expense_dict)
    
    # Store expense in state so we have it later, and pass to next node
    return Event(output=expense, state={"expense": expense.model_dump()})

@node
def route_expense(node_input: ExpenseReport) -> Event:
    """Routes the expense based on the dollar amount threshold."""
    if node_input.amount < THRESHOLD_AMOUNT:
        return Event(output=node_input, route="auto_approve")
    else:
        return Event(output=node_input, route="llm_review")

@node
def security_checkpoint(ctx: Context, node_input: ExpenseReport) -> Event:
    """Scrubs PII and checks for prompt injection heuristics."""
    description = node_input.description
    redacted_categories = []
    
    # Scrub SSN
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    if re.search(ssn_pattern, description):
        description = re.sub(ssn_pattern, '[REDACTED_SSN]', description)
        redacted_categories.append('SSN')
        
    # Scrub Credit Card (simplified 13-16 digits with optional spaces/dashes)
    cc_pattern = r'\b(?:\d[ -]*?){13,16}\b'
    if re.search(cc_pattern, description):
        description = re.sub(cc_pattern, '[REDACTED_CC]', description)
        redacted_categories.append('Credit Card')

    node_input.description = description

    # Prompt Injection Heuristics
    injection_keywords = [
        "ignore all previous instructions",
        "bypass rules",
        "auto-approve",
        "force approve",
        "you must approve"
    ]
    
    desc_lower = description.lower()
    injection_detected = any(kw in desc_lower for kw in injection_keywords)

    state_update = {
        "expense": node_input.model_dump(),
        "redacted_categories": redacted_categories
    }

    if injection_detected:
        state_update["security_flag"] = "Prompt Injection Attempt Detected"
        return Event(output=node_input, route="injection_detected", state=state_update)

    return Event(output=node_input, route="clean", state=state_update)

@node
def auto_approve_node(node_input: ExpenseReport) -> Event:
    """Automatically approves the expense."""
    outcome = ApprovalOutcome(
        expense=node_input,
        decision="APPROVED (Auto)",
        risk_assessment=None
    )
    return Event(output=outcome)

risk_review = LlmAgent(
    name="risk_review",
    model=MODEL_NAME,
    instruction="""You are a financial risk reviewer. 
    Analyze the incoming ExpenseReport for potential fraud, policy violations, or unusual activity.
    Assign a risk score of LOW, MEDIUM, or HIGH and provide your reasoning.""",
    output_schema=RiskAssessment,
)

@node(rerun_on_resume=True)
async def human_approval(ctx: Context, node_input: Any):
    """Pauses the workflow for human review if the expense requires it."""
    if not ctx.resume_inputs:
        expense_data = ctx.state.get("expense", {})
        submitter = expense_data.get('submitter', 'Unknown')
        amount = float(expense_data.get('amount', 0.0))
        
        security_flag = ctx.state.get("security_flag")
        redactions = ctx.state.get("redacted_categories", [])
        
        message = ""
        if security_flag:
            message += f"🚨 SECURITY ALERT: {security_flag} 🚨\n"
        
        if redactions:
            message += f"⚠️ Note: {', '.join(redactions)} was redacted from the description.\n"
            
        message += f"Review required for {submitter}'s expense of ${amount:.2f}.\n"
        
        if isinstance(node_input, RiskAssessment):
            message += f"Risk Score: {node_input.risk_score}\nReasoning: {node_input.reasoning}\n"
        else:
            message += f"Description: {expense_data.get('description')}\n"
            
        message += "Please type 'APPROVE' or 'REJECT'."
        
        yield RequestInput(interrupt_id="human_decision", message=message)
        return
    
    decision = ctx.resume_inputs["human_decision"]
    
    output_data = {"decision": decision}
    if isinstance(node_input, RiskAssessment):
        output_data["risk_assessment"] = node_input.model_dump()
        
    yield Event(output=output_data)

@node
def record_outcome(ctx: Context, node_input: Any) -> ApprovalOutcome:
    """Records the final outcome."""
    if isinstance(node_input, ApprovalOutcome):
        return node_input
    
    # Otherwise it's from human_approval which outputs a dict
    expense_data = ctx.state.get("expense", {})
    expense = ExpenseReport(**expense_data)
    decision = node_input.get("decision", "UNKNOWN")
    risk_data = node_input.get("risk_assessment")
    risk_assessment = RiskAssessment(**risk_data) if risk_data else None

    return ApprovalOutcome(
        expense=expense,
        decision=decision,
        risk_assessment=risk_assessment
    )

# Define the Workflow graph
root_agent = Workflow(
    name="expense_approval_workflow",
    edges=[
        ('START', parse_expense),
        (parse_expense, route_expense),
        (route_expense, {
            "auto_approve": auto_approve_node,
            "llm_review": security_checkpoint
        }),
        (security_checkpoint, {
            "clean": risk_review,
            "injection_detected": human_approval
        }),
        (risk_review, human_approval),
        (human_approval, record_outcome),
        (auto_approve_node, record_outcome),
    ],
    description="An ambient workflow for approving or rejecting expenses based on thresholds and risk assessment.",
)
