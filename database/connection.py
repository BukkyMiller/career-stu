"""
Database connection management for Career STU
"""
import os
import duckdb
from pathlib import Path
from dotenv import load_dotenv
import threading

load_dotenv()

# Database paths
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "./data/career_stu.duckdb")
JOBS_PARQUET_PATH = os.getenv("JOBS_PARQUET_PATH", "./data/unified_jobs.parquet")
SALARY_PARQUET_PATH = os.getenv("SALARY_PARQUET_PATH", "./data/salary_reference.parquet")
RIASEC_JSON_PATH = os.getenv("RIASEC_JSON_PATH", "./data/riasec_framework.json")

# Thread-local storage for connection pooling
_thread_local = threading.local()


def get_connection():
    """
    Get a DuckDB connection with thread-local pooling
    Creates the database file if it doesn't exist
    Reuses connection within the same thread for better performance
    """
    # Check if we already have a connection for this thread
    if not hasattr(_thread_local, 'connection') or _thread_local.connection is None:
        db_path = Path(DUCKDB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        _thread_local.connection = duckdb.connect(str(db_path))

    return _thread_local.connection


def init_db():
    """
    Initialize the database with schema
    Run this once to create all tables
    """
    conn = get_connection()

    # Read schema file
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    # Execute schema (DuckDB can handle multiple statements in one execute)
    conn.execute(schema_sql)

    print(f"Database initialized at {DUCKDB_PATH}")
    return conn


def verify_data_files():
    """
    Verify that all required data files exist
    """
    files = {
        "Jobs": JOBS_PARQUET_PATH,
        "Salary": SALARY_PARQUET_PATH,
        "RIASEC": RIASEC_JSON_PATH
    }

    missing = []
    for name, path in files.items():
        if not Path(path).exists():
            missing.append(f"{name}: {path}")

    if missing:
        raise FileNotFoundError(
            f"Missing required data files:\n" + "\n".join(missing)
        )

    return True


if __name__ == "__main__":
    # Initialize database when run directly
    print("Verifying data files...")
    verify_data_files()
    print("All data files found!")

    print("\nInitializing database...")
    init_db()
    print("Database ready!")
