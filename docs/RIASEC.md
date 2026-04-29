# RIASEC Framework

RIASEC (Holland Codes) is Career STU's core framework for matching learners to careers.

## The Six Types

| Code | Type | Description | Example Skills |
|------|------|-------------|----------------|
| **R** | Realistic | Hands-on, practical, mechanical | CDL, HVAC, welding, construction |
| **I** | Investigative | Analytical, intellectual, scientific | Python, SQL, data analysis, research |
| **A** | Artistic | Creative, expressive, original | Graphic design, Photoshop, UI/UX |
| **S** | Social | Helping, teaching, counseling | Nursing, teaching, customer service |
| **E** | Enterprising | Leading, persuading, managing | Sales, management, business development |
| **C** | Conventional | Organizing, detail-oriented, systematic | Accounting, Excel, administrative |

## RIASEC Stack Logic (3-Letter Codes)

Each position in the 3-letter code has meaning:

| Position | Role | Question |
|----------|------|----------|
| **Position 1** | WHY | Core drive — why you act |
| **Position 2** | HOW | Primary expression — how you act |
| **Position 3** | WHAT | Supporting amplifier — what strengthens impact |

### Example: SRI (Social-Realistic-Investigative)
- **S (WHY):** Driven to help people
- **R (HOW):** Through hands-on, practical methods
- **I (WHAT):** Strengthened by analytical insight

Careers: Occupational therapist, physical therapist, medical technician

## Job Distribution in Database

From `unified_jobs.parquet` (1.3M jobs):

| Type | Count | Percentage |
|------|-------|------------|
| Social (S) | 483,223 | 37.3% |
| Enterprising (E) | 277,167 | 21.4% |
| Investigative (I) | 249,941 | 19.3% |
| Realistic (R) | 159,829 | 12.3% |
| Conventional (C) | 111,977 | 8.6% |
| Artistic (A) | 14,244 | 1.1% |

## RIASEC Matching Process

### 1. From Skills
Analyze learner's skills to infer their RIASEC profile using the 316 skill-to-RIASEC indicators in `riasec_framework.json`.

```python
# Tool: infer_riasec_from_skills
result = infer_riasec_from_skills(["Python", "SQL", "data analysis"])
# Returns: {"riasec_code": "ICE", "confidence": 85}
```

### 2. From Preferences
Ask about work style preferences:
- Hands-on vs analytical
- People vs data
- Creative vs systematic
- Leading vs supporting

### 3. Job Matching
Find jobs with matching RIASEC codes.

```python
# Tool: search_jobs_by_riasec
jobs = search_jobs_by_riasec(riasec_code="IRA", limit=10)
```

### 4. Validation
Cross-reference with salary and market data from `salary_reference.parquet`.

## riasec_framework.json Structure

Location: `data/riasec_framework.json`

Contains:
- **120 RIASEC code combinations** with descriptions and career themes
- **316 skill-to-RIASEC indicators** for classification

Example code description:
```json
{
  "SRI": {
    "description": "You help people by applying insight to real-world action",
    "career_themes": ["Healthcare", "Social Services", "Education"],
    "example_careers": ["Occupational Therapist", "Physical Therapist"]
  }
}
```

## 7 Career Exploration Methods

Career STU offers multiple ways to discover RIASEC profile:

1. **Full RIASEC Assessment** — 48-question validated assessment
2. **Quick 5-Question Quiz** — Fast RIASEC inference for impatient learners
3. **Would You Rather** — Binary choices that narrow RIASEC profile
4. **Day in the Life** — Walk through what a typical day looks like in matching careers
5. **YouTube Career Videos** — Curate career spotlight videos
6. **Skills You Enjoy Picker** — Interactive skill selector that maps to RIASEC
7. **Salary-First Explorer** — Start from desired salary, find matching careers

## RIASEC Tools

### infer_riasec_from_skills
Given skills, predict likely RIASEC code.

### get_riasec_description
Get description and career themes for a RIASEC code.

### compare_riasec_codes
Compare learner's RIASEC to a target job's RIASEC to assess fit.

### search_jobs_by_riasec
Find jobs matching a RIASEC code.

## Query Examples

### Find jobs by RIASEC code
```python
import duckdb

result = duckdb.query("""
    SELECT job_title, company, job_location, riasec_confidence
    FROM 'data/unified_jobs.parquet'
    WHERE riasec_code = 'SRI'
    ORDER BY riasec_confidence DESC
    LIMIT 10
""").fetchdf()
```

### Get RIASEC distribution
```python
result = duckdb.query("""
    SELECT primary_riasec_type, COUNT(*) as count
    FROM 'data/unified_jobs.parquet'
    GROUP BY primary_riasec_type
    ORDER BY count DESC
""").fetchdf()
```
