"""
Pathway management tools - Create and track learning pathways
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any
from database.connection import get_connection


def create_pathway(
    learner_id: str,
    goal_id: str,
    skills_to_learn: List[str]
) -> Dict[str, Any]:
    """
    Create a learning pathway for the learner
    """
    conn = get_connection()

    # Verify goal exists and belongs to learner
    goal = conn.execute(
        "SELECT * FROM learner_goals WHERE id = ? AND learner_id = ?",
        [goal_id, learner_id]
    ).fetchdf()

    if len(goal) == 0:
        return {"error": f"Goal not found or does not belong to learner"}

    # Create pathway
    pathway_id = str(uuid.uuid4())
    total_skills = len(skills_to_learn)

    # Estimate hours (rough estimate: 20 hours per skill)
    estimated_hours = total_skills * 20

    conn.execute(
        """
        INSERT INTO pathways (id, learner_id, goal_id, status, total_skills, completed_skills, estimated_hours, created_at)
        VALUES (?, ?, ?, 'active', ?, 0, ?, CURRENT_TIMESTAMP)
        """,
        [pathway_id, learner_id, goal_id, total_skills, estimated_hours]
    )

    # Add pathway skills
    for idx, skill_name in enumerate(skills_to_learn, start=1):
        skill_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO pathway_skills (id, pathway_id, skill_name, sequence_order, status, estimated_hours)
            VALUES (?, ?, ?, ?, 'not_started', 20)
            """,
            [skill_id, pathway_id, skill_name, idx]
        )

    conn.commit()

    return {
        "success": True,
        "pathway_id": pathway_id,
        "goal_id": goal_id,
        "total_skills": total_skills,
        "estimated_hours": estimated_hours,
        "skills": skills_to_learn
    }


def update_pathway_progress(
    pathway_id: str,
    skill_name: str,
    new_status: str
) -> Dict[str, Any]:
    """
    Update the status of a skill in a pathway
    Statuses: not_started, in_progress, completed
    """
    conn = get_connection()

    # Update skill status
    if new_status == "in_progress":
        conn.execute(
            """
            UPDATE pathway_skills
            SET status = ?, started_at = CURRENT_TIMESTAMP
            WHERE pathway_id = ? AND skill_name = ?
            """,
            [new_status, pathway_id, skill_name]
        )
    elif new_status == "completed":
        conn.execute(
            """
            UPDATE pathway_skills
            SET status = ?, completed_at = CURRENT_TIMESTAMP
            WHERE pathway_id = ? AND skill_name = ?
            """,
            [new_status, pathway_id, skill_name]
        )
    else:
        conn.execute(
            """
            UPDATE pathway_skills
            SET status = ?
            WHERE pathway_id = ? AND skill_name = ?
            """,
            [new_status, pathway_id, skill_name]
        )

    # Update pathway completed count
    completed_count = conn.execute(
        "SELECT COUNT(*) as count FROM pathway_skills WHERE pathway_id = ? AND status = 'completed'",
        [pathway_id]
    ).fetchdf().iloc[0]['count']

    conn.execute(
        "UPDATE pathways SET completed_skills = ? WHERE id = ?",
        [completed_count, pathway_id]
    )

    conn.commit()

    return {
        "success": True,
        "pathway_id": pathway_id,
        "skill_name": skill_name,
        "new_status": new_status,
        "completed_count": completed_count
    }


def get_pathway_details(pathway_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a pathway
    """
    conn = get_connection()

    # Get pathway
    pathway = conn.execute(
        "SELECT * FROM pathways WHERE id = ?",
        [pathway_id]
    ).fetchdf()

    if len(pathway) == 0:
        return {"error": f"Pathway not found: {pathway_id}"}

    # Get pathway skills
    skills = conn.execute(
        "SELECT * FROM pathway_skills WHERE pathway_id = ? ORDER BY sequence_order",
        [pathway_id]
    ).fetchdf()

    # Get goal details
    goal_id = pathway.iloc[0]['goal_id']
    goal = conn.execute(
        "SELECT * FROM learner_goals WHERE id = ?",
        [goal_id]
    ).fetchdf()

    return {
        "pathway": pathway.iloc[0].to_dict(),
        "skills": skills.to_dict('records'),
        "goal": goal.iloc[0].to_dict() if len(goal) > 0 else None
    }


def get_current_skill(pathway_id: str) -> Dict[str, Any]:
    """
    Get the current skill the learner should be working on
    """
    conn = get_connection()

    # First, check for in_progress skills
    in_progress = conn.execute(
        """
        SELECT * FROM pathway_skills
        WHERE pathway_id = ? AND status = 'in_progress'
        ORDER BY sequence_order
        LIMIT 1
        """,
        [pathway_id]
    ).fetchdf()

    if len(in_progress) > 0:
        return {
            "current_skill": in_progress.iloc[0].to_dict(),
            "status": "in_progress"
        }

    # If none in progress, get next not_started skill
    not_started = conn.execute(
        """
        SELECT * FROM pathway_skills
        WHERE pathway_id = ? AND status = 'not_started'
        ORDER BY sequence_order
        LIMIT 1
        """,
        [pathway_id]
    ).fetchdf()

    if len(not_started) > 0:
        return {
            "current_skill": not_started.iloc[0].to_dict(),
            "status": "next_to_start"
        }

    # All skills completed
    return {
        "current_skill": None,
        "status": "all_completed"
    }
