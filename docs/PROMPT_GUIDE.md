# Prompt Guide

Career STU uses a single agent with four operating modes. Each mode loads a different system prompt.

## Mode-to-Prompt Mapping

| Mode | Prompt File | Trigger |
|------|-------------|---------|
| INTAKE | `orchestrator_intake.md` | `learner.status == 'new'` or `profile_complete == False` |
| CAREER_EXPLORATORY | `career_explorer_goal_setting.md` | `goal_status == 'exploring'` or NULL |
| CAREER_GOAL_SETTING | `career_explorer_goal_setting.md` | Learner ready to narrow down |
| PATHWAY | `career_path.md` | `goal_status == 'committed'` AND no pathway |
| LEARNING | `course_creation_learning.md` | Has active pathway |

## Prompt Files Location

```
agent/prompts/
├── __init__.py                    # Prompt loader module
├── ORCHESTRATION_OVERVIEW.md      # Architecture reference
├── orchestrator_intake.md         # INTAKE mode
├── career_explorer_goal_setting.md # CAREER_EXPLORATORY / CAREER_GOAL_SETTING
├── career_path.md                 # PATHWAY mode
└── course_creation_learning.md    # LEARNING mode
```

## How Prompts Load

1. `career_stu.py` calls `build_system_prompt(mode, learner_context)`
2. `system_prompt.py` calls `load_prompt_for_mode(mode)` from `agent/prompts/`
3. The loader maps mode → prompt file
4. Dynamic learner context is appended to the loaded prompt
5. Falls back to legacy inline prompt if markdown file is missing

## Mode Details

### INTAKE Mode (orchestrator_intake.md)

**Purpose:** New learner onboarding

**Key Features:**
- 13-item intake gate
- Skills Input Protocol (4 options)
- Early capital signals gathering
- One question at a time rule

**13-Item Intake Gate:**
1. Name
2. Current job title
3. Industry
4. Years experience
5. Education level
6. Employment status
7. Weekly study hours
8. Preferred study times
9. Has family obligations
10. Preferred format
11. Disposition (unclear, discontent, promotion, called)
12. Skills (via Skills Input Protocol)
13. Early capital signals

**Skills Input Protocol:**
- A) Suggest & Confirm — Agent suggests skills based on background, learner confirms
- B) Upload Resume — Parse resume for structured skill extraction
- C) Share URL — Parse LinkedIn profile or portfolio page
- D) Tell Directly — Learner lists skills manually

### CAREER_EXPLORATORY Mode (career_explorer_goal_setting.md)

**Purpose:** Career exploration and discovery

**Key Features:**
- Mandatory 7-method exploration menu
- RIASEC Stack Logic
- Labor market intelligence with web search fallback
- Converges on 2-3 finalist careers

**7 Career Exploration Methods:**
1. Full RIASEC Assessment (48 questions)
2. Quick 5-Question Quiz
3. Would You Rather (binary choices)
4. Day in the Life
5. YouTube Career Videos
6. Skills You Enjoy Picker
7. Salary-First Explorer

### CAREER_GOAL_SETTING Mode (career_explorer_goal_setting.md)

**Purpose:** Goal validation and commitment

**Key Features:**
- Validates goal with labor market data
- Skills validation via Skills Input Protocol
- Four Capitals gap summary before committing
- Commits goal to database

### PATHWAY Mode (career_path.md)

**Purpose:** Create learning pathway

**Key Features:**
- Four-Capital gap analysis
- Skill gap calculation algorithm
- Competency map presentation
- Celebrates strengths before gaps
- Mandatory negotiation on timeline/priorities
- Stepping-stone suggestions for 3+ year goals

### LEARNING Mode (course_creation_learning.md)

**Purpose:** Content delivery and progress tracking

**Key Features:**
- Mandatory learning style selection (Step 1)
- Content for all 4 capitals
- Continuous embedded assessment
- Checkpoint model (draft → feedback → revise → final)

**4 Learning Styles:**
1. Project-based
2. Structured modules
3. Real-world practice
4. Social learning

**5 Evidence Types:**
1. Micro-assessments
2. Application evidence
3. Conversational demonstrations
4. Project checkpoints
5. Self-assessment reflections

## Cross-Cutting Behaviors

### One Question at a Time
All modes follow this rule: **never ask multiple questions in the same message.**

Exceptions:
- Confirmation of extracted data
- PATHWAY mode negotiation questions (presented as group)

### Labor Market Data Search Protocol
1. **FIRST:** Search app database (unified_jobs.parquet, salary_reference.parquet)
2. **IF insufficient:** Use `web_search` tool for current market data
3. **NEVER** tell the learner "we don't have that data" and stop
4. **ALWAYS** cite the data source to the learner

### Mode Transitions

```
INTAKE → CAREER_EXPLORATORY    (when profile_complete = True)
CAREER_EXPLORATORY → PATHWAY   (when goal committed)
PATHWAY → LEARNING             (when pathway created)
LEARNING → CAREER_EXPLORATORY  (if learner changes goal)
```
