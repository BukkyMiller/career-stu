"""
System prompt builder for Career STU — Multi-Agent Orchestration Architecture

This module builds agent-specific system prompts for the supervisor/worker architecture:
  - Agent 1: Orchestrator & Intake  (handles routing + INTAKE mode directly)
  - Agent 2: Career Explorer & Goal Setting  (CAREER_EXPLORATORY + CAREER_GOAL_SETTING)
  - Agent 3: Career Path  (PATHWAY mode)
  - Agent 4: Course Creation & Learning  (LEARNING mode)

Prompts are stored as markdown files in agent/prompts/ and loaded at runtime.
The build_system_prompt() and determine_mode() functions remain the public API
so that career_stu.py continues to work without changes.
"""
from typing import Dict, Any

from agent.prompts import load_prompt_for_mode, MODE_TO_AGENT


# ---------------------------------------------------------------------------
# Legacy inline prompts preserved for reference / fallback
# ---------------------------------------------------------------------------

_LEGACY_BASE_PROMPT = """You are Career STU, an AI career support assistant that guides learners from where they are now to their career goals.

# Core Principle
You are the ORCHESTRATOR of a multi-agent career support system. You analyse every
learner message, decide which specialised agent should handle it, and return a
seamless, consolidated response. The learner never sees agent boundaries.

# Your Tools

You have access to these tools to help learners:

**Job Search:**
- search_jobs: Find jobs by title, skills, location, or level
- search_jobs_by_riasec: Find jobs matching a RIASEC code
- get_job_details: Get full details for a specific job

**RIASEC Matching:**
- infer_riasec_from_skills: Predict RIASEC code from skills
- get_riasec_description: Get description for a RIASEC code
- compare_riasec_codes: Compare learner's RIASEC to job's RIASEC

**Salary & Market:**
- get_salary_info: Look up salary and market demand (with fuzzy matching and cross-database fallback)
- get_comprehensive_market_data: Search BOTH databases in one call — salary, listings, skills, RIASEC, market demand
- get_high_demand_jobs: Find jobs with labor shortages

**Skills Analysis:**
- calculate_skill_gap: Compare learner skills to job requirements
- find_jobs_by_skill_match: Find jobs with highest skill match

**Learner Management:**
- get_learner_context: Get full learner profile and progress
- update_learner_profile: Update learner information
- add_learner_skill: Add a skill to learner's profile
- set_learner_goal: Set or update career goal
- create_pathway: Create a learning pathway

# Conversation Style

- Be encouraging and supportive, but honest
- Use clear, simple language (avoid jargon unless learner uses it first)
- Ask one question at a time to avoid overwhelming
- Celebrate progress and milestones
- Be direct about challenges and realistic timelines
- Use data to validate career choices (salary, demand, skill fit)

# RIASEC Framework

The six types:
- **R (Realistic)**: Hands-on, practical, mechanical
- **I (Investigative)**: Analytical, intellectual, scientific
- **A (Artistic)**: Creative, expressive, original
- **S (Social)**: Helping, teaching, counseling
- **E (Enterprising)**: Leading, persuading, managing
- **C (Conventional)**: Organizing, detail-oriented, systematic

RIASEC codes are 3 letters (e.g., "SRI", "IRA") where:
- Position 1: Core drive (WHY you act)
- Position 2: Primary expression (HOW you act)
- Position 3: Supporting amplifier (WHAT strengthens impact)
"""


# ---------------------------------------------------------------------------
# Public API  (consumed by career_stu.py)
# ---------------------------------------------------------------------------

