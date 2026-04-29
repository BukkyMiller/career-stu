# Career STU — Comprehensive Agent Prompt Update Plan

**Date:** February 2026
**Version:** 0.3 → 0.4
**Sources:** Blueprint document, test conversation analysis, Bukola's feedback

---

## Overview

This document outlines every update needed across all four agent prompts to align Career STU with the "Here to There" Learner Experience Blueprint, fix workflow issues identified during testing, and incorporate new capabilities. Updates are organized by agent, with cross-cutting changes noted.

---

## CROSS-CUTTING CHANGES (Affect All Agents)

### 1. Four Capitals Framework (Replaces 5-Dimension Gap Analysis)

**Current state:** Agent 3 uses a 5-dimension gap analysis (Technical Skills, Competencies & Domain Knowledge, Credentials, Social & Network, Experience).

**Blueprint vision:** The learner emerges with a map of their "four capitals that actually determine career success."

**New framework:**

| Capital | Definition | What It Covers | Replaces |
|---------|-----------|---------------|----------|
| **KSA Capital** | What they know and can do | Technical skills, tools, domain knowledge, competencies, certifications. The measurable "hard" and "soft" skills. Current proficiency vs. required proficiency. | Old Dimensions 1, 2, 3 merged |
| **Behavioral Capital** | How they show up professionally | Understanding unwritten rules of the target field. Professional norms, workplace culture, communication styles, executive presence, industry etiquette. Do they know how people in this field talk, dress, present, negotiate? | Partially in old Dimension 2 (soft skills) but now expanded significantly |
| **Social Capital** | Who they know and can access | Professional network strength. Weak ties, mentorship relationships, sponsorship, industry connections. LinkedIn presence. Community involvement. Access to opportunities through people. | Old Dimension 4, expanded |
| **Navigation Capital** | How they navigate systems | Understanding how to find opportunities, apply strategically, negotiate compensation, advance within organizations, handle workplace politics, build a personal brand, leverage credentials for maximum impact. | **Entirely new** — not in current system at all |

**Impact:** This framework must be woven into ALL agents, not just Agent 3:
- **Agent 1 (Intake):** Gather early signals for all 4 capitals during intake
- **Agent 2 (Explorer):** Factor capitals into career fit assessment
- **Agent 3 (Pathway):** Build pathway tracks around all 4 capitals (not just KSA)
- **Agent 4 (Learning):** Create learning content for behavioral, social, and navigation capitals — not just technical skills

### 2. Online Search Fallback for Labor Market Data

**Current state:** Agents can only search `unified_jobs.parquet` (1.3M jobs) and `salary_reference.parquet` (999 jobs). If a job title isn't in these files, the agent is stuck.

**What happened in testing:** Career STU searched for "AI Product Manager" and found nothing. It kept retrying with broader queries and eventually gave up, telling the user "there may be a gap in our job postings."

**New capability:** When the app database doesn't have information for a specific job title, the agent MUST fall back to online search (via `web_search` tool) to find:
- Job descriptions and requirements
- Salary ranges (from Glassdoor, Levels.fyi, BLS, LinkedIn Salary Insights)
- Labor market demand signals (job posting volumes, growth trends)
- Required skills, certifications, and qualifications
- Career pathway and entry points
- Job levels and typical progression

**Implementation across agents:**

```
SEARCH PROTOCOL (All agents that look up job data):

1. FIRST: Search app database (unified_jobs.parquet, salary_reference.parquet)
2. IF no results or insufficient results:
   → Use web_search tool to find:
     - "[job title] job description requirements"
     - "[job title] salary range [year]"
     - "[job title] labor market demand"
     - "[job title] career path entry level to senior"
3. ALWAYS tell the learner where the data came from:
   - "Based on our database of 1.3M job postings..." (if from app data)
   - "Based on current market research..." (if from web search)
4. NEVER tell the learner "we don't have that data" and stop.
```

### 3. Skills Sharing Options (URL Parsing + Resume Upload + Manual)

**Current state:** The prompts mention resume/LinkedIn review as one of three validation options in Agent 2's Goal Setting mode, but there's no actual parsing capability defined, no URL handling, and no structured flow for HOW skills get into the system.

**New capability:** A structured Skills Input Protocol that gives learners clear options:

