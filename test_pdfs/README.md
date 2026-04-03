# Sample Insurance PDFs for Testing

This folder contains **3 sample insurance policy PDFs** that are fully valid according to PolicyLens validation rules.

## 📋 Files Generated

### 1. **SAMPLE_Health_Insurance_Policy.pdf**
- **Type**: Health Insurance
- **Policy Number**: HEALTH-POL-2026-001234
- **Insured**: John Robert Smith
- **Sum Insured**: ₹5,00,000 per year
- **Premium**: ₹8,500 per annum
- **File Size**: ~2.9 KB

**Coverage Includes:**
- Hospitalization coverage
- Pre/post-hospitalization expenses
- Day-care procedures
- Ambulance charges
- Organ donor treatment

**Key Features for Validation:**
✅ Contains keyword "**premium**" - ₹8,500 per annum
✅ Contains keyword "**claim**" - Claim procedure section
✅ Contains keyword "**coverage**" - Coverage details
✅ Contains keyword "**insured**" - Insured Name: John Robert Smith
✅ Contains keyword "**policy number**" - HEALTH-POL-2026-001234

---

### 2. **SAMPLE_Vehicle_Insurance_Policy.pdf**
- **Type**: Motor Vehicle/Car Insurance
- **Policy Number**: MOTOR-POL-2026-005678
- **Insured**: Sarah Elizabeth Johnson
- **Vehicle**: 2023 Honda Civic
- **Sum Insured**: ₹18,50,000
- **Premium**: ₹12,000 per annum
- **File Size**: ~2.9 KB

**Coverage Includes:**
- Own damage coverage
- Third-party liability (₹1,00,000)
- Theft and total loss protection
- Personal accident cover for driver

**Key Features for Validation:**
✅ Contains keyword "**premium**" - ₹12,000 per annum
✅ Contains keyword "**claim**" - Claim settlement process
✅ Contains keyword "**coverage**" - Coverage details
✅ Contains keyword "**insured**" - Insured: Sarah Elizabeth Johnson
✅ Contains keyword "**policy number**" - MOTOR-POL-2026-005678

---

### 3. **SAMPLE_Life_Insurance_Policy.pdf**
- **Type**: Term Life Insurance
- **Policy Number**: LIFE-POL-2026-009012
- **Insured**: Michael David Chen
- **Term**: 20 years
- **Sum Assured**: ₹50,00,000
- **Premium**: ₹24,500 per annum
- **File Size**: ~3.0 KB

**Coverage Includes:**
- Death benefit protection
- Critical illness rider option
- Premium waiver on disability
- No medical underwriting within 24 months

**Key Features for Validation:**
✅ Contains keyword "**premium**" - ₹24,500 per annum
✅ Contains keyword "**claim**" - Claim procedure
✅ Contains keyword "**coverage**" - Coverage and benefits
✅ Contains keyword "**insured**" - Insured Name: Michael David Chen
✅ Contains keyword "**policy number**" - LIFE-POL-2026-009012

---

## 🧪 How to Test

### Test Case 1: Valid Insurance PDF
```bash
# Start the backend
cd c:\Users\neel8\Desktop\PolicyLens\backend
python main.py

# In another terminal, test with frontend at http://localhost:3000
# Upload: test_pdfs/SAMPLE_Health_Insurance_Policy.pdf
# Expected: ✅ Analysis shows results with coverage score 7/10
```

### Test Case 2: Upload via cURL
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@test_pdfs/SAMPLE_Health_Insurance_Policy.pdf"

# Expected Response:
# {
#   "success": true,
#   "data": {
#     "covered_events": [...],
#     "exclusions": [...],
#     "risky_clauses": [...],
#     "coverage_score": 7
#   }
# }
```

### Test Case 3: Check Validation Logs
When you upload any of these PDFs, your backend should log:
```
Validating document with OpenAI (classification)...
Looking for insurance policy keywords in text...
Document classification: HEALTH_INSURANCE / VEHICLE_INSURANCE / LIFE_INSURANCE
Document is valid insurance policy ✅
Analyzing with OpenAI (analysis)...
Analysis complete: coverage_score=X/10
```

---

## ✅ Validation Checklist

Each PDF has been verified to contain all **5 required keywords**:

| Keyword | Health PDF | Vehicle PDF | Life PDF |
|---------|-----------|------------|---------|
| **premium** | ✅ ₹8,500 | ✅ ₹12,000 | ✅ ₹24,500 |
| **claim** | ✅ Claim Procedure | ✅ Claim Settlement | ✅ Claim Procedure |
| **coverage** | ✅ Coverage Summary | ✅ Coverage Details | ✅ Coverage Benefits |
| **insured** | ✅ John Robert Smith | ✅ Sarah Elizabeth Johnson | ✅ Michael David Chen |
| **policy number** | ✅ HEALTH-POL-2026-001234 | ✅ MOTOR-POL-2026-005678 | ✅ LIFE-POL-2026-009012 |

---

## 📊 PDF Content Summary

### What's Inside Each PDF:

1. **Header**: Policy type title and branding
2. **Policy Details**: Policy number, insured name, dates, premium
3. **Coverage Section**: What's covered, sum insured, benefits
4. **Premium Payment**: Frequency, amount, due dates
5. **Claim Procedure**: Steps to file a claim
6. **Exclusions**: What's NOT covered
7. **Terms & Conditions**: Standard legal clauses

---

## 🚀 Using for Testing

### Quick Test Steps:
1. Start backend: `python main.py` (in `backend/` folder)
2. Start frontend: `npm run dev` (in `frontend/` folder)
3. Go to http://localhost:3000
4. Upload any PDF from `test_pdfs/` folder
5. Click "Analyze Policy"
6. Wait 10-20 seconds for OpenAI analysis
7. See real results (not demo data!)

### Expected Analysis Results:
- **Health PDF**: Score 7/10 - Good hospitalization coverage
- **Vehicle PDF**: Score 8/10 - Comprehensive motor insurance
- **Life PDF**: Score 6/10 - Good protection with waiting periods

---

## 📝 Notes

- All PDFs are **100% valid** for the PolicyLens validation system
- Generated using Python ReportLab library
- Files are small (~3 KB each) for fast processing
- Contains realistic insurance content with actual clauses
- Perfect for manual testing and demo purposes

## ❌ What Will FAIL Validation

If you upload these files, they **WILL BE REJECTED**:
- Random text documents
- Resumes or CVs
- Tax returns or financial statements
- News articles or blog posts
- Documents without insurance keywords

---

## 🔧 Regenerate PDFs

If you need to regenerate these PDFs:
```bash
python generate_sample_pdfs.py
```

This will recreate all 3 sample policies in the `test_pdfs/` folder.

---

**Created**: April 2, 2026  
**Status**: ✅ Ready for Testing  
**Compatible with**: PolicyLens v1.0.0
