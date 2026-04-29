# Tools Reference

Career STU provides 22 tools organized into 6 categories.

## Job Search Tools (3)

### search_jobs
Search jobs by title, skills, location, or level in the unified_jobs database.

```python
{
    "name": "search_jobs",
    "parameters": {
        "job_title": {"type": "string", "optional": True},
        "skills": {"type": "array", "items": {"type": "string"}, "optional": True},
        "location": {"type": "string", "optional": True},
        "job_level": {"type": "string", "optional": True},  # Entry, Mid-Senior, Director, Associate
        "limit": {"type": "integer", "default": 10}
    }
}
```

### search_jobs_by_riasec
Find jobs matching a RIASEC code.

```python
{
    "name": "search_jobs_by_riasec",
    "parameters": {
        "riasec_code": {"type": "string", "required": True},  # e.g., "SRI", "IRA"
        "primary_type_only": {"type": "boolean", "default": False},
        "job_level": {"type": "string", "optional": True},
        "limit": {"type": "integer", "default": 10}
    }
}
```

### get_job_details
Get full details for a specific job using its job_link.

```python
{
    "name": "get_job_details",
    "parameters": {
        "job_link": {"type": "string", "required": True}
    }
}
```

## RIASEC Tools (3)

### infer_riasec_from_skills
Given a list of skills, predict the most likely RIASEC code.

```python
{
    "name": "infer_riasec_from_skills",
    "parameters": {
        "skills": {"type": "array", "items": {"type": "string"}, "required": True}
    }
}
```

### get_riasec_description
Get description and career themes for a RIASEC code.

```python
{
    "name": "get_riasec_description",
    "parameters": {
        "riasec_code": {"type": "string", "required": True}
    }
}
```

### compare_riasec_codes
Compare learner's RIASEC code to a target job's RIASEC code to assess fit.

```python
{
    "name": "compare_riasec_codes",
    "parameters": {
        "learner_riasec": {"type": "string", "required": True},
        "job_riasec": {"type": "string", "required": True}
    }
}
```

## Salary & Market Tools (4)

### get_salary_info
Look up salary and market demand for a job title. Implements fuzzy matching.

```python
{
    "name": "get_salary_info",
    "parameters": {
        "job_title": {"type": "string", "required": True}
    }
}
```

Returns: salary data, market demand, recent postings count. If no exact match, tries base title (strips "Senior", "Lead", etc.) and cross-references unified_jobs for listing data.

### get_comprehensive_market_data
Search BOTH salary_reference AND unified_jobs databases in a single call.

```python
{
    "name": "get_comprehensive_market_data",
    "parameters": {
        "job_title": {"type": "string", "required": True}
    }
}
```

Returns: salary data, job listing counts, common skills, market demand, level distribution.

### get_high_demand_jobs
Find jobs with labor shortages (good career prospects).

```python
{
    "name": "get_high_demand_jobs",
    "parameters": {
        "riasec_type": {"type": "string", "optional": True},  # S, I, R, A, E, C
        "min_salary": {"type": "integer", "optional": True},
        "limit": {"type": "integer", "default": 10}
    }
}
```

### get_market_insights
Get overall market insights about job demand and salaries by labor market category.

```python
{
    "name": "get_market_insights",
    "parameters": {}
}
```

## Skills Tools (3)

### calculate_skill_gap
Compare learner's skills to a target job's requirements.

```python
{
    "name": "calculate_skill_gap",
    "parameters": {
        "learner_skills": {"type": "array", "items": {"type": "string"}, "required": True},
        "target_job_link": {"type": "string", "required": True}
    }
}
```

Returns: skills you have, skills you need, match percentage.

### find_jobs_by_skill_match
Find jobs where learner has the highest skill match percentage.

```python
{
    "name": "find_jobs_by_skill_match",
    "parameters": {
        "learner_skills": {"type": "array", "items": {"type": "string"}, "required": True},
        "min_match_percent": {"type": "number", "default": 50},
        "limit": {"type": "integer", "default": 10}
    }
}
```

### suggest_next_skills
Suggest which skills to learn next based on skill gap analysis.