```
SKILLS INPUT PROTOCOL (Used by Agent 1 during Intake AND Agent 2 during Goal Setting):

"I'd love to understand your skills. Here are a few ways we can do this:

A) 📋 I'll List & You Confirm — Based on your background as a [current role],
   I'll suggest skills you likely have and you tell me which ones fit
   and at what level.

B) 📄 Upload Your Resume — Send me your resume and I'll extract your skills,
   experience, and credentials automatically.

C) 🔗 Share a URL — Paste a link to your LinkedIn profile, portfolio site,
   or any professional page and I'll pull your skills from there.

D) ✍️ Tell Me Directly — Just list out your skills and I'll capture them.

Which works best for you?"
```

**URL Parsing capability:**
```
Tool: parse_professional_url
Parameters:
  url: "https://linkedin.com/in/username" OR "https://portfolio-site.com"
Description: Fetches the URL content and extracts:
  - Job titles and work history
  - Listed skills and endorsements
  - Education and certifications
  - Projects and accomplishments
  - Recommendations/testimonials (for social capital signals)

Implementation: Use web_search or web_fetch tool to retrieve the page,
then use LLM to parse and structure the extracted information.
```

**Resume Parsing capability:**
```
Tool: parse_resume
Parameters:
  file_content: <uploaded resume text/PDF>
Description: Extracts and structures:
  - Contact information
  - Work experience (titles, companies, durations, responsibilities)
  - Skills (explicit + inferred from job descriptions)
  - Education (degrees, institutions, dates)
  - Certifications and training
  - Proficiency inference (years of use, context of use, recency)

Implementation: Use LLM to parse resume content, then map to
structured skill objects with inferred proficiency levels.
```

**After parsing (URL or Resume), ALWAYS confirm with the learner:**
```
"Based on your [resume/profile], here's what I found:

🛠️ Skills identified:
  - [Skill 1] — I'd estimate [Intermediate/Advanced] based on [reason]
  - [Skill 2] — I'd estimate [Beginner/Intermediate] based on [reason]
  ...

📚 Education:
  - [Degree] from [Institution]

🏅 Certifications:
  - [Cert 1], [Cert 2]

Does this look right? Anything I missed or got wrong?
Any skills you have that aren't reflected here?"
```

---

## AGENT 1: ORCHESTRATOR & INTAKE — Updates

### Update 1.1: Stricter Intake Completion Enforcement

**Problem from testing:** The agent declared profile "complete" after getting only name, job title, education, and a resume dump — skipping weekly study hours, employment status, family obligations, disposition, and RIASEC signal.

**Fix:** Add a HARD GATE to the intake flow:

```
INTAKE COMPLETION GATE — Before setting profile_complete: True, you MUST have ALL of these.
No exceptions. No shortcuts. Check each one:

□ Name — captured
□ Current job title or situation — captured
□ Current industry — captured
□ Years of experience — captured
□ Education level — captured
□ At least 5 skills with proficiency levels — captured and confirmed by learner
□ Weekly study hours (realistic number) — explicitly asked and answered
□ Preferred study times — explicitly asked and answered
□ Employment status — explicitly confirmed
□ Family/life obligations affecting schedule — asked (yes/no)
□ Disposition identified — inferred from conversation (unclear/discontent/promotion/called)
□ Preliminary RIASEC signal — gathered via lightweight questions

If ANY item is missing, DO NOT set profile_complete: True.
If the learner seems eager to skip ahead, acknowledge their enthusiasm but explain:
"I want to make sure I set you up for success. A few more quick questions
will help me give you much better recommendations."
```

### Update 1.2: Skills Input Protocol in Intake

**Add to Step 3 (Skills Discovery):**

Replace the current simple "What are your strongest skills?" with the full Skills Input Protocol defined above. During intake, the agent should:

1. Present the 4 options (List & Confirm, Upload Resume, Share URL, Tell Directly)
2. Process whichever method the learner chooses
3. ALWAYS confirm extracted skills with proficiency levels back to the learner
4. Save each skill via `add_learner_skill` with proficiency and evidence_source
5. Evidence source should reflect the method: `self_reported`, `resume_parsed`, `url_parsed`

### Update 1.3: Early Capital Signals in Intake

**Add a new intake dimension — Capital Signals:**

During the motivation/disposition question (Step 5), also gather lightweight signals for the 4 capitals:

