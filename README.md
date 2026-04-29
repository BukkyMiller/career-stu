# Career STU

**AI-Powered Career Support Assistant**

Career STU is an AI career assistant that guides learners from "here" (where they are now) to "there" (their career goals) through personalized RIASEC matching, skill gap analysis, and adaptive learning pathways.

## What is Career STU?

Career STU uses a **single-agent architecture with four operating modes**. One agent class loads different system prompts based on learner state:

1. **INTAKE** — Onboards new learners with 13-item questionnaire and skills input
2. **CAREER_EXPLORATORY** — 7 exploration methods including RIASEC assessment, salary-first search, and "Would You Rather" games to help learners discover and commit to a career goal
3. **PATHWAY** — Four-Capital gap analysis and pathway construction with timeline negotiation
4. **LEARNING** — Project-based courses with 4 learning styles, assessments, and progress tracking

**Key Principle:** The learner experiences one seamless assistant — mode transitions are automatic and invisible.

## Key Features

### Mode-Switching Intelligence
- **Single agent** that dynamically loads prompts based on learner state
- **Context-aware** responses that remember the learner's full journey
- **Automatic transitions** between modes based on learner progress
- **22 specialized tools** for job search, salary lookup, skills analysis, and pathway creation

### Data-Driven Career Matching
- **1.3M jobs** database with detailed skills and RIASEC classifications
- **Salary data** and market demand analysis for 999+ job titles
- **RIASEC framework** with 120 three-letter personality codes and 316 skill indicators
- **Skill gap calculator** comparing current skills to target roles

### 7 Career Exploration Methods (CAREER_EXPLORATORY mode)
- Full RIASEC Assessment (48 questions)
- Quick 5-Question Quiz
- "Would You Rather" binary choices
- Day in the Life walkthroughs
- YouTube Career Videos
- Skills You Enjoy Picker
- Salary-First Explorer

### Personalized Learning Pathways (PATHWAY mode)
- **5-dimension gap analysis**: technical skills, competencies, credentials, network, experience
- **Parallel-track pathways** optimized for learner constraints
- **Time estimates** with 20% buffer based on weekly availability
- **Learner negotiation** on timeline and priorities

### Project-Based Learning (LEARNING mode)
- **4 learning style choices** per skill
- **Real-world projects** with rubrics and case studies
- **Assessments** with 80%+ pass threshold
- **Progress tracking** with milestone celebrations

### RIASEC Career Matching
Based on Holland's career theory, RIASEC classifies interests into 6 types:
- **R (Realistic)**: Hands-on, practical, mechanical
- **I (Investigative)**: Analytical, intellectual, scientific
- **A (Artistic)**: Creative, expressive, original
- **S (Social)**: Helping, teaching, counseling
- **E (Enterprising)**: Leading, persuading, managing
- **C (Conventional)**: Organizing, detail-oriented, systematic

Your 3-letter code (e.g., "IRA") reveals your unique career "superpower stack" — Position 1 is WHY you act, Position 2 is HOW, Position 3 is WHAT strengthens your impact.

## Quick Start

### Prerequisites
- Python 3.9+
- Anthropic API key OR OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/BukkyMiller/career-stu.git
cd career-stu

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your API key to .env

# Initialize database
python3 -c "from database.connection import init_db; init_db()"

# Launch the UI
streamlit run ui/streamlit_app.py
```

**Note:** The large job database files (400MB+) are not in the repository. See `data/DATA.md` for instructions on obtaining them.

### Your First Session

1. **Open** http://localhost:8501
2. **Create** a learner profile with your email
3. **Chat** with Career STU about your background and goals
4. **Watch** as the modes guide you through discovery, planning, and learning

Example conversation:
```
You: "Hi! I'm a software developer with 3 years experience in Python and SQL.
      I'm interested in transitioning to data science."

Career STU: "Great to meet you! Let me help you explore data science careers.
             First, I'll analyze your skills to understand your RIASEC type..."
