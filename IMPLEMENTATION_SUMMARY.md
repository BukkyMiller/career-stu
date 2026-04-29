# Career STU - Implementation Summary

## What Was Built

A complete MVP implementation of Career STU, an AI-powered career support assistant using a **single-agent architecture with four operating modes**. One `CareerSTU` class loads different system prompts based on learner state, guiding them through intake, career exploration, pathway planning, and learning.

## Architecture

```
Career STU = 1 AGENT + 4 MODES + 22 TOOLS + Data-Driven Matching
```

### Design Pattern

**Single agent, mode-switching architecture.** The agent determines the current mode from learner state and loads the appropriate system prompt. This is NOT multi-agent — it's one agent that changes behavior based on context.

### Core Components

#### 1. Agent Prompt System (`agent/prompts/`)
Four mode-specific markdown prompts loaded dynamically at runtime:

- **`orchestrator_intake.md`** (INTAKE mode) — 13-item intake questionnaire, 5 intake dimensions, skills input protocol
- **`career_explorer_goal_setting.md`** (CAREER_EXPLORATORY mode) — 7 career exploration methods, RIASEC matching, goal commitment workflow
- **`career_path.md`** (PATHWAY mode) — Four-Capital gap analysis, pathway creation, timeline negotiation
- **`course_creation_learning.md`** (LEARNING mode) — 4 learning styles, project design, progress tracking

#### 2. Agent Layer (`agent/`)
- **system_prompt.py** — Mode router + prompt builder; `determine_mode()` reads learner state, `build_system_prompt()` loads the appropriate prompt
- **context_builder.py** — Conversation history management
- **career_stu.py** — Main agent with Anthropic API, 22-tool registry, multi-turn tool execution loop
- **career_stu_openai.py** — OpenAI-compatible version with same 22-tool registry

#### 3. Database Layer (`database/`)
- **schema.sql** — DuckDB schema (7 tables: learners, skills, goals, pathways, pathway_skills, conversation_history, sessions)
- **connection.py** — Database connection manager with initialization

#### 4. Tools Layer (`tools/`)
All 22 tools implemented with Anthropic-compatible schemas:

**Job Search (3):**
- `search_jobs` — Search by title, skills, location, level
- `search_jobs_by_riasec` — Find jobs matching RIASEC codes
- `get_job_details` — Get full job information

**RIASEC (3):**
- `infer_riasec_from_skills` — Predict RIASEC from skill list
- `get_riasec_description` — Get code descriptions and themes
- `compare_riasec_codes` — Compare learner vs job fit

**Salary & Market (4):**
- `get_salary_info` — Lookup salary and demand data
- `get_comprehensive_market_data` — Combined salary + jobs database query
- `get_high_demand_jobs` — Find jobs with labor shortages
- `get_market_insights` — Overall market insights by category

**Skills (3):**
- `calculate_skill_gap` — Compare learner to job requirements
- `find_jobs_by_skill_match` — Find best-fit jobs by skill match %
- `suggest_next_skills` — Recommend skills to learn next

**Learner (5):**
- `get_learner_context` — Full profile, skills, goals, progress
- `update_learner_profile` — Update learner information
- `add_learner_skill` — Add skills to profile
- `set_learner_goal` — Set career goals
- `create_learner` — Create new learner record

**Pathway (4):**
- `create_pathway` — Generate learning pathway
- `update_pathway_progress` — Update skill status in pathway
- `get_pathway_details` — Get full pathway with all skills
- `get_current_skill` — Get current skill to work on

#### 5. API Layer (`api/`)
FastAPI application with two route modules:

**Chat Routes:**
- `POST /chat/message` — Send message and get response
- `POST /chat/reset` — Reset conversation
- `GET /chat/mode/{learner_id}` — Get current mode

**Learner Routes:**
- `POST /learner/create` — Create new learner
- `GET /learner/context/{learner_id}` — Get full context
- `POST /learner/profile/update` — Update profile
- `POST /learner/skill/add` — Add skill
- `POST /learner/goal/set` — Set goal

#### 6. UI Layer (`ui/`)
- **streamlit_app.py** — Interactive chat interface with learner creation, real-time mode display, context viewer

## The Four Modes

| Mode | Trigger | Purpose |
|------|---------|---------|
| **INTAKE** | `learner.status == 'new'` or `profile_complete == False` | 13-item intake questionnaire, skills input |
| **CAREER_EXPLORATORY** | `goal_status == 'exploring'` or NULL | 7 exploration methods, RIASEC matching |
| **PATHWAY** | `goal_status == 'committed'` AND no pathway | Four-Capital gap analysis, pathway creation |
| **LEARNING** | Has active pathway | Content delivery, progress tracking |

## Data Integration

### Jobs Database (1.3M jobs)
- Unified job listings with RIASEC classifications
- Skills, company, location, level data
- Confidence scores for RIASEC assignments

### Salary Reference (999 jobs)
- Median salaries
- Labor market tags (Shortage/Surplus)
- Recent posting volumes

### RIASEC Framework
- 120 three-letter code combinations
- Career themes and descriptions
- 316 skill indicators for classification

## Key Design Decisions

### 1. Single Agent with Mode-Switching
One agent class loads different system prompts based on learner state. Simpler than multi-agent, easier to maintain, same user experience.

### 2. Markdown-Based Prompt System
Agent prompts stored as markdown files in `agent/prompts/`, loaded dynamically. Enables versioning and editing without code changes.

### 3. 22 Tools Fully Wired
All 22 tools are imported and registered in both `career_stu.py` and `career_stu_openai.py` tool_functions dicts.

### 4. Database-First Approach
All learner data persists in DuckDB for fast local queries, no external dependencies.

### 5. Four Capitals Framework
Career readiness measured across: KSA (technical), Behavioral (professional norms), Social (network), Navigation (job search skills).

## File Statistics

```
Agent Prompts: 4 mode-specific markdown files
Tool Definitions: 22 tools
Database Tables: 7
API Endpoints: 8
```

## Ready to Use

### Installation:
```bash
pip install -r requirements.txt
cp .env.example .env  # Add API key
python3 -c "from database.connection import init_db; init_db()"
```

### Run Streamlit:
```bash
streamlit run ui/streamlit_app.py
```

### Run API:
```bash
uvicorn api.main:app --reload
```

## 22 Tools (Final Reference)

**Job Search (3)**
1. search_jobs
2. search_jobs_by_riasec
3. get_job_details

**RIASEC (3)**
4. infer_riasec_from_skills
5. get_riasec_description
6. compare_riasec_codes

**Salary & Market (4)**
7. get_salary_info
8. get_comprehensive_market_data
9. get_high_demand_jobs
10. get_market_insights

**Skills (3)**
11. calculate_skill_gap
12. find_jobs_by_skill_match
13. suggest_next_skills

**Learner (5)**
14. get_learner_context
15. update_learner_profile
16. add_learner_skill
17. set_learner_goal
18. create_learner

**Pathway (4)**
19. create_pathway
20. update_pathway_progress
21. get_pathway_details
22. get_current_skill

---

**Version:** 0.4 (Four Capitals + "Here to There" Blueprint)
**Architecture:** Single agent with four operating modes
**Status:** Ready for Testing
