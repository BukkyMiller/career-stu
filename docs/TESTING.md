# Testing Checklist

Use this checklist to validate Career STU functionality across all modes.

## Test Files

```
tests/
├── test_tools.py    # 5 unit tests for tools
├── test_agent.py    # 6 unit tests for agent
└── test_flows.py    # 4 integration tests
```

## Flow 1: New Learner Intake (INTAKE Mode)

### Acceptance Criteria
- [ ] Career STU starts intake for new learner
- [ ] Asks one question at a time (never multiple)
- [ ] Offers Skills Input Protocol (4 options)
- [ ] Gathers all 13 intake items including early capital signals
- [ ] Saves profile to database with capital signal fields
- [ ] Routes to CAREER_EXPLORATORY when `profile_complete == True`

### 13-Item Intake Gate
1. [ ] Name
2. [ ] Current job title
3. [ ] Industry
4. [ ] Years experience
5. [ ] Education level
6. [ ] Employment status
7. [ ] Weekly study hours
8. [ ] Preferred study times
9. [ ] Has family obligations
10. [ ] Preferred format
11. [ ] Disposition
12. [ ] Skills (via Skills Input Protocol)
13. [ ] Early capital signals

### Skills Input Protocol
- [ ] Option A: Suggest & Confirm works
- [ ] Option B: Upload Resume works
- [ ] Option C: Share URL works
- [ ] Option D: Tell Directly works

## Flow 2: Career Exploration & Goal Setting (CAREER_EXPLORATORY Mode)

### Acceptance Criteria
- [ ] Presents mandatory 7-method exploration menu
- [ ] Runs RIASEC assessment with Stack Logic
- [ ] Uses labor market intelligence (app DB + web search fallback)
- [ ] Shows salary and market demand data
- [ ] Validates goal with Four Capitals gap summary
- [ ] Commits goal and transitions to PATHWAY mode

### 7 Exploration Methods
- [ ] Full RIASEC Assessment (48 questions)
- [ ] Quick 5-Question Quiz
- [ ] Would You Rather
- [ ] Day in the Life
- [ ] YouTube Career Videos
- [ ] Skills You Enjoy Picker
- [ ] Salary-First Explorer

### Labor Market Search Protocol
- [ ] Searches app database first
- [ ] Falls back to web search if needed
- [ ] Never says "we don't have that data"
- [ ] Cites data source to learner

## Flow 3: Pathway Creation (PATHWAY Mode)

### Acceptance Criteria
- [ ] Runs Four-Capital gap analysis
- [ ] Executes skill gap calculation algorithm
- [ ] Presents competency map with progress bars per capital
- [ ] Celebrates existing strengths before showing gaps
- [ ] Conducts mandatory negotiation on timeline/priorities
- [ ] Creates pathway with parallel capital tracks
- [ ] Saves pathway to database with `capital_type` per skill

### Competency Map
- [ ] Shows KSA Capital progress
- [ ] Shows Behavioral Capital progress
- [ ] Shows Social Capital progress
- [ ] Shows Navigation Capital progress

### Negotiation Questions
- [ ] Timeline acceptable?
- [ ] Priority ordering correct?
- [ ] Resource constraints addressed?

## Flow 4: Learning Support (LEARNING Mode)

### Acceptance Criteria
- [ ] Asks for learning style selection (mandatory Step 1)
- [ ] Creates content for all 4 capitals (not just KSA)
- [ ] Uses continuous embedded assessment (5 evidence types)
- [ ] Tracks progress with Four Capitals visibility
- [ ] Handles goal change scenario (transition back to CAREER_EXPLORATORY)

### Learning Styles
- [ ] Project-based
- [ ] Structured modules
- [ ] Real-world practice
- [ ] Social learning

### 5 Evidence Types
- [ ] Micro-assessments
- [ ] Application evidence
- [ ] Conversational demonstrations
- [ ] Project checkpoints
- [ ] Self-assessment reflections

### Content by Capital
- [ ] KSA content generated
- [ ] Behavioral content generated
- [ ] Social content generated
- [ ] Navigation content generated

## Database Validation

### Tables Populated Correctly
- [ ] `learners` has new record
- [ ] `learner_profiles` has all fields including capital signals
- [ ] `learner_skills` has skills with evidence source
- [ ] `learner_goals` has goal with correct status
- [ ] `pathways` created with correct totals
- [ ] `pathway_skills` has skills with `capital_type`

## Tool Functionality

### Job Search Tools
- [ ] `search_jobs` returns results
- [ ] `search_jobs_by_riasec` returns results
- [ ] `get_job_details` returns job info

### RIASEC Tools
- [ ] `infer_riasec_from_skills` infers code
- [ ] `get_riasec_description` returns description
- [ ] `compare_riasec_codes` computes fit

### Salary & Market Tools
- [ ] `get_salary_info` returns salary data
- [ ] `get_comprehensive_market_data` returns combined view
- [ ] `get_high_demand_jobs` returns high-demand jobs
- [ ] `get_market_insights` returns market breakdown

### Skills Tools
- [ ] `calculate_skill_gap` computes gap
- [ ] `find_jobs_by_skill_match` finds matching jobs
- [ ] `suggest_next_skills` suggests skills

### Learner Tools
- [ ] `get_learner_context` returns full context
- [ ] `update_learner_profile` updates profile
- [ ] `add_learner_skill` adds skill
- [ ] `set_learner_goal` sets goal
- [ ] `create_learner` creates new learner
- [ ] `create_pathway` creates pathway

### Pathway Tools
- [ ] `update_pathway_progress` updates skill status
- [ ] `get_pathway_details` returns details
- [ ] `get_current_skill` returns current skill

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_tools.py

# Run with verbose output
pytest -v tests/

# Run specific test
pytest tests/test_tools.py::test_search_jobs
```
