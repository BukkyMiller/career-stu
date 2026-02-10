# Career STU Data Files

This directory contains the data files required for Career STU to function.

## Required Files

### Large Files (Not in Git - Too Big for GitHub)

These files are too large for GitHub's file size limits. You need to obtain them separately:

1. **`unified_jobs.parquet`** (194.73 MB)
   - 1.3M job postings with RIASEC classifications
   - Contains: job titles, companies, locations, skills, RIASEC codes

2. **`jobs_riasec.parquet`** (213.44 MB)
   - Extended job database with RIASEC metadata

**Where to get these files:**
- Contact the repository maintainer
- Or regenerate using the scripts in `scripts/` directory

### Included Files (In Git)

These files are included in the repository:

1. **`riasec_framework.json`** (35 KB)
   - RIASEC framework definitions
   - 120 three-letter code combinations
   - 316 skill indicators

2. **`salary_reference.parquet`** (59 KB)
   - 999 jobs with salary and market demand data
   - Median salaries, labor market tags, supply/demand ratios

## Data Structure

### unified_jobs.parquet
```
Columns:
- job_link (VARCHAR): Unique job identifier
- job_title (VARCHAR): Job title
- company (VARCHAR): Company name
- job_location (VARCHAR): Location
- job_level (VARCHAR): Entry, Mid-Senior, Director, etc.
- job_skills (VARCHAR): Comma-separated skills
- riasec_code (VARCHAR): 3-letter RIASEC code
- riasec_confidence (FLOAT): Classification confidence (0-100)
- primary_riasec_type (CHAR): S, I, R, A, E, or C
```

### salary_reference.parquet
```
Columns:
- Job Title (VARCHAR)
- Median Annual Advertised Salary (INTEGER)
- Labor Market Tag (VARCHAR): Shortage/Surplus indicators
- Supply/Demand Ratio (FLOAT)
- Top 3 RIASEC Code (VARCHAR)
- Latest 30 Days Unique Postings (INTEGER)
```

## Setup

After obtaining the large parquet files:

1. Place them in this `data/` directory
2. Run the verification script:
   ```bash
   python3 verify_setup.py
   ```
3. Initialize the database:
   ```bash
   python3 -c "from database.connection import init_db; init_db()"
   ```

## Regenerating Data (Optional)

If you have the raw job data, you can regenerate the parquet files:

```bash
python3 scripts/process_jobs.py
```

This will create the `unified_jobs.parquet` file with RIASEC classifications.
