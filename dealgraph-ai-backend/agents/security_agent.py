def verify_security(deal_data: dict, risk_score: float = 0.0, approvals: list = None, recommendation: str = "") -> dict:
    """Security Agent: Protects the system from unsafe input and unsafe decisions."""
    
    detected_issues = []
    
    # 1. Prompt Injection Checks
    injection_phrases = [
        "ignore previous instructions",
        "bypass approval",
        "auto approve",
        "delete logs",
        "reveal api key",
        "override policy"
    ]
    
    data_str = str(deal_data).lower()
    for phrase in injection_phrases:
        if phrase in data_str:
            detected_issues.append(f"Prompt injection phrase detected: '{phrase}'")
            
    # 2. Missing Required Fields
    # (Double checking even though intake agent validates, as security is a defense-in-depth layer)
    required = ["customer_name", "deal_value", "discount_requested", "contract_term_months"]
    for field in required:
        if field not in deal_data or deal_data[field] is None:
            detected_issues.append(f"Missing required business field: {field}")
            
    # 3. High-risk deal auto-approval prevention
    approvals = approvals or []
    if risk_score > 70.0:
        if len(approvals) == 0:
            detected_issues.append("Safety Violation: High-risk deal (score > 70) lacks human approval path.")
        
        # Ensure recommendation isn't bypassing human approval
        if "approve" in recommendation.lower() and "conditions" not in recommendation.lower():
            detected_issues.append("Safety Violation: Recommendation bypasses human approval for high-risk deal.")
            
    blocked = len(detected_issues) > 0
    
    if blocked:
        status = "Fail"
        safety_recommendation = "Block transaction immediately and alert security."
    else:
        status = "Pass"
        safety_recommendation = "Input and automated decisions are within safe operational bounds."
        
    return {
        "status": status,
        "detected_issues": detected_issues,
        "safety_recommendation": safety_recommendation,
        "blocked": blocked
    }
