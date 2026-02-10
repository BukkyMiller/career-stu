"""
Salary and market demand tools - Query salary_reference.parquet
"""
import duckdb
from typing import Optional, List, Dict, Any
from database.connection import SALARY_PARQUET_PATH, JOBS_PARQUET_PATH


def get_salary_info(job_title: str) -> Dict[str, Any]:
    """
    Look up salary and market demand for a job title
    """
    query = f"""
        SELECT
            "Job Title" as job_title,
            "Median Annual Advertised Salary" as median_salary,
            "Labor Market Tag" as market_demand,
            "Supply/Demand Ratio" as supply_demand_ratio,
            "Top 3 RIASEC Code" as riasec_code,
            "Latest 30 Days Unique Postings" as recent_postings
        FROM '{SALARY_PARQUET_PATH}'
        WHERE "Job Title" ILIKE '%{job_title}%'
        ORDER BY "Latest 30 Days Unique Postings" DESC
        LIMIT 5
    """

    result = duckdb.query(query).fetchdf()

    if len(result) == 0:
        return {
            "found": False,
            "message": f"No salary data found for '{job_title}'. This may be a less common job title.",
            "searched_for": job_title
        }

    return {
        "found": True,
        "results": result.to_dict('records')
    }


def get_high_demand_jobs(
    riasec_type: Optional[str] = None,
    min_salary: Optional[int] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Find jobs with labor shortages (good career prospects)
    """
    # Start with salary reference for market demand
    query = f"""
        SELECT
            s."Job Title" as job_title,
            s."Median Annual Advertised Salary" as median_salary,
            s."Labor Market Tag" as market_demand,
            s."Supply/Demand Ratio" as supply_demand_ratio,
            s."Top 3 RIASEC Code" as riasec_code,
            s."Latest 30 Days Unique Postings" as recent_postings
        FROM '{SALARY_PARQUET_PATH}' s
        WHERE s."Labor Market Tag" LIKE '%Shortage%'
    """

    if min_salary:
        query += f" AND s.\"Median Annual Advertised Salary\" >= {min_salary}"

    if riasec_type:
        # Filter by RIASEC primary type
        riasec_upper = riasec_type.upper()
        query += f" AND s.\"Top 3 RIASEC Code\" LIKE '{riasec_upper}%'"

    query += f"""
        ORDER BY s."Latest 30 Days Unique Postings" DESC
        LIMIT {limit}
    """

    result = duckdb.query(query).fetchdf()
    return result.to_dict('records')


def get_market_insights(riasec_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get overall market insights about job demand and salaries
    """
    if riasec_type:
        riasec_filter = f"WHERE \"Top 3 RIASEC Code\" LIKE '{riasec_type.upper()}%'"
    else:
        riasec_filter = ""

    query = f"""
        SELECT
            "Labor Market Tag" as market_tag,
            COUNT(*) as job_count,
            AVG("Median Annual Advertised Salary") as avg_salary,
            SUM("Latest 30 Days Unique Postings") as total_postings
        FROM '{SALARY_PARQUET_PATH}'
        {riasec_filter}
        GROUP BY "Labor Market Tag"
        ORDER BY job_count DESC
    """

    result = duckdb.query(query).fetchdf()

    return {
        "riasec_type": riasec_type,
        "market_breakdown": result.to_dict('records'),
        "total_jobs_analyzed": int(result['job_count'].sum())
    }
