def get_customer_profile(customer_name: str) -> dict:
    """Returns a mock customer profile based on customer_name."""
    name_lower = customer_name.lower()
    
    profiles = {
        "acme corp": {
            "customer_name": "Acme Corp",
            "industry": "Manufacturing",
            "tier": "Enterprise",
            "health_score": 85,
            "status": "Green"
        },
        "globex": {
            "customer_name": "Globex",
            "industry": "Technology",
            "tier": "Mid-Market",
            "health_score": 40,
            "status": "Red"
        }
    }
    
    return profiles.get(name_lower, {
        "customer_name": customer_name,
        "industry": "Unknown",
        "tier": "Standard",
        "health_score": 50,
        "status": "Yellow"
    })
