def assess_risk(deal_data: dict) -> dict:
    """Revenue Risk Agent: Calculates revenue and commercial risk based on deal parameters."""
    
    score = 0.0
    drivers = []
    
    discount = deal_data.get("discount_requested", 0.0)
    payment_terms = deal_data.get("payment_terms", "")
    custom_sla = deal_data.get("custom_sla", False)
    renewal_risk = deal_data.get("renewal_risk", "Low")
    deal_value = deal_data.get("deal_value", 0.0)
    contract_term = deal_data.get("contract_term_months", 12)
    industry = deal_data.get("industry", "")
    country = deal_data.get("country", "")
    
    # 1. Discount Risk
    if discount > 30.0:
        score += 40.0
        drivers.append("Discount above 30% is high risk.")
    elif discount > 25.0:
        score += 20.0
        drivers.append("Discount above 25% increases margin risk.")
        
    # 2. Payment Terms Risk
    if "Net 90" in payment_terms:
        score += 15.0
        drivers.append("Net 90 payment terms increase cash flow risk.")
        
    # 3. Custom SLA Risk
    if custom_sla:
        score += 20.0
        drivers.append("Custom SLA increases delivery and legal risk.")
        
    # 4. Renewal Risk
    if renewal_risk.lower() == "high":
        score += 20.0
        drivers.append("High renewal risk increases account churn probability.")
        
    # 5. Deal Value Complexity
    if deal_value > 250000:
        score += 10.0
        drivers.append("Deal value > 250k increases approval and execution complexity.")
        
    # 6. Contract Term
    if contract_term < 12:
        score += 15.0
        drivers.append("Contract term under 12 months increases renewal risk.")
        
    # 7. Industry & Country Compliance Risk
    if industry == "Healthcare" or industry == "Financial Services":
        score += 15.0
        drivers.append(f"Highly regulated industry ({industry}) increases compliance risk (e.g. HIPAA/SEC).")
        
    if country == "Germany" or country == "United Kingdom":
        score += 10.0
        drivers.append(f"European country ({country}) requires strict GDPR data residency commitments.")
        
    # V2 Roadmap: ASC 606 Revenue Recognition Compliance
    asc_606_compliant = True
    if custom_sla and "opt-out" in renewal_risk.lower():
        score += 30.0
        drivers.append("CRITICAL COMPLIANCE: Custom SLA with opt-out triggers ASC 606 revenue deferral.")
        asc_606_compliant = False
    elif "90" in payment_terms:
        drivers.append("WARNING: Extended payment terms may require ASC 606 collectability assessment.")
        asc_606_compliant = False

    # Cap score
    score = min(100.0, score)
    
    # Determine Risk Level
    if score >= 75:
        level = "Critical"
    elif score >= 50:
        level = "High"
    elif score >= 25:
        level = "Medium"
    else:
        level = "Low"
        
    # Revenue Exposure (heuristic: risk % of deal value)
    exposure = deal_value * (score / 100.0)
    
    financial_summary = f"Total Value: ${deal_value:,.2f}, Discount: {discount}%, Term: {contract_term} mos. Risk Exposure: ${exposure:,.2f}"
    
    return {
        "risk_score": score,
        "risk_level": level,
        "risk_drivers": drivers,
        "revenue_exposure": exposure,
        "financial_summary": financial_summary,
        "asc_606_compliant": asc_606_compliant
    }