```
CAPITAL SIGNAL QUESTIONS (weave into natural conversation, don't ask as a checklist):

KSA Capital: Already captured via skills inventory above.

Behavioral Capital Signal:
  "Have you ever worked in or around [target field] before?
   Do you have a sense of what the day-to-day professional culture is like?"
  → Captures: familiarity with target field norms

Social Capital Signal:
  "Do you know anyone who works in the kind of role you're interested in?
   Any mentors, former colleagues, or connections in that space?"
  → Captures: network strength for target field

Navigation Capital Signal:
  "Have you done any job searching or career transitions before?
   How comfortable are you with things like networking, interviewing,
   or negotiating offers?"
  → Captures: career navigation experience
```

Store these as fields in learner_profiles or as tags in a new `capital_signals` structure.

### Update 1.4: One-Question-at-a-Time Enforcement

**Add to Conversation Guidelines (bolded, top of list):**

```
⚠️ CRITICAL RULE: ONE QUESTION PER MESSAGE. NEVER ASK TWO OR MORE QUESTIONS
IN THE SAME RESPONSE.

Bad: "What's your current job? And how long have you been doing it? What's your education?"
Good: "What's your current job or situation?"
[wait for answer]
Good: "How long have you been in that role?"
[wait for answer]

The only exception is CONFIRMING information:
Acceptable: "So you're a Senior PM with 15 years of experience — did I get that right?"
```

---

## AGENT 2: CAREER EXPLORER & GOAL SETTING — Updates

### Update 2.1: Mandatory Exploration Menu Enforcement

**Problem from testing:** The agent skipped the 7-method exploration menu entirely and went straight to job searching.

**Fix:** Add a hard rule at the top of the CAREER_EXPLORATORY section:

```
⚠️ MANDATORY: When entering CAREER_EXPLORATORY mode, you MUST present the
exploration menu. No exceptions. Do not skip to job searching.

Even if the learner has already stated a career interest (e.g., "I want to be an AI Product Manager"),
the exploration menu should STILL be offered because:
- They may not have considered alternatives
- The RIASEC assessment may reveal better fits
- Salary/market data may change their perspective

Frame it as: "Before we dive in, let me offer you some fun ways to explore
your options. Even if you have a direction in mind, these can confirm your
instinct or reveal something surprising."
```

### Update 2.2: Labor Market Intelligence with Online Fallback

**Add to both CAREER_EXPLORATORY and CAREER_GOAL_SETTING modes:**

```
LABOR MARKET INTELLIGENCE PROTOCOL:

When presenting career options or validating goals, ALWAYS provide:
1. Job descriptions — what the role actually involves day-to-day
2. Required qualifications — education, certs, years of experience
3. Salary range — median, entry-level, and senior ranges
4. Market demand — shortage/surplus, growth trajectory
5. Job levels — entry points, mid-level, senior, leadership
6. Career pathway — typical progression (e.g., Junior → Mid → Senior → Lead → Director)
7. Entry points — realistic first roles for career changers

DATA SOURCE PRIORITY:
1. App database (salary_reference.parquet, unified_jobs.parquet)
2. If insufficient → web_search for current market data
3. NEVER say "I don't have that data" — always search online as fallback

For EACH career option presented, include:
- 💼 Job Title & Description
- 💰 Salary Range (entry → senior)
- 📊 Market Demand (shortage/surplus + trend)
- 🎓 Entry Requirements (education, certs, experience)
- 🪜 Career Ladder (entry point → where it leads)
- 🧬 RIASEC Fit Score
```

### Update 2.3: Skills Validation with Multi-Method Protocol

**Replace the current 3-option skills validation in Goal Setting with the enhanced Skills Input Protocol:**

When the learner reaches Goal Setting Step 4 (Skills Validation), if skills haven't already been thoroughly validated during intake, offer:

```
SKILLS VALIDATION FOR GOAL SETTING:

"Now let's make sure I have an accurate picture of your skills relative to
[target role]. How would you like to do this?

A) 📋 Confirm Against Requirements — I'll show you the skills [target role]
   typically requires and you rate yourself on each one.

B) 📄 Upload/Re-review Your Resume — I'll extract skills and match them
   specifically against [target role] requirements.

C) 🔗 Share Your LinkedIn/Portfolio — I'll pull your latest professional
   profile and map it to [target role].

D) 🧪 Quick Skill Check — I'll ask 5-8 scenario questions relevant to
   [target role] to gauge your readiness."
```

### Update 2.4: RIASEC Explanation Must Use Stack Logic

**Problem from testing:** The agent assigned "IRA" without explanation or proper Stack Logic.

**Fix:** Reinforce that ANY time a RIASEC code is presented, it MUST use the full Stack Logic:

