# Career STU — Multi-Agent Orchestration Architecture (v0.4)

## System Overview

Career STU uses a **Supervisor Agent (Orchestrator)** architecture where a single orchestrator agent manages all learner interactions and delegates work to specialized worker agents. The system is built around the **"Here to There" Learner Experience Blueprint** — guiding learners from where they are now to their career destination.

**The Fundamental Promise:** The learner never starts over. Every skill they've developed, every job they've held, every course they've taken, every informal learning moment — it all counts. The system meets them exactly where they are, sees clearly where they want to go, and builds a living bridge between those two points.

**Core Framework — Four Capitals:** Career readiness is measured across four capitals that actually determine career success:

| Capital | What It Measures |
|---------|-----------------|
| **KSA Capital** | What they know and can do — technical skills, domain knowledge, competencies, credentials |
| **Behavioral Capital** | How they show up professionally — unwritten rules, industry culture, communication norms |
| **Social Capital** | Who they know and can access — professional network, mentors, community membership |
| **Navigation Capital** | How they navigate systems — job search, interviewing, negotiating, career advancement |

```
                         ┌──────────────┐
                         │   LEARNER    │
                         │   (Chat UI)  │
                         └──────┬───────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│              AGENT 1: ORCHESTRATOR & INTAKE AGENT                      │
│                                                                        │
│  Responsibilities:                                                     │
│  • Single entry point for ALL learner messages                        │
│  • Analyzes intent and routes to correct worker agent                 │
│  • Directly handles INTAKE mode for new/incomplete profiles           │
│  • Manages state transitions and conversation continuity              │
│  • Returns consolidated responses to learner                          │
│  • Owns learner status and conversation log                           │
│  • Gathers early capital signals during intake                        │
│  • Enforces one-question-at-a-time conversation rule                  │
│                                                                        │
│  Routing Logic:                                                        │
│  ├── New/incomplete profile → Handle INTAKE directly                  │
│  ├── Exploring careers → Delegate to Agent 2 (Exploratory)            │
│  ├── Setting/refining goal → Delegate to Agent 2 (Goal Setting)      │
│  ├── Needs career pathway → Delegate to Agent 3 (Pathway)            │
│  └── Ready to learn → Delegate to Agent 4 (Learning)                 │
│                                                                        │
└────────┬──────────────────┬──────────────────┬────────────────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────────────┐
│    AGENT 2     │ │    AGENT 3     │ │       AGENT 4          │
│ Career Explorer│ │  Career Path   │ │  Course Creation       │
│ & Goal Setting │ │    Agent       │ │  & Learning Agent      │
│                │ │                │ │                        │
│ MODES:         │ │ MODE:          │ │ MODE:                  │
│ • Exploratory  │ │ • Pathway      │ │ • Learning             │
│ • Goal Setting │ │                │ │                        │
│                │ │ 4-Capital gap  │ │ Content for ALL 4      │
│ 7 exploration  │ │ analysis with  │ │ capitals: KSA courses, │
│ methods incl.  │ │ skill gap      │ │ behavioral exercises,  │
│ RIASEC, quiz,  │ │ algorithm,     │ │ social activities,     │
│ salary, videos │ │ competency map │ │ navigation prep.       │
│ + labor market │ │ presentation,  │ │ Continuous embedded    │
│ intelligence   │ │ negotiation    │ │ assessment. Multi-     │
│ w/ web search  │ │               │ │ sourced learning.      │
└────────────────┘ └────────────────┘ └────────────────────────┘
```

## Agent Summary

| Agent | File | Modes | Key Capabilities |
|-------|------|-------|-----------------|
| **Agent 1: Orchestrator & Intake** | `orchestrator_intake.md` | Orchestration + INTAKE | Routes messages, 13-item intake gate, Skills Input Protocol (suggest/resume/URL/manual), early capital signals, one-question-at-a-time |
| **Agent 2: Career Explorer & Goal Setting** | `career_explorer_goal_setting.md` | CAREER_EXPLORATORY + CAREER_GOAL_SETTING | 7 mandatory exploration methods, RIASEC Stack Logic, labor market intelligence with web search fallback, goal validation with Four Capitals gap summary |
| **Agent 3: Career Path** | `career_path.md` | PATHWAY | Four-Capital gap analysis, skill gap calculation algorithm, competency map presentation, parallel capital tracks, mandatory negotiation, stepping-stone role suggestions |
| **Agent 4: Course Creation & Learning** | `course_creation_learning.md` | LEARNING | 4 learning styles, content for all 4 capitals (KSA courses, behavioral exercises, social activities, navigation prep), continuous embedded assessment, multi-sourced learning |

## Cross-Cutting Capabilities (All Agents)

### Four Capitals Framework
All agents reference and build upon the Four Capitals. Capital assessment begins in intake (Agent 1), deepens during goal setting (Agent 2), drives pathway construction (Agent 3), and shapes learning content (Agent 4).

### Labor Market Data Search Protocol
All agents that look up job/career data follow this protocol:
1. **FIRST:** Search app database (unified_jobs.parquet, salary_reference.parquet)
2. **IF insufficient:** Use `web_search` tool for current market data
3. **NEVER** tell the learner "we don't have that data" and stop
4. **ALWAYS** cite the data source to the learner

### Skills Input Protocol
Learners share skills through 4 options offered during intake (Agent 1) and validated during goal setting (Agent 2):
- **A) Suggest & Confirm** — Agent suggests skills based on background, learner confirms
- **B) Upload Resume** — Parse resume for structured skill extraction
- **C) Share URL** — Parse LinkedIn profile or portfolio page
- **D) Tell Directly** — Learner lists skills manually
Evidence source is tagged: `self_reported`, `resume_parsed`, `url_parsed`, `validated`

