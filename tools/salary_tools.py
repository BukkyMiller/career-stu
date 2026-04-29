"""
Salary and market demand tools - Query salary_reference.parquet and unified_jobs.parquet
Implements Labor Market Data Search Protocol: app DB first, fuzzy matching, cross-database fallback
"""
import re
import duckdb
from typing import Optional, List, Dict, Any
from database.connection import SALARY_PARQUET_PATH, JOBS_PARQUET_PATH


# Level prefixes to strip for fuzzy matching (order matters — longest first)
LEVEL_PREFIXES = [
    "senior principal", "associate principal", "principal",
    "senior lead", "lead senior", "lead",
    "senior staff", "staff senior", "staff",
    "senior associate", "associate",
    "senior", "sr.", "sr",
    "junior", "jr.", "jr",
    "entry level", "entry-level",
]


def _strip_level_prefix(title: str) -> str:
    """Strip common level prefixes from a job title for fuzzy matching."""
    clean = title.strip().lower()
    for prefix in LEVEL_PREFIXES:
        pattern = rf'^{re.escape(prefix)}\s+'
        result = re.sub(pattern, '', clean, flags=re.IGNORECASE)
        if result != clean:
            return result.strip()
    return clean


def _get_jobs_data(job_title: str, limit: int = 20) -> Dict[str, Any]:
    """Search unified_jobs.parquet for listing counts, skills, and levels.
    NOTE: RIASEC data is intentionally excluded — it only surfaces during
    career exploration assessments (Agent 2), never in labor market lookups."""
    query = f"""
        SELECT
            job_title,
            job_level,
            job_skills,
            COUNT(*) OVER () as total_listings
        FROM '{JOBS_PARQUET_PATH}'
        WHERE job_title ILIKE '%{job_title}%'
        LIMIT {limit}
    """
    result = duckdb.query(query).fetchdf()

    if len(result) == 0:
        return {"found": False, "total_listings": 0}

    # Extract common skills across listings
    all_skills = []
    for skills_str in result['job_skills'].dropna():
        all_skills.extend([s.strip() for s in skills_str.split(',') if s.strip()])

    # Count skill frequency
    skill_counts = {}
    for skill in all_skills:
        skill_lower = skill.lower()
        skill_counts[skill_lower] = skill_counts.get(skill_lower, 0) + 1

    # Sort by frequency, take top 15
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:15]

    # Get level distribution
    level_counts = result['job_level'].value_counts().to_dict() if 'job_level' in result else {}

    return {
        "found": True,
        "total_listings": int(result['total_listings'].iloc[0]) if len(result) > 0 else 0,
        "top_skills": [{"skill": s, "frequency": c} for s, c in top_skills],
        "level_distribution": level_counts,
        "sample_titles": result['job_title'].unique().tolist()[:10]
    }