```python
{
    "name": "suggest_next_skills",
    "parameters": {
        "learner_skills": {"type": "array", "items": {"type": "string"}, "required": True},
        "target_job_link": {"type": "string", "required": True},
        "count": {"type": "integer", "default": 5}
    }
}
```

## Learner Tools (5)

### get_learner_context
Get full learner profile, skills, goals, and pathway progress.

```python
{
    "name": "get_learner_context",
    "parameters": {
        "learner_id": {"type": "string", "required": True}
    }
}
```

### update_learner_profile
Update learner profile information.

```python
{
    "name": "update_learner_profile",
    "parameters": {
        "learner_id": {"type": "string", "required": True},
        "updates": {"type": "object", "required": True}
    }
}
```

Allowed fields: `current_job_title`, `current_industry`, `years_experience`, `education_level`, `weekly_study_hours`, `preferred_study_times`, `has_family_obligations`, `employment_status`, `preferred_format`, `disposition`, `inferred_riasec_code`, `profile_complete`, `behavioral_capital_signal`, `social_capital_signal`, `navigation_capital_signal`

### add_learner_skill
Add a skill to learner's profile.

```python
{
    "name": "add_learner_skill",
    "parameters": {
        "learner_id": {"type": "string", "required": True},
        "skill_name": {"type": "string", "required": True},
        "proficiency_level": {"type": "string", "required": True},  # none, beginner, intermediate, advanced, expert
        "evidence_source": {"type": "string", "default": "self_reported"}  # self_reported, validated, credential
    }
}
```

### set_learner_goal
Set or update learner's career goal.

```python
{
    "name": "set_learner_goal",
    "parameters": {
        "learner_id": {"type": "string", "required": True},
        "target_job_title": {"type": "string", "required": True},
        "status": {"type": "string", "default": "exploring"}  # exploring, committed, achieved, changed
    }
}
```

### create_learner
Create a new learner record.

```python
{
    "name": "create_learner",
    "parameters": {
        "email": {"type": "string", "required": True},
        "name": {"type": "string", "optional": True}
    }
}
```

## Pathway Tools (4)

### create_pathway
Create a learning pathway for the learner.

```python
{
    "name": "create_pathway",
    "parameters": {
        "learner_id": {"type": "string", "required": True},
        "goal_id": {"type": "string", "required": True},
        "skills_to_learn": {"type": "array", "items": {"type": "string"}, "required": True}
    }
}
```

### update_pathway_progress
Update the status of a skill in a pathway.

```python
{
    "name": "update_pathway_progress",
    "parameters": {
        "pathway_id": {"type": "string", "required": True},
        "skill_name": {"type": "string", "required": True},
        "new_status": {"type": "string", "required": True}  # not_started, in_progress, completed
    }
}
```

### get_pathway_details
Get detailed information about a pathway including all skills and their status.

```python
{
    "name": "get_pathway_details",
    "parameters": {
        "pathway_id": {"type": "string", "required": True}
    }
}
```

### get_current_skill
Get the current skill the learner should be working on.

```python
{
    "name": "get_current_skill",
    "parameters": {
        "pathway_id": {"type": "string", "required": True}
    }
}
```

Returns either the skill marked `in_progress`, or the next `not_started` skill, or `all_completed`.

## Query Examples

### Search jobs by RIASEC code

```python
import duckdb

result = duckdb.query("""
    SELECT job_title, company, job_location, job_level, riasec_confidence
    FROM 'data/unified_jobs.parquet'
    WHERE riasec_code = 'SRI'
    ORDER BY riasec_confidence DESC
    LIMIT 10
""").fetchdf()
```

### Get salary and market demand

```python
result = duckdb.query("""
    SELECT
        "Job Title",
        "Median Annual Advertised Salary" as salary,
        "Labor Market Tag" as market_status
    FROM 'data/salary_reference.parquet'
    WHERE "Job Title" ILIKE '%data scientist%'
""").fetchdf()
```

### Calculate skill gap

```python
def calculate_skill_gap(learner_skills: list[str], job_skills_string: str) -> dict:
    required = set(s.strip() for s in job_skills_string.split(','))
    has = set(learner_skills)
    return {
        "has": list(has & required),
        "needs": list(required - has),
        "match_percent": round(len(has & required) / len(required) * 100, 1) if required else 0
    }
```
