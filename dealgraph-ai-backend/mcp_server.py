from mcp.server.fastmcp import FastMCP
import json

# Initialize the MCP Server
mcp = FastMCP("Salesforce CRM Mock")

# Mock database of external CRM data
CUSTOMER_DATA = {
    "Acme Corp": {
        "historical_churn_risk": "High",
        "previous_deals_count": 3,
        "active_escalations": True,
        "notes": "Customer has threatened to churn twice in the last year over SLA disputes."
    },
    "Globex": {
        "historical_churn_risk": "Low",
        "previous_deals_count": 12,
        "active_escalations": False,
        "notes": "Highly satisfied enterprise customer."
    }
}

@mcp.tool()
def check_docusign_status(customer_name: str) -> str:
    """Check if a customer has a verified DocuSign signer setup."""
    customer = customer_name.lower()
    if "acme" in customer:
        return json.dumps({"docusign_verified": True, "signer": "vp_engineering@acme.corp"})
    return json.dumps({"docusign_verified": False})

@mcp.tool()
def check_zendesk_health(customer_name: str) -> str:
    """Check Zendesk support ticket health for a customer."""
    customer = customer_name.lower()
    if "acme" in customer:
        return json.dumps({"open_critical_tickets": 2, "health_score": 65})
    return json.dumps({"open_critical_tickets": 0, "health_score": 100})

@mcp.tool()
def get_customer_history(customer_name: str) -> str:
    """Retrieve historical CRM data for a given customer to assess long-term risk."""
    print(f"[MCP SERVER] Received request for customer: {customer_name}")
    data = CUSTOMER_DATA.get(customer_name)
    if not data:
        return json.dumps({"status": "Not Found", "message": f"No historical data for {customer_name}."})
    return json.dumps(data)

if __name__ == "__main__":
    mcp.run(transport="stdio")
