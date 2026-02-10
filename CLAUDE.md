# Career STU - AI Career Support Assistant

**Project:** Career STU MVP Prototype
**Version:** 0.2 (Updated with actual data structure)
**Date:** February 2026

---

## What Is Career STU?

Career STU is an AI-powered career support assistant that guides learners from **"Here"** (where they are now) to **"There"** (their career goal). It combines four capabilities into a single conversational agent:

1. **Intake** - Understand who the learner is and what skills they have
2. **Goal Discovery** - Help learner identify and validate career goals using RIASEC matching
3. **Pathway** - Generate personalized learning paths to reach the goal
4. **Learning Support** - Guide learner through content and track progress

**Key Principle:** Career STU is ONE agent with FOUR MODES, not four separate agents.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CAREER STU ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│                              ┌──────────────┐                                   │
│                              │   LEARNER    │                                   │
│                              │   (Chat UI)  │                                   │
│                              └──────┬───────┘                                   │
│                                     │                                            │
│                                     ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                         CAREER STU (LLM Agent)                            │   │
│  │                                                                           │   │
│  │   ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │   │                    MASTER SYSTEM PROMPT                          │    │   │
│  │   │                                                                  │    │   │
│  │   │  MODES:                                                         │    │   │
│  │   │  ├── INTAKE         (new learners)                              │    │   │
│  │   │  ├── GOAL_DISCOVERY (exploring careers + RIASEC matching)       │    │   │
│  │   │  ├── PATHWAY        (planning learning path)                    │    │   │
│  │   │  └── LEARNING       (active study support)                      │    │   │
│  │   │                                                                  │    │   │
│  │   └─────────────────────────────────────────────────────────────────┘    │   │
│  │                                     │                                     │   │
│  │                          TOOLS (Function Calls)                          │   │
│  │                                     │                                     │   │
│  └─────────────────────────────────────┼────────────────────────────────────┘   │
│                                        │                                         │
│       ┌────────────────────────────────┼────────────────────────────────┐       │
│       │                                │                                │       │
│       ▼                                ▼                                ▼       │
│  ┌──────────┐                   ┌──────────────┐                 ┌──────────┐  │
│  │ DuckDB   │                   │ Job/Skills   │                 │ External │  │
│  │ (Local)  │                   │ Parquet      │                 │ APIs     │  │
│  │          │                   │ Files        │                 │          │  │
│  │ Tables:  │                   │              │                 │ • LLM    │  │
│  │ • learners│                  │ Files:       │                 │  (Claude)│  │
│  │ • skills │                   │ • unified_   │                 │          │  │
│  │ • goals  │                   │   jobs       │                 │ • Future:│  │
│  │ • pathways│                  │ • salary_    │                 │   Calendar│  │
│  │ • convos │                   │   reference  │                 │          │  │
│  └──────────┘                   └──────────────┘                 └──────────┘  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## The Four Modes

### Mode Transitions

```
┌──────────┐     Profile      ┌───────────────┐     Goal        ┌─────────┐
│  INTAKE  │ ──────────────▶  │ GOAL_DISCOVERY│ ─────────────▶  │ PATHWAY │
│          │   Complete       │  + RIASEC     │   Committed     │         │
└──────────┘                  └───────────────┘                 └────┬────┘
                                     ▲                               │
                                     │                               │ Pathway
                                     │ Goal Changed                  │ Accepted
                                     │                               ▼
                                     │                          ┌─────────┐
                                     └────────────────────────  │ LEARNING│
                                                                └─────────┘
```

### Mode Details

| Mode | Trigger | Purpose | Key Actions |
|------|---------|---------|-------------|
| **INTAKE** | `learner.status == 'new'` | Build learner profile | Ask background, skills, constraints |
| **GOAL_DISCOVERY** | `learner.goal_status == 'exploring'` | Find career direction | Infer RIASEC type, show matching jobs, validate feasibility |
| **PATHWAY** | `goal_status == 'committed'` AND no pathway | Create learning plan | Calculate skill gaps, generate pathway, negotiate timeline |
| **LEARNING** | Has active pathway | Support daily learning | Recommend content, answer questions, track progress |