```

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│              SINGLE AGENT + FOUR OPERATING MODES                  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │           AGENT 1: ORCHESTRATOR & INTAKE                   │  │
│  │           Routes messages + handles onboarding             │  │
│  └──────┬──────────────────┬──────────────────┬──────────────┘  │
│         │                  │                  │                   │
│         ▼                  ▼                  ▼                   │
│  ┌─────────────┐   ┌─────────────┐   ┌──────────────────┐      │
│  │  AGENT 2:   │   │  AGENT 3:   │   │  AGENT 4:        │      │
│  │  Explorer & │   │  Career     │   │  Course Creator   │      │
│  │  Goal Set   │   │  Path       │   │  & Learning       │      │
│  └──────┬──────┘   └──────┬──────┘   └────────┬─────────┘      │
│         └──────────────────┴───────────────────┘                 │
│                            │                                      │
│                    ┌───────┴────────┐                             │
│                    │   22 TOOLS     │                             │
│                    └───────┬────────┘                             │
└────────────────────────────┼─────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐        ┌─────▼──────┐       ┌────▼────┐
   │ DuckDB  │        │  1.3M Jobs │       │  APIs   │
   │ Learner │        │  Parquet   │       │  LLM    │
   │  Data   │        │  Files     │       │ (Claude)│
   └─────────┘        └────────────┘       └─────────┘
```

## The Four Modes

### INTAKE Mode
**Goal:** Build learner profiles

Handles new learner onboarding with 13-item questionnaire covering background, skills, constraints, and disposition.

**Transition:** Profile complete → CAREER_EXPLORATORY

### CAREER_EXPLORATORY Mode
**Goal:** Help learner find and commit to a career direction

Offers 7 exploration methods to match different learner preferences. Uses RIASEC inference, job database searches, and salary/market data to help learners converge on a career goal. Validates feasibility before committing.

**Transition:** Goal committed → PATHWAY

### PATHWAY Mode
**Goal:** Create a personalized learning plan

Runs Four-Capital gap analysis (KSA, Behavioral, Social, Navigation). Builds pathways with time estimates. Negotiates timeline with the learner based on their constraints.

**Transition:** Pathway accepted → LEARNING

### LEARNING Mode
**Goal:** Support daily learning with project-based content

Creates courses aligned to each skill in the pathway. Offers 4 learning style choices, real-world projects with rubrics, case studies, YouTube curation, and assessments. Tracks progress and celebrates milestones.

**Transition:** Goal changed → back to CAREER_EXPLORATORY

## Available Tools

Career STU has 22 specialized tools:

**Job Search (3):**
- `search_jobs` - Find by title, skills, location, level
- `search_jobs_by_riasec` - Find by personality match
- `get_job_details` - Get complete job information

**RIASEC Analysis (3):**
- `infer_riasec_from_skills` - Predict personality type
- `get_riasec_description` - Explain codes
- `compare_riasec_codes` - Assess job fit

**Salary & Market (4):**
- `get_salary_info` - Salary and demand data
- `get_comprehensive_market_data` - Combined salary + jobs data
- `get_high_demand_jobs` - Find hot careers
- `get_market_insights` - Overall market insights

**Skills Analysis (3):**
- `calculate_skill_gap` - Compare to target role
- `find_jobs_by_skill_match` - Find best-fit jobs
- `suggest_next_skills` - Recommend skills to learn

**Learner Management (5):**
- `get_learner_context` - Full profile and progress
- `update_learner_profile` - Update information
- `add_learner_skill` - Track new skills
- `set_learner_goal` - Define career targets
- `create_learner` - Create new learner record

**Pathway (4):**
- `create_pathway` - Generate learning plans
- `update_pathway_progress` - Update skill status
- `get_pathway_details` - Get full pathway info
- `get_current_skill` - Get current skill to work on

## Usage Options

### Option 1: Streamlit UI (Recommended for Testing)

```bash
streamlit run ui/streamlit_app.py
```

Interactive chat interface with real-time mode display, profile and progress viewer, conversation history, and easy learner switching.

### Option 2: FastAPI Backend

```bash
uvicorn api.main:app --reload
```

