# Career STU 🎓

**AI-Powered Career Support Assistant**

Career STU is an intelligent agent that guides learners from "here" (where they are now) to "there" (their career goals) through personalized RIASEC matching, skill gap analysis, and adaptive learning pathways.

## 🌟 What is Career STU?

Career STU combines four capabilities into a single conversational AI agent:

1. **Intake** - Understand who the learner is and what skills they have
2. **Goal Discovery** - Help identify career goals using RIASEC personality matching
3. **Pathway** - Generate personalized learning paths to reach the goal
4. **Learning Support** - Guide learner through content and track progress

**Key Principle:** ONE agent with FOUR MODES, not four separate agents.

## 🎯 Key Features

### 🤖 Intelligent Agent System
- **Adaptive modes** that automatically transition based on learner progress
- **Conversational interface** powered by GPT-4 or Claude
- **Context-aware** responses that remember your journey
- **15 specialized tools** for job search, salary lookup, and skills analysis

### 📊 Data-Driven Career Matching
- **1.3M jobs** database with detailed skills and RIASEC classifications
- **Salary data** and market demand analysis for 999+ job titles
- **RIASEC framework** with 120 three-letter personality codes
- **Skill gap calculator** comparing your skills to target roles

### 🎯 Personalized Learning Pathways
- **Automatic skill gap analysis** between current and target roles
- **Ordered learning sequences** optimized for your constraints
- **Time estimates** based on your weekly availability
- **Progress tracking** as you complete each skill

### 🔍 RIASEC Career Matching
Based on Holland's career theory, RIASEC classifies interests into 6 types:
- **R (Realistic)**: Hands-on, practical, mechanical
- **I (Investigative)**: Analytical, intellectual, scientific
- **A (Artistic)**: Creative, expressive, original
- **S (Social)**: Helping, teaching, counseling
- **E (Enterprising)**: Leading, persuading, managing
- **C (Conventional)**: Organizing, detail-oriented, systematic

Your 3-letter code (e.g., "IRA") reveals your unique career "superpower stack."

## 🚀 Quick Start

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
4. **Watch** as the agent guides you through discovery, planning, and learning

Example conversation:
```
You: "Hi! I'm a software developer with 3 years experience in Python and SQL.
      I'm interested in transitioning to data science."

Career STU: "Great to meet you! Let me help you explore data science careers.
             First, I'll analyze your skills to understand your RIASEC type..."
```

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     CAREER STU AGENT                             │
│                                                                  │
│  ┌──────────┐    ┌──────────────┐    ┌──────────┐    ┌────────┐│
│  │  INTAKE  │───▶│GOAL_DISCOVERY│───▶│ PATHWAY  │───▶│LEARNING││
│  └──────────┘    └──────────────┘    └──────────┘    └────────┘│
│       │                 │                   │              │     │
│       └─────────────────┴───────────────────┴──────────────┘     │
│                            │                                     │
│                    ┌───────┴────────┐                           │
│                    │   15 TOOLS     │                           │
│                    └───────┬────────┘                           │
└────────────────────────────┼──────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐        ┌──────▼──────┐      ┌────▼────┐
   │ DuckDB  │        │   1.3M Jobs │      │  APIs   │
   │ Learner │        │   Parquet   │      │ LLM     │
   │  Data   │        │   Files     │      │ (GPT-4) │
   └─────────┘        └─────────────┘      └─────────┘
