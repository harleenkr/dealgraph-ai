import os
from google import genai
from google.genai import types

def create_brief(deal_data: dict, risk_assessment: dict, policy_results: dict, recommendation: str) -> str:
    """Executive Brief Agent: Generates a concise summary for decision makers."""
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Extract data for the prompt
    customer = deal_data.get('customer_name', 'Unknown')
    industry = deal_data.get('industry', 'Unknown')
    country = deal_data.get('country', 'Unknown')
    value = deal_data.get('deal_value', 0)
    term = deal_data.get('contract_term_months', 12)
    discount = deal_data.get('discount_requested', 0)
    
    risk_level = risk_assessment.get("risk_level", "Unknown")
    risk_drivers = risk_assessment.get("risk_drivers", [])
    
    violations = policy_results.get("policy_violations", [])
    approvals = policy_results.get("approval_path", [])
    
    prompt = f"""
    Create an executive-ready decision brief for the following deal.
    
    Deal Context:
    - Customer: {customer}
    - Industry: {industry}
    - Country: {country}
    - Value: ${value:,.2f}
    - Term: {term} months
    - Discount Requested: {discount}%
    
    Risk & Compliance:
    - Risk Level: {risk_level}
    - Risk Drivers: {', '.join(risk_drivers) if risk_drivers else 'None'}
    - Policy Violations: {', '.join(violations) if violations else 'None'}
    - Required Human Approvals: {', '.join(approvals) if approvals else 'None'}
    - Final Recommendation: {recommendation}
    
    Requirements:
    1. Include the following sections:
       - Deal summary (mentioning the industry and country implications)
       - Revenue opportunity
       - Key risks (highlighting any specific industry or country regulations like GDPR or HIPAA)
       - Policy violations
       - Approval recommendation
       - Required human approvals
       - Suggested negotiation response
       - Final executive decision
    2. Tone: Director-level, concise, business-focused, trustworthy.
    3. Constraint: Do not make unsupported legal or financial claims. Rely strictly on the provided context.
    """
    
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-pro',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2, # Low temperature for factual, grounded output
                )
            )
            return response.text
        except Exception as e:
            print(f"Executive Brief Agent warning: API failed, using fallback. Error: {e}")
            
    # Fallback template if Gemini is unavailable
    fallback = (
        f"**Deal Summary**: Evaluated {term}-month contract with {customer} (Industry: {industry}, Country: {country}).\n\n"
        f"**Revenue Opportunity**: ${value:,.2f} at a {discount}% discount.\n\n"
        f"**Key Risks**: {risk_level} risk level. Drivers: {', '.join(risk_drivers) if risk_drivers else 'None'}.\n\n"
        f"**Policy Violations**: {', '.join(violations) if violations else 'None'}.\n\n"
        f"**Approval Recommendation**: {recommendation}.\n\n"
        f"**Required Human Approvals**: {', '.join(approvals) if approvals else 'None'}.\n\n"
        f"**Suggested Negotiation Response**: Proceed carefully given the risk profile and required approvals.\n\n"
        f"**Final Executive Decision**: {recommendation} (pending required human sign-offs)."
    )
    return fallback