```
RIASEC PRESENTATION RULE:
Every RIASEC code presentation MUST include:
- Position 1 explanation (Core Drive — WHY)
- Position 2 explanation (Primary Expression — HOW)
- Position 3 explanation (Supporting Amplifier — WHAT)
- Least interest type and what it means
- What this combination uniquely enables
```

---

## AGENT 3: CAREER PATH — Updates (Most Significant Changes)

### Update 3.1: Replace 5-Dimension Gap Analysis with 4 Capitals

**This is the most critical update.** Replace the entire Phase 1 gap analysis.

```
PHASE 1: COMPREHENSIVE CAPITAL ASSESSMENT

Analyze the learner's readiness across FOUR CAPITALS:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAPITAL 1: KSA CAPITAL — What They Know and Can Do
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This combines technical skills, domain knowledge, competencies, and credentials.

A) Technical Skills Gap:
   Use calculate_skill_gap tool or web_search to identify:
   - Must-have skills (required in 70%+ of job postings)
   - Should-have skills (40-70% of postings)
   - Nice-to-have skills (<40% of postings)
   For each: learner's current level vs. required level

B) Domain Knowledge Gap:
   - Industry terminology and concepts
   - Regulatory/compliance knowledge
   - Market trends and current state
   - Key players, tools, platforms

C) Credentials Gap:
   - Required degrees or licenses (non-negotiable)
   - Preferred certifications (significant advantage)
   - Optional credentials (differentiators)

D) Competencies Gap:
   - Communication (written, verbal, presentation)
   - Critical thinking and problem-solving
   - Project management
   - Leadership and collaboration

Present as: "Here's your KSA Capital snapshot — what you already have
and what you'll need to build."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAPITAL 2: BEHAVIORAL CAPITAL — How They Show Up Professionally
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is about the UNWRITTEN RULES of the target field.

Assess and address:
A) Professional Norms:
   - How do people in [target field] communicate? (Formal? Casual? Data-driven? Story-driven?)
   - What are the meeting cultures? (Stand-ups? Lengthy reviews? Async-first?)
   - What's the dress code / presentation expectation?

B) Industry Culture:
   - What values does this field prioritize? (Innovation? Compliance? Speed? Precision?)
   - What are the taboos or common mistakes newcomers make?
   - How is success measured and recognized?

C) Communication Style:
   - How do professionals in this field write emails, reports, presentations?
   - What jargon and acronyms are expected?
   - How do they handle disagreements or pushback?

D) Executive Presence (for senior roles):
   - Stakeholder management expectations
   - How to present to leadership
   - Strategic thinking demonstration

Gather from learner: "Have you worked in or near [target field]?
What's your understanding of how professionals in that space operate day to day?"

If the learner is transitioning into a very different field culture
(e.g., marketing → engineering, corporate → startup), this capital
becomes HIGH PRIORITY in the pathway.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAPITAL 3: SOCIAL CAPITAL — Who They Know and Can Access
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Professional networks are the #1 predictor of career transition success.

Assess:
A) Current Network in Target Field:
   - Do they know anyone in [target role/industry]?
   - Do they have mentors or sponsors in the field?
   - Are they in any professional communities or groups?

B) Network Strength:
   - Strong ties (close contacts who would advocate for them)
   - Weak ties (acquaintances who could make introductions)
   - Digital presence (LinkedIn connections, followers, engagement)

C) Access Gaps:
   - Missing: mentors in target field
   - Missing: peer network of others making similar transitions
   - Missing: visibility to hiring managers or recruiters
   - Missing: industry community membership

Build networking activities into the pathway:
   - LinkedIn profile optimization (Week 1)
   - Join 2-3 professional communities (Week 2-3)
   - Attend 1 industry event per month
   - Conduct 2 informational interviews per month
   - Identify and approach a potential mentor by Week 8

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAPITAL 4: NAVIGATION CAPITAL — How They Navigate Systems
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is the meta-skill of career management — entirely missing from
the current system and one of the biggest predictors of career success.

Assess:
A) Job Search Savvy:
   - Do they know how to find opportunities beyond job boards?
   - Do they understand hidden job markets and referral hiring?
   - Can they identify and target companies strategically?
   - Do they know how to read a job description and decode requirements?

B) Application & Interview Skills:
   - Resume optimization for ATS and human readers
   - Cover letter and cold outreach effectiveness
   - Interview preparation (behavioral, technical, case)
   - Portfolio/work sample presentation

C) Negotiation Skills:
   - Salary negotiation fundamentals
   - Benefits and equity negotiation
   - Counter-offer handling
   - Knowing their market value

D) Career Advancement:
   - Understanding promotion dynamics
   - Building internal visibility and sponsorship
   - Strategic project selection
   - Performance review navigation
   - When and how to make lateral moves

E) System Literacy:
   - Understanding how hiring actually works (recruiter screens, hiring manager decisions)
   - Knowing which credentials actually matter vs. are just listed
   - Recognizing credentialism vs. skill-based hiring trends
   - Understanding industry-specific entry points and back doors

For career changers, Navigation Capital is often the BIGGEST gap.
They may know their old industry's systems but not their target industry's.
```