def get_salary_info(job_title: str) -> Dict[str, Any]:
    """
    Look up salary and market demand for a job title.

    Implements the Labor Market Data Search Protocol:
    1. FIRST: Exact match in salary_reference.parquet
    2. IF no match: Fuzzy match (strip level prefixes like "Senior", "Lead")
    3. ALWAYS: Cross-reference unified_jobs.parquet for listing data
    4. NEVER return "no data found" without exhausting all sources
    """
    # === Step 1: Exact match in salary database ===
    # NOTE: RIASEC codes intentionally excluded from salary/market queries.
    # RIASEC only surfaces during career exploration assessments (Agent 2).
    exact_query = f"""
        SELECT
            "Job Title" as job_title,
            "Median Annual Advertised Salary" as median_salary,
            "Labor Market Tag" as market_demand,
            "Supply/Demand Ratio" as supply_demand_ratio,
            "Latest 30 Days Unique Postings" as recent_postings
        FROM '{SALARY_PARQUET_PATH}'
        WHERE "Job Title" ILIKE '%{job_title}%'
        ORDER BY "Latest 30 Days Unique Postings" DESC
        LIMIT 5
    """
    exact_result = duckdb.query(exact_query).fetchdf()

    if len(exact_result) > 0:
        # Exact match found — also get jobs data for completeness
        jobs_data = _get_jobs_data(job_title)
        return {
            "found": True,
            "match_type": "exact",
            "salary_data": exact_result.to_dict('records'),
            "jobs_data": jobs_data if jobs_data["found"] else None,
            "data_source": "salary_reference + unified_jobs"
        }

    # === Step 2: Fuzzy match — strip level prefix and try base title ===
    base_title = _strip_level_prefix(job_title)
    fuzzy_result = None

    if base_title != job_title.strip().lower():
        fuzzy_query = f"""
            SELECT
                "Job Title" as job_title,
                "Median Annual Advertised Salary" as median_salary,
                "Labor Market Tag" as market_demand,
                "Supply/Demand Ratio" as supply_demand_ratio,
                "Latest 30 Days Unique Postings" as recent_postings
            FROM '{SALARY_PARQUET_PATH}'
            WHERE "Job Title" ILIKE '%{base_title}%'
            ORDER BY "Latest 30 Days Unique Postings" DESC
            LIMIT 5
        """
        fuzzy_df = duckdb.query(fuzzy_query).fetchdf()
        if len(fuzzy_df) > 0:
            fuzzy_result = fuzzy_df.to_dict('records')

    # === Step 3: Always check unified_jobs for the ORIGINAL title ===
    jobs_data = _get_jobs_data(job_title)

    # === Step 4: Build response — never say "no data" if any source has info ===
    if fuzzy_result or jobs_data["found"]:
        response = {
            "found": True,
            "match_type": "fuzzy" if fuzzy_result else "jobs_only",
            "searched_for": job_title,
            "data_source": "",
            "note": ""
        }

        if fuzzy_result:
            response["salary_data"] = fuzzy_result
            response["base_title_used"] = base_title
            response["note"] = (
                f"No exact salary data for '{job_title}'. "
                f"Showing salary for base title '{base_title}' as reference. "
                f"Senior-level roles typically earn 15-30% more. "
                f"Use web_search for precise senior-level salary data."
            )
            response["data_source"] = "salary_reference (fuzzy match)"

        if jobs_data["found"]:
            response["jobs_data"] = jobs_data
            response["data_source"] += (
                (" + " if response["data_source"] else "") + "unified_jobs"
            )
            if not fuzzy_result:
                response["note"] = (
                    f"No salary data in salary_reference for '{job_title}', "
                    f"but found {jobs_data['total_listings']} job listings "
                    f"in unified_jobs with skills and level data. "
                    f"Use web_search for salary estimates."
                )

        return response

    # === Step 5: Neither database has data — signal to use web_search ===
    return {
        "found": False,
        "match_type": "none",
        "searched_for": job_title,
        "base_title_tried": base_title if base_title != job_title.strip().lower() else None,
        "note": (
            f"'{job_title}' not found in either database. "
            f"You MUST use web_search to find salary and market data. "
            f"Do NOT tell the learner 'we don't have that data'."
        ),
        "action_required": "web_search"
    }


