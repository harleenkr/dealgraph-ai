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
    pdf.set_font('Arial', '', 10)

    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    
    content = f"""This Master Services Agreement (this "Agreement") is entered into as of {date_str}, between DealGraph AI ("Provider") and MegaCorp Global ("Customer").

1. SERVICES AND DEAL STRUCTURE
1.1 Provision of Services. The Provider agrees to provide the AI Governance platform, including all associated software, documentation, and support services (collectively, the "Services"), as described in the applicable Order Form and subject to the terms of this Agreement.
1.2 Deal Value: $4,500,000
1.3 Term: 48 months
1.4 Discount: 35.0%
1.5 License Grant. Subject to Customer's compliance with this Agreement, Provider grants Customer a limited, non-exclusive, non-transferable right to access and use the Services for its internal business operations during the Term.

2. PAYMENT TERMS
2.1 Invoicing. Provider will invoice Customer in accordance with the billing frequency specified in the Order Form.
2.2 Payment. Customer shall pay all undisputed invoices within Net 30 days from the invoice date. Late payments will incur a 1.5% monthly interest penalty.
2.3 Taxes. Fees are exclusive of all taxes, levies, or duties imposed by taxing authorities. Customer shall be responsible for payment of all such taxes, excluding only United States taxes based solely on Provider's income.
2.4 Disputed Charges. If Customer reasonably disputes any charge in good faith, Customer must notify Provider in writing within thirty (30) days of the invoice date.

3. REVENUE RECOGNITION & COMPLIANCE (ASC 606)
3.1 Non-Standard Term. This agreement contains a non-standard Opt-Out clause allowing the Customer to terminate without cause within the first 60 days. This Custom SLA requires immediate review by the Deal Desk and Finance to ensure compliance with ASC 606 collectability criteria.
3.2 Allocation of Transaction Price. The transaction price allocated to the performance obligations under this Agreement shall be determined in accordance with ASC 606 principles.
3.3 Milestone Payments. Any milestone-based payments must represent the transfer of control of goods or services to the Customer.

4. DATA GOVERNANCE & SECURITY
4.1 SOC 2 Compliance. Provider shall maintain SOC 2 Type II compliance and provide a copy of the annual audit report upon written request.
4.2 Encryption. All Customer data will be encrypted at rest (using AES-256) and in transit (using TLS 1.2 or higher).
4.3 Data Ownership. The Customer retains all rights to data processed by the platform. Provider shall not use Customer Data except to provide the Services.
4.4 Breach Notification. Provider will notify Customer without undue delay (and in no event later than 48 hours) upon becoming aware of any confirmed Data Breach affecting Customer Data.

5. LIABILITY & INDEMNIFICATION
5.1 Limitation of Liability. Provider's total aggregate liability shall not exceed the total fees paid by the Customer in the twelve (12) months preceding the claim.
5.2 Exclusion of Consequential Damages. In no event shall either party be liable for any indirect, incidental, special, or consequential damages.
5.3 Indemnification. Provider shall defend, indemnify, and hold harmless Customer from any claims alleging that the Services infringe any third-party intellectual property rights.

6. CONFIDENTIALITY
6.1 Definition. "Confidential Information" means any non-public information disclosed by one party to the other party.
6.2 Protection. The receiving party agrees to protect the disclosing party's Confidential Information with the same degree of care it uses to protect its own.

7. TERMINATION
7.1 Termination for Cause. Either party may terminate this Agreement if the other party materially breaches this Agreement and fails to cure such breach within thirty (30) days of receipt of written notice.
7.2 Effect of Termination. Upon termination, Customer's right to use the Services shall immediately cease, and Provider will delete all Customer Data within sixty (60) days.

8. GENERAL PROVISIONS
8.1 Governing Law. This Agreement shall be governed by the laws of the State of Delaware, without regard to its conflict of laws principles.
8.2 Entire Agreement. This Agreement constitutes the entire agreement between the parties and supersedes all prior agreements.
8.3 Severability. If any provision is held invalid, the remainder of this Agreement shall continue in full force and effect.

SIGNATURES
By signing below, both parties agree to the terms herein.

_________________________
Customer Authorized Signatory
Name: 
Title: 
Date: 

_________________________
Provider Authorized Signatory
Name: 
Title: 
Date: 
"""
    
    for line in content.split('\n'):
        if line.strip() == "":
            pdf.ln(5)
        else:
            pdf.multi_cell(0, 6, line)
        
    pdf.output("MegaCorp_Enterprise_MSA_Dense.pdf")
    print("Generated MegaCorp_Enterprise_MSA_Dense.pdf")

if __name__ == "__main__":
    generate_enterprise_msa()
