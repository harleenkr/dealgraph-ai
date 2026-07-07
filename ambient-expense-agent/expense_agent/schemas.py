from pydantic import BaseModel, Field

class ExpenseReport(BaseModel):
    amount: float
    submitter: str
    category: str
    description: str
    date: str

class RiskAssessment(BaseModel):
    risk_score: str = Field(description="The level of risk: LOW, MEDIUM, or HIGH.")
    reasoning: str = Field(description="Explanation for the assigned risk score.")

class ApprovalOutcome(BaseModel):
    expense: ExpenseReport
    decision: str
    risk_assessment: RiskAssessment | None = None