def get_comprehensive_market_data(job_title: str) -> Dict[str, Any]:
    """
    Single tool that searches BOTH salary_reference AND unified_jobs databases,
    returning a combined market intelligence view for any job title.

    Returns salary data, job listing counts, common skills, market demand,
    and level distribution — all in one call. RIASEC codes are intentionally
    excluded — they only surface during career exploration assessments.

    Implements fuzzy matching so "Senior Product Manager" will still find
    "Product Manager" salary data as a baseline.
    """
    result = {
        "job_title": job_title,
        "salary_info": None,
        "jobs_info": None,
        "combined_summary": {},
        "data_sources_used": [],
        "web_search_recommended": False,
        "web_search_reason": None
    }

    # === Salary database: exact then fuzzy ===
    # NOTE: RIASEC codes intentionally excluded from market data queries.
    exact_query = f"""
        SELECT
            "Job Title" as job_title,
            "Median Annual Advertised Salary" as median_salary,
            "Labor Market Tag" as market_demand,
            "Supply/Demand Ratio" as supply_demand_ratio,
            "Latest 30 Days Unique Postings" as recent_postings
        FROM '{SALARY_PARQUET_PATH}'
        WHERE "Job Title" ILIKE '%{job_title}%'
        ORDER BY "Latest 30 Days Unique Postings" DESC
        LIMIT 5
    """
    salary_df = duckdb.query(exact_query).fetchdf()

    salary_match_type = "exact"
    base_title = None

    if len(salary_df) == 0:
        # Try fuzzy match
        base_title = _strip_level_prefix(job_title)
        if base_title != job_title.strip().lower():
            fuzzy_query = f"""
                SELECT
                    "Job Title" as job_title,
                    "Median Annual Advertised Salary" as median_salary,
                    "Labor Market Tag" as market_demand,
                    "Supply/Demand Ratio" as supply_demand_ratio,
                    "Latest 30 Days Unique Postings" as recent_postings
                FROM '{SALARY_PARQUET_PATH}'
                WHERE "Job Title" ILIKE '%{base_title}%'
                ORDER BY "Latest 30 Days Unique Postings" DESC
                LIMIT 5
            """
            salary_df = duckdb.query(fuzzy_query).fetchdf()
            salary_match_type = "fuzzy"

    if len(salary_df) > 0:
        result["salary_info"] = {
            "match_type": salary_match_type,
            "base_title_used": base_title if salary_match_type == "fuzzy" else None,
            "data": salary_df.to_dict('records')
        }
        result["data_sources_used"].append("salary_reference")

        if salary_match_type == "fuzzy":
            result["web_search_recommended"] = True
            result["web_search_reason"] = (
                f"Salary data is for base title '{base_title}', not '{job_title}'. "
                f"Use web_search for precise salary at this level."
            )

    # === Jobs database: always check ===
    jobs_data = _get_jobs_data(job_title)

    if jobs_data["found"]:
        result["jobs_info"] = jobs_data
        result["data_sources_used"].append("unified_jobs")

    # === Build combined summary ===
    summary = {}

    if result["salary_info"]:
        top_salary = result["salary_info"]["data"][0]
        summary["median_salary"] = top_salary.get("median_salary")
        summary["market_demand"] = top_salary.get("market_demand")
        summary["supply_demand_ratio"] = top_salary.get("supply_demand_ratio")
        summary["salary_is_estimate"] = salary_match_type == "fuzzy"
        if salary_match_type == "fuzzy":
            summary["salary_note"] = (
                f"Based on '{base_title}' — senior-level typically earns 15-30% more"
            )

    if jobs_data["found"]:
        summary["total_job_listings"] = jobs_data["total_listings"]
        summary["top_required_skills"] = [s["skill"] for s in jobs_data["top_skills"][:10]]
        summary["job_levels_available"] = jobs_data.get("level_distribution", {})

    result["combined_summary"] = summary

    # If neither database had anything
    if not result["salary_info"] and not jobs_data["found"]:
        result["web_search_recommended"] = True
        result["web_search_reason"] = (
            f"'{job_title}' not found in either database. "
            f"You MUST use web_search. Do NOT tell the learner 'we don't have that data'."
        )

    return result


def get_high_demand_jobs(
    riasec_type: Optional[str] = None,
    min_salary: Optional[int] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Find jobs with labor shortages (good career prospects)
    """
    # Start with salary reference for market demand
    # NOTE: RIASEC is used internally for filtering but NOT returned in results.
    # RIASEC only surfaces during career exploration assessments (Agent 2).
    query = f"""
        SELECT
            s."Job Title" as job_title,
            s."Median Annual Advertised Salary" as median_salary,
            s."Labor Market Tag" as market_demand,
            s."Supply/Demand Ratio" as supply_demand_ratio,
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


def get_market_insights() -> Dict[str, Any]:
    """
    Get overall market insights about job demand and salaries.
    NOTE: RIASEC filtering removed — RIASEC only surfaces during
    career exploration assessments (Agent 2), not in market data.
    """
    query = f"""
        SELECT
            "Labor Market Tag" as market_tag,
            COUNT(*) as job_count,
            AVG("Median Annual Advertised Salary") as avg_salary,
            SUM("Latest 30 Days Unique Postings") as total_postings
        FROM '{SALARY_PARQUET_PATH}'
        GROUP BY "Labor Market Tag"
        ORDER BY job_count DESC
    """

    result = duckdb.query(query).fetchdf()

    return {
        "market_breakdown": result.to_dict('records'),
        "total_jobs_analyzed": int(result['job_count'].sum())
    }
