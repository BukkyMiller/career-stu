#!/usr/bin/env python3
"""
RIASEC Query Tool
=================
Query and explore the classified jobs database.

Usage:
    # Find jobs by RIASEC code
    python query_riasec.py --code IRC
    
    # Find jobs by primary type
    python query_riasec.py --type Investigative
    
    # Search for specific skills
    python query_riasec.py --skills "Python, Machine Learning"
    
    # Get statistics
    python query_riasec.py --stats
    
    # Find similar jobs to a title
    python query_riasec.py --similar "Software Engineer"
"""

import os
import sys
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'data')

# Default database path
DEFAULT_DB = os.path.join(DATA_DIR, 'jobs_riasec.parquet')

def check_dependencies():
    try:
        import duckdb
        import pandas
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install',
            '--break-system-packages', '--quiet',
            'duckdb', 'pandas', 'pyarrow'
        ])

def get_connection(db_path: str):
    """Get DuckDB connection."""
    check_dependencies()
    import duckdb
    return duckdb.connect()

def query_by_code(db_path: str, code: str, limit: int = 20):
    """Find jobs with a specific RIASEC code."""
    conn = get_connection(db_path)
    
    query = f"""
    SELECT 
        riasec_code,
        extracted_title,
        riasec_confidence,
        job_skills
    FROM '{db_path}'
    WHERE riasec_code = '{code.upper()}'
    ORDER BY riasec_confidence DESC
    LIMIT {limit}
    """
    
    print(f"\n{'='*60}")
    print(f"JOBS WITH RIASEC CODE: {code.upper()}")
    print(f"{'='*60}\n")
    
    results = conn.execute(query).fetchdf()
    
    if len(results) == 0:
        print(f"No jobs found with code {code}")
        return
    
    for _, row in results.iterrows():
        print(f"Title: {row['extracted_title']}")
        print(f"Confidence: {row['riasec_confidence']:.0%}")
        skills = str(row['job_skills'])[:100] + '...' if len(str(row['job_skills'])) > 100 else str(row['job_skills'])
        print(f"Skills: {skills}")
        print("-" * 40)
    
    # Count total
    count_query = f"SELECT COUNT(*) FROM '{db_path}' WHERE riasec_code = '{code.upper()}'"
    total = conn.execute(count_query).fetchone()[0]
    print(f"\nTotal jobs with code {code}: {total:,}")
    
    conn.close()

def query_by_type(db_path: str, type_name: str, limit: int = 20):
    """Find jobs with a specific primary RIASEC type."""
    conn = get_connection(db_path)
    
    query = f"""
    SELECT 
        riasec_code,
        primary_riasec_type,
        extracted_title,
        riasec_confidence,
        job_skills
    FROM '{db_path}'
    WHERE LOWER(primary_riasec_type) LIKE '%{type_name.lower()}%'
    ORDER BY riasec_confidence DESC
    LIMIT {limit}
    """
    
    print(f"\n{'='*60}")
    print(f"JOBS WITH PRIMARY TYPE: {type_name.title()}")
    print(f"{'='*60}\n")
    
    results = conn.execute(query).fetchdf()
    
    if len(results) == 0:
        print(f"No jobs found with type {type_name}")
        return
    
    # Group by code
    code_counts = results['riasec_code'].value_counts()
    print("Top RIASEC codes for this type:")
    for code, count in code_counts.head(10).items():
        print(f"  {code}: {count}")
    
    print(f"\n{'─'*40}")
    print("Sample jobs:")
    print(f"{'─'*40}\n")
    
    for _, row in results.head(10).iterrows():
        print(f"[{row['riasec_code']}] {row['extracted_title']} ({row['riasec_confidence']:.0%})")
    
    # Total count
    count_query = f"SELECT COUNT(*) FROM '{db_path}' WHERE LOWER(primary_riasec_type) LIKE '%{type_name.lower()}%'"
    total = conn.execute(count_query).fetchone()[0]
    print(f"\nTotal jobs with {type_name} primary type: {total:,}")
    
    conn.close()