### Update 3.2: Skill Gap Calculation Algorithm

**Problem identified:** The skill gap calculation is too simplistic — just a set-difference of skill names. Need an algorithmic approach.

```
SKILL GAP CALCULATION ALGORITHM:

1. COLLECT target role requirements:
   a. Query unified_jobs.parquet for top 20 postings of [target_job_title]
   b. If < 5 results, use web_search to find 5+ job descriptions
   c. Aggregate all skills mentioned across postings
   d. Calculate frequency: skill_frequency = count(postings with skill) / total_postings

2. CATEGORIZE by frequency:
   - MUST-HAVE: frequency >= 0.70 (in 70%+ of postings)
   - SHOULD-HAVE: 0.40 <= frequency < 0.70
   - NICE-TO-HAVE: frequency < 0.40

3. MATCH against learner skills:
   For each required skill:
   a. Exact match: learner has skill by same name
   b. Semantic match: learner has equivalent skill (e.g., "data visualization" ≈ "Tableau")
   c. Partial match: learner has foundational version (e.g., "basic SQL" partially covers "Advanced SQL")

4. CALCULATE gap score per skill:
   required_level = inferred from job postings (entry/mid/senior context)
   current_level = learner's proficiency (none/beginner/intermediate/advanced/expert)

   Level numeric mapping:
     none = 0, beginner = 1, intermediate = 2, advanced = 3, expert = 4

   gap_score = max(0, required_level - current_level)

5. CALCULATE overall readiness:
   must_have_readiness = avg(1 - gap_score/4) for must-have skills
   overall_readiness = weighted_avg(must_have * 0.5 + should_have * 0.3 + nice_to_have * 0.2)

6. ESTIMATE hours to close each gap:
   Per skill:
     gap_of_1_level ≈ 20-40 hours
     gap_of_2_levels ≈ 60-100 hours
     gap_of_3_levels ≈ 100-160 hours
     gap_of_4_levels ≈ 160-240 hours
   Multiply by complexity factor (programming skills = 1.5x, soft skills = 0.7x, certifications = fixed hours)

7. PRESENT to learner:
   "Your KSA Capital Readiness: [X]%

   ✅ Skills you already have: [list with levels]
   🔶 Skills that need leveling up: [list with current → required]
   ❌ Skills you need to learn from scratch: [list with estimated hours]

   Estimated total learning hours: [X] hours
   At [Y] hours/week: ~[Z] months"
```

### Update 3.3: Pathway Tracks Organized by Capital

**Replace the current 5-track pathway with 4-capital tracks:**

```
PATHWAY STRUCTURE — Four Capital Tracks:

TRACK 1: KSA CAPITAL (Primary — highest time investment)
├── Technical Skills: [sequenced by dependency]
├── Domain Knowledge: [industry fundamentals → advanced]
├── Certifications: [prep → exam, scheduled around skill completion]
└── Competencies: [communication, leadership, etc.]

TRACK 2: BEHAVIORAL CAPITAL (Ongoing — woven throughout)
├── Industry culture orientation (research + observation)
├── Communication style adaptation (practice exercises)
├── Professional norms documentation (create personal reference guide)
└── Simulated workplace scenarios (case studies from target field)

TRACK 3: SOCIAL CAPITAL (Ongoing — consistent light effort)
├── LinkedIn optimization (Week 1)
├── Community membership (Weeks 2-4)
├── Informational interviews (2/month ongoing)
├── Mentor identification and outreach (by Week 8)
├── Conference/event attendance (1/month)
└── Online presence building (content creation, engagement)

TRACK 4: NAVIGATION CAPITAL (Phased — builds toward job readiness)
├── Phase A (Early): Understanding the hiring landscape for [target role]
├── Phase B (Mid): Resume + portfolio development
├── Phase C (Late): Interview prep, salary research, negotiation practice
└── Phase D (Final): Active job search strategy, application tracking
```

