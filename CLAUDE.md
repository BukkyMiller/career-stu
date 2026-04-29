# Career STU - AI Career Support Assistant

**Project:** Career STU MVP Prototype
**Version:** 0.4 (Four Capitals + "Here to There" Blueprint)

## What Is This?

Career STU is an AI career assistant that guides learners from "here" to "there" — from their current skills to their career destination.

**Architecture:** Single agent with four operating modes, switching prompts based on learner state. Not multi-agent — one `CareerSTU` class loads different system prompts depending on learner context.

**Core Promise:** The learner never starts over. Every skill they've developed, every job they've held — it all counts. The system meets them where they are and builds a path to where they want to go.

## The Four Modes

| Mode | Trigger | Purpose |
|------|---------|---------|
| **INTAKE** | `learner.status == 'new'` or `profile_complete == False` | 13-item intake questionnaire, skills input |
| **CAREER_EXPLORATORY** | `goal_status == 'exploring'` or NULL | 7 career exploration methods, RIASEC matching |
| **PATHWAY** | `goal_status == 'committed'` AND no pathway | Four-Capital gap analysis, pathway creation |
| **LEARNING** | Has active pathway | Content delivery, progress tracking |

## Four Capitals Framework

Career readiness measured across four dimensions:

| Capital | What It Measures |
|---------|-----------------|
| **KSA** | Technical skills, domain knowledge, credentials |
| **Behavioral** | Professional norms, communication, industry culture |
| **Social** | Network, mentors, community access |
| **Navigation** | Job search, interviewing, negotiating, advancement |

See `docs/FOUR_CAPITALS.md` for full framework details.

## Quick Start

```bash
# 1. Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Verify data files exist
ls data/unified_jobs.parquet data/salary_reference.parquet data/riasec_framework.json

# 3. Initialize database
python -c "from database.connection import init_db; init_db()"

# 4. Run Streamlit UI
streamlit run ui/streamlit_app.py

# 5. Or run API
uvicorn api.main:app --reload
```

## Project Structure

```
career-stu/
├── CLAUDE.md              # This file (quick reference)
├── docs/                  # Detailed documentation
│   ├── FOUR_CAPITALS.md   # Capital framework details
│   ├── TOOLS_REFERENCE.md # All 22 tools with parameters
│   ├── PROMPT_GUIDE.md    # How prompts work
│   ├── DATABASE.md        # Schema and queries
│   ├── RIASEC.md          # RIASEC framework
│   └── TESTING.md         # Testing checklist
│
├── agent/
│   ├── career_stu.py      # Main agent (Anthropic)
│   ├── career_stu_openai.py
│   ├── system_prompt.py   # Mode router + prompt builder
│   └── prompts/           # 4 mode-specific prompt files
│       ├── orchestrator_intake.md
│       ├── career_explorer_goal_setting.md
│       ├── career_path.md
│       └── course_creation_learning.md
│
├── tools/                 # 22 tool implementations
│   ├── definitions.py     # Anthropic-compatible schemas
│   ├── job_search_tools.py
│   ├── riasec_tools.py
│   ├── salary_tools.py
│   ├── skills_tools.py
│   ├── learner_tools.py
│   └── pathway_tools.py
│
├── api/                   # FastAPI endpoints
│   ├── main.py
│   └── routes/
│
├── ui/
│   └── streamlit_app.py   # Test interface
│
├── database/
│   ├── schema.sql         # DuckDB schema (7 tables)
│   └── connection.py
│
└── data/
    ├── unified_jobs.parquet      # 1.3M jobs with RIASEC
    ├── salary_reference.parquet  # 999 jobs with salary/market
    └── riasec_framework.json     # RIASEC definitions
```

## Data Files

| File | Size | Contents |
|------|------|----------|
| `unified_jobs.parquet` | 204 MB | 1.3M jobs with RIASEC codes, skills, levels |
| `salary_reference.parquet` | 58 KB | 999 jobs with salary, market demand tags |
| `riasec_framework.json` | 35 KB | RIASEC type definitions + 316 skill indicators |

## Key File References

| What | Where |
|------|-------|
| Mode routing logic | `agent/system_prompt.py` |
| Tool definitions | `tools/definitions.py` |
| Prompt loading | `agent/prompts/__init__.py` |
| Database connection | `database/connection.py` |

## Tool Categories (22 total)

- **Job Search (3):** `search_jobs`, `search_jobs_by_riasec`, `get_job_details`
- **RIASEC (3):** `infer_riasec_from_skills`, `get_riasec_description`, `compare_riasec_codes`
- **Salary & Market (4):** `get_salary_info`, `get_comprehensive_market_data`, `get_high_demand_jobs`, `get_market_insights`
- **Skills (3):** `calculate_skill_gap`, `find_jobs_by_skill_match`, `suggest_next_skills`
- **Learner (5):** `get_learner_context`, `update_learner_profile`, `add_learner_skill`, `set_learner_goal`, `create_learner`
- **Pathway (4):** `create_pathway`, `update_pathway_progress`, `get_pathway_details`, `get_current_skill`

See `docs/TOOLS_REFERENCE.md` for full schemas and parameters.

## Environment Variables

```bash
# .env
DUCKDB_PATH=./data/career_stu.duckdb
JOBS_PARQUET_PATH=./data/unified_jobs.parquet
SALARY_PARQUET_PATH=./data/salary_reference.parquet
RIASEC_JSON_PATH=./data/riasec_framework.json
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key
```

## Key Behaviors

1. **One question at a time** — Never ask multiple questions in the same message
2. **Labor Market Search Protocol** — Search app database first, then web search fallback. Never say "we don't have that data"
3. **Skills Input Protocol** — 4 options: suggest & confirm, upload resume, share URL, tell directly
4. **Mode transitions** — Profile complete → exploration → goal committed → pathway → learning

## Detailed Documentation

- `docs/FOUR_CAPITALS.md` — Capital framework, gap analysis, competency maps
- `docs/TOOLS_REFERENCE.md` — All 22 tools with parameters and examples
- `docs/PROMPT_GUIDE.md` — Agent modes, prompt structure, transitions
- `docs/DATABASE.md` — Schema, tables, indexes, queries
- `docs/RIASEC.md` — RIASEC types, stack logic, matching
- `docs/TESTING.md` — Testing checklist, flow validation
