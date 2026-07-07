from pydantic import BaseModel
from typing import List, Optional, Any

class Product(BaseModel):
    name: str
    quantity: int
    list_price: float
    discount_percentage: float
    final_price: float

class Deal(BaseModel):
    deal_id: str
    account_name: str
    opportunity_owner: str
    total_value: float
    currency: str
    products: List[Product]
    payment_terms: str
    contract_length_months: int
    special_conditions: str

class AnalysisResult(BaseModel):
    deal_id: str
    executive_summary: str
    risk_assessment: str
    policy_violations: List[str]
    required_approvals: List[str]
    knowledge_graph: dict
    confidence_score: float
    security_flag: bool
