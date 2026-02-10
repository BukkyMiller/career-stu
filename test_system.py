#!/usr/bin/env python3
"""
Quick system test for Career STU
Tests all components without requiring API key
"""
import sys

def test_imports():
    """Test that all modules can be imported"""
    print("\n🔧 Testing imports...")
    try:
        from tools.job_search_tools import search_jobs, search_jobs_by_riasec
        from tools.riasec_tools import infer_riasec_from_skills
        from tools.salary_tools import get_salary_info
        from tools.learner_tools import create_learner, get_learner_context
        from tools.pathway_tools import create_pathway
        from agent.system_prompt import determine_mode, build_system_prompt
        from database.connection import get_connection
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_database():
    """Test database operations"""
    print("\n🗄️  Testing database...")
    try:
        from tools.learner_tools import create_learner, get_learner_context
        from agent.system_prompt import determine_mode

        # Create test learner
        result = create_learner('test_system@example.com', 'System Test')
        learner_id = result['learner_id']
        print(f"✓ Created test learner: {learner_id[:8]}...")

        # Get context
        context = get_learner_context(learner_id)
        print(f"✓ Retrieved learner context")

        # Check mode
        mode = determine_mode(context)
        print(f"✓ Current mode: {mode}")

        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_riasec():
    """Test RIASEC classification"""
    print("\n🎯 Testing RIASEC tools...")
    try:
        from tools.riasec_tools import infer_riasec_from_skills, compare_riasec_codes

        # Test inference
        result = infer_riasec_from_skills(['Python', 'SQL', 'Machine Learning'])
        print(f"✓ Inferred RIASEC: {result['riasec_code']} ({result['primary_type']})")

        # Test comparison
        comparison = compare_riasec_codes('IRA', 'IRC')
        print(f"✓ RIASEC comparison: {comparison['fit_level']} fit")

        return True
    except Exception as e:
        print(f"✗ RIASEC test failed: {e}")
        return False

def test_job_search():
    """Test job search functionality"""
    print("\n💼 Testing job search...")
    try:
        from tools.job_search_tools import search_jobs_by_riasec, search_jobs

        # Search by RIASEC
        jobs = search_jobs_by_riasec('IRA', limit=3)
        print(f"✓ Found {len(jobs)} IRA jobs")
        if jobs:
            print(f"  Example: {jobs[0]['job_title']}")

        # Search by title
        data_jobs = search_jobs(job_title='Data Scientist', limit=3)
        print(f"✓ Found {len(data_jobs)} Data Scientist jobs")

        return True
    except Exception as e:
        print(f"✗ Job search test failed: {e}")
        return False

def test_salary_data():
    """Test salary lookup"""
    print("\n💰 Testing salary data...")
    try:
        from tools.salary_tools import get_salary_info

        result = get_salary_info('Software Engineer')
        if result.get('found'):
            print(f"✓ Found salary data for Software Engineer")
            print(f"  {len(result['results'])} entries found")
        else:
            print(f"⚠ No salary data found (this is OK)")

        return True
    except Exception as e:
        print(f"✗ Salary test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("Career STU System Test")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Database", test_database),
        ("RIASEC Tools", test_riasec),
        ("Job Search", test_job_search),
        ("Salary Data", test_salary_data)
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ All systems operational!")
        print("\nReady to launch:")
        print("  streamlit run ui/streamlit_app.py")
        print("\nOr API:")
        print("  uvicorn api.main:app --reload")
        print("\nNote: You'll need to add your ANTHROPIC_API_KEY to .env for chat to work")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