### Update 3.4: Pathway Negotiation Enforcement

**Problem from testing:** The agent created the pathway and locked it in without asking.

**Add hard rule:**

```
⚠️ MANDATORY: NEVER finalize a pathway without learner negotiation.

After presenting the pathway, you MUST ask:
1. "Does this timeline feel realistic for your life right now?"
2. "Are there any areas you'd like to prioritize differently?"
3. "Should we adjust the intensity?"
4. "Anything here that surprises you or you want to discuss?"

Wait for the learner to respond. Adjust if needed. Only THEN save to database.
```

---

## AGENT 4: COURSE CREATION & LEARNING — Updates

### Update 4.1: Learning Style Choice Enforcement

**Problem from testing:** The agent produced generic course content without offering learning style choices.

**Add hard rule:**

```
⚠️ MANDATORY: Before creating ANY course content, ALWAYS present the
4 learning style options. Do not skip this step.

A) 🏗️ Project-Based
B) 📚 Structured Course
C) 🧩 Problem-Based
D) 🎬 Video + Practice

If the learner already selected a preference in a previous session, confirm:
"Last time you preferred [project-based] learning. Want to continue with
that style, or try something different for this skill?"
```

### Update 4.2: Content for ALL Four Capitals — Not Just KSA

**Current state:** Agent 4 only creates technical skill courses. It has no content design for behavioral, social, or navigation capitals.

**Add content design for each capital:**

```
CONTENT BY CAPITAL TYPE:

KSA CAPITAL CONTENT (existing, enhanced):
  - Modules with concept introductions, videos, practice exercises
  - Project-based learning with career-relevant scenarios
  - Assessments with 80%+ pass threshold
  (Keep current design, but ensure career-alignment per blueprint)

BEHAVIORAL CAPITAL CONTENT (new):
  - "Industry Culture Guide" for their target field
  - Communication style exercises (write an email as a [target role], present to [audience])
  - Professional scenario simulations ("You're in a meeting and...")
  - Unwritten rules documentation (research assignment)
  - Shadow/observation assignments (watch YouTube videos of professionals in the field)

SOCIAL CAPITAL CONTENT (new):
  - LinkedIn profile optimization guide and exercise
  - Informational interview preparation (script, questions to ask, follow-up template)
  - Networking event preparation guide
  - Community engagement plan (where to participate, what to contribute)
  - Mentor outreach template and strategy
  - Personal introduction / elevator pitch development

NAVIGATION CAPITAL CONTENT (new):
  - Resume optimization for [target role] (ATS keywords, format, content)
  - Job search strategy document (where to look, how to apply, hidden job market tactics)
  - Interview preparation modules:
    - Behavioral interview (STAR method with career-specific examples)
    - Technical interview (domain-specific)
    - Case interview (if applicable)
  - Salary negotiation simulation
  - Offer evaluation framework (comparing multiple offers)
  - 30-60-90 day plan template for new role
```

### Update 4.3: Career-Aligned Content Rule

**Problem from testing:** The course for "AI Product Manager" taught neural network implementation details instead of product management with AI.

**Reinforce the blueprint principle:**

```
CONTENT ALIGNMENT RULE:
Every piece of content must pass this test:
"Would someone in [target role] actually need to know/do this?"

For an AI Product Manager:
  ❌ "Implement a neural network from scratch in Python" — PMs don't code models
  ✅ "Evaluate an AI model's performance and explain trade-offs to stakeholders"
  ✅ "Write a product requirements document for an AI feature"
  ✅ "Understand the ethical implications of deploying AI in [industry]"

For a Data Scientist:
  ✅ "Implement a neural network from scratch" — Scientists DO code models
  ❌ "Write a go-to-market strategy" — Not their job

Always ask: "What would the HIRING MANAGER for this role want to see?"
```

### Update 4.4: Multi-Sourced Learning (Blueprint Requirement)

**Blueprint says:** "Learning might come from AI-generated content, curated external resources, workplace application, mentorship conversations, or peer collaboration."

**Add to course design:**

```
CONTENT SOURCES PER MODULE:

Each module should include content from MULTIPLE sources:

1. 🤖 AI-Generated Content — Explanations, exercises, case studies
   (Created by Career STU, tailored to the learner)

2. 🎬 Curated External Resources — YouTube videos, tutorials, articles
   (Found via web_search, vetted for quality and relevance)

3. 🛠️ Workplace Application — Real-world tasks to try at current job
   "This week, try [applying concept] in your current role. Here's how..."

4. 👥 Mentorship/Peer Activity — Social learning tasks
   "Ask your mentor about [topic]" or "Discuss [concept] in your
   professional community and report back what you learned"

5. 📊 Self-Assessment — Reflective exercises
   "After trying [activity], rate your confidence from 1-5 and note
   what was harder/easier than expected"
```

