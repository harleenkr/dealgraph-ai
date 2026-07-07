import os
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import uuid

# In production, this would be a Cloud SQL Postgres connection string
# We fallback to sqlite for the local hackathon demo
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////tmp/dealgraph.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DealRecord(Base):
    __tablename__ = "deal_records"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    customer_name = Column(String, index=True)
    deal_value = Column(Float)
    discount_requested = Column(Float)
    contract_term_months = Column(Integer)
    payment_terms = Column(String)
    custom_sla = Column(Boolean)
    renewal_risk = Column(String)
    region = Column(String)
    sales_stage = Column(String)
    industry = Column(String, default="Unknown")
    country = Column(String, default="Unknown")
    risk_score = Column(Float, default=0.0)
    recommendation = Column(String, default="Pending")
    has_asc606 = Column(Boolean, default=False)
    has_gdpr = Column(Boolean, default=False)
    has_hipaa = Column(Boolean, default=False)
    msa_pdf_path = Column(String, nullable=True)
    knowledge_graph = Column(String, nullable=True)
    executive_brief = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class EvaluationLog(Base):
    __tablename__ = "evaluation_logs"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    deal_id = Column(String, index=True)
    decision = Column(String)
    feedback = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Safely migrate existing tables by adding columns if they don't exist
    from sqlalchemy import text
    with engine.connect() as conn:
        columns_to_add = [
            "ALTER TABLE deal_records ADD COLUMN industry VARCHAR DEFAULT 'Unknown'",
            "ALTER TABLE deal_records ADD COLUMN country VARCHAR DEFAULT 'Unknown'",
            "ALTER TABLE deal_records ADD COLUMN risk_score FLOAT DEFAULT 0.0",
            "ALTER TABLE deal_records ADD COLUMN recommendation VARCHAR DEFAULT 'Pending'",
            "ALTER TABLE deal_records ADD COLUMN has_asc606 BOOLEAN DEFAULT 0",
            "ALTER TABLE deal_records ADD COLUMN has_gdpr BOOLEAN DEFAULT 0",
            "ALTER TABLE deal_records ADD COLUMN has_hipaa BOOLEAN DEFAULT 0",
            "ALTER TABLE deal_records ADD COLUMN msa_pdf_path VARCHAR",
            "ALTER TABLE deal_records ADD COLUMN knowledge_graph TEXT",
            "ALTER TABLE deal_records ADD COLUMN executive_brief TEXT"
        ]
        for cmd in columns_to_add:
            try:
                conn.execute(text(cmd))
                conn.commit()
            except Exception as e:
                pass

    seed_database()

def seed_database():
    import random
    from datetime import datetime, timedelta
    
    with SessionLocal() as db:
        count = db.query(DealRecord).count()
        if count < 50:
            print("Seeding database with mock historical deals...")
            industries = ["Technology", "Healthcare", "Financial Services", "Retail", "Manufacturing"]
            countries = ["United States", "United Kingdom", "Germany", "Japan", "Australia"]
            recommendations = ["Approve", "Approve", "Approve", "Escalate", "Revise"]
            
            for _ in range(50 - count):
                industry = random.choice(industries)
                # Create a slight bias in discount by industry
                base_discount = 10 if industry == 'Healthcare' or industry == 'Financial Services' else 20
                discount = base_discount + random.uniform(-5, 5)
                
                deal = DealRecord(
                    customer_name=f"Legacy Corp {random.randint(100, 999)}",
                    deal_value=random.uniform(50000, 1000000),
                    discount_requested=discount,
                    contract_term_months=random.choice([12, 24, 36]),
                    payment_terms="Net 30",
                    custom_sla=random.choice([True, False]),
                    renewal_risk=random.choice(["Low", "Medium", "High"]),
                    region="NA",
                    sales_stage="Closed Won" if random.random() > 0.3 else "Closed Lost",
                    industry=industry,
                    country=random.choice(countries),
                    risk_score=random.uniform(20, 90),
                    recommendation=random.choice(recommendations),
                    has_asc606=random.random() > 0.8,
                    has_gdpr=random.random() > 0.85,
                    has_hipaa=random.random() > 0.9,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 180))
                )
                db.add(deal)
            db.commit()