def query_by_skills(db_path: str, skills: str, limit: int = 20):
    """Find jobs matching specific skills."""
    conn = get_connection(db_path)
    
    # Build skill conditions
    skill_list = [s.strip().lower() for s in skills.split(',')]
    conditions = ' AND '.join([f"LOWER(job_skills) LIKE '%{s}%'" for s in skill_list])
    
    query = f"""
    SELECT 
        riasec_code,
        extracted_title,
        riasec_confidence,
        job_skills
    FROM '{db_path}'
    WHERE {conditions}
    ORDER BY riasec_confidence DESC
    LIMIT {limit}
    """
    
    print(f"\n{'='*60}")
    print(f"JOBS WITH SKILLS: {skills}")
    print(f"{'='*60}\n")
    
    results = conn.execute(query).fetchdf()
    
    if len(results) == 0:
        print(f"No jobs found with skills: {skills}")
        return
    
    # RIASEC distribution for these skills
    code_counts = results['riasec_code'].value_counts()
    print("RIASEC codes for jobs with these skills:")
    for code, count in code_counts.head(10).items():
        pct = count / len(results) * 100
        print(f"  {code}: {count} ({pct:.0f}%)")
    
    print(f"\n{'─'*40}")
    print("Sample jobs:")
    print(f"{'─'*40}\n")
    
    for _, row in results.head(10).iterrows():
        print(f"[{row['riasec_code']}] {row['extracted_title']}")
    
    # Total count
    count_query = f"SELECT COUNT(*) FROM '{db_path}' WHERE {conditions}"
    total = conn.execute(count_query).fetchone()[0]
    print(f"\nTotal matching jobs: {total:,}")
    
    conn.close()

def show_statistics(db_path: str):
    """Show database statistics."""
    conn = get_connection(db_path)
    
    print(f"\n{'='*60}")
    print("DATABASE STATISTICS")
    print(f"{'='*60}")
    
    # Total count
    total = conn.execute(f"SELECT COUNT(*) FROM '{db_path}'").fetchone()[0]
    print(f"\nTotal jobs: {total:,}")
    
    # RIASEC code distribution
    print(f"\n{'─'*40}")
    print("RIASEC CODE DISTRIBUTION (Top 25)")
    print(f"{'─'*40}")
    
    code_query = f"""
    SELECT riasec_code, COUNT(*) as count
    FROM '{db_path}'
    GROUP BY riasec_code
    ORDER BY count DESC
    LIMIT 25
    """
    
    codes = conn.execute(code_query).fetchdf()
    for _, row in codes.iterrows():
        pct = row['count'] / total * 100
        bar = '█' * int(pct / 2)
        print(f"  {row['riasec_code']}: {row['count']:>10,} ({pct:>5.1f}%) {bar}")
    
    # Primary type distribution
    print(f"\n{'─'*40}")
    print("PRIMARY TYPE DISTRIBUTION")
    print(f"{'─'*40}")
    
    type_query = f"""
    SELECT primary_riasec_type, COUNT(*) as count
    FROM '{db_path}'
    GROUP BY primary_riasec_type
    ORDER BY count DESC
    """
    
    types = conn.execute(type_query).fetchdf()
    for _, row in types.iterrows():
        pct = row['count'] / total * 100
        bar = '█' * int(pct / 5)
        print(f"  {row['primary_riasec_type']:<15}: {row['count']:>10,} ({pct:>5.1f}%) {bar}")
    
    # Confidence distribution
    print(f"\n{'─'*40}")
    print("CONFIDENCE DISTRIBUTION")
    print(f"{'─'*40}")
    
    conf_query = f"""
    SELECT 
        CASE 
            WHEN riasec_confidence >= 0.7 THEN 'High (≥70%)'
            WHEN riasec_confidence >= 0.4 THEN 'Medium (40-70%)'
            ELSE 'Low (<40%)'
        END as confidence_level,
        COUNT(*) as count
    FROM '{db_path}'
    GROUP BY confidence_level
    ORDER BY confidence_level
    """
    
    conf = conn.execute(conf_query).fetchdf()
    for _, row in conf.iterrows():
        pct = row['count'] / total * 100
        print(f"  {row['confidence_level']:<20}: {row['count']:>10,} ({pct:>5.1f}%)")
    
    # Top job titles
    print(f"\n{'─'*40}")
    print("TOP JOB TITLES")
    print(f"{'─'*40}")
    
    title_query = f"""
    SELECT extracted_title, riasec_code, COUNT(*) as count
    FROM '{db_path}'
    WHERE extracted_title IS NOT NULL AND extracted_title != ''
    GROUP BY extracted_title, riasec_code
    ORDER BY count DESC
    LIMIT 20
    """
    
    titles = conn.execute(title_query).fetchdf()
    for _, row in titles.iterrows():
        print(f"  [{row['riasec_code']}] {row['extracted_title'][:40]:<40}: {row['count']:>6,}")
    
    conn.close()

