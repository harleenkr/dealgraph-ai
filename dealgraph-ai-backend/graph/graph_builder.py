def build_deal_graph(deal: dict, risk_result: dict, policy_result: dict, recommendation: str) -> dict:
    """Builds a structured knowledge graph for frontend visualization."""
    nodes = []
    edges = []
    
    def add_node(node_id: str, label: str, node_type: str, risk_level: str = "Low") -> str:
        # Create stable, frontend-friendly IDs
        stable_id = node_id.lower().replace(" ", "_").replace(":", "").replace("$", "").replace(",", "")
        if not any(n["id"] == stable_id for n in nodes):
            nodes.append({"id": stable_id, "label": label, "type": node_type, "riskLevel": risk_level})
        return stable_id
            
    def add_edge(source: str, target: str, label: str):
        edges.append({"source": source, "target": target, "label": label})

    # Base Deal Nodes
    customer_label = deal.get("customer_name", "Unknown Customer")
    deal_label = deal.get("deal_id", "Deal")
    
    customer_id = add_node(f"customer_{customer_label}", customer_label, "Customer", "Low")
    deal_id = add_node(f"deal_{deal_label}", deal_label, "Deal", risk_result.get("risk_level", "Low"))
    add_edge(customer_id, deal_id, "requests")
    
    # Value & Discount
    deal_val_label = f"Value: ${deal.get('deal_value', 0):,.2f}"
    discount_label = f"Discount: {deal.get('discount_requested', 0)}%"
    
    val_id = add_node("metric_value", deal_val_label, "Metric", "Low")
    disc_id = add_node("metric_discount", discount_label, "Metric", "High" if deal.get("discount_requested", 0) > 25 else "Medium")
    
    add_edge(deal_id, val_id, "has_value")
    add_edge(deal_id, disc_id, "contains")
    
    # Conditions
    terms_label = f"Terms: {deal.get('payment_terms', 'Standard')}"
    terms_id = add_node("condition_terms", terms_label, "Condition", "High" if "Net 90" in terms_label else "Low")
    add_edge(deal_id, terms_id, "has_terms")
    
    if "Net 90" in terms_label:
        cash_risk_id = add_node("risk_cash_flow", "Cash Flow Risk", "Risk", "High")
        add_edge(terms_id, cash_risk_id, "creates")

    if deal.get("custom_sla"):
        sla_id = add_node("condition_sla", "Custom SLA", "Condition", "Medium")
        add_edge(deal_id, sla_id, "contains")
        legal_id = add_node("process_legal", "Legal Review", "Process", "High")
        add_edge(sla_id, legal_id, "requires")
        
    renewal_label = f"Renewal Risk: {deal.get('renewal_risk', 'Low')}"
    renewal_risk_val = str(deal.get('renewal_risk', 'Low')).capitalize()
    renewal_id = add_node("condition_renewal", renewal_label, "Condition", renewal_risk_val if renewal_risk_val in ["Low", "Medium", "High", "Critical"] else "Low")
    add_edge(deal_id, renewal_id, "has_risk")

    # Risk Agent
    risk_level = risk_result.get("risk_level", "Low")
    risk_node_label = f"Revenue Risk: {risk_level}"
    risk_node_id = add_node("risk_revenue", risk_node_label, "Risk", risk_level)
    add_edge(deal_id, risk_node_id, "assessed_as")

    # Policy Agent
    last_violation_id = None
    for violation in policy_result.get("policy_violations", []):
        viol_id = add_node(f"violation_{violation[:15]}", violation, "Violation", "High")
        add_edge(deal_id, viol_id, "violates_policy")
        last_violation_id = viol_id
        
    approvals = policy_result.get("approval_path", [])
    if approvals:
        for approver in approvals:
            owner_id = add_node(f"owner_{approver}", approver, "Owner", "Medium")
            add_edge(deal_id, owner_id, "requires_approval_from")
            if last_violation_id:
                add_edge(last_violation_id, owner_id, "escalates_to")

    # Recommendation
    rec_id = add_node("recommendation", recommendation, "Recommendation", "Critical" if recommendation == "Escalate" else "Low")
    add_edge(deal_id, rec_id, "results_in")

    return {
        "nodes": nodes,
        "edges": edges
    }
