def evaluate_policy(deal_data: dict, risk_score: float) -> dict:
    """Policy Agent: Checks business policy and approval requirements."""
    
    violations = []
    approvals = set()
    
    discount = deal_data.get("discount_requested", 0.0)
    
    # Discount rules
    if discount <= 15.0:
        approvals.add("Sales Manager")
    elif discount <= 25.0:
        approvals.add("Director Sales")
        
    if discount > 25.0:
        approvals.add("Finance")
        violations.append("Discount exceeds 25%.")
        
    if discount > 30.0:
        approvals.add("VP Sales")
        violations.append("Discount exceeds 30% policy limit.")
        
    # Payment Terms
    payment_terms = deal_data.get("payment_terms", "")
    if "Net 90" in payment_terms:
        approvals.add("Finance")
        violations.append("Extended payment terms (Net 90) requested.")
        
    # Custom SLA
    if deal_data.get("custom_sla"):
        approvals.add("Legal")
        violations.append("Custom SLA requested.")
        
    # Renewal Risk
    renewal_risk = deal_data.get("renewal_risk", "Low")
    if renewal_risk.lower() == "high":
        approvals.add("Customer Success")
        
    # Risk Score
    if risk_score > 70:
        approvals.add("Executive")
        violations.append(f"Risk score > 70 ({risk_score}) triggered executive escalation.")
        
    approval_path = sorted(list(approvals))
    human_approval_required = len(approval_path) > 0
    
    if len(approval_path) > 2:
        recommendation = "Complex approval chain required. Plan for extended review."
    elif len(approval_path) > 0:
        recommendation = f"Approvals required from: {', '.join(approval_path)}."
    else:
        recommendation = "Auto-approve. No human approval required."
        
    return {
        "policy_violations": violations,
        "approval_path": approval_path,
        "human_approval_required": human_approval_required,
        "approval_recommendation": recommendation
    }