def build_system_prompt(mode: str, learner_context: Dict[str, Any]) -> str:
    """
    Build a complete system prompt for the current mode by loading
    the full agent prompt from agent/prompts/<agent>.md and appending
    dynamic learner context.

    Args:
        mode: One of INTAKE, GOAL_DISCOVERY, CAREER_EXPLORATORY,
              CAREER_GOAL_SETTING, PATHWAY, LEARNING
        learner_context: Current learner data from get_learner_context

    Returns:
        Complete system prompt string
    """
    # --- Load the rich agent prompt from markdown --------------------------
    try:
        agent_prompt = load_prompt_for_mode(mode)
    except (ValueError, FileNotFoundError):
        # Fallback: use the legacy base prompt if file is missing
        agent_prompt = _LEGACY_BASE_PROMPT

    prompt = agent_prompt + "\n\n"

    # --- Append dynamic learner context ------------------------------------
    if learner_context:
        prompt += "# Current Learner Context\n\n"

        learner = learner_context.get("learner", {})
        profile = learner_context.get("profile", {})
        skills = learner_context.get("skills", [])
        goals = learner_context.get("goals", [])
        pathway = learner_context.get("active_pathway")

        if learner:
            prompt += f"**Learner ID:** {learner.get('id')}\n"
            prompt += f"**Status:** {learner.get('status')}\n"

        if profile:
            if profile.get('current_job_title'):
                prompt += f"**Current Role:** {profile.get('current_job_title')}\n"
            if profile.get('current_industry'):
                prompt += f"**Industry:** {profile.get('current_industry')}\n"
            if profile.get('years_experience'):
                prompt += f"**Years Experience:** {profile.get('years_experience')}\n"
            if profile.get('education_level'):
                prompt += f"**Education:** {profile.get('education_level')}\n"
            if profile.get('inferred_riasec_code'):
                prompt += f"**RIASEC Type:** {profile.get('inferred_riasec_code')}\n"
            if profile.get('weekly_study_hours'):
                prompt += f"**Weekly Study Hours:** {profile.get('weekly_study_hours')}\n"
            if profile.get('disposition'):
                prompt += f"**Disposition:** {profile.get('disposition')}\n"
            if profile.get('employment_status'):
                prompt += f"**Employment Status:** {profile.get('employment_status')}\n"
            prompt += f"**Profile Complete:** {profile.get('profile_complete', False)}\n"

        if skills:
            prompt += f"\n**Skills ({len(skills)} total):**\n"
            for s in skills[:10]:
                name = s.get('skill_name', 'unknown')
                level = s.get('proficiency_level', 'unknown')
                prompt += f"- {name} ({level})\n"
            if len(skills) > 10:
                prompt += f"- ... and {len(skills) - 10} more\n"

        if goals:
            prompt += "\n**Goals:**\n"
            for g in goals[:3]:
                title = g.get('target_job_title', 'unknown')
                status = g.get('status', 'unknown')
                prompt += f"- {title} (status: {status})\n"

        if pathway:
            prompt += f"\n**Active Pathway:**\n"
            prompt += f"- Total Skills: {pathway.get('total_skills', 0)}\n"
            prompt += f"- Completed: {pathway.get('completed_skills', 0)}\n"
            prompt += f"- Status: {pathway.get('status', 'unknown')}\n"
            prompt += f"- Estimated Hours: {pathway.get('estimated_hours', 'N/A')}\n"

    return prompt


def determine_mode(learner_context: Dict[str, Any]) -> str:
    """
    Determine which mode / agent should handle the next interaction
    based on learner context.

    Returns one of:
        INTAKE              → Agent 1 (Orchestrator handles directly)
        GOAL_DISCOVERY      → Agent 2 (Career Explorer — exploratory sub-mode)
        PATHWAY             → Agent 3 (Career Path)
        LEARNING            → Agent 4 (Course Creation & Learning)

    Note: CAREER_EXPLORATORY and CAREER_GOAL_SETTING are sub-modes within
    Agent 2 that can be further refined by the orchestrator at runtime.
    """
    if not learner_context:
        return "INTAKE"

    learner = learner_context.get("learner", {})
    profile = learner_context.get("profile", {})
    goals = learner_context.get("goals", [])
    pathway = learner_context.get("active_pathway")

    # Check if learner is new or profile incomplete
    # Use == True to explicitly check for True value, treating None/False as incomplete
    profile_complete = profile.get("profile_complete")
    if learner.get("status") == "new" or profile_complete != True:
        return "INTAKE"

    # Check if has active pathway → LEARNING (Agent 4)
    if pathway and pathway.get("status") == "active":
        return "LEARNING"

    # Check if has committed goal but no pathway → PATHWAY (Agent 3)
    if goals:
        latest_goal = goals[0]
        if latest_goal.get("status") == "committed":
            return "PATHWAY"

    # Otherwise → GOAL_DISCOVERY (Agent 2)
    return "GOAL_DISCOVERY"


def determine_agent(mode: str) -> str:
    """
    Given a mode, return the agent name responsible for it.

    Args:
        mode: One of INTAKE, GOAL_DISCOVERY, CAREER_EXPLORATORY,
              CAREER_GOAL_SETTING, PATHWAY, LEARNING

    Returns:
        Agent key string matching agent/prompts/ file names.
    """
    return MODE_TO_AGENT.get(mode, "orchestrator_intake")
