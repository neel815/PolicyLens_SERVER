"""
Generate sample insurance policy PDFs for testing
These PDFs contain all required insurance keywords for validation:
- premium
- claim
- coverage
- insured
- policy number
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
import os

def create_health_insurance_pdf():
    """Create a sample health insurance policy PDF"""
    filename = "test_pdfs/SAMPLE_Health_Insurance_Policy.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1A3FBE'),
        spaceAfter=12,
        alignment=1  # Center
    )
    
    story.append(Paragraph("HEALTH INSURANCE POLICY DOCUMENT", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Policy details
    details = f"""
    <b>Policy Number:</b> HEALTH-POL-2026-001234<br/>
    <b>Insured Name:</b> John Robert Smith<br/>
    <b>Policy Period:</b> 01-April-2026 to 31-March-2027<br/>
    <b>Premium Amount:</b> ₹8,500 per annum<br/>
    <b>Date of Issue:</b> 01-April-2024<br/>
    """
    story.append(Paragraph(details, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Coverage details
    coverage_text = """
    <b>COVERAGE SUMMARY</b><br/>
    This health insurance policy provides comprehensive coverage for hospitalization and medical expenses. 
    The insured is entitled to claim reimbursement for eligible medical treatments and procedures.
    <br/><br/>
    <b>Sum Insured:</b> ₹5,00,000 per policy year<br/>
    <b>Coverage includes:</b><br/>
    • Hospitalization for 24 hours or more<br/>
    • Pre-hospitalization expenses (30 days before admission)<br/>
    • Post-hospitalization expenses (60 days after discharge)<br/>
    • Day-care procedures and surgeries<br/>
    • Ambulance charges up to ₹2,000<br/>
    • Organ donor treatment costs<br/>
    """
    story.append(Paragraph(coverage_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Premium payment
    premium_text = """
    <b>PREMIUM PAYMENT TERMS</b><br/>
    Annual Premium: ₹8,500<br/>
    Premium Payment Mode: Annual/Monthly<br/>
    Due Date: On or before the expiry date of previous policy period<br/>
    """
    story.append(Paragraph(premium_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Claims
    claims_text = """
    <b>CLAIM PROCEDURE</b><br/>
    To claim benefits under this policy:<br/>
    1. Notify the insurance company within 48 hours of hospitalization<br/>
    2. Submit claim form along with supporting medical documents<br/>
    3. Insurance company will process the claim within 30 days<br/>
    4. Claim will be settled through reimbursement or direct payment to hospital<br/>
    """
    story.append(Paragraph(claims_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Exclusions
    exclusions_text = """
    <b>EXCLUSIONS</b><br/>
    The following are not covered under this policy:<br/>
    • Pre-existing conditions for first 24 months<br/>
    • Cosmetic or plastic surgery<br/>
    • Self-inflicted injuries<br/>
    • Dental treatment (unless accident-related)<br/>
    • Experimental or unproven treatments<br/>
    • Treatment related to alcohol or drug abuse<br/>
    """
    story.append(Paragraph(exclusions_text, styles['Normal']))
    
    doc.build(story)
    print(f"✓ Created: {filename}")


def create_vehicle_insurance_pdf():
    """Create a sample vehicle/motor insurance policy PDF"""
    filename = "test_pdfs/SAMPLE_Vehicle_Insurance_Policy.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1A3FBE'),
        spaceAfter=12,
        alignment=1
    )
    
    story.append(Paragraph("MOTOR VEHICLE INSURANCE POLICY", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Policy details
    details = """
    <b>Policy Number:</b> MOTOR-POL-2026-005678<br/>
    <b>Insured:</b> Sarah Elizabeth Johnson<br/>
    <b>Vehicle:</b> 2023 Honda Civic, Registration: DL01AB1234<br/>
    <b>Premium:</b> ₹12,000 per annum<br/>
    <b>Policy Period:</b> 01-April-2026 to 31-March-2027<br/>
    """
    story.append(Paragraph(details, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    coverage_text = """
    <b>COVERAGE DETAILS</b><br/>
    This comprehensive motor vehicle insurance policy provides coverage for damage, theft, and third-party liability.
    <br/><br/>
    <b>Insured Vehicle Declared Value:</b> ₹18,50,000<br/>
    <b>Coverage Includes:</b><br/>
    • Own damage coverage - Full replacement value<br/>
    • Third-party liability coverage - Up to ₹1,00,000<br/>
    • Theft and total loss coverage<br/>
    • Accidental damage to vehicle<br/>
    • Personal accident cover for driver - ₹10,00,000<br/>
    • No Claim Bonus protection<br/>
    """
    story.append(Paragraph(coverage_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    premium_text = """
    <b>PREMIUM DETAILS</b><br/>
    Annual Premium (including GST): ₹12,000<br/>
    Premium Payment Frequency: Annual preferred<br/>
    Premium Due Date: Annually on policy renewal date<br/>
    """
    story.append(Paragraph(premium_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    claims_text = """
    <b>CLAIM SETTLEMENT PROCESS</b><br/>
    For vehicle damage claim or if insured vehicle is involved in accident:<br/>
    1. Report the accident and file claim within 30 days<br/>
    2. Provide police FIR (for theft), photographs, and repair quotation<br/>
    3. Our surveyor will inspect the vehicle<br/>
    4. Claim settlement within 45 days of complete documentation<br/>
    """
    story.append(Paragraph(claims_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    exclusions_text = """
    <b>EXCLUSIONS FROM COVERAGE</b><br/>
    This policy does not cover:<br/>
    • Damage while racing or speed testing<br/>
    • Mechanical or electrical breakdown<br/>
    • Wear and tear or depreciation<br/>
    • Driving under influence of alcohol or drugs<br/>
    • Use of vehicle for commercial hire (unless specified)<br/>
    • War, civil unrest, or terrorism damage<br/>
    """
    story.append(Paragraph(exclusions_text, styles['Normal']))
    
    doc.build(story)
    print(f"✓ Created: {filename}")


def create_life_insurance_pdf():
    """Create a sample life insurance policy PDF"""
    filename = "test_pdfs/SAMPLE_Life_Insurance_Policy.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1A3FBE'),
        spaceAfter=12,
        alignment=1
    )
    
    story.append(Paragraph("TERM LIFE INSURANCE POLICY", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    details = """
    <b>Policy Number:</b> LIFE-POL-2026-009012<br/>
    <b>Insured Name:</b> Michael David Chen<br/>
    <b>Age at Issue:</b> 35 years<br/>
    <b>Policy Term:</b> 20 years (Up to age 55)<br/>
    <b>Annual Premium:</b> ₹24,500<br/>
    <b>Commencement Date:</b> 01-April-2026<br/>
    """
    story.append(Paragraph(details, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    coverage_text = """
    <b>COVERAGE AND BENEFITS</b><br/>
    This term life insurance policy provides financial protection to beneficiaries in case of death of the insured person.
    <br/><br/>
    <b>Sum Assured (Death Benefit):</b> ₹50,00,000<br/>
    <b>Coverage Type:</b> Pure protection with no maturity benefit<br/>
    <b>Benefits Include:</b><br/>
    • Death claim - Full sum assured paid to nominees<br/>
    • Critical illness benefit - ₹25,00,000 (optional rider)<br/>
    • Premium waiver on disability<br/>
    • Death benefit continues even after premium payment period<br/>
    • No medical underwriting if claim within first 24 months<br/>
    """
    story.append(Paragraph(coverage_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    premium_text = """
    <b>PREMIUM PAYMENT SCHEDULE</b><br/>
    Monthly Premium: ₹2,040 (if monthly payment mode selected)<br/>
    Annual Premium: ₹24,500<br/>
    Premium payment due: On or before 30 days of each policy anniversary<br/>
    Grace period: 30 days for premium payment<br/>
    """
    story.append(Paragraph(premium_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    claims_text = """
    <b>CLAIM PROCEDURE FOR DEATH</b><br/>
    In case of death of the insured person:<br/>
    1. Notify insurance company and file claim within 90 days<br/>
    2. Submit original policy document and death certificate<br/>
    3. Company will verify and settle claim within 30 days<br/>
    4. Death benefit will be paid to nominated beneficiaries<br/>
    5. Multiple claims can be filed under rider benefits<br/>
    """
    story.append(Paragraph(claims_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    exclusions_text = """
    <b>POLICY EXCLUSIONS</b><br/>
    The policy excludes coverage in following circumstances:<br/>
    • Death within 6 months of policy issue due to non-disclosure of health facts<br/>
    • Suicide within first 12 months of policy inception<br/>
    • Death due to unlawful activities or criminal acts<br/>
    • Death due to extreme sports or hazardous activities<br/>
    • Death due to war, terrorism, or civil unrest<br/>
    • Claims if premium not paid within grace period<br/>
    """
    story.append(Paragraph(exclusions_text, styles['Normal']))
    
    doc.build(story)
    print(f"✓ Created: {filename}")


if __name__ == "__main__":
    # Check if reportlab is installed
    try:
        create_health_insurance_pdf()
        create_vehicle_insurance_pdf()
        create_life_insurance_pdf()
        print("\n✅ All sample insurance PDFs created successfully!")
        print("📁 Location: test_pdfs/")
        print("\nGenerated files:")
        for file in os.listdir("test_pdfs"):
            filepath = os.path.join("test_pdfs", file)
            size = os.path.getsize(filepath) / 1024
            print(f"   • {file} ({size:.1f} KB)")
    except ImportError:
        print("❌ reportlab not installed. Installing...")
        import subprocess
        subprocess.check_call(["pip", "install", "reportlab"])
        print("✓ reportlab installed. Running script again...")
        create_health_insurance_pdf()
        create_vehicle_insurance_pdf()
        create_life_insurance_pdf()
        print("\n✅ All sample insurance PDFs created successfully!")
