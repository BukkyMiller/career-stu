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
├── agent/                  # Agent logic (system prompts, context)
├── api/                    # FastAPI application
│   └── routes/            # API endpoints
├── database/              # DuckDB schema and connection
├── data/                  # Parquet files and RIASEC framework
├── scripts/               # Utility scripts (including riasec_classifier.py)
├── tests/                 # Test files
├── tools/                 # Tool implementations for agent
├── ui/                    # Streamlit interface
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── CLAUDE.md             # Detailed project documentation
```

## Testing the Four Modes

### 1. INTAKE Mode
Start a new conversation. Career STU will ask about:
- Your current job and background
- Your skills and proficiency levels
- Time constraints and study availability
- Why you're exploring career options

### 2. GOAL_DISCOVERY Mode
After completing your profile, Career STU will:
- Infer your RIASEC type from your skills
- Show matching job opportunities
- Display salary and market demand data
- Help you commit to a career goal

### 3. PATHWAY Mode
Once you commit to a goal, Career STU will:
- Calculate your skill gap
- Generate an ordered learning pathway
- Estimate time based on your availability
- Create a trackable pathway

### 4. LEARNING Mode
With an active pathway, Career STU will:
- Track your current skill progress
- Recommend learning content
- Answer questions about skills
- Update completion status

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

## Next Steps

1. **Try the Streamlit UI** - Easiest way to test the full system
2. **Explore the API** - Check out the Swagger docs at `/docs`
3. **Run the tests** - Ensure everything is working
4. **Read CLAUDE.md** - Detailed documentation on architecture and design

## Development

### Adding New Tools
1. Define tool schema in `tools/definitions.py`
2. Implement function in appropriate `tools/` module
3. Register function in `agent/career_stu.py`
4. Add tests in `tests/test_tools.py`

### Modifying System Prompts
Edit `agent/system_prompt.py` to adjust:
- Base prompt for all modes
- Mode-specific instructions
- Mode transition logic

### Database Schema Changes
1. Update `database/schema.sql`
2. Drop existing database: `rm data/career_stu.duckdb`
3. Reinitialize: `python -c "from database.connection import init_db; init_db()"`

## Support

For questions or issues:
1. Check `CLAUDE.md` for detailed documentation
2. Review test files for usage examples
3. Check the API docs at `/docs`

## License

[Add your license here]
