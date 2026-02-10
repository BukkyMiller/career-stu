"""
Integration tests for Career STU flows
Tests the complete user journeys through the four modes
"""
import pytest
import uuid
from database.connection import init_db
from tools.learner_tools import (
    create_learner,
    get_learner_context,
    update_learner_profile,
    add_learner_skill,
    set_learner_goal
)
from tools.pathway_tools import create_pathway
from agent.system_prompt import determine_mode


@pytest.fixture(scope="module")
def setup_database():
    """Initialize database for tests"""
    init_db()


def test_flow_intake_to_goal_discovery(setup_database):
    """
    Test Flow 1: New Learner Intake
    - Create learner
    - Add profile information
    - Add skills
    - Verify transition to GOAL_DISCOVERY
    """
    # Create learner
    email = f"test_{uuid.uuid4()}@example.com"
    result = create_learner(email, "Test Learner")

    assert result["success"] is True
    learner_id = result["learner_id"]

    # Update profile
    updates = {
        "current_job_title": "Software Developer",
        "years_experience": 3,
        "weekly_study_hours": 10,
        "profile_complete": True
    }
    update_result = update_learner_profile(learner_id, updates)
    assert update_result["success"] is True

    # Add skills
    add_learner_skill(learner_id, "Python", "intermediate")
    add_learner_skill(learner_id, "SQL", "beginner")

    # Check mode
    context = get_learner_context(learner_id)
    mode = determine_mode(context)

    assert mode == "GOAL_DISCOVERY"


def test_flow_goal_discovery_to_pathway(setup_database):
    """
    Test Flow 2: Goal Discovery with RIASEC
    - Create learner with complete profile
    - Set a goal
    - Verify transition to PATHWAY
    """
    # Create learner
    email = f"test_{uuid.uuid4()}@example.com"
    result = create_learner(email, "Test Learner 2")
    learner_id = result["learner_id"]

    # Complete profile
    updates = {
        "current_job_title": "Data Analyst",
        "years_experience": 2,
        "inferred_riasec_code": "IRA",
        "profile_complete": True
    }
    update_learner_profile(learner_id, updates)

    # Add skills
    add_learner_skill(learner_id, "Python", "intermediate")
    add_learner_skill(learner_id, "SQL", "advanced")

    # Set committed goal
    goal_result = set_learner_goal(learner_id, "Data Scientist", "committed")
    assert goal_result["success"] is True

    # Check mode
    context = get_learner_context(learner_id)
    mode = determine_mode(context)

    assert mode == "PATHWAY"


def test_flow_pathway_to_learning(setup_database):
    """
    Test Flow 3: Pathway Creation
    - Create learner with committed goal
    - Create pathway
    - Verify transition to LEARNING
    """
    # Create learner
    email = f"test_{uuid.uuid4()}@example.com"
    result = create_learner(email, "Test Learner 3")
    learner_id = result["learner_id"]

    # Complete profile
    updates = {
        "current_job_title": "Junior Developer",
        "years_experience": 1,
        "weekly_study_hours": 15,
        "profile_complete": True
    }
    update_learner_profile(learner_id, updates)

    # Set committed goal
    goal_result = set_learner_goal(learner_id, "Senior Developer", "committed")
    goal_id = goal_result["goal_id"]

    # Create pathway
    skills_to_learn = ["Advanced Python", "System Design", "Cloud Architecture"]
    pathway_result = create_pathway(learner_id, goal_id, skills_to_learn)

    assert pathway_result["success"] is True
    assert pathway_result["total_skills"] == 3

    # Check mode
    context = get_learner_context(learner_id)
    mode = determine_mode(context)

    assert mode == "LEARNING"


def test_complete_learner_journey(setup_database):
    """
    Test complete journey from intake to learning
    """
    # 1. INTAKE: Create learner
    email = f"test_{uuid.uuid4()}@example.com"
    learner = create_learner(email, "Complete Journey Test")
    learner_id = learner["learner_id"]

    context = get_learner_context(learner_id)
    assert determine_mode(context) == "INTAKE"

    # 2. Complete profile for GOAL_DISCOVERY
    update_learner_profile(learner_id, {
        "current_job_title": "Beginner",
        "years_experience": 0,
        "weekly_study_hours": 20,
        "inferred_riasec_code": "IRA",
        "profile_complete": True
    })

    context = get_learner_context(learner_id)
    assert determine_mode(context) == "GOAL_DISCOVERY"

    # 3. Set goal for PATHWAY
    goal = set_learner_goal(learner_id, "Machine Learning Engineer", "committed")
    goal_id = goal["goal_id"]

    context = get_learner_context(learner_id)
    assert determine_mode(context) == "PATHWAY"

    # 4. Create pathway for LEARNING
    skills = ["Python", "Machine Learning", "Deep Learning", "MLOps"]
    pathway = create_pathway(learner_id, goal_id, skills)

    context = get_learner_context(learner_id)
    assert determine_mode(context) == "LEARNING"

    # Verify pathway details
    assert len(context["pathway_skills"]) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
