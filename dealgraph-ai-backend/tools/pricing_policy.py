def get_pricing_policies() -> dict:
    """Returns discount and approval policy rules."""
    return {
        "discount_thresholds": {
            "sales_manager": 15.0,
            "director_sales": 25.0,
            "finance_required_above": 25.0,
            "vp_sales_required_above": 30.0
        },
        "payment_terms_rules": {
            "requires_finance": ["Net 90", "Net 120"]
        },
        "sla_rules": {
            "requires_legal_for_custom": True
        },
        "risk_rules": {
            "requires_executive_above": 70.0
        }
    }
