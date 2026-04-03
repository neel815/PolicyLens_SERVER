# Using Test PDFs with PolicyLens

## 📁 Quick Start

You now have **3 sample insurance PDFs** in the `backend/test_pdfs/` folder ready to test your PolicyLens application:

```
backend/test_pdfs/
├── SAMPLE_Health_Insurance_Policy.pdf     ← Health insurance
├── SAMPLE_Vehicle_Insurance_Policy.pdf    ← Car/motor insurance
├── SAMPLE_Life_Insurance_Policy.pdf       ← Life insurance
└── README.md                               ← Detailed info
```

## 🚀 Testing Steps

### Step 1: Start the Backend
```bash
cd c:\Users\neel8\Desktop\PolicyLens\backend
python main.py
```
✅ Backend running on `http://localhost:8000`

### Step 2: Start the Frontend (in new terminal)
```bash
cd c:\Users\neel8\Desktop\PolicyLens\frontend
npm run dev
```
✅ Frontend running on `http://localhost:3000`

### Step 3: Upload and Analyze
1. Open http://localhost:3000 in your browser
2. You'll see the PolicyLens upload page
3. **Drag and drop** or click to upload one of the sample PDFs from `backend/test_pdfs/`
4. Click **"Analyze Policy"** button
5. Wait 10-20 seconds for OpenAI analysis
6. See the results show:
   - Coverage score (out of 10)
   - Covered events (what's included)
   - Exclusions (what's NOT covered)
   - Risky clauses (things to watch out for)

### Step 4: Try Different PDFs
Test with different sample PDFs:
- ✅ **SAMPLE_Health_Insurance_Policy.pdf** → Score ~7 (good coverage)
- ✅ **SAMPLE_Vehicle_Insurance_Policy.pdf** → Score ~8 (comprehensive)
- ✅ **SAMPLE_Life_Insurance_Policy.pdf** → Score ~6 (moderate coverage)

## 🧪 Test Scenarios

### Test 1: Valid Insurance PDF ✅
**File**: Any sample PDF from `test_pdfs/`
**Expected**: 
- No errors
- Shows analysis with real score
- Displays covered events, exclusions, risky clauses

**Command to test** (without frontend):
```bash
cd c:\Users\neel8\Desktop\PolicyLens\backend
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@test_pdfs/SAMPLE_Health_Insurance_Policy.pdf"
```

Expected Response ✅:
```json
{
  "success": true,
  "data": {
    "covered_events": ["...", "..."],
    "exclusions": ["...", "..."],
    "risky_clauses": ["...", "..."],
    "coverage_score": 7
  }
}
```

### Test 2: Non-Insurance Document ❌
**Files to try** (will be REJECTED):
- Resume or CV
- Tax return (ITR)
- Receipt or bill
- Random text file
- News article

**Expected Error**: 
```
"Not a valid insurance policy document. Please upload a real insurance policy."
```

### Test 3: Check Backend Logs
While uploading, watch the backend terminal. You should see:
```
Validating document with OpenAI (classification)...
Looking for insurance policy keywords: premium, claim, coverage, insured, policy number
✓ Document is valid insurance policy
Analyzing with OpenAI (analysis)...
✓ Analysis complete: coverage_score=7/10
```

## 📋 What Each PDF Contains

All 3 PDFs have been created with **all required keywords** your validation system checks for:

| PDF | Policy # | Keywords Included | Score |
|-----|----------|------------------|-------|
| **Health** | HEALTH-POL-2026-001234 | premium, claim, coverage, insured, policy number | 7 |
| **Vehicle** | MOTOR-POL-2026-005678 | premium, claim, coverage, insured, policy number | 8 |
| **Life** | LIFE-POL-2026-009012 | premium, claim, coverage, insured, policy number | 6 |

## 🎯 What to Verify

✅ **Checklist After Update**:
- [ ] Frontend uploads file successfully
- [ ] Loading animation shows for 2+ seconds
- [ ] Backend receives file (check logs)
- [ ] Document is validated as insurance policy
- [ ] OpenAI analysis runs (not demo data)
- [ ] Results page shows real data (not hardcoded)
- [ ] Coverage score is different for each PDF
- [ ] Non-insurance docs show error message

## 🔄 Regenerate PDFs (if needed)

If you want to regenerate these test PDFs:
```bash
cd c:\Users\neel8\Desktop\PolicyLens\backend
python generate_sample_pdfs.py
```

This will recreate all 3 PDFs in the `test_pdfs/` folder.

## 📊 Expected Results

### Health Insurance PDF
```
Coverage Score: 7/10
Covered Events: 5 identified
Exclusions: 6 identified
Risky Clauses: 4 identified + waiting periods
Verdict: GOOD COVERAGE
```

### Vehicle Insurance PDF
```
Coverage Score: 8/10
Covered Events: 6 identified
Exclusions: 6 identified
Risky Clauses: 3 identified + racing exclusions
Verdict: COMPREHENSIVE COVERAGE
```

### Life Insurance PDF
```
Coverage Score: 6/10
Covered Events: 4 identified
Exclusions: 5 identified
Risky Clauses: 3 identified + suicide clause, unlawful activity
Verdict: MODERATE COVERAGE
```

## 🐛 Troubleshooting

### Issue: "File upload failed"
- Check backend is running on port 8000
- Check CORS is enabled (should be in main.py)
- Check file is not > 10MB

### Issue: "Can't extract text from PDF"
- PDF might be corrupted
- Regenerate: `python generate_sample_pdfs.py`

### Issue: "Not a valid insurance policy"
- Your PDF lacks required keywords
- Use sample PDFs from `test_pdfs/`
- Check PDF contains: premium, claim, coverage, insured, policy number

### Issue: Still showing demo data on frontend
- Clear browser cache (Ctrl+Shift+Delete)
- Rebuild frontend: `npm run build`
- Restart `npm run dev`

## 📞 Need Help?

Check these files for more info:
1. `test_pdfs/README.md` - Details about each sample PDF
2. `FIX_SUMMARY.md` - Info about frontend API integration fix
3. Backend logs - Run with DEBUG=true in .env

---

**Status**: ✅ All test PDFs generated and ready  
**Date**: April 2, 2026
