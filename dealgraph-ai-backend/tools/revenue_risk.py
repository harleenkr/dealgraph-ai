def calculate_risk_score(discount: float, payment_terms: str, custom_sla: bool, renewal_risk: str, deal_value: float, contract_term_months: int) -> tuple[float, list]:
    """Provides reusable risk scoring logic. Returns (score, drivers_list)."""
    score = 0.0
    drivers = []
    
    if discount > 30.0:
        score += 40.0
        drivers.append("Discount > 30%")
    elif discount > 25.0:
        score += 20.0
        drivers.append("Discount > 25%")
        
    if "Net 90" in payment_terms:
        score += 15.0
        drivers.append("Net 90 payment terms")
        
    if custom_sla:
        score += 20.0
        drivers.append("Custom SLA requested")
        
    if renewal_risk.lower() == "high":
        score += 20.0
        drivers.append("High renewal risk")
        
    if deal_value > 250000:
        score += 10.0
        drivers.append("Deal value > 250k")
        
    if contract_term_months < 12:
        score += 15.0
        drivers.append("Contract term < 12 months")
        
    return min(100.0, score), drivers
