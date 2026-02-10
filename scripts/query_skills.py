#!/usr/bin/env python3
import duckdb
import sys

DB_PATH = "~/career-explorer/data/job_skills.parquet"

def search_jobs(keyword):
    """Search for jobs by keyword"""
    result = duckdb.sql(f"""
        SELECT 
            split_part(split_part(job_link, '/view/', 2), '-at-', 1) as job_title,
            job_skills
        FROM '{DB_PATH}'
        WHERE job_link ILIKE '%{keyword}%'
        LIMIT 20
    """)
    print(result.df().to_string())

def search_skills(skill):
    """Find jobs that require a specific skill"""
    result = duckdb.sql(f"""
        SELECT 
            split_part(split_part(job_link, '/view/', 2), '-at-', 1) as job_title,
            job_skills
        FROM '{DB_PATH}'
        WHERE job_skills ILIKE '%{skill}%'
        LIMIT 20
    """)
    print(result.df().to_string())

def get_skills_for_job(job_keyword):
    """Get all skills for a job type"""
    result = duckdb.sql(f"""
        SELECT job_skills
        FROM '{DB_PATH}'
        WHERE job_link ILIKE '%{job_keyword}%'
        LIMIT 5
    """)
    df = result.df()
    all_skills = []
    for skills in df['job_skills']:
        all_skills.extend([s.strip() for s in skills.split(',')])
    unique_skills = list(set(all_skills))
    print(f"Skills for '{job_keyword}' jobs:")
    for skill in sorted(unique_skills)[:30]:
        print(f"  - {skill}")

def count_jobs():
    """Count total jobs"""
    result = duckdb.sql(f"SELECT COUNT(*) as total FROM '{DB_PATH}'")
    print(result.df())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 query_skills.py jobs <keyword>      - Search jobs")
        print("  python3 query_skills.py skills <skill>      - Find jobs with skill")
        print("  python3 query_skills.py for-job <job>       - Get skills for job type")
        print("  python3 query_skills.py count               - Count total jobs")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "jobs" and len(sys.argv) > 2:
        search_jobs(sys.argv[2])
    elif command == "skills" and len(sys.argv) > 2:
        search_skills(sys.argv[2])
    elif command == "for-job" and len(sys.argv) > 2:
        get_skills_for_job(sys.argv[2])
    elif command == "count":
        count_jobs()
    else:
        print("Invalid command. Run without arguments for help.")