### Update 4.5: Continuous Embedded Assessment (Blueprint Requirement)

**Blueprint says:** "Assessment is continuous and embedded, not episodic and high-stakes."

**Update assessment design:**

```
CONTINUOUS ASSESSMENT MODEL:

Replace the current "assessment at end of skill" model with:

1. MICRO-ASSESSMENTS (every module):
   - 3-5 quick check questions woven INTO the learning content
   - Not a separate "quiz" section — integrated naturally
   - "Before we move on, quick thought: How would you apply [concept]
     to [career-relevant scenario]?"

2. APPLICATION EVIDENCE (ongoing):
   - Learner shares real-world attempts to apply skills
   - Career STU evaluates and provides feedback
   - "I tried [thing] at work. Here's what happened..."
   - This counts as assessment evidence

3. CONVERSATIONAL DEMONSTRATIONS:
   - Through normal chat, the learner demonstrates understanding
   - Career STU tracks these as informal assessment data
   - "Based on how you just explained [concept], you clearly understand it"

4. PROJECT MILESTONES (per skill):
   - One project per skill, but with checkpoints rather than pass/fail at end
   - Submit draft → feedback → revise → submit final
   - Rubric scoring with specific actionable feedback

5. SKILL MASTERY SIGNAL:
   - Skill is "mastered" when MULTIPLE evidence types converge:
     □ Knowledge checks passed (80%+)
     □ Project completed to rubric standards
     □ Conversational evidence of understanding
     □ Real-world application attempted
```

---

## GAPS BETWEEN BLUEPRINT AND CURRENT SYSTEM

### Gap 1: "Every skill they've developed... it all counts"

**Blueprint vision:** The system recognizes and validates ALL prior learning — formal, informal, work experience, self-taught, volunteer work.

**Current gap:** The system only captures self-reported skills with proficiency levels. It doesn't deeply map prior experience to target role readiness.

**Recommendation:** During intake and goal setting, explicitly map the learner's EXISTING experience to the target role:

```
"You mentioned you managed spreadsheets and did data analysis for 3 years.
In the context of becoming a [target role], that experience gives you:
- ✅ Data analysis fundamentals (you have this)
- ✅ Excel/spreadsheet proficiency (you have this)
- 🔶 Statistical thinking (you have some, need to deepen)
- Transferable: stakeholder communication, deadline management, attention to detail

Not everything needs to be learned from scratch. Let's build on what you already have."
```

### Gap 2: "The pathway isn't a list of courses. It's a competency map."

**Blueprint vision:** A visual competency map showing every skill/knowledge area with the learner's current proficiency marked against each one.

**Current gap:** The pathway is stored as a sequential list of skills in `pathway_skills` table. No visual map, no proficiency overlay.

**Recommendation:** When presenting the pathway, structure it as a COMPETENCY MAP:

```
"Here's your competency map for [Target Role]:

KSA Capital:
  Python ████████░░ (You: Beginner → Need: Advanced)     ⏱️ ~80 hours
  SQL    ██████████ (You: Intermediate → Need: Intermediate) ✅ Already there!
  ML     ░░░░░░░░░░ (You: None → Need: Intermediate)     ⏱️ ~100 hours
  Stats  ████░░░░░░ (You: Beginner → Need: Advanced)     ⏱️ ~60 hours

Behavioral Capital:
  AI industry norms  ██░░░░░░░░ (Low familiarity)        ⏱️ ~15 hours
  Technical communication █████░░░░░ (Moderate)           ⏱️ ~10 hours

Social Capital:
  Industry network ░░░░░░░░░░ (Starting from scratch)    ⏱️ Ongoing
  LinkedIn presence ████░░░░░░ (Needs AI PM optimization) ⏱️ ~5 hours

Navigation Capital:
  Job search strategy ██████░░░░ (Some experience)        ⏱️ ~10 hours
  Interview prep ████░░░░░░ (Need AI-specific prep)       ⏱️ ~15 hours
  Salary negotiation ██░░░░░░░░ (Needs development)       ⏱️ ~8 hours"
```

### Gap 3: "The learner has agency in how they traverse it"

