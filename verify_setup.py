#!/usr/bin/env python3
"""
Verify Career STU setup
Checks that all components are properly configured
"""
import os
import sys
from pathlib import Path


def check_file(path: str, description: str) -> bool:
    """Check if a file exists"""
    if Path(path).exists():
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - MISSING: {path}")
        return False


def check_directory(path: str, description: str) -> bool:
    """Check if a directory exists"""
    if Path(path).is_dir():
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - MISSING: {path}")
        return False


def main():
    print("=" * 60)
    print("Career STU Setup Verification")
    print("=" * 60)

    checks = []

    print("\n📁 Directory Structure:")
    checks.append(check_directory("agent", "agent/ directory"))
    checks.append(check_directory("api", "api/ directory"))
    checks.append(check_directory("database", "database/ directory"))
    checks.append(check_directory("tools", "tools/ directory"))
    checks.append(check_directory("ui", "ui/ directory"))
    checks.append(check_directory("tests", "tests/ directory"))
    checks.append(check_directory("data", "data/ directory"))
    checks.append(check_directory("scripts", "scripts/ directory"))

    print("\n📄 Core Files:")
    checks.append(check_file("requirements.txt", "requirements.txt"))
    checks.append(check_file(".env.example", ".env.example"))
    checks.append(check_file("CLAUDE.md", "CLAUDE.md"))
    checks.append(check_file("SETUP.md", "SETUP.md"))

    print("\n🗄️  Database Files:")
    checks.append(check_file("database/schema.sql", "database/schema.sql"))
    checks.append(check_file("database/connection.py", "database/connection.py"))

    print("\n🔧 Tool Files:")
    checks.append(check_file("tools/definitions.py", "tools/definitions.py"))
    checks.append(check_file("tools/job_search_tools.py", "tools/job_search_tools.py"))
    checks.append(check_file("tools/riasec_tools.py", "tools/riasec_tools.py"))
    checks.append(check_file("tools/salary_tools.py", "tools/salary_tools.py"))
    checks.append(check_file("tools/skills_tools.py", "tools/skills_tools.py"))
    checks.append(check_file("tools/learner_tools.py", "tools/learner_tools.py"))
    checks.append(check_file("tools/pathway_tools.py", "tools/pathway_tools.py"))

    print("\n🤖 Agent Files:")
    checks.append(check_file("agent/system_prompt.py", "agent/system_prompt.py"))
    checks.append(check_file("agent/context_builder.py", "agent/context_builder.py"))
    checks.append(check_file("agent/career_stu.py", "agent/career_stu.py"))

    print("\n🌐 API Files:")
    checks.append(check_file("api/main.py", "api/main.py"))
    checks.append(check_file("api/routes/chat.py", "api/routes/chat.py"))
    checks.append(check_file("api/routes/learner.py", "api/routes/learner.py"))

    print("\n🖥️  UI Files:")
    checks.append(check_file("ui/streamlit_app.py", "ui/streamlit_app.py"))

    print("\n🧪 Test Files:")
    checks.append(check_file("tests/test_tools.py", "tests/test_tools.py"))
    checks.append(check_file("tests/test_agent.py", "tests/test_agent.py"))
    checks.append(check_file("tests/test_flows.py", "tests/test_flows.py"))

    print("\n📊 Data Files:")
    checks.append(check_file("data/unified_jobs.parquet", "unified_jobs.parquet"))
    checks.append(check_file("data/salary_reference.parquet", "salary_reference.parquet"))
    checks.append(check_file("data/riasec_framework.json", "riasec_framework.json"))

    print("\n🔨 Script Files:")
    checks.append(check_file("scripts/riasec_classifier.py", "riasec_classifier.py"))

    # Summary
    print("\n" + "=" * 60)
    passed = sum(checks)
    total = len(checks)

    if passed == total:
        print(f"✓ All checks passed! ({passed}/{total})")
        print("\n✅ Career STU is ready to use!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and add your ANTHROPIC_API_KEY")
        print("2. Run: python -c \"from database.connection import init_db; init_db()\"")
        print("3. Run: streamlit run ui/streamlit_app.py")
        return 0
    else:
        print(f"✗ Some checks failed ({passed}/{total} passed)")
        print("\n⚠️  Please resolve missing files before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