---

## Available Data Files

### 1. unified_jobs.parquet (1.3M jobs - MAIN DATABASE)

Location: `data/unified_jobs.parquet`

| Column | Type | Description |
|--------|------|-------------|
| job_link | VARCHAR | Unique job identifier (PRIMARY KEY) |
| job_title | VARCHAR | Job title (e.g., "Data Scientist") |
| company | VARCHAR | Company name |
| job_location | VARCHAR | Location (e.g., "San Francisco, CA") |
| job_level | VARCHAR | Entry, Mid senior, Director, Associate, etc. |
| job_skills | VARCHAR | Comma-separated skills (e.g., "Python, SQL, Machine Learning") |
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

### 2. salary_reference.parquet (999 jobs - SALARY & MARKET DATA)

Location: `data/salary_reference.parquet`

| Column | Type | Description |
|--------|------|-------------|
| Job Title | VARCHAR | Job title for salary lookup |
| Median Annual Advertised Salary | INTEGER | Salary in USD |
| Labor Market Tag | VARCHAR | "Severe Shortage", "Moderate Shortage", "Moderate Surplus" |
| Supply/Demand Ratio | FLOAT | Market supply vs demand |
| Top 3 RIASEC Code | VARCHAR | Verified RIASEC code |
| Latest 30 Days Unique Postings | INTEGER | Recent job posting volume |

**Use for:** Salary estimates, market demand validation, career feasibility checks

### 3. riasec_framework.json (RIASEC Definitions)

Location: `data/riasec_framework.json`

Contains 120 RIASEC code combinations with:
- Code description (e.g., "SRI: You help people by applying insight to real-world action")
- Career themes
- 316 skill-to-RIASEC indicators for classification

---

## RIASEC Framework

### The Six Types

| Code | Type | Description | Example Skills |
|------|------|-------------|----------------|
| R | Realistic | Hands-on, practical, mechanical | CDL, HVAC, welding, construction |
| I | Investigative | Analytical, intellectual, scientific | Python, SQL, data analysis, research |
| A | Artistic | Creative, expressive, original | Graphic design, Photoshop, UI/UX |
| S | Social | Helping, teaching, counseling | Nursing, teaching, customer service |
| E | Enterprising | Leading, persuading, managing | Sales, management, business development |
| C | Conventional | Organizing, detail-oriented, systematic | Accounting, Excel, administrative |

### How RIASEC Matching Works

1. **From Skills:** Analyze learner's skills to infer their RIASEC profile
2. **From Preferences:** Ask about work style preferences (hands-on vs analytical, people vs data)
3. **Job Matching:** Find jobs with matching RIASEC codes
4. **Validation:** Cross-reference with salary and market data

---

## Database Schema (Learner Data - DuckDB)

File: `data/career_stu.duckdb`

```sql
-- LEARNERS
CREATE TABLE learners (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE,
    name VARCHAR,
    status VARCHAR DEFAULT 'new',  -- new, active, paused, completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
    inferred_riasec_code VARCHAR,  -- Learner's RIASEC profile
    profile_complete BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SKILLS
CREATE TABLE learner_skills (
    id VARCHAR PRIMARY KEY,
    learner_id VARCHAR REFERENCES learners(id),
    skill_name VARCHAR,
    proficiency_level VARCHAR,  -- none, beginner, intermediate, advanced, expert
    evidence_source VARCHAR,  -- self_reported, validated, credential
    validated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(learner_id, skill_name)
);

-- GOALS
CREATE TABLE learner_goals (
    id VARCHAR PRIMARY KEY,
    learner_id VARCHAR REFERENCES learners(id),
    target_job_title VARCHAR,
    target_riasec_code VARCHAR,
    status VARCHAR DEFAULT 'exploring',  -- exploring, committed, achieved, changed
    is_feasible BOOLEAN,
    estimated_time_months INTEGER,
    salary_estimate INTEGER,
    market_demand VARCHAR,  -- from salary_reference Labor Market Tag
    committed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PATHWAYS
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

CREATE TABLE pathway_skills (
    id VARCHAR PRIMARY KEY,
    pathway_id VARCHAR REFERENCES pathways(id),
    skill_name VARCHAR,
    sequence_order INTEGER,
    status VARCHAR DEFAULT 'not_started',  -- not_started, in_progress, completed
    estimated_hours INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- CONVERSATIONS
CREATE TABLE conversations (
    id VARCHAR PRIMARY KEY,
    learner_id VARCHAR REFERENCES learners(id),
    mode VARCHAR,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    summary TEXT
);
```

