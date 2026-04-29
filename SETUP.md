# Career STU - Setup Guide

Quick start guide to get Career STU running locally.

## Prerequisites

- Python 3.9+
- pip or conda
- Anthropic API key

## Installation

### 1. Clone and Setup Environment

```bash
# Navigate to project directory
cd career-explorer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Anthropic API key
# nano .env  # or use your preferred editor
```

Update `.env` with your actual API key:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### 3. Initialize Database

```bash
# Run database initialization
python -c "from database.connection import init_db; init_db()"
```

You should see:
```
Verifying data files...
All data files found!

Initializing database...
Database initialized at ./data/career_stu.duckdb
Database ready!
```

### 4. Verify Data Files

Ensure these files exist in the `data/` directory:
- `unified_jobs.parquet` (1.3M jobs)
- `salary_reference.parquet` (999 jobs with salary data)
- `riasec_framework.json` (RIASEC definitions)

## Running the Application

### Option 1: Streamlit UI (Recommended for Testing)

```bash
streamlit run ui/streamlit_app.py
```

This will open a browser window at `http://localhost:8501`

**Using the Streamlit UI:**
1. Enter an email and optional name to create a new learner
2. Start chatting with Career STU
3. Watch the mode change as you progress (shown in sidebar)
4. View learner context anytime using "View Context" button

### Option 2: FastAPI Server

```bash
# Start the API server
uvicorn api.main:app --reload
```

Server will be available at `http://localhost:8000`

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Example API Usage:**

Create a learner:
```bash
curl -X POST http://localhost:8000/learner/create \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "name": "Test User"}'
```

Send a chat message:
```bash
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "learner_id": "your-learner-id",
    "message": "Hello, I want to explore career options"
  }'
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_tools.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## Project Structure

```
career-explorer/
├── agent/                      # Multi-agent system
│   ├── system_prompt.py            # Prompt builder (loads from prompts/)
│   ├── career_stu.py               # Main agent (Anthropic)
│   ├── career_stu_openai.py        # OpenAI version
│   ├── context_builder.py          # Learner context management
│   └── prompts/                    # Agent prompt markdown files
│       ├── __init__.py                 # Prompt loader module
│       ├── ORCHESTRATION_OVERVIEW.md   # Architecture reference
│       ├── orchestrator_intake.md      # Agent 1 prompt
│       ├── career_explorer_goal_setting.md  # Agent 2 prompt
│       ├── career_path.md             # Agent 3 prompt
│       └── course_creation_learning.md # Agent 4 prompt
├── api/                        # FastAPI application
│   └── routes/                     # API endpoints
├── database/                   # DuckDB schema and connection
├── data/                       # Parquet files and RIASEC framework
├── scripts/                    # Utility scripts (including riasec_classifier.py)
├── tests/                      # Test files
├── tools/                      # 15 tool implementations for agents
├── ui/                         # Streamlit interface
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
└── CLAUDE.md                   # Detailed project documentation
```

## Testing the Four Agents

### 1. Agent 1: Orchestrator & Intake
Start a new conversation. Career STU will:
- Ask about your current job and background
- Gather your skills and proficiency levels
- Understand time constraints and study availability
- Determine why you're exploring career options
- Automatically route you to Agent 2 when your profile is complete

### 2. Agent 2: Career Explorer & Goal Setting
After completing your profile, Career STU will:
- Offer you a choice of 7 career exploration methods
- Infer your RIASEC type from your skills and preferences
- Show matching job opportunities with salary data
- Help you converge on and commit to a career goal

### 3. Agent 3: Career Path
Once you commit to a goal, Career STU will:
- Run a 5-dimension gap analysis (skills, competencies, credentials, network, experience)
- Build a parallel-track learning pathway
- Estimate time based on your availability (with 20% buffer)
- Negotiate timeline and priorities with you
- Create a trackable pathway in the database

### 4. Agent 4: Course Creation & Learning
With an active pathway, Career STU will:
- Offer 4 learning style choices for each skill
- Create project-based content with rubrics
- Curate YouTube videos and case studies
- Run assessments (80%+ to pass)
- Track your progress and celebrate milestones

## Troubleshooting

### Database Connection Errors
```bash
# Reinitialize database
python -c "from database.connection import init_db; init_db()"
```

### Missing Data Files
Ensure all parquet files are in the `data/` directory:
```bash
ls -lh data/
```

### Import Errors
Make sure you're in the project root and virtual environment is activated:
```bash
# Check current directory
pwd

# Should show: /path/to/career-explorer

# Activate venv if not already active
source venv/bin/activate
```

### API Key Issues
Verify your `.env` file has the correct API key:
```bash
cat .env | grep ANTHROPIC_API_KEY
```

### Prompt Loading Issues
Verify agent prompt files are present:
```bash
ls agent/prompts/*.md
```

You should see 5 markdown files: `orchestrator_intake.md`, `career_explorer_goal_setting.md`, `career_path.md`, `course_creation_learning.md`, and `ORCHESTRATION_OVERVIEW.md`.

Test prompt loading:
```python
python -c "from agent.prompts import get_all_agent_prompts; print(list(get_all_agent_prompts().keys()))"
```

## Next Steps

1. **Try the Streamlit UI** - Easiest way to test the full system
2. **Explore the API** - Check out the Swagger docs at `/docs`
3. **Run the tests** - Ensure everything is working
4. **Read CLAUDE.md** - Detailed documentation on architecture and design
5. **Review agent prompts** - See `agent/prompts/ORCHESTRATION_OVERVIEW.md` for architecture reference

## Development

### Adding New Tools
1. Define tool schema in `tools/definitions.py`
2. Implement function in appropriate `tools/` module
3. Register function in `agent/career_stu.py`
4. Add tests in `tests/test_tools.py`

### Modifying Agent Prompts
Edit the markdown files in `agent/prompts/`:
- `orchestrator_intake.md` — Agent 1 routing and intake behavior
- `career_explorer_goal_setting.md` — Agent 2 exploration methods and goal setting
- `career_path.md` — Agent 3 gap analysis and pathway construction
- `course_creation_learning.md` — Agent 4 course creation and progress tracking

Prompts are loaded dynamically at runtime — no code changes needed after editing markdown files.

### Modifying Mode-to-Agent Mapping
Edit `agent/prompts/__init__.py` to update the `MODE_TO_AGENT` dictionary or add new agent prompt files to `AGENT_PROMPT_FILES`.

### Modifying Transition Logic
Edit `agent/system_prompt.py` to adjust:
- `determine_mode()` — Controls which mode/agent is active based on learner state
- `determine_agent()` — Maps mode to agent name
- `build_system_prompt()` — Assembles final prompt with dynamic learner context

### Database Schema Changes
1. Update `database/schema.sql`
2. Drop existing database: `rm data/career_stu.duckdb`
3. Reinitialize: `python -c "from database.connection import init_db; init_db()"`

## Support

For questions or issues:
1. Check `CLAUDE.md` for detailed documentation
2. Review `agent/prompts/ORCHESTRATION_OVERVIEW.md` for architecture reference
3. Review test files for usage examples
4. Check the API docs at `/docs`

## License

[Add your license here]
