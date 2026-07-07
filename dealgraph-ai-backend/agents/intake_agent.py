import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json
import uuid
from database import SessionLocal, DealRecord

async def fetch_crm_mcp(customer_name: str):
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                crm = await session.call_tool("get_customer_history", arguments={"customer_name": customer_name})
                docusign = await session.call_tool("check_docusign_status", arguments={"customer_name": customer_name})
                zendesk = await session.call_tool("check_zendesk_health", arguments={"customer_name": customer_name})
                
                result_dict = json.loads(crm.content[0].text)
                result_dict.update(json.loads(docusign.content[0].text))
                result_dict.update(json.loads(zendesk.content[0].text))
                return json.dumps(result_dict)
    except Exception as e:
        return json.dumps({"status": "Error", "message": str(e)})

def process_intake(deal_data: dict) -> tuple[dict, str]:
    """Intake Agent: Validates deal, saves to Cloud SQL, fetches CRM data via MCP."""
    
    cleaned_deal = deal_data.copy()
    missing_fields = []
    
    # Required fields check
    required = ["customer_name", "deal_value", "discount_requested", "contract_term_months"]
    for field in required:
        if field not in cleaned_deal or cleaned_deal[field] is None:
            missing_fields.append(field)
            
    # Number conversion
    try:
        cleaned_deal["deal_value"] = float(cleaned_deal.get("deal_value", 0))
    except (ValueError, TypeError):
        cleaned_deal["deal_value"] = 0.0
        missing_fields.append("deal_value_invalid")
        
    try:
        cleaned_deal["discount_requested"] = float(cleaned_deal.get("discount_requested", 0))
    except (ValueError, TypeError):
        cleaned_deal["discount_requested"] = 0.0
        missing_fields.append("discount_requested_invalid")
        
    try:
        cleaned_deal["contract_term_months"] = int(cleaned_deal.get("contract_term_months", 0))
    except (ValueError, TypeError):
        cleaned_deal["contract_term_months"] = 0
        missing_fields.append("contract_term_invalid")

    # Normalization
    if "payment_terms" in cleaned_deal and isinstance(cleaned_deal["payment_terms"], str):
        cleaned_deal["payment_terms"] = cleaned_deal["payment_terms"].strip().title()
    
    if "renewal_risk" in cleaned_deal and isinstance(cleaned_deal["renewal_risk"], str):
        cleaned_deal["renewal_risk"] = cleaned_deal["renewal_risk"].strip().capitalize()
        
    if "region" in cleaned_deal and isinstance(cleaned_deal["region"], str):
        cleaned_deal["region"] = cleaned_deal["region"].strip().upper()
        
    if "sales_stage" in cleaned_deal and isinstance(cleaned_deal["sales_stage"], str):
        cleaned_deal["sales_stage"] = cleaned_deal["sales_stage"].strip().capitalize()

    # Save to Cloud SQL Database
    db = SessionLocal()
    deal_uuid = str(uuid.uuid4())
    try:
        new_deal_record = DealRecord(
            id=deal_uuid,
            customer_name=cleaned_deal.get("customer_name", "Unknown"),
            deal_value=cleaned_deal["deal_value"],
            discount_requested=cleaned_deal["discount_requested"],
            contract_term_months=cleaned_deal["contract_term_months"],
            payment_terms=cleaned_deal.get("payment_terms", "Net-30"),
            custom_sla=cleaned_deal.get("custom_sla", False),
            renewal_risk=cleaned_deal.get("renewal_risk", "Low"),
            region=cleaned_deal.get("region", "NA"),
            sales_stage=cleaned_deal.get("sales_stage", "Negotiation")
        )
        db.add(new_deal_record)
        db.commit()
    except Exception as e:
        print(f"Failed to save deal to SQL DB: {e}")
    finally:
        db.close()

    summary = ""
    # Fetch external data using MCP Server
    customer = cleaned_deal.get("customer_name")
    if customer:
        mcp_result = asyncio.run(fetch_crm_mcp(customer))
        try:
            crm_data = json.loads(mcp_result)
            cleaned_deal["crm_data"] = crm_data
            if crm_data.get("historical_churn_risk"):
                summary += f"MCP Server connected. Salesforce CRM data loaded for {customer}. "
            else:
                summary += f"MCP Server connected. No historical Salesforce data for {customer}. "
        except Exception:
            summary += "MCP Server connection failed. "
            cleaned_deal["crm_data"] = {}
    
    # Summary Generation
    if missing_fields:
        summary += f"Intake warnings. Missing fields: {', '.join(missing_fields)}."
    else:
        summary += "Core intake completed successfully. Deal saved to Cloud SQL."

    return cleaned_deal, summary
