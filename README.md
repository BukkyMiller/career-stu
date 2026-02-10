# RIASEC Career Explorer

AI-powered career classification system that maps job skills to RIASEC (Holland) codes.

## Overview

This system classifies 1.3M+ jobs into 120 unique 3-letter RIASEC codes based on their skills and job titles.

### RIASEC Types

| Code | Type | Description |
|------|------|-------------|
| **R** | Realistic | The Doers - practical, hands-on, mechanical |
| **I** | Investigative | The Thinkers - analytical, research, problem-solving |
| **A** | Artistic | The Creators - creative, expressive, innovative |
| **S** | Social | The Helpers - teaching, caring, service |
| **E** | Enterprising | The Persuaders - leading, selling, managing |
| **C** | Conventional | The Organizers - detail-oriented, systematic |

### 3-Letter Superpower Stack

Each job gets a 3-letter code where:
- **1st letter** = Core drive (WHY you act)
- **2nd letter** = Primary expression (HOW you act)
- **3rd letter** = Supporting amplifier (WHAT strengthens impact)

Example: **IRC** (Investigative-Realistic-Conventional)
> "You analyze systems, build practical solutions, and organize them reliably."

## Quick Start

### 1. Classify a Single Job

```bash
cd scripts
python riasec_classifier.py --skills "Python, SQL, Machine Learning" --title "Data Scientist" -v
```

Output:
```
RIASEC Code: IRC
Primary Type: Investigative
Confidence: 85%
Description: You analyze systems, build practical solutions, and organize them reliably.
```

### 2. Interactive Mode

```bash
python riasec_classifier.py --interactive
```

### 3. Process Your Job Database (1.3M jobs)

```bash
# Process job_skills.csv
python process_jobs.py --input ../data/job_skills.csv --output ../data/jobs_riasec.parquet

# Quick test with 1000 samples first
python process_jobs.py --input ../data/job_skills.csv --sample 1000
```

### 4. Query the Classified Database

```bash
# View statistics
python query_riasec.py --stats

# Find jobs by RIASEC code
python query_riasec.py --code IRC

# Find jobs by skills
python query_riasec.py --skills "Python, Machine Learning"

# Find similar jobs
python query_riasec.py --similar "Software Engineer"
```

## Project Structure

```
career-explorer/
├── data/
│   ├── riasec_framework.json     # RIASEC definitions & 120 combinations
│   ├── job_skills.csv            # Your 1.3M jobs with skills
│   ├── job_details.csv           # Job details (title, company, location)
│   └── jobs_riasec.parquet       # Classified output database
│
├── scripts/
│   ├── riasec_classifier.py      # Core classification logic
│   ├── process_jobs.py           # Batch database processor
│   └── query_riasec.py           # Query and explore results
│
└── README.md
```

## Classification Logic

### How Skills Map to RIASEC

The classifier uses weighted scoring:

| Match Type | Points | Example |
|------------|--------|---------|
| Strong indicator | +3.0 | "machine learning" → I |
| Moderate indicator | +1.5 | "analytical" → I |
| Type keyword | +1.0 | "research" → I |
| Title bonus | +2.0 | Extra if skill appears in title |

### Sample Skill Mappings

**Realistic (R):**
- Strong: maintenance, repair, construction, welding, CDL, truck driving, HVAC, forklift
- Moderate: hands-on, technical, field work, troubleshooting

**Investigative (I):**
- Strong: research, data analysis, Python, machine learning, statistics, engineering
- Moderate: problem-solving, analytical, critical thinking

**Artistic (A):**
- Strong: graphic design, UI/UX, photography, creative writing, Adobe, Figma
- Moderate: creative, innovative, visual, design

**Social (S):**
- Strong: teaching, nursing, customer service, counseling, healthcare
- Moderate: communication, empathy, teamwork, helping

**Enterprising (E):**
- Strong: sales, management, leadership, marketing, business development
- Moderate: strategic, competitive, networking, persuading

**Conventional (C):**
- Strong: accounting, administrative, data entry, compliance, Excel, QuickBooks
- Moderate: organized, detail-oriented, systematic, documentation

## Advanced Usage

### Join Multiple Data Sources

```bash
python process_jobs.py \
  --skills-csv ../data/job_skills.csv \
  --details-csv ../data/job_details.csv \
  --output ../data/unified_jobs.parquet
```

### Custom Column Names

```bash
python process_jobs.py \
  --input jobs.csv \
  --output classified.parquet \
  --skills-col "skills_column" \
  --link-col "url_column" \
  --title-col "position_column"
```

### Using in Python

```python
from riasec_classifier import classify_job

# Classify a job
result = classify_job(
    skills_text="Python, SQL, Data Analysis, Machine Learning",
    job_title="Data Scientist"
)

print(result['riasec_code'])      # IRC
print(result['primary_type'])     # Investigative
print(result['confidence'])       # 0.85
print(result['description'])      # Your unique gift...
```

### Processing DataFrames

```python
import pandas as pd
from riasec_classifier import process_dataframe

df = pd.read_csv('jobs.csv')
df_classified = process_dataframe(df, skills_col='job_skills')
```

## Output Schema

The processed database includes:

| Column | Type | Description |
|--------|------|-------------|
| job_link | string | Original LinkedIn URL |
| job_skills | string | Comma-separated skills |
| extracted_title | string | Job title (from URL or provided) |
| riasec_code | string | 3-letter RIASEC code (e.g., "IRC") |
| riasec_confidence | float | Confidence score (0-1) |
| primary_riasec_type | string | Primary type name (e.g., "Investigative") |

## Performance

- **Processing speed:** ~5,000-10,000 jobs/second
- **Memory efficient:** Uses batch processing
- **1.3M jobs:** ~5-10 minutes on standard hardware

## Validation

Compare AI classifications against the Labor Market Analysis Excel (999 jobs with known RIASEC codes):

```python
# Load Excel reference
excel_df = pd.read_excel('Labor_Market_Analysis_2025.xlsx')

# Compare codes
accuracy = (classified_df['riasec_code'] == excel_df['Top 3 RIASEC Code']).mean()
```

## Framework Reference

See `data/riasec_framework.json` for:
- All 120 RIASEC combinations
- Skill indicators (247 total)
- Type definitions and characteristics
- Superpower descriptions

## Credits

Based on Holland's RIASEC model (Holland Codes) with extensions from the RIASEC Career Framework document.

---

**Questions?** Open the interactive classifier:
```bash
python riasec_classifier.py --interactive
```
