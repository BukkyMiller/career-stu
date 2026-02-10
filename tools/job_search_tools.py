"""
Job search tools - Query the unified_jobs.parquet database
"""
import duckdb
from typing import Optional, List, Dict, Any
from database.connection import JOBS_PARQUET_PATH


def search_jobs(
    job_title: Optional[str] = None,
    skills: Optional[List[str]] = None,
    location: Optional[str] = None,
    job_level: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search jobs by title, skills, location, or level
    """
    query = f"""
        SELECT
            job_link,
            job_title,
            company,
            job_location,
            job_level,
            job_skills,
            riasec_code,
            riasec_confidence,
            primary_riasec_type
        FROM '{JOBS_PARQUET_PATH}'
        WHERE 1=1
    """

    conditions = []

    if job_title:
        conditions.append(f"job_title ILIKE '%{job_title}%'")

    if skills:
        # Match any of the provided skills
        skill_conditions = [f"job_skills ILIKE '%{skill}%'" for skill in skills]
        conditions.append(f"({' OR '.join(skill_conditions)})")

    if location:
        conditions.append(f"job_location ILIKE '%{location}%'")

    if job_level:
        conditions.append(f"job_level ILIKE '%{job_level}%'")

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += f" ORDER BY riasec_confidence DESC LIMIT {limit}"

    result = duckdb.query(query).fetchdf()
    return result.to_dict('records')


def search_jobs_by_riasec(
    riasec_code: str,
    primary_type_only: bool = False,
    job_level: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Find jobs matching a RIASEC code
    """
    if primary_type_only:
        # Match only the first letter
        primary_type = riasec_code[0].upper()
        where_clause = f"primary_riasec_type = '{primary_type}'"
    else:
        # Match exact RIASEC code
        where_clause = f"riasec_code = '{riasec_code.upper()}'"

    query = f"""
        SELECT
            job_link,
            job_title,
            company,
            job_location,
            job_level,
            job_skills,
            riasec_code,
            riasec_confidence,
            primary_riasec_type
        FROM '{JOBS_PARQUET_PATH}'
        WHERE {where_clause}
    """

    if job_level:
        query += f" AND job_level ILIKE '%{job_level}%'"

    query += f" ORDER BY riasec_confidence DESC LIMIT {limit}"

    result = duckdb.query(query).fetchdf()
    return result.to_dict('records')


def get_job_details(job_link: str) -> Dict[str, Any]:
    """
    Get full details for a specific job
    """
    query = f"""
        SELECT *
        FROM '{JOBS_PARQUET_PATH}'
        WHERE job_link = '{job_link}'
    """

    result = duckdb.query(query).fetchdf()

    if len(result) == 0:
        return {"error": f"Job not found: {job_link}"}

    return result.iloc[0].to_dict()
