"""
Learner management routes for Career STU API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from tools.learner_tools import (
    create_learner,
    get_learner_context,
    update_learner_profile,
    add_learner_skill,
    set_learner_goal
)

router = APIRouter()


class CreateLearnerRequest(BaseModel):
    email: str
    name: Optional[str] = None


class UpdateProfileRequest(BaseModel):
    learner_id: str
    current_job_title: Optional[str] = None
    current_industry: Optional[str] = None
    years_experience: Optional[int] = None
    education_level: Optional[str] = None
    weekly_study_hours: Optional[int] = None
    preferred_study_times: Optional[str] = None
    has_family_obligations: Optional[bool] = None
    employment_status: Optional[str] = None
    preferred_format: Optional[str] = None
    disposition: Optional[str] = None
    inferred_riasec_code: Optional[str] = None
    profile_complete: Optional[bool] = None


class AddSkillRequest(BaseModel):
    learner_id: str
    skill_name: str
    proficiency_level: str
    evidence_source: Optional[str] = "self_reported"


class SetGoalRequest(BaseModel):
    learner_id: str
    target_job_title: str
    status: Optional[str] = "exploring"


@router.post("/create")
def create_new_learner(request: CreateLearnerRequest):
    """
    Create a new learner

    Args:
        email: Learner's email
        name: Learner's name (optional)

    Returns:
        Learner ID and details
    """
    try:
        result = create_learner(request.email, request.name)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context/{learner_id}")
def get_context(learner_id: str):
    """
    Get full learner context including profile, skills, goals, and pathway

    Args:
        learner_id: Learner's unique ID

    Returns:
        Complete learner context
    """
    try:
        context = get_learner_context(learner_id)

        if "error" in context:
            raise HTTPException(status_code=404, detail=context["error"])

        return context

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profile/update")
def update_profile(request: UpdateProfileRequest):
    """
    Update learner profile

    Args:
        Updates to learner profile

    Returns:
        Success message
    """
    try:
        # Convert request to dict and filter None values
        updates = {k: v for k, v in request.dict().items() if v is not None and k != "learner_id"}

        result = update_learner_profile(request.learner_id, updates)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/skill/add")
def add_skill(request: AddSkillRequest):
    """
    Add a skill to learner's profile

    Args:
        learner_id: Learner's unique ID
        skill_name: Name of the skill
        proficiency_level: Proficiency level
        evidence_source: Source of evidence

    Returns:
        Success message
    """
    try:
        result = add_learner_skill(
            request.learner_id,
            request.skill_name,
            request.proficiency_level,
            request.evidence_source
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/goal/set")
def set_goal(request: SetGoalRequest):
    """
    Set learner's career goal

    Args:
        learner_id: Learner's unique ID
        target_job_title: Target job title
        status: Goal status

    Returns:
        Success message with goal ID
    """
    try:
        result = set_learner_goal(
            request.learner_id,
            request.target_job_title,
            request.status
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