### One Question at a Time
All agents follow the rule: **never ask multiple questions in the same message.** The only exceptions are confirmation of extracted data and Agent 3's negotiation questions (presented as a group).

## State Transition Map

```
┌──────────┐   profile_complete (13 items)   ┌───────────────────┐
│  INTAKE  │ ──────────────────────────────▶ │ CAREER_EXPLORATORY│
│ (Agent 1)│                                  │    (Agent 2)      │
└──────────┘                                  └────────┬──────────┘
     │                                                 │
     │ has goal already              Mandatory 7-method menu
     │                               RIASEC assessment
     ▼                               identifies target careers
┌──────────────────────┐                               │
│ CAREER_GOAL_SETTING  │◀──────────────────────────────┘
│     (Agent 2)        │  Validates goal w/ labor market data
└──────────┬───────────┘  Four Capitals gap summary
           │              Skills validation
           │ goal.status == 'committed'
           ▼
┌───────────────────┐
│     PATHWAY       │  Four-Capital gap analysis
│    (Agent 3)      │  Skill gap algorithm
│                   │  Competency map presentation
│                   │  Mandatory negotiation
└────────┬──────────┘
         │
         │ pathway accepted by learner
         ▼
┌───────────────────┐
│     LEARNING      │──────▶ Goal changed? → Back to Agent 2
│    (Agent 4)      │──────▶ Pathway complete? → Job readiness!
│                   │
│ Content for all   │
│ 4 capitals.       │
│ Continuous         │
│ embedded           │
│ assessment.        │
└───────────────────┘
```

## Delegation Context Protocol

When the Orchestrator delegates to a worker agent, it passes structured context:

```json
{
  "learner_id": "<id>",
  "mode": "CAREER_EXPLORATORY | CAREER_GOAL_SETTING | PATHWAY | LEARNING",
  "learner_context": {
    "profile": { "...all profile fields including capital signals..." },
    "skills": [{ "skill_name", "proficiency_level", "evidence_source" }],
    "committed_goal": { "...if exists..." },
    "ksa_gaps": { "...from Agent 2 if available..." },
    "capital_signals": {
      "behavioral": "...",
      "social": "...",
      "navigation": "..."
    },
    "pathway": { "...if exists..." }
  },
  "user_message": "<the learner's latest message>"
}
```

## Shared Database Schema

All agents read from and write to the same DuckDB database (`data/career_stu.duckdb`):

| Table | Primary Writer | Readers | Key Fields |
|-------|---------------|---------|------------|
| `learners` | Agent 1 (Orchestrator) | All agents | id, name, email, status |
| `learner_profiles` | Agent 1 (Intake) | All agents | All profile fields + `behavioral_capital_signal`, `social_capital_signal`, `navigation_capital_signal` |
| `learner_skills` | Agent 1, Agent 2, Agent 4 | All agents | skill_name, proficiency_level, `evidence_source` (self_reported, resume_parsed, url_parsed, validated) |
| `learner_goals` | Agent 2 (Goal Setting) | Agent 1, Agent 3 | target_job_title, target_riasec_code, status, salary_estimate, market_demand |
| `pathways` | Agent 3 (Career Path) | Agent 1, Agent 4 | status, total_skills, completed_skills, estimated_hours |
| `pathway_skills` | Agent 3, Agent 4 | Agent 1, Agent 4 | skill_name, sequence_order, status, estimated_hours, `capital_type` (ksa, behavioral, social, navigation) |
| `conversations` | Agent 1 (Orchestrator) | Agent 1 | mode, summary |

## Shared Data Sources

| Source | File | Used By | Notes |
|--------|------|---------|-------|
| Jobs database (1.3M) | `data/unified_jobs.parquet` | Agent 2, Agent 3 | Primary job/skills data |
| Salary & market data (999) | `data/salary_reference.parquet` | Agent 2, Agent 3 | Salary, demand, supply/demand ratio |
| RIASEC framework | `data/riasec_framework.json` | Agent 1, Agent 2 | 120 codes, 316 skill indicators, Stack Logic |
| Web search (fallback) | `web_search` tool | All agents | When app data is insufficient |

## Communication Protocol

Worker agents never speak to the learner directly. All communication flows through the Orchestrator:

```
Learner → Orchestrator → [Route to Worker Agent] → Worker Response → Orchestrator → Learner
```

Worker agents signal transitions by returning structured metadata:
```json
{
  "status": "profile_complete | goal_committed | pathway_accepted | skill_completed | goal_change_requested | pathway_completed",
  "transition_to": "AGENT_2 | AGENT_3 | AGENT_4 | null",
  "mode": "CAREER_EXPLORATORY | CAREER_GOAL_SETTING | PATHWAY | LEARNING",
  "context": {
    "// handoff data — varies by transition type"
  }
}
```

Only the Orchestrator can execute transitions. Worker agents REQUEST; the Orchestrator DECIDES.

## Mode-to-Agent Mapping

```python
MODE_TO_AGENT = {
    "INTAKE": "orchestrator_intake",
    "CAREER_EXPLORATORY": "career_explorer_goal_setting",
    "CAREER_GOAL_SETTING": "career_explorer_goal_setting",
    "GOAL_DISCOVERY": "career_explorer_goal_setting",  # legacy compat
    "PATHWAY": "career_path",
    "LEARNING": "course_creation_learning",
}
```