def find_similar(db_path: str, title: str, limit: int = 20):
    """Find jobs similar to a given title."""
    conn = get_connection(db_path)
    
    # First, find the RIASEC code for jobs with this title
    title_query = f"""
    SELECT riasec_code, COUNT(*) as count
    FROM '{db_path}'
    WHERE LOWER(extracted_title) LIKE '%{title.lower()}%'
    GROUP BY riasec_code
    ORDER BY count DESC
    LIMIT 1
    """
    
    result = conn.execute(title_query).fetchdf()
    
    if len(result) == 0:
        print(f"No jobs found matching '{title}'")
        return
    
    target_code = result.iloc[0]['riasec_code']
    
    print(f"\n{'='*60}")
    print(f"JOBS SIMILAR TO: {title}")
    print(f"{'='*60}")
    print(f"\nTarget RIASEC code: {target_code}")
    
    # Find other jobs with the same code
    similar_query = f"""
    SELECT DISTINCT extracted_title, riasec_confidence, riasec_code
    FROM '{db_path}'
    WHERE riasec_code = '{target_code}'
    AND LOWER(extracted_title) NOT LIKE '%{title.lower()}%'
    ORDER BY riasec_confidence DESC
    LIMIT {limit}
    """
    
    similar = conn.execute(similar_query).fetchdf()
    
    print(f"\nJobs with same RIASEC profile ({target_code}):")
    print(f"{'─'*40}")
    
    for _, row in similar.iterrows():
        print(f"  {row['extracted_title']} ({row['riasec_confidence']:.0%})")
    
    conn.close()

def main():
    parser = argparse.ArgumentParser(
        description="Query the RIASEC-classified jobs database",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--db', type=str, default=DEFAULT_DB, help='Database path')
    parser.add_argument('--code', type=str, help='Query by RIASEC code (e.g., IRC)')
    parser.add_argument('--type', type=str, help='Query by primary type (e.g., Investigative)')
    parser.add_argument('--skills', type=str, help='Query by skills (comma-separated)')
    parser.add_argument('--similar', type=str, help='Find jobs similar to a title')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    parser.add_argument('--limit', type=int, default=20, help='Result limit')
    
    args = parser.parse_args()
    
    # Check if database exists
    if not os.path.exists(args.db):
        print(f"Database not found: {args.db}")
        print("\nRun process_jobs.py first to create the classified database:")
        print("  python process_jobs.py --input data/job_skills.csv --output data/jobs_riasec.parquet")
        sys.exit(1)
    
    if args.code:
        query_by_code(args.db, args.code, args.limit)
    elif args.type:
        query_by_type(args.db, args.type, args.limit)
    elif args.skills:
        query_by_skills(args.db, args.skills, args.limit)
    elif args.similar:
        find_similar(args.db, args.similar, args.limit)
    elif args.stats:
        show_statistics(args.db)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