**Blueprint vision:** Multiple valid routes through the pathway. Learner chooses modality and sequence.

**Current gap:** Pathway is rigidly sequenced. Learner can't easily skip around.

**Recommendation:** Present pathway with REQUIRED dependencies vs. FLEXIBLE ordering:

```
"Some skills must be done in order (you need Python basics before ML).
But many can be done in whatever order interests you:

🔒 Required sequence: Python → Statistics → ML Basics → Advanced ML
🔓 Flexible (do in any order): Domain Knowledge, Communication, Networking
🔓 Flexible (do in any order): LinkedIn Optimization, Interview Prep, Resume Writing"
```

### Gap 4: Blueprint mentions "Lazuli" as the content system

**Blueprint vision:** References "Lazuli" as the content system and "Lazuli" as the assessment system.

**Current gap:** Agent 4 generates all content itself. There's no integration with an external content system called Lazuli.

**Recommendation:** This is noted as a future integration point. For now, Agent 4 serves as the content engine. When Lazuli is ready, Agent 4 should be able to:
- Pull content from Lazuli instead of generating from scratch
- Feed learner performance data back to Lazuli for content optimization
- Use Lazuli's assessment framework for embedded evaluation

---

## NEW TOOLS NEEDED

| Tool | Agent(s) | Purpose |
|------|----------|---------|
| `parse_professional_url` | Agent 1, 2 | Fetch and parse LinkedIn/portfolio URLs for skills extraction |
| `parse_resume` | Agent 1, 2 | Parse uploaded resume for structured skill/experience extraction |
| `web_search` (enhanced role) | All | Fallback for labor market data when app database lacks info |
| `calculate_capital_gaps` | Agent 3 | Enhanced skill gap algorithm with frequency analysis and proficiency levels |
| `generate_competency_map` | Agent 3 | Visual/structured representation of all 4 capitals with gap overlay |

---

## DATABASE SCHEMA ADDITIONS

```sql
-- New: Capital signals captured during intake
ALTER TABLE learner_profiles ADD COLUMN behavioral_capital_signal TEXT;
ALTER TABLE learner_profiles ADD COLUMN social_capital_signal TEXT;
ALTER TABLE learner_profiles ADD COLUMN navigation_capital_signal TEXT;

-- New: Track evidence source for skills more granularly
-- (existing learner_skills.evidence_source: add 'resume_parsed', 'url_parsed')

-- New: Pathway tracks by capital type
ALTER TABLE pathway_skills ADD COLUMN capital_type VARCHAR DEFAULT 'ksa';
-- Values: 'ksa', 'behavioral', 'social', 'navigation'
```

---

## SUMMARY OF ALL CHANGES

| Agent | Update | Priority | Complexity |
|-------|--------|----------|------------|
| **All** | Four Capitals framework | 🔴 Critical | High |
| **All** | Online search fallback for labor market data | 🔴 Critical | Medium |
| **All** | Skills Input Protocol (URL + resume + manual) | 🔴 Critical | High |
| **Agent 1** | Stricter intake completion gate | 🔴 Critical | Low |
| **Agent 1** | One-question-at-a-time enforcement | 🟡 High | Low |
| **Agent 1** | Early capital signals in intake | 🟡 High | Medium |
| **Agent 2** | Mandatory exploration menu | 🔴 Critical | Low |
| **Agent 2** | Full labor market intelligence protocol | 🔴 Critical | Medium |
| **Agent 2** | RIASEC Stack Logic enforcement | 🟡 High | Low |
| **Agent 3** | 4-Capital gap analysis (replaces 5-dimension) | 🔴 Critical | High |
| **Agent 3** | Skill gap calculation algorithm | 🔴 Critical | High |
| **Agent 3** | Capital-organized pathway tracks | 🔴 Critical | High |
| **Agent 3** | Pathway negotiation enforcement | 🟡 High | Low |
| **Agent 3** | Competency map presentation | 🟡 High | Medium |
| **Agent 4** | Learning style choice enforcement | 🔴 Critical | Low |
| **Agent 4** | Content for all 4 capitals (not just KSA) | 🔴 Critical | High |
| **Agent 4** | Career-aligned content rule | 🟡 High | Low |
| **Agent 4** | Multi-sourced learning | 🟡 High | Medium |
| **Agent 4** | Continuous embedded assessment | 🟡 High | High |
| **System** | New tools (URL parser, resume parser, capital gaps) | 🟡 High | High |
| **System** | Schema additions for capital tracking | 🟢 Medium | Low |
