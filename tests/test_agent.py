"""
Tests for Career STU agent
"""
import pytest
import os
from agent.system_prompt import determine_mode, build_system_prompt
from agent.context_builder import ContextBuilder


def test_determine_mode_intake():
    """Test mode determination for new learner"""
    learner_context = {
        "learner": {"id": "test-123", "status": "new"},
        "profile": {"profile_complete": False},
        "skills": [],
        "goals": [],
        "active_pathway": None
    }

    mode = determine_mode(learner_context)
    assert mode == "INTAKE"


def test_determine_mode_goal_discovery():
    """Test mode determination for learner with complete profile"""
    learner_context = {
        "learner": {"id": "test-123", "status": "active"},
        "profile": {"profile_complete": True},
        "skills": [{"skill_name": "Python"}],
        "goals": [],
        "active_pathway": None
    }

    mode = determine_mode(learner_context)
    assert mode == "GOAL_DISCOVERY"


def test_determine_mode_pathway():
    """Test mode determination for learner with committed goal"""
    learner_context = {
        "learner": {"id": "test-123", "status": "active"},
        "profile": {"profile_complete": True},
        "skills": [{"skill_name": "Python"}],
        "goals": [{"target_job_title": "Data Scientist", "status": "committed"}],
        "active_pathway": None
    }

    mode = determine_mode(learner_context)
    assert mode == "PATHWAY"


def test_determine_mode_learning():
    """Test mode determination for learner with active pathway"""
    learner_context = {
        "learner": {"id": "test-123", "status": "active"},
        "profile": {"profile_complete": True},
        "skills": [{"skill_name": "Python"}],
        "goals": [{"target_job_title": "Data Scientist", "status": "committed"}],
        "active_pathway": {"id": "path-123", "status": "active"}
    }

    mode = determine_mode(learner_context)
    assert mode == "LEARNING"


def test_build_system_prompt():
    """Test system prompt building"""
    learner_context = {
        "learner": {"id": "test-123", "status": "new"},
        "profile": {},
        "skills": [],
        "goals": [],
        "active_pathway": None
    }

    prompt = build_system_prompt("INTAKE", learner_context)
    assert "INTAKE" in prompt
    assert "Career STU" in prompt


def test_context_builder():
    """Test context builder"""
    builder = ContextBuilder("test-learner-123")

    builder.add_message("user", "Hello")
    builder.add_message("assistant", "Hi there!")

    messages = builder.get_messages()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