RESTful API with endpoints for:
- `/chat/message` - Send messages to agent
- `/chat/mode/{learner_id}` - Get current mode
- `/learner/create` - Create new learner
- `/learner/context/{learner_id}` - Get full context

**API Docs:** http://localhost:8000/docs

### Option 3: Python SDK

```python
from agent.career_stu import create_agent

agent = create_agent("learner-id")
response = agent.chat("Tell me about data science careers")
```

## Data Sources

### Job Database (1.3M jobs)
- LinkedIn job postings with skills and RIASEC codes
- Confidence scores for classifications
- Job levels (Entry, Mid-Senior, Director, etc.)
- Companies and locations

### Salary Reference (999 jobs)
- Median annual salaries
- Labor market tags (Shortage/Surplus)
- Supply/demand ratios
- Recent posting volumes

### RIASEC Framework
- 120 three-letter code combinations
- 316 skill-to-type indicators
- Career themes and descriptions
- "Superpower gift" interpretations

## Testing

```bash
# Run all tests
pytest tests/ -v

# Test specific components
pytest tests/test_tools.py -v
pytest tests/test_agent.py -v
pytest tests/test_flows.py -v

# System verification
python3 test_system.py
```

## LLM Provider Support

Career STU works with:
- **Anthropic Claude** (Claude 3.5 Sonnet)
- **OpenAI GPT** (GPT-4 Turbo)

Configure in `.env`:
```bash
LLM_PROVIDER=openai  # or anthropic
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
```

## Project Structure

```
career-stu/
├── .claude/
│   └── skills/             # Integrated Anthropic skills
├── agent/                  # Single agent with 4 modes
│   ├── system_prompt.py        # Prompt builder (loads from prompts/)
│   ├── career_stu.py           # Main agent (Anthropic)
│   ├── career_stu_openai.py    # OpenAI version
│   ├── context_builder.py      # Learner context management
│   └── prompts/                # Agent prompt markdown files
│       ├── __init__.py             # Prompt loader module
│       ├── ORCHESTRATION_OVERVIEW.md
│       ├── orchestrator_intake.md          # INTAKE mode
│       ├── career_explorer_goal_setting.md # EXPLORATORY mode
│       ├── career_path.md                  # PATHWAY mode
│       └── course_creation_learning.md     # LEARNING mode
├── api/                    # FastAPI backend
│   └── routes/             # Chat and learner endpoints
├── database/               # DuckDB schema
├── data/                   # Job and RIASEC data
├── scripts/                # RIASEC classifier utilities
├── tools/                  # 22 agent tools
├── ui/                     # Streamlit interface
└── tests/                  # Test suite
```

## Integrated Anthropic Skills

Career STU includes four powerful skills from [Anthropic's Skills Repository](https://github.com/anthropics/skills) to enhance the learning experience:

### Frontend Design
Create production-grade UI for course creation and learning dashboards
```bash
/frontend-design
```

### Web Artifacts Builder
Build interactive modules, widgets, and simulations for course content
```bash
/web-artifacts-builder
```

### Webapp Testing
Automated E2E testing with Playwright for quality assurance
```bash
/webapp-testing
```

### Canvas Design
Generate visual artifacts like infographics, posters, and certificates
```bash
/canvas-design
```

**Learn more:** See `.claude/skills/SKILLS_OVERVIEW.md` for detailed usage guide.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Key areas for contribution:
1. **Career Exploration Methods** - Add new interactive exploration experiences
2. **Learning Content** - Integrate with Learn Anything API
3. **Analytics** - Track learner outcomes and success metrics
4. **UI Enhancement** - Leverage integrated skills for better interfaces

## License

[Add your license here]

## Credits

- **RIASEC Framework** - Based on Holland's career theory
- **Job Data** - LinkedIn job postings with skill analysis
- **AI Models** - Anthropic Claude & OpenAI GPT-4

## Support

- **Issues:** https://github.com/BukkyMiller/career-stu/issues
- **Discussions:** [Coming soon]
- **Documentation:** See `CLAUDE.md` for detailed specs

---

**Built to help people find their career path**

Start your journey: `streamlit run ui/streamlit_app.py`
