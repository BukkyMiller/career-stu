#!/usr/bin/env python3
"""
RIASEC Database Processor
=========================
Process large job databases (1M+ jobs) efficiently with RIASEC classification.

Uses DuckDB for efficient data processing and supports:
- CSV and Parquet input/output
- Batch processing with progress tracking
- Memory-efficient streaming
- Parallel processing options

Usage:
    # Process job_skills.csv
    python process_jobs.py --input data/job_skills.csv --output data/jobs_riasec.parquet
    
    # Process and join multiple files
    python process_jobs.py --skills-csv job_skills.csv --details-csv job_details.csv --output unified.parquet
    
    # Quick sample test
    python process_jobs.py --input data/job_skills.csv --sample 1000
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional
import time

# Add scripts directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from riasec_classifier import classify_job, RIASEC_TYPES, COMBINATIONS

# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_BATCH_SIZE = 50000
PROGRESS_INTERVAL = 10000

# ============================================================================
# DEPENDENCY CHECK
# ============================================================================

def check_dependencies():
    """Check and install required packages."""
    required = {'duckdb': 'duckdb', 'pandas': 'pandas', 'pyarrow': 'pyarrow'}
    missing = []
    
    for package, pip_name in required.items():
        try:
            __import__(package)
        except ImportError:
            missing.append(pip_name)
    
    if missing:
        print(f"Installing required packages: {', '.join(missing)}")
        import subprocess
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            '--break-system-packages', '--quiet'
        ] + missing)
        print("Packages installed successfully!")

# ============================================================================
# DATA PROCESSING
# ============================================================================

def extract_title_from_link(job_link: str) -> str:
    """Extract job title from LinkedIn URL."""
    if not job_link or not isinstance(job_link, str):
        return ""
    try:
        import re
        if '/view/' in job_link:
            path = job_link.split('/view/')[-1]
            path = re.sub(r'-\d+$', '', path)
            if '-at-' in path:
                path = path.split('-at-')[0]
            return path.replace('-', ' ').strip().title()
    except:
        pass
    return ""

def process_batch(batch_data: List[tuple], has_title: bool = False) -> List[Dict]:
    """Process a batch of jobs and return classification results."""
    results = []
    
    for row in batch_data:
        if has_title:
            job_link, job_skills, job_title = row
        else:
            job_link, job_skills = row
            job_title = extract_title_from_link(job_link)
        
        skills = str(job_skills) if job_skills else ""
        title = str(job_title) if job_title else ""
        
        classification = classify_job(skills, title, job_link)
        
        results.append({
            'job_link': job_link,
            'job_skills': job_skills,
            'extracted_title': title,
            'riasec_code': classification['riasec_code'],
            'riasec_confidence': classification['confidence'],
            'primary_riasec_type': classification['primary_type'],
            'riasec_total_score': classification['total_score']
        })
    
    return results

def process_csv_file(input_path: str, output_path: str, 
                     skills_col: str = 'job_skills',
                     link_col: str = 'job_link',
                     title_col: str = None,
                     batch_size: int = DEFAULT_BATCH_SIZE,
                     sample_size: int = None):
    """
    Process a CSV file with RIASEC classification.
    
    Args:
        input_path: Path to input CSV
        output_path: Path to output file (CSV or Parquet)
        skills_col: Column name for skills
        link_col: Column name for job link
        title_col: Column name for job title (optional)
        batch_size: Number of rows to process at a time
        sample_size: If set, only process this many rows
    """
    check_dependencies()
    import duckdb
    import pandas as pd
    
    print("\n" + "="*60)
    print("RIASEC DATABASE PROCESSOR")
    print("="*60)
    print(f"\nInput:  {input_path}")
    print(f"Output: {output_path}")
    
    conn = duckdb.connect()
    
    # Get total row count
    count_query = f"SELECT COUNT(*) FROM '{input_path}'"
    total_rows = conn.execute(count_query).fetchone()[0]
    
    if sample_size:
        total_rows = min(total_rows, sample_size)
        print(f"\nSample mode: Processing {total_rows:,} rows")
    else:
        print(f"\nTotal rows: {total_rows:,}")
    
    print(f"Batch size: {batch_size:,}")
    print(f"\nProcessing...")
    
    start_time = datetime.now()
    all_results = []
    processed = 0
    
    # Build query
    select_cols = [link_col, skills_col]
    if title_col:
        select_cols.append(title_col)
    
    while processed < total_rows:
        # Query batch
        limit = min(batch_size, total_rows - processed)
        
        query = f"""
        SELECT {', '.join(select_cols)}
        FROM '{input_path}'
        LIMIT {limit}
        OFFSET {processed}
        """
        
        batch_data = conn.execute(query).fetchall()
        
        # Process batch
        batch_results = process_batch(batch_data, has_title=(title_col is not None))
        all_results.extend(batch_results)
        
        processed += len(batch_data)
        
        # Progress update
        elapsed = (datetime.now() - start_time).total_seconds()
        rate = processed / elapsed if elapsed > 0 else 0
        eta = (total_rows - processed) / rate if rate > 0 else 0
        
        print(f"  {processed:,}/{total_rows:,} ({processed/total_rows*100:.1f}%) "
              f"- {rate:.0f} rows/sec - ETA: {eta/60:.1f} min")
    
    # Convert to DataFrame
    print("\nConverting to DataFrame...")
    df = pd.DataFrame(all_results)
    
    # Save output
    print(f"Saving to {output_path}...")
    if output_path.endswith('.parquet'):
        df.to_parquet(output_path, compression='zstd', index=False)
    else:
        df.to_csv(output_path, index=False)
    
    # Print statistics
    elapsed_total = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60)
    print(f"\nTotal rows processed: {len(df):,}")
    print(f"Total time: {elapsed_total/60:.1f} minutes")
    print(f"Average rate: {len(df)/elapsed_total:.0f} rows/second")
    
    # RIASEC distribution
    print("\n" + "-"*40)
    print("RIASEC CODE DISTRIBUTION (Top 20)")
    print("-"*40)
    code_dist = df['riasec_code'].value_counts().head(20)
    for code, count in code_dist.items():
        pct = count / len(df) * 100
        bar = '█' * int(pct / 2)
        print(f"  {code}: {count:>8,} ({pct:>5.1f}%) {bar}")
    
    # Primary type distribution
    print("\n" + "-"*40)
    print("PRIMARY TYPE DISTRIBUTION")
    print("-"*40)
    type_dist = df['primary_riasec_type'].value_counts()
    for type_name, count in type_dist.items():
        pct = count / len(df) * 100
        bar = '█' * int(pct / 5)
        print(f"  {type_name:<15}: {count:>8,} ({pct:>5.1f}%) {bar}")
    
    # Confidence distribution
    print("\n" + "-"*40)
    print("CONFIDENCE LEVELS")
    print("-"*40)
    high_conf = (df['riasec_confidence'] >= 0.7).sum()
    med_conf = ((df['riasec_confidence'] >= 0.4) & (df['riasec_confidence'] < 0.7)).sum()
    low_conf = (df['riasec_confidence'] < 0.4).sum()
    print(f"  High (≥70%):   {high_conf:>8,} ({high_conf/len(df)*100:>5.1f}%)")
    print(f"  Medium (40-70%): {med_conf:>8,} ({med_conf/len(df)*100:>5.1f}%)")
    print(f"  Low (<40%):    {low_conf:>8,} ({low_conf/len(df)*100:>5.1f}%)")
    
    conn.close()
    return df

def join_and_process(skills_csv: str, details_csv: str, output_path: str,
                     batch_size: int = DEFAULT_BATCH_SIZE):
    """
    Join skills CSV with details CSV and process with RIASEC classification.
    
    Args:
        skills_csv: Path to job_skills.csv (job_link, job_skills)
        details_csv: Path to job details CSV (job_link, job_title, company, etc.)
        output_path: Path to output file
    """
    check_dependencies()
    import duckdb
    import pandas as pd
    
    print("\n" + "="*60)
    print("JOIN AND PROCESS")
    print("="*60)
    print(f"\nSkills CSV:  {skills_csv}")
    print(f"Details CSV: {details_csv}")
    print(f"Output:      {output_path}")
    
    conn = duckdb.connect()
    
    # Check columns in details CSV
    sample_query = f"SELECT * FROM '{details_csv}' LIMIT 1"
    sample = conn.execute(sample_query).fetchdf()
    detail_cols = list(sample.columns)
    print(f"\nDetails CSV columns: {detail_cols}")
    
    # Find title column
    title_col = None
    for col in ['job_title', 'title', 'Job Title', 'position']:
        if col in detail_cols:
            title_col = col
            break
    
    print(f"Using title column: {title_col or 'None (will extract from URL)'}")
    
    # Count matching records
    count_query = f"""
    SELECT COUNT(*) FROM '{skills_csv}' s
    INNER JOIN '{details_csv}' d ON s.job_link = d.job_link
    """
    
    try:
        match_count = conn.execute(count_query).fetchone()[0]
        print(f"\nMatching records: {match_count:,}")
    except Exception as e:
        print(f"\nJoin failed: {e}")
        print("Processing skills CSV only...")
        return process_csv_file(skills_csv, output_path, batch_size=batch_size)
    
    # Process with join
    print("\nProcessing joined data...")
    start_time = datetime.now()
    
    # Build joined query
    join_cols = ['s.job_link', 's.job_skills']
    if title_col:
        join_cols.append(f'd.{title_col} as job_title')
    for col in detail_cols:
        if col not in ['job_link', title_col]:
            join_cols.append(f'd.{col}')
    
    all_results = []
    offset = 0
    
    while offset < match_count:
        query = f"""
        SELECT {', '.join(join_cols)}
        FROM '{skills_csv}' s
        INNER JOIN '{details_csv}' d ON s.job_link = d.job_link
        LIMIT {batch_size}
        OFFSET {offset}
        """
        
        batch_df = conn.execute(query).fetchdf()
        
        # Classify each row
        for _, row in batch_df.iterrows():
            skills = str(row.get('job_skills', '')) if pd.notna(row.get('job_skills')) else ''
            title = str(row.get('job_title', '')) if 'job_title' in row and pd.notna(row.get('job_title')) else ''
            link = str(row.get('job_link', ''))
            
            if not title:
                title = extract_title_from_link(link)
            
            result = classify_job(skills, title, link)
            
            row_dict = row.to_dict()
            row_dict['extracted_title'] = title
            row_dict['riasec_code'] = result['riasec_code']
            row_dict['riasec_confidence'] = result['confidence']
            row_dict['primary_riasec_type'] = result['primary_type']
            
            all_results.append(row_dict)
        
        offset += len(batch_df)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        rate = offset / elapsed if elapsed > 0 else 0
        eta = (match_count - offset) / rate if rate > 0 else 0
        print(f"  {offset:,}/{match_count:,} ({offset/match_count*100:.1f}%) "
              f"- {rate:.0f} rows/sec - ETA: {eta/60:.1f} min")
    
    # Save
    df = pd.DataFrame(all_results)
    print(f"\nSaving {len(df):,} rows to {output_path}...")
    
    if output_path.endswith('.parquet'):
        df.to_parquet(output_path, compression='zstd', index=False)
    else:
        df.to_csv(output_path, index=False)
    
    print(f"\nComplete! Total time: {(datetime.now() - start_time).total_seconds()/60:.1f} minutes")
    
    conn.close()
    return df

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Process large job databases with RIASEC classification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process skills CSV
  python process_jobs.py --input data/job_skills.csv --output data/jobs_riasec.parquet
  
  # Quick test with sample
  python process_jobs.py --input data/job_skills.csv --sample 1000
  
  # Join and process multiple files
  python process_jobs.py --skills-csv skills.csv --details-csv details.csv --output unified.parquet
  
  # Custom column names
  python process_jobs.py --input jobs.csv --output classified.csv --skills-col skills --link-col url
        """
    )
    
    # Input options
    parser.add_argument('--input', '-i', type=str, help='Input CSV file')
    parser.add_argument('--skills-csv', type=str, help='Skills CSV (for join mode)')
    parser.add_argument('--details-csv', type=str, help='Details CSV (for join mode)')
    
    # Output options
    parser.add_argument('--output', '-o', type=str, help='Output file (CSV or Parquet)')
    
    # Column options
    parser.add_argument('--skills-col', type=str, default='job_skills', help='Skills column name')
    parser.add_argument('--link-col', type=str, default='job_link', help='Job link column name')
    parser.add_argument('--title-col', type=str, default=None, help='Job title column name')
    
    # Processing options
    parser.add_argument('--batch-size', type=int, default=DEFAULT_BATCH_SIZE, help='Batch size')
    parser.add_argument('--sample', type=int, default=None, help='Sample size (for testing)')
    
    args = parser.parse_args()
    
    # Determine mode
    if args.skills_csv and args.details_csv:
        # Join mode
        output = args.output or 'unified_jobs_riasec.parquet'
        join_and_process(args.skills_csv, args.details_csv, output, args.batch_size)
    elif args.input:
        # Single file mode
        output = args.output or args.input.replace('.csv', '_riasec.parquet')
        process_csv_file(
            args.input, output,
            skills_col=args.skills_col,
            link_col=args.link_col,
            title_col=args.title_col,
            batch_size=args.batch_size,
            sample_size=args.sample
        )
    else:
        parser.print_help()
        print("\nError: Please provide --input or both --skills-csv and --details-csv")
        sys.exit(1)

if __name__ == "__main__":
    main()
