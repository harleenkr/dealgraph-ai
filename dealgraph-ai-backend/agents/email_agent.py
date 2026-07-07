import os
from google import genai
from google.genai import types

def generate_negotiation_email(deal_data: dict) -> str:
    """Agent that drafts a negotiation email to the customer."""
    api_key = os.getenv("GEMINI_API_KEY")
    
    customer = deal_data.get('customer_name', 'Customer')
    discount = deal_data.get('discount_requested', 0)
    
    prompt = f"""
    Write a professional, enterprise-grade negotiation email to the procurement team at {customer}.
    
    Context:
    They requested a {discount}% discount, which violates our pricing policy and has been flagged by our deal desk.
    We are attaching a redlined counter-proposal (Amended Draft) that offers a more reasonable compromise.
    
    Requirements:
    1. Start the email addressing the "{customer} Procurement Team,".
    2. Use the phrase: "Thanks for your strategic alliance." instead of standard greetings.
    3. State: "We have reviewed your recent request for a {discount}% discount. Unfortunately, this exceeds our standard policy thresholds and cannot be approved in its current form."
    4. Follow up with: "However, we remain dedicated to finding a mutually beneficial agreement. We have attached an Amended Draft that outlines a compromise we can fully support."
    5. Conclude with: "Please review the attached document and let us know if you have any questions."
    6. Sign off exactly as: "Best regards,\n\nDealGraph AI Automated Negotiator".
    7. Do not include any other placeholders or text.
    """
    
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-pro',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                )
            )
            return response.text
        except Exception as e:
            print(f"Email Agent warning: API failed, using fallback. Error: {e}")
            
    # Fallback template
    return (
        f"{customer} Procurement Team,\n\n"
        f"Thanks for your strategic alliance. We have reviewed your recent request for a {discount}% discount. "
        f"Unfortunately, this exceeds our standard policy thresholds and cannot be approved in its current form.\n\n"
        f"However, we remain dedicated to finding a mutually beneficial agreement. "
        f"We have attached an Amended Draft that outlines a compromise we can fully support.\n\n"
        f"Please review the attached document and let us know if you have any questions.\n\n"
        f"Best regards,\n\n"
        f"DealGraph AI Automated Negotiator"
    )
