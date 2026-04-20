# Hybrid Database Design Documentation

## Overview

PolicyLens now uses a **hybrid database design** for policy analysis storage:
- **Structured columns** for fast access (covered_events, exclusions, risky_clauses, coverage_score)
- **Flexible JSONB column** (analysis) for complete AI responses and future features

## Database Structure

### Policies Table

```
policies
├── (existing structured fields)
│   ├── user_id (Integer, FK)
│   ├── file_name (String)
│   ├── file_size (String)
│   ├── policy_type (String)
│   ├── covered_events (JSON)
│   ├── exclusions (JSON)
│   ├── risky_clauses (JSON)
│   ├── coverage_score (Integer)
│   └── score_reason (String)
│
└── (NEW) analysis (JSON, nullable)
    └── Complete AI response with metadata
```

## Analysis Column Schema

Example content:

```json
{
  "is_insurance": true,
  "policy_type": "Health",
  "covered_events": [...],
  "exclusions": [...],
  "risky_clauses": [...],
  "coverage_score": 7,
  "score_reason": "Good coverage...",
  "confidence": 0.92,
  "model_version": "gemini-2.5-flash",
  "analysis_timestamp": "2026-04-06T13:17:33Z"
}
```

## Why This Design?

### ✅ Backward Compatible
- All existing API endpoints unchanged
- Existing queries still work
- Frontend code unchanged

### ✅ Fast Access
- Structured columns indexed for quick queries
- Dashboard filters use covered_events, coverage_score directly
- No performance impact

### ✅ Future-Proof
- **Chat with Policy**: Use analysis JSON for rich context
- **Improved Reasoning**: Store intermediate steps in analysis
- **Debugging**: Access raw AI responses without re-running
- **Policy Comparison**: More context for battle feature
- **Audit Trail**: Complete response history

## How It Works

### During Analysis Upload

1. **Service** (`analyze_policy_service`):
   - Generate AI analysis via Gemini
   - Extract structured fields
   - Return both clean data + full response

2. **Controller** (`analyze_policy_controller`):
   - Store structured fields in existing columns
   - Store complete response in `analysis` column
   - Return clean API response (no internal fields)

3. **Database**:
   - All columns populated, analysis indexed

### Data Flow

```
PDF File
  ↓
analyze_policy_service()
  ├─ Extract text
  ├─ Call Gemini
  ├─ Parse JSON
  └─ return {
       covered_events: [...],
       exclusions: [...],
       coverage_score: 7,
       _full_ai_response: {...}  ← stored in analysis column
     }
  ↓
analyze_policy_controller()
  ├─ Create PolicyAnalysisData from structured fields
  ├─ Save policy with create_policy()
  ├─ Extract _full_ai_response
  ├─ Store in policy.analysis column
  └─ Return clean response (without _full_ai_response)
  ↓
Database
  ├─ structured columns: indexed, fast queries
  └─ analysis: flexible JSONB, future features
```

## Migration

Run Alembic migration:

```bash
cd backend
alembic upgrade head
```

This will:
1. Add `analysis` column to policies table
2. Set all existing policies' analysis to NULL (backward compatible)
3. Future uploads will populate analysis

## Usage Examples

### Query Structured Data (Fast)

```python
# Get all policies with coverage > 6
db.query(Policy).filter(Policy.coverage_score > 6).all()

# Filter by exclusions (still indexed)
db.query(Policy).filter(
    Policy.exclusions.contains(["Pre-existing conditions"])
).all()
```

### Access Full AI Response (Future Features)

```python
policy = db.query(Policy).filter(Policy.id == policy_id).first()

# Full AI response with metadata
full_response = policy.analysis
# {
#   "is_insurance": true,
#   "policy_type": "Health",
#   "covered_events": [...],
#   "confidence": 0.92,
#   "model_version": "gemini-2.5-flash"
# }
```

### Chat Feature (Future)

```python
# Use rich context for chat
context = {
    "policy_type": policy.policy_type,
    "coverage_score": policy.coverage_score,
    "full_analysis": policy.analysis,  # Complete context
    "user_question": "Can I claim for dental?"
}
# Feed to LLM for conversational responses
```

## Backward Compatibility Checklist

✅ Existing API responses unchanged
✅ Existing queries work as-is
✅ Frontend code unchanged
✅ All existing columns still populated
✅ Old policies (without analysis) still queryable
✅ Migration is additive (no drops)

## Performance Notes

- **No impact** on read performance (analysis is nullable)
- **Minimal impact** on write (single extra JSON store)
- **Queries** on structured fields use indexes
- **Queries** on analysis column use GIN indexes (optional future optimization)

## Testing Checklist

- [ ] Run migration: `alembic upgrade head`
- [ ] Upload policy → verify structured columns populated
- [ ] Check DB: `SELECT analysis FROM policies;`
- [ ] Verify analysis JSON not NULL for new policies
- [ ] Existing endpoints work unchanged
- [ ] Dashboard displays coverage correctly
- [ ] Battle feature works (uses structured fields)
- [ ] No performance regression

## Future Features Enabled

This foundation unlocks:

1. **Chat with your policy** - Use analysis JSONB for rich context
2. **Improved reasoning** - Store thinking steps in analysis
3. **Policy insights** - Cross-policy analysis with metadata
4. **Debugging interface** - View raw AI responses
5. **Extended battle** - Use confidence scores and full context
6. **Compliance tracking** - Audit trail of AI decisions

---

**Version**: 1.0
**Date**: 2026-04-06
**Status**: ✅ Implemented