```

## 🔧 The Four Modes

### 1️⃣ INTAKE Mode
**Goal:** Build comprehensive learner profile

Career STU gathers:
- Current job and industry
- Skills with proficiency levels
- Time constraints and study availability
- Career motivation (exploring, promotion, transition, etc.)

**Transition:** Profile complete → GOAL_DISCOVERY

### 2️⃣ GOAL_DISCOVERY Mode
**Goal:** Find career direction using RIASEC

Career STU:
- Infers your RIASEC type from skills and preferences
- Shows matching jobs from 1.3M database
- Displays salary data and market demand
- Helps you commit to a specific career goal

**Transition:** Goal committed → PATHWAY

### 3️⃣ PATHWAY Mode
**Goal:** Create personalized learning plan

Career STU:
- Calculates your skill gap vs. target role
- Generates ordered learning sequence
- Estimates time based on your availability
- Creates trackable pathway in database

**Transition:** Pathway accepted → LEARNING

### 4️⃣ LEARNING Mode
**Goal:** Support daily learning and track progress

Career STU:
- Knows your current skill in progress
- Recommends learning resources
- Answers questions about concepts
- Updates completion status
- Celebrates milestones

**Transition:** Goal changed → back to GOAL_DISCOVERY

## 🛠️ Available Tools

Career STU has 15 specialized tools:

**Job Search:**
- `search_jobs` - Find by title, skills, location, level
- `search_jobs_by_riasec` - Find by personality match
- `get_job_details` - Get complete job information

**RIASEC Analysis:**
- `infer_riasec_from_skills` - Predict personality type
- `get_riasec_description` - Explain codes
- `compare_riasec_codes` - Assess job fit

**Market Intelligence:**
- `get_salary_info` - Salary and demand data
- `get_high_demand_jobs` - Find hot careers

**Skills Analysis:**
- `calculate_skill_gap` - Compare to target role
- `find_jobs_by_skill_match` - Find best-fit jobs

**Learner Management:**
- `get_learner_context` - Full profile and progress
- `update_learner_profile` - Update information
- `add_learner_skill` - Track new skills
- `set_learner_goal` - Define career targets
- `create_pathway` - Generate learning plans

## 💻 Usage Options

### Option 1: Streamlit UI (Recommended for Testing)

```bash
streamlit run ui/streamlit_app.py
```

Interactive chat interface with:
- Real-time mode display
- Profile and progress viewer
- Conversation history
- Easy learner switching

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

### Option 3: Python SDK (Coming Soon)

```python
from agent.career_stu import create_agent

agent = create_agent("learner-id")
response = agent.chat("Tell me about data science careers")
```

## 📊 Data Sources

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

## 🧪 Testing

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

## 🔌 LLM Provider Support

Career STU works with:
- **Anthropic Claude** (Claude 3.5 Sonnet)
- **OpenAI GPT** (GPT-4 Turbo)

Configure in `.env`:
```bash
LLM_PROVIDER=openai  # or anthropic
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
```

## 📁 Project Structure

```
career-stu/
├── agent/              # AI agent system
│   ├── system_prompt.py    # Mode-specific prompts
│   ├── career_stu.py       # Main agent (Anthropic)
│   └── career_stu_openai.py # OpenAI version
├── api/                # FastAPI backend
│   └── routes/         # Chat and learner endpoints
├── database/           # DuckDB schema
├── data/               # Job and RIASEC data
├── scripts/            # RIASEC classifier utilities
├── tools/              # 15 agent tools
├── ui/                 # Streamlit interface
└── tests/              # Test suite
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Key areas for contribution:
1. **RIASEC Assessment** - Add conversational 48-question assessment
2. **Learning Content** - Integrate with Learn Anything API
3. **Analytics** - Track learner outcomes and success metrics
4. **UI Enhancement** - Improve Streamlit interface

## 📝 License

[Add your license here]

## 🙏 Credits

- **RIASEC Framework** - Based on Holland's career theory
- **Job Data** - LinkedIn job postings with skill analysis
- **AI Models** - Anthropic Claude & OpenAI GPT-4

## 📞 Support

- **Issues:** https://github.com/BukkyMiller/career-stu/issues
- **Discussions:** [Coming soon]
- **Documentation:** See `CLAUDE.md` for detailed specs

---

**Built with ❤️ to help people find their career path**

Start your journey: `streamlit run ui/streamlit_app.py`
