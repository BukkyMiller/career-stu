---
description: "Use when looking up job skills, finding careers, matching skills to jobs, or querying the career database"
---

# Skills Database Access

We have 1.3 million jobs with their required skills.

## Query Commands

### Find jobs by title keyword
```bash
python3 scripts/query_skills.py jobs nurse
python3 scripts/query_skills.py jobs software-engineer
python3 scripts/query_skills.py jobs data-analyst
```

### Find jobs that need a specific skill
```bash
python3 scripts/query_skills.py skills python
python3 scripts/query_skills.py skills "project management"
python3 scripts/query_skills.py skills excel
```

### Get all skills for a job type
```bash
python3 scripts/query_skills.py for-job nurse
python3 scripts/query_skills.py for-job accountant
python3 scripts/query_skills.py for-job teacher
```

## Output Format
- Jobs query: Returns job titles and their skills
- Skills query: Returns jobs that require that skill
- For-job query: Returns aggregated unique skills (top 30)

## Tips
- Use hyphens for multi-word jobs: `software-engineer`, `data-analyst`
- Skills search is case-insensitive
- Limit results to 20 jobs per query
