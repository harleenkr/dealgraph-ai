import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from agents.orchestrator import analyze_deal
from tools.audit_log import log_audit_event
from database import init_db, SessionLocal, EvaluationLog, DealRecord
from agents.redline_agent import generate_redlined_contract
from agents.email_agent import generate_negotiation_email
import os
from fastapi.responses import FileResponse

class DealInput(BaseModel):
    customer_name: str
    industry: str
    country: str
    deal_value: float
    discount_requested: float
    contract_term_months: int
    payment_terms: str
    custom_sla: Optional[bool] = False
    renewal_risk: Optional[str] = "Low"
    region: Optional[str] = "NA"
    sales_stage: Optional[str] = "Negotiation"
    msa_pdf_path: Optional[str] = None

class HITLEvaluationInput(BaseModel):
    deal_id: str
    decision: str
    feedback: str

class DealOutput(BaseModel):
    deal_id: str
    risk_score: float
    recommendation: str
    approval_path: List[str]
    executive_brief: str
    graph: Dict[str, Any]
    evaluation: str
    security_checks: str
    asc606: bool
    agent_trace: List[str]
    audit_log: List[str]

app = FastAPI(
    title="DealGraph AI API",
    description="Multi-Agent Revenue Risk & Approval Assistant",
    version="1.1.0"
)

# Add CORS support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import RedirectResponse

@app.get("/")
def read_root():
    """Redirects to the Swagger API documentation."""
    return RedirectResponse(url="/docs")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    print("Initializing Cloud SQL Database tables...")
    init_db()

@app.get("/sync-salesforce")
def sync_salesforce():
    """Mock endpoint to simulate fetching an opportunity from Salesforce."""
    import random
    opportunities = [
        {"customer_name": "Globex Corp (CRM Sync)", "industry": "Technology", "country": "United States", "deal_value": 1250000, "discount_requested": 40, "contract_term_months": 24, "payment_terms": "Net 60", "custom_sla": True, "renewal_risk": "Medium"},
        {"customer_name": "Initech (CRM Sync)", "industry": "Financial Services", "country": "United Kingdom", "deal_value": 750000, "discount_requested": 15, "contract_term_months": 36, "payment_terms": "Net 30", "custom_sla": False, "renewal_risk": "Low"},
        {"customer_name": "Umbrella Corp (CRM Sync)", "industry": "Healthcare", "country": "Germany", "deal_value": 3000000, "discount_requested": 25, "contract_term_months": 60, "payment_terms": "Net 90", "custom_sla": True, "renewal_risk": "High"}
    ]
    return {"status": "success", "data": random.choice(opportunities)}

@app.post("/analyze-deal", response_model=DealOutput)
def analyze_deal_endpoint(deal: DealInput, db: Session = Depends(get_db)):
    """
    Analyzes a deal, triggering the multi-agent workflow.
    """
    try:
        deal_dict = deal.model_dump()
        # Call the orchestrator agent
        workflow_result = analyze_deal(deal_dict)
        
        # Save the deal evaluation to the database
        try:
            deal_record = DealRecord(
                deal_id=workflow_result["deal_id"],
                customer_name=deal.customer_name,
                industry=deal.industry,
                country=deal.country,
                deal_value=deal.deal_value,
                discount_requested=deal.discount_requested,
                contract_term_months=deal.contract_term_months,
                payment_terms=deal.payment_terms,
                custom_sla=deal.custom_sla,
                renewal_risk=deal.renewal_risk,
                region=deal.region,
                sales_stage=deal.sales_stage,
                risk_score=workflow_result["risk_score"],
                recommendation=workflow_result["recommendation"],
                has_asc606=not workflow_result["asc606"],
                has_gdpr=any("GDPR" in c for c in workflow_result["security_checks"]),
                has_hipaa=any("HIPAA" in c for c in workflow_result["security_checks"]),
                msa_pdf_path=deal.msa_pdf_path,
                knowledge_graph=str(workflow_result.get("graph", "")),
                executive_brief=workflow_result.get("executive_brief", "")
            )
            db.add(deal_record)
            db.commit()
        except Exception as e:
            print("Failed to save DealRecord:", e)
            db.rollback()

        return workflow_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error during analysis: {str(e)}")

@app.post("/submit-evaluation")
def submit_evaluation(eval_data: HITLEvaluationInput):
    """Logs explicit Human-in-the-Loop evaluation into Cloud SQL and BigQuery audit trail."""
    # Save to Cloud SQL Transactional DB
    db = SessionLocal()
    try:
        new_log = EvaluationLog(
            deal_id=eval_data.deal_id,
            decision=eval_data.decision,
            feedback=eval_data.feedback
        )
        db.add(new_log)
        
        # Update the DealRecord so the Analytics dashboard reflects the human decision
        deal_record = db.query(DealRecord).filter(DealRecord.deal_id == eval_data.deal_id).first()
        if deal_record:
            if eval_data.decision.lower() == 'override':
                # If they override an escalation, we assume it's an Approval for analytics
                deal_record.recommendation = 'Approve (Human Override)'
            elif eval_data.decision.lower() == 'approve':
                # If they approve the AI's Approve, it's an Approval. 
                # If they approve the AI's Escalate, we leave it as Escalate (Lost).
                pass
                
        db.commit()
    except Exception as e:
        print(f"DB Error: {e}")
        db.rollback()
    finally:
        db.close()
        
    # Save to BigQuery Analytics
    msg = f"Human Evaluation: {eval_data.decision.upper()} - Feedback: '{eval_data.feedback}'"
    log_audit_event(eval_data.deal_id, "HUMAN_IN_THE_LOOP", msg)
    return {"status": "success", "message": "Evaluation recorded in Database and BigQuery."}

