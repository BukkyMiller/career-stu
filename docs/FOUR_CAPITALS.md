# Four Capitals Framework

Career STU measures career readiness across four capitals that determine career success.

## The Four Capitals

| Capital | What It Measures | Examples |
|---------|-----------------|----------|
| **KSA Capital** | What they know and can do — technical skills, domain knowledge, competencies, credentials | Python, SQL, project management, certifications |
| **Behavioral Capital** | How they show up professionally — unwritten rules, industry culture, communication norms | Email etiquette, meeting behavior, dress code, Slack norms |
| **Social Capital** | Who they know and can access — professional network, mentors, community membership | LinkedIn connections, industry mentors, professional associations |
| **Navigation Capital** | How they navigate systems — job search, interviewing, negotiating, career advancement | Resume writing, interview skills, salary negotiation, promotion strategies |

## Capital Assessment Across Modes

Capital assessment begins in intake and deepens throughout the learner journey:

### INTAKE Mode (Agent 1)
- Gathers **early capital signals** through natural conversation
- Stores signals in `behavioral_capital_signal`, `social_capital_signal`, `navigation_capital_signal` fields
- Examples: "I'm nervous about interviews" (navigation), "I don't know anyone in tech" (social)

### CAREER_EXPLORATORY Mode (Agent 2)
- Deepens understanding through exploration activities
- RIASEC assessment reveals KSA patterns
- Labor market research surfaces behavioral expectations

### PATHWAY Mode (Agent 3)
- Runs **Four-Capital gap analysis**
- Presents **competency map** with progress bars per capital
- Celebrates existing strengths before showing gaps

### LEARNING Mode (Agent 4)
- Creates content for **all 4 capitals** (not just KSA)
- Tracks progress with Four Capitals visibility

## Four-Capital Gap Analysis (Agent 3)

### Skill Gap Calculation Algorithm

1. **Frequency Analysis:** Analyze skill occurrence across job postings for target role
2. **Proficiency Mapping:** Map learner skills to 0-4 proficiency scale
3. **Weighted Gap Scores:** Calculate gaps weighted by skill frequency
4. **Hours Estimation:** Estimate learning hours with complexity factors

### Proficiency Scale

| Level | Score | Description |
|-------|-------|-------------|
| None | 0 | No exposure |
| Beginner | 1 | Basic understanding |
| Intermediate | 2 | Can apply with guidance |
| Advanced | 3 | Can apply independently |
| Expert | 4 | Can teach others |

### Competency Map Presentation

Visual progress bars per capital showing current vs required:

```
KSA Capital:        ████████░░░░ 65% (8 of 12 skills)
Behavioral Capital: ██████░░░░░░ 50% (basic professional norms)
Social Capital:     ████░░░░░░░░ 35% (limited network)
Navigation Capital: ██░░░░░░░░░░ 20% (no interview experience)
```

## Content Types by Capital

### KSA Capital Content
- AI-generated technical modules
- Curated external resources (courses, tutorials)
- Guided practice exercises
- Workplace application assignments
- Project checkpoints

### Behavioral Capital Content
- Industry culture guides
- Communication exercises (email, Slack, meetings)
- Professional scenario simulations
- Observation assignments
- "Unwritten rules" documentation

### Social Capital Content
- LinkedIn profile optimization
- Informational interview preparation
- Community engagement activities
- Mentor outreach templates
- Elevator pitch development

### Navigation Capital Content
- Resume optimization workshops
- Job search strategy guides
- Interview preparation (behavioral, technical, case)
- Salary negotiation simulation
- 30-60-90 day plan templates
- Offer evaluation frameworks

## Database Fields

Capital signals are stored in `learner_profiles`:

```sql
behavioral_capital_signal TEXT,   -- Early signals gathered during intake
social_capital_signal TEXT,       -- Early signals gathered during intake
navigation_capital_signal TEXT,   -- Early signals gathered during intake
```

Pathway skills are tagged by capital type:

```sql
-- In pathway_skills table
capital_type VARCHAR,  -- ksa, behavioral, social, navigation
```

## Parallel Capital Tracks

Pathways contain skills from all four capitals, organized into parallel tracks:

- **Required sequences:** Some skills must be learned in order (e.g., basic Python before advanced Python)
- **Flexible ordering:** Most skills across capitals can be learned in parallel
- **Time estimation:** 20% buffer based on `weekly_study_hours`

## Key Principle

**Celebrate existing strengths before showing gaps.** When presenting the competency map, always highlight what the learner already has before discussing what they need to develop.
