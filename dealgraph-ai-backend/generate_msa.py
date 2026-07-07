from fpdf import FPDF
import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'MASTER SERVICES AGREEMENT', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_enterprise_msa():
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 11)

    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    
    content = f"""
This Master Services Agreement (this "Agreement") is entered into as of {date_str}, between DealGraph AI ("Provider") and MegaCorp Global ("Customer").

1. SERVICES AND DEAL STRUCTURE
The Provider agrees to provide the AI Governance platform as described in the applicable Order Form.
- Deal Value: $1,250,000
- Term: 36 months
- Discount: 45.0%

2. PAYMENT TERMS
Customer shall pay all undisputed invoices within Net 90 days from the invoice date. Late payments will incur a 1.5% monthly interest penalty.

3. REVENUE RECOGNITION & COMPLIANCE (ASC 606)
This agreement contains a non-standard Opt-Out clause allowing the Customer to terminate without cause within the first 60 days. This Custom SLA requires immediate review by the Deal Desk and Finance to ensure compliance with ASC 606 collectability criteria.

4. DATA GOVERNANCE & SECURITY
Provider shall maintain SOC 2 Type II compliance. All Customer data will be encrypted at rest and in transit. The Customer retains all rights to data processed by the platform.

5. LIABILITY & INDEMNIFICATION
Provider's total aggregate liability shall not exceed the total fees paid by the Customer in the twelve (12) months preceding the claim.

6. SIGNATURES
By signing below, both parties agree to the terms herein.

_________________________
Customer Authorized Signatory
"""
    
    for line in content.split('\n'):
        pdf.multi_cell(0, 8, line)
        
    pdf.output("MegaCorp_Enterprise_MSA.pdf")
    print("Generated MegaCorp_Enterprise_MSA.pdf")

if __name__ == "__main__":
    generate_enterprise_msa()
