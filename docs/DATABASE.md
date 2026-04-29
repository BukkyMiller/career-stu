# Database Reference

Career STU uses DuckDB for learner data and Parquet files for job/salary data.

## Database Files

| File | Type | Contents |
|------|------|----------|
| `data/career_stu.duckdb` | DuckDB | Learner data (7 tables) |
| `data/unified_jobs.parquet` | Parquet | 1.3M jobs with RIASEC |
| `data/salary_reference.parquet` | Parquet | 999 jobs with salary/market data |
| `data/riasec_framework.json` | JSON | RIASEC definitions + 316 skill indicators |

## DuckDB Schema (7 Tables)

### learners
Core learner record.

```sql
CREATE TABLE learners (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE,
    name VARCHAR,
    status VARCHAR DEFAULT 'new',  -- new, active, paused, completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### learner_profiles
Extended profile information.

```sql
CREATE TABLE learner_profiles (
    learner_id VARCHAR PRIMARY KEY REFERENCES learners(id),
    current_job_title VARCHAR,
    current_industry VARCHAR,
    years_experience INTEGER,
    education_level VARCHAR,
    weekly_study_hours INTEGER,
    preferred_study_times VARCHAR,
    has_family_obligations BOOLEAN DEFAULT FALSE,
    employment_status VARCHAR,
    preferred_format VARCHAR DEFAULT 'any',
    disposition VARCHAR,  -- unclear, discontent, promotion, called
    inferred_riasec_code VARCHAR,
    behavioral_capital_signal TEXT,   -- Early signals gathered during intake
    social_capital_signal TEXT,       -- Early signals gathered during intake
    navigation_capital_signal TEXT,   -- Early signals gathered during intake
    profile_complete BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### learner_skills
Skills with proficiency and evidence source.

```sql
CREATE TABLE learner_skills (
    id VARCHAR PRIMARY KEY,
    learner_id VARCHAR REFERENCES learners(id),
    skill_name VARCHAR,
    proficiency_level VARCHAR,  -- none, beginner, intermediate, advanced, expert
    evidence_source VARCHAR,    -- self_reported, resume_parsed, url_parsed, validated
    validated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(learner_id, skill_name)
);
```

### learner_goals
Career goals with status and market data.

```sql
CREATE TABLE learner_goals (
    id VARCHAR PRIMARY KEY,
    learner_id VARCHAR REFERENCES learners(id),
    target_job_title VARCHAR,
    target_riasec_code VARCHAR,
    status VARCHAR DEFAULT 'exploring',  -- exploring, committed, achieved, changed
    is_feasible BOOLEAN,
    estimated_time_months INTEGER,
    salary_estimate INTEGER,
    market_demand VARCHAR,
    committed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### pathways
Learning pathways linked to goals.

```sql
CREATE TABLE pathways (
    id VARCHAR PRIMARY KEY,
    learner_id VARCHAR REFERENCES learners(id),
    goal_id VARCHAR REFERENCES learner_goals(id),
    status VARCHAR DEFAULT 'active',  -- active, paused, completed, superseded
    total_skills INTEGER,
    completed_skills INTEGER DEFAULT 0,
    estimated_hours INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### pathway_skills
Individual skills within a pathway.

```sql
CREATE TABLE pathway_skills (
    id VARCHAR PRIMARY KEY,
    pathway_id VARCHAR REFERENCES pathways(id),
    skill_name VARCHAR,
    capital_type VARCHAR,  -- ksa, behavioral, social, navigation
    sequence_order INTEGER,
    status VARCHAR DEFAULT 'not_started',  -- not_started, in_progress, completed
    estimated_hours INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

### conversations
Conversation tracking (minimal).

```sql
CREATE TABLE conversations (
    id VARCHAR PRIMARY KEY,
    learner_id VARCHAR REFERENCES learners(id),
    mode VARCHAR,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    summary TEXT
);
```

## Indexes

```sql
CREATE INDEX idx_learner_status ON learners(status);
CREATE INDEX idx_learner_skills_learner_id ON learner_skills(learner_id);
CREATE INDEX idx_learner_goals_learner_id ON learner_goals(learner_id);
CREATE INDEX idx_learner_goals_status ON learner_goals(status);
CREATE INDEX idx_pathways_learner_id ON pathways(learner_id);
CREATE INDEX idx_pathways_status ON pathways(status);
CREATE INDEX idx_pathway_skills_pathway_id ON pathway_skills(pathway_id);
CREATE INDEX idx_conversations_learner_id ON conversations(learner_id);
```

## Parquet Files

### unified_jobs.parquet (1.3M jobs)

| Column | Type | Description |
|--------|------|-------------|
| job_link | VARCHAR | Unique job identifier (PRIMARY KEY) |
| job_title | VARCHAR | Job title (e.g., "Data Scientist") |
| company | VARCHAR | Company name |
| job_location | VARCHAR | Location (e.g., "San Francisco, CA") |
| job_level | VARCHAR | Entry, Mid senior, Director, Associate, etc. |
| job_skills | VARCHAR | Comma-separated skills |
| riasec_code | VARCHAR | 3-letter code (e.g., "IRA", "SRI") |
| riasec_confidence | FLOAT | Classification confidence (0-100) |
| primary_riasec_type | CHAR(1) | First letter: S, I, R, A, E, or C |

**Distribution by Primary RIASEC Type:**
- Social (S): 483,223 jobs (37.3%)
- Enterprising (E): 277,167 jobs (21.4%)
- Investigative (I): 249,941 jobs (19.3%)
- Realistic (R): 159,829 jobs (12.3%)
- Conventional (C): 111,977 jobs (8.6%)
- Artistic (A): 14,244 jobs (1.1%)

### salary_reference.parquet (999 jobs)

| Column | Type | Description |
|--------|------|-------------|
| Job Title | VARCHAR | Job title for salary lookup |
| Median Annual Advertised Salary | INTEGER | Salary in USD |
| Labor Market Tag | VARCHAR | "Severe Shortage", "Moderate Shortage", "Moderate Surplus" |
| Supply/Demand Ratio | FLOAT | Market supply vs demand |
| Top 3 RIASEC Code | VARCHAR | Verified RIASEC code |
| Latest 30 Days Unique Postings | INTEGER | Recent job posting volume |

## Environment Variables

```bash
DUCKDB_PATH=./data/career_stu.duckdb
JOBS_PARQUET_PATH=./data/unified_jobs.parquet
SALARY_PARQUET_PATH=./data/salary_reference.parquet
RIASEC_JSON_PATH=./data/riasec_framework.json
```

## Database Connection

```python
from database.connection import get_connection, init_db

# Initialize database (creates tables if not exist)
init_db()

# Get connection for queries
conn = get_connection()
```