---

## Tool Definitions

### Job Search Tools

```python
{
    "name": "search_jobs",
    "description": "Search jobs by title, skills, location, or level",
    "parameters": {
        "job_title": {"type": "string", "optional": True},
        "skills": {"type": "array", "items": {"type": "string"}, "optional": True},
        "location": {"type": "string", "optional": True},
        "job_level": {"type": "string", "optional": True},
        "limit": {"type": "integer", "default": 10}
    }
}

{
    "name": "search_jobs_by_riasec",
    "description": "Find jobs matching a RIASEC code",
    "parameters": {
        "riasec_code": {"type": "string", "description": "e.g., 'SRI', 'IRA'"},
        "primary_type_only": {"type": "boolean", "default": False},
        "job_level": {"type": "string", "optional": True},
        "limit": {"type": "integer", "default": 10}
    }
}

{
    "name": "get_job_details",
    "description": "Get full details for a specific job",
    "parameters": {
        "job_link": {"type": "string"}
    }
}
```

### RIASEC Tools

```python
{
    "name": "infer_riasec_from_skills",
    "description": "Given skills, predict likely RIASEC code",
    "parameters": {
        "skills": {"type": "array", "items": {"type": "string"}}
    }
}

{
    "name": "get_riasec_description",
    "description": "Get description and career themes for a RIASEC code",
    "parameters": {
        "riasec_code": {"type": "string"}
    }
}

{
    "name": "compare_riasec_codes",
    "description": "Compare learner's RIASEC to a target job's RIASEC",
    "parameters": {
        "learner_riasec": {"type": "string"},
        "job_riasec": {"type": "string"}
    }
}
```

### Salary & Market Tools

```python
{
    "name": "get_salary_info",
    "description": "Look up salary and market demand for a job title",
    "parameters": {
        "job_title": {"type": "string"}
    }
}

{
    "name": "get_high_demand_jobs",
    "description": "Find jobs with labor shortages (good career prospects)",
    "parameters": {
        "riasec_type": {"type": "string", "optional": True},
        "min_salary": {"type": "integer", "optional": True},
        "limit": {"type": "integer", "default": 10}
    }
}
```

### Skills Gap Tools

```python
{
    "name": "calculate_skill_gap",
    "description": "Compare learner skills to job requirements",
    "parameters": {
        "learner_skills": {"type": "array", "items": {"type": "string"}},
        "target_job_link": {"type": "string"}
    }
}

{
    "name": "find_jobs_by_skill_match",
    "description": "Find jobs where learner has highest skill match percentage",
    "parameters": {
        "learner_skills": {"type": "array", "items": {"type": "string"}},
        "min_match_percent": {"type": "number", "default": 50},
        "limit": {"type": "integer", "default": 10}
    }
}
```

### Learner Management Tools

