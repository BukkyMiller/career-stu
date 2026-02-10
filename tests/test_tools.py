"""
Unit tests for Career STU tools
"""
import pytest
from tools.job_search_tools import search_jobs, search_jobs_by_riasec
from tools.riasec_tools import infer_riasec_from_skills, compare_riasec_codes
from tools.salary_tools import get_salary_info
from tools.skills_tools import calculate_skill_gap


def test_search_jobs():
    """Test job search by title"""
    results = search_jobs(job_title="Data Scientist", limit=5)
    assert len(results) <= 5
    assert all("job_title" in job for job in results)


def test_search_jobs_by_riasec():
    """Test job search by RIASEC code"""
    results = search_jobs_by_riasec("IRA", limit=5)
    assert len(results) <= 5
    assert all(job["riasec_code"] == "IRA" for job in results)


def test_infer_riasec_from_skills():
    """Test RIASEC inference from skills"""
    skills = ["Python", "SQL", "Machine Learning", "Data Analysis"]
    result = infer_riasec_from_skills(skills)

    assert "riasec_code" in result
    assert "confidence" in result
    assert result["riasec_code"][0] == "I"  # Should be Investigative


def test_compare_riasec_codes():
    """Test RIASEC comparison"""
    result = compare_riasec_codes("IRA", "IRA")
    assert result["fit_score"] == 100  # Perfect match

    result = compare_riasec_codes("IRA", "SRI")
    assert result["fit_score"] < 100  # Not a perfect match


def test_get_salary_info():
    """Test salary lookup"""
    result = get_salary_info("Data Scientist")
    assert "found" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
