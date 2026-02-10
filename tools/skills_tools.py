"""
Skills gap analysis tools
"""
import duckdb
from typing import List, Dict, Any
from database.connection import JOBS_PARQUET_PATH
from tools.job_search_tools import get_job_details


def normalize_skill(skill: str) -> str:
    """Normalize a skill name for comparison"""
    return skill.lower().strip()


def calculate_skill_gap(learner_skills: List[str], target_job_link: str) -> Dict[str, Any]:
    """
    Compare learner's skills to a target job's requirements
    Returns what they have, what they need, and match percentage
    """
    # Get job details
    job = get_job_details(target_job_link)

    if "error" in job:
        return job

    # Parse job skills
    job_skills_str = job.get('job_skills', '')
    if not job_skills_str:
        return {
            "error": "No skills data available for this job",
            "job_link": target_job_link
        }

    # Split and normalize skills
    required_skills = [normalize_skill(s) for s in job_skills_str.split(',') if s.strip()]
    learner_skills_normalized = [normalize_skill(s) for s in learner_skills]

    # Find matches and gaps
    has = []
    needs = []

    for req_skill in required_skills:
        matched = False
        for learner_skill in learner_skills_normalized:
            # Exact match or substring match
            if req_skill == learner_skill or req_skill in learner_skill or learner_skill in req_skill:
                has.append(req_skill)
                matched = True
                break
        if not matched:
            needs.append(req_skill)

    # Calculate match percentage
    total_required = len(required_skills)
    match_count = len(has)
    match_percent = round((match_count / total_required * 100), 1) if total_required > 0 else 0

    return {
        "job_title": job.get('job_title'),
        "company": job.get('company'),
        "job_link": target_job_link,
        "total_required_skills": total_required,
        "skills_you_have": has,
        "skills_you_need": needs,
        "match_count": match_count,
        "gap_count": len(needs),
        "match_percentage": match_percent
    }


def find_jobs_by_skill_match(
    learner_skills: List[str],
    min_match_percent: float = 50,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Find jobs where learner has the highest skill match percentage
    This is computationally intensive, so we limit the search
    """
    learner_skills_normalized = set(normalize_skill(s) for s in learner_skills)

    # Query a sample of jobs (we'll filter by having at least one matching skill)
    # Build OR conditions for skills
    skill_conditions = [f"job_skills ILIKE '%{skill}%'" for skill in learner_skills[:10]]  # Limit to first 10 skills

    if not skill_conditions:
        return []

    query = f"""
        SELECT
            job_link,
            job_title,
            company,
            job_location,
            job_level,
            job_skills,
            riasec_code
        FROM '{JOBS_PARQUET_PATH}'
        WHERE {' OR '.join(skill_conditions)}
        LIMIT 100
    """

    result = duckdb.query(query).fetchdf()

    # Calculate match percentage for each job
    matches = []
    for _, row in result.iterrows():
        job_skills_str = row['job_skills']
        if not job_skills_str:
            continue

        required_skills = [normalize_skill(s) for s in job_skills_str.split(',') if s.strip()]
        required_set = set(required_skills)

        # Count matches
        match_count = 0
        for req_skill in required_skills:
            for learner_skill in learner_skills_normalized:
                if req_skill == learner_skill or req_skill in learner_skill or learner_skill in req_skill:
                    match_count += 1
                    break

        total_required = len(required_skills)
        match_percent = round((match_count / total_required * 100), 1) if total_required > 0 else 0

        if match_percent >= min_match_percent:
            matches.append({
                "job_link": row['job_link'],
                "job_title": row['job_title'],
                "company": row['company'],
                "job_location": row['job_location'],
                "job_level": row['job_level'],
                "riasec_code": row['riasec_code'],
                "match_percentage": match_percent,
                "skills_matched": match_count,
                "total_skills": total_required
            })

    # Sort by match percentage
    matches.sort(key=lambda x: x['match_percentage'], reverse=True)

    return matches[:limit]


def suggest_next_skills(learner_skills: List[str], target_job_link: str, count: int = 5) -> Dict[str, Any]:
    """
    Suggest which skills to learn next based on priority
    Currently returns skills in order, but could be enhanced with learning dependencies
    """
    gap_analysis = calculate_skill_gap(learner_skills, target_job_link)

    if "error" in gap_analysis:
        return gap_analysis

    needed_skills = gap_analysis["skills_you_need"]

    # For MVP, return in order. Future: could prioritize by:
    # - Frequency in similar jobs
    # - Learning difficulty
    # - Prerequisite relationships
    # - Market demand

    return {
        "job_title": gap_analysis["job_title"],
        "suggested_next_skills": needed_skills[:count],
        "total_skills_needed": len(needed_skills),
        "current_match_percentage": gap_analysis["match_percentage"]
    }