```python
{
    "name": "get_learner_context",
    "description": "Get full learner profile, skills, goals, and progress",
    "parameters": {
        "learner_id": {"type": "string"}
    }
}

{
    "name": "update_learner_profile",
    "description": "Update learner profile information",
    "parameters": {
        "learner_id": {"type": "string"},
        "updates": {"type": "object"}
    }
}

{
    "name": "add_learner_skill",
    "description": "Add a skill to learner's profile",
    "parameters": {
        "learner_id": {"type": "string"},
        "skill_name": {"type": "string"},
        "proficiency_level": {"type": "string"},
        "evidence_source": {"type": "string", "default": "self_reported"}
    }
}

{
    "name": "set_learner_goal",
    "description": "Set or update learner's career goal",
    "parameters": {
        "learner_id": {"type": "string"},
        "target_job_title": {"type": "string"},
        "status": {"type": "string", "default": "exploring"}
    }
}

{
    "name": "create_pathway",
    "description": "Create a learning pathway for the learner",
    "parameters": {
        "learner_id": {"type": "string"},
        "goal_id": {"type": "string"},
        "skills_to_learn": {"type": "array", "items": {"type": "string"}}
    }
}
```

---

## Query Examples

### Search jobs by RIASEC code

```python
import duckdb

# Find Social-Realistic-Investigative jobs
result = duckdb.query("""
    SELECT job_title, company, job_location, job_level, riasec_confidence
    FROM 'data/unified_jobs.parquet'
    WHERE riasec_code = 'SRI'
    ORDER BY riasec_confidence DESC
    LIMIT 10
""").fetchdf()
```

### Get salary and market demand

```python
# Look up salary for "Data Scientist"
result = duckdb.query("""
    SELECT 
        "Job Title",
        "Median Annual Advertised Salary" as salary,
        "Labor Market Tag" as market_status
    FROM 'data/salary_reference.parquet'
    WHERE "Job Title" ILIKE '%data scientist%'
""").fetchdf()
```

### Calculate skill gap

```python
def calculate_skill_gap(learner_skills: list[str], job_skills_string: str) -> dict:
    required = set(s.strip() for s in job_skills_string.split(','))
    has = set(learner_skills)
    return {
        "has": list(has & required),
        "needs": list(required - has),
        "match_percent": round(len(has & required) / len(required) * 100, 1) if required else 0
    }
```

### Find high-demand jobs matching skills

```python
# Jobs in shortage with Python skill
result = duckdb.query("""
    SELECT u.job_title, u.company, s."Median Annual Advertised Salary" as salary,
           s."Labor Market Tag" as demand
    FROM 'data/unified_jobs.parquet' u
    JOIN 'data/salary_reference.parquet' s 
        ON LOWER(u.job_title) LIKE '%' || LOWER(s."Job Title") || '%'
    WHERE u.job_skills LIKE '%Python%'
    AND s."Labor Market Tag" LIKE '%Shortage%'
    LIMIT 10
""").fetchdf()
```

---

## Project Structure

```
career-stu/
├── CLAUDE.md                    # This file (context for Claude Code)
├── README.md
├── requirements.txt
├── .env.example
│
├── data/
│   ├── unified_jobs.parquet     # 1.3M jobs with RIASEC
│   ├── salary_reference.parquet # 999 jobs with salary/market data
│   ├── riasec_framework.json    # RIASEC definitions
│   └── career_stu.duckdb        # Learner data (created at runtime)
│
├── database/
│   ├── schema.sql               # DuckDB schema for learner tables
│   └── connection.py            # Database connection helper
│
├── tools/
│   ├── __init__.py
│   ├── definitions.py           # All tool definitions
│   ├── job_search_tools.py      # Job database queries
│   ├── riasec_tools.py          # RIASEC matching logic
│   ├── salary_tools.py          # Salary lookups
│   ├── skills_tools.py          # Skill gap calculations
│   ├── learner_tools.py         # Learner profile management
│   └── pathway_tools.py         # Pathway management
│
├── agent/
│   ├── __init__.py
│   ├── system_prompt.py         # System prompt builder
│   ├── context_builder.py       # Builds learner context
│   └── career_stu.py            # Main agent logic
│
├── api/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app
│   └── routes/
│       ├── chat.py              # Chat endpoint
│       └── learner.py           # Learner management
│
├── ui/
│   └── streamlit_app.py         # Quick test interface
│
└── tests/
    ├── test_tools.py
    ├── test_agent.py
    └── test_flows.py
```