@app.post("/generate-redline")
def redline_endpoint(deal: DealInput):
    """Generates a redlined counter-proposal .docx and returns it."""
    deal_dict = deal.dict()
    deal_dict["id"] = "mock_id"
    try:
        filepath = generate_redlined_contract(deal_dict)
        return FileResponse(path=filepath, filename=os.path.basename(filepath), media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    except Exception as e:
        print(f"Redline error: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/generate-email")
def generate_email_endpoint(deal: DealInput):
    """Generates an automated negotiation email."""
    try:
        deal_dict = deal.model_dump()
        email_body = generate_negotiation_email(deal_dict)
        return {"status": "success", "email": email_body}
    except Exception as e:
        print(f"Email error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """Returns aggregated data for the Historical Analytics dashboard."""
    try:
        # Win/Loss Trend (last 6 months approximation based on sales_stage)
        # Using raw SQL for simplicity in SQLite date extraction
        win_loss_query = db.execute(
            text("SELECT strftime('%Y-%m', created_at) as month, "
                 "SUM(CASE WHEN recommendation LIKE 'Approve%' THEN 1 ELSE 0 END) as won, "
                 "SUM(CASE WHEN recommendation NOT LIKE 'Approve%' THEN 1 ELSE 0 END) as lost "
                 "FROM deal_records GROUP BY month ORDER BY month DESC LIMIT 6")
        ).fetchall()
        
        months_map = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun", 
                      "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}
        
        winLossData = []
        for row in reversed(win_loss_query): # reverse to make it chronological
            if row[0]:
                m_str = row[0].split('-')[1]
                winLossData.append({"month": months_map.get(m_str, m_str), "won": row[1], "lost": row[2]})
        
        # Avg Discount by Industry
        discount_query = db.execute(
            text("SELECT industry, AVG(discount_requested) as avg_discount FROM deal_records GROUP BY industry")
        ).fetchall()
        
        discountData = [{"industry": row[0], "avgDiscount": round(row[1] or 0, 1)} for row in discount_query]
        
        # Compliance Violations
        violations = db.execute(
            text("SELECT SUM(has_asc606), SUM(has_gdpr), SUM(has_hipaa) FROM deal_records")
        ).fetchone()
        
        violationData = [
            {"name": "ASC 606 RevRec", "value": int(violations[0] or 0)},
            {"name": "GDPR Data Residency", "value": int(violations[1] or 0)},
            {"name": "HIPAA Compliance", "value": int(violations[2] or 0)}
        ]
        
        return {
            "status": "success",
            "data": {
                "winLossData": winLossData,
                "discountData": discountData,
                "violationData": violationData
            }
        }
    except Exception as e:
        print(f"Analytics error: {e}")
        return {"status": "error", "message": str(e)}

from fastapi import UploadFile, File
import PyPDF2
import io
import re
import uuid

@app.post("/parse-msa")
async def parse_msa(file: UploadFile = File(...)):
    """Parses an uploaded MSA PDF, saves it, and extracts key deal terms."""
    try:
        contents = await file.read()
        
        # Save the uploaded file
        uploads_dir = "/tmp/uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = os.path.join(uploads_dir, filename)
        with open(filepath, "wb") as f:
            f.write(contents)

        pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        # Simple extraction heuristics
        customer_name = "Extracted Corp"
        customer_match = re.search(r"between\s+DealGraph.*?and\s+([A-Z][a-zA-Z\s]+)(?:\s*\(|\,)", text, flags=re.IGNORECASE | re.DOTALL)
        if customer_match:
            customer_name = customer_match.group(1).replace('\n', ' ').strip()
            
        deal_value = 0.0
        val_match = re.search(r"Deal Value:?\s*\$([\d,]+)", text, re.IGNORECASE)
        if val_match:
            deal_value = float(val_match.group(1).replace(",", ""))
            
        discount = 0.0
        disc_match = re.search(r"Discount:?\s*([\d\.]+)%", text, re.IGNORECASE)
        if disc_match:
            discount = float(disc_match.group(1))
            
        term = 12
        term_match = re.search(r"Term:?\s*(\d+)\s*months", text, re.IGNORECASE)
        if term_match:
            term = int(term_match.group(1))
            
        payment = "Net 30"
        pay_match = re.search(r"Payment Terms:?\s*(Net\s*\d+)", text, re.IGNORECASE)
        if pay_match:
            payment = pay_match.group(1).replace(" ", "-").title()
            
        custom_sla = "custom sla" in text.lower()
        renewal_risk = "high" if "opt-out" in text.lower() else "low"

        industry = "Technology"
        if "healthcare" in text.lower() or "medical" in text.lower():
            industry = "Healthcare"
        elif "finance" in text.lower() or "bank" in text.lower():
            industry = "Financial Services"
        elif "retail" in text.lower() or "shop" in text.lower():
            industry = "Retail"
        elif "manufacturing" in text.lower() or "factory" in text.lower():
            industry = "Manufacturing"

        country = "United States"
        if "united kingdom" in text.lower() or "uk" in text.lower():
            country = "United Kingdom"
        elif "germany" in text.lower():
            country = "Germany"
        elif "japan" in text.lower():
            country = "Japan"
        elif "australia" in text.lower():
            country = "Australia"
        elif "canada" in text.lower():
            country = "Canada"

        return {
            "status": "success",
            "extracted_data": {
                "customer_name": customer_name,
                "industry": industry,
                "country": country,
                "deal_value": deal_value,
                "discount_requested": discount,
                "contract_term_months": term,
                "payment_terms": payment,
                "custom_sla": custom_sla,
                "renewal_risk": renewal_risk.capitalize(),
                "region": "NA",
                "sales_stage": "Legal Review",
                "msa_pdf_path": filepath
            }
        }
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
