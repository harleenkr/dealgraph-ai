def get_approval_owners(discount: float, payment_terms: str, custom_sla: bool, renewal_risk: str, risk_score: float) -> list:
    """Returns approval owners based on deal parameters."""
    owners = set()
    
    if discount <= 15.0:
        owners.add("Sales Manager")
    elif discount <= 25.0:
        owners.add("Director Sales")
        
    if discount > 25.0:
        owners.add("Finance")
    if discount > 30.0:
        owners.add("VP Sales")
        
    if "Net 90" in payment_terms:
        owners.add("Finance")
        
    if custom_sla:
        owners.add("Legal")
        
    if renewal_risk.lower() == "high":
        owners.add("Customer Success")
        
    if risk_score > 70.0:
        owners.add("Executive")
        
    return sorted(list(owners))