---

## Mode-Specific Behavior

### INTAKE Mode

**Trigger:** `learner.status == 'new'` or `profile_complete == False`

**Goals:**
- Gather background (job, industry, experience, education)
- Collect skills (ask what they know, validate claims)
- Understand constraints (time, family, employment status)
- Determine disposition (unclear, discontent, promotion-seeking, called)

**Transitions to:** GOAL_DISCOVERY when `profile_complete == True`

### GOAL_DISCOVERY Mode

**Trigger:** `goal_status == 'exploring'` or `goal_status is NULL`

**Goals:**
- Explore career interests through conversation
- Infer RIASEC type from skills and preferences
- Search matching jobs using `search_jobs_by_riasec`
- Show salary and market demand data
- Help learner commit to a goal

**Key Questions:**
- "Do you prefer working with people, data, or things?"
- "Are you more creative or analytical?"
- "Do you like leading teams or working independently?"

**Transitions to:** PATHWAY when learner commits to a goal

### PATHWAY Mode

**Trigger:** `goal_status == 'committed'` AND no active pathway

**Goals:**
- Calculate skill gap between learner and target job
- Generate ordered list of skills to learn
- Estimate time based on weekly_study_hours
- Create pathway record in database

**Transitions to:** LEARNING when pathway is accepted

### LEARNING Mode

**Trigger:** Has active pathway

**Goals:**
- Know current skill in progress
- Recommend learning content (future: Learn Anything integration)
- Answer questions about the skill
- Track completion and update progress
- Celebrate milestones

**Transitions to:** GOAL_DISCOVERY if learner changes goal

---

## Environment Variables

```bash
# .env.example

# Database paths
DUCKDB_PATH=./data/career_stu.duckdb
JOBS_PARQUET_PATH=./data/unified_jobs.parquet
SALARY_PARQUET_PATH=./data/salary_reference.parquet
RIASEC_JSON_PATH=./data/riasec_framework.json

# LLM
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key

# API
API_HOST=localhost
API_PORT=8000
```

---

## Quick Start

```bash
# 1. Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Verify data files exist
ls data/unified_jobs.parquet
ls data/salary_reference.parquet
ls data/riasec_framework.json

# 3. Initialize learner database
python -c "from database.connection import init_db; init_db()"

# 4. Run API
uvicorn api.main:app --reload

# 5. Or run Streamlit UI
streamlit run ui/streamlit_app.py
```

---

## MVP Scope

### In Scope
- [x] Four modes (intake, goal discovery, pathway, learning)
- [x] RIASEC-based job matching
- [x] 1.3M job database with skills
- [x] Salary and market demand data (999 jobs)
- [x] Skill gap calculation
- [x] DuckDB storage for learner data
- [x] Pathway generation
- [ ] Simple chat API
- [ ] Basic UI

### Out of Scope (Future)
- [ ] Learn Anything content integration
- [ ] Vector database for semantic search
- [ ] Calendar integration
- [ ] Multi-user authentication
- [ ] Production deployment

---

## Testing Checklist

### Flow 1: New Learner Intake
- [ ] Career STU starts intake for new learner
- [ ] Gathers background, constraints, skills
- [ ] Saves profile to database
- [ ] Transitions to goal discovery

### Flow 2: Goal Discovery with RIASEC
- [ ] Infers RIASEC from learner skills
- [ ] Shows matching jobs by RIASEC
- [ ] Displays salary and market demand
- [ ] Saves committed goal

### Flow 3: Pathway Creation
- [ ] Calculates skill gap correctly
- [ ] Creates reasonable pathway
- [ ] Respects time constraints
- [ ] Saves pathway to database

### Flow 4: Learning Support
- [ ] Knows current progress
- [ ] Recommends next skill
- [ ] Updates progress when completed
