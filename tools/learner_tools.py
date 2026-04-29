"""
Learner management tools - Profile, skills, and goals
"""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd
from database.connection import get_connection


def get_learner_context(learner_id: str) -> Dict[str, Any]:
    """
    Get full learner profile, skills, goals, and pathway progress
    Optimized to reduce number of database queries
    """
    conn = get_connection()

    # Query 1: Get learner and profile in one query with LEFT JOIN
    learner_profile = conn.execute(
        """
        SELECT l.*, p.*
        FROM learners l
        LEFT JOIN learner_profiles p ON l.id = p.learner_id
        WHERE l.id = ?
        """,
        [learner_id]
    ).fetchdf()

    if len(learner_profile) == 0:
        return {"error": f"Learner not found: {learner_id}"}

    row = learner_profile.iloc[0]

    # Extract learner fields (handle pandas NA values)
    learner_fields = ['id', 'email', 'name', 'status', 'created_at', 'updated_at']
    learner = {}
    for k in learner_fields:
        if k in row:
            val = row[k]
            # Convert pandas NA/NaN to None
            learner[k] = None if pd.isna(val) else val

    # Extract profile fields (exclude learner_id to avoid confusion)
    profile_fields = [
        'current_job_title', 'current_industry', 'years_experience',
        'education_level', 'weekly_study_hours', 'preferred_study_times',
        'has_family_obligations', 'employment_status', 'preferred_format',
        'disposition', 'inferred_riasec_code', 'profile_complete',
        'behavioral_capital_signal', 'social_capital_signal', 'navigation_capital_signal'
    ]
    # Handle pandas NA values properly
    profile = {}
    for k in profile_fields:
        if k in row:
            val = row[k]
            # Convert pandas NA/NaN to None, keep other values
            if pd.isna(val):
                continue  # Skip NA values
            profile[k] = val

    # Query 2: Get skills, goals, and active pathway in parallel using UNION ALL
    # This reduces round trips but returns data that needs to be separated
    skills = conn.execute(
        "SELECT * FROM learner_skills WHERE learner_id = ? ORDER BY created_at DESC",
        [learner_id]
    ).fetchdf()

    goals = conn.execute(
        "SELECT * FROM learner_goals WHERE learner_id = ? ORDER BY created_at DESC",
        [learner_id]
    ).fetchdf()

    pathways = conn.execute(
        """
        SELECT p.*,
               (SELECT COUNT(*) FROM pathway_skills WHERE pathway_id = p.id) as total_skills_count,
               (SELECT COUNT(*) FROM pathway_skills WHERE pathway_id = p.id AND status = 'completed') as completed_skills_count
        FROM pathways p
        WHERE p.learner_id = ? AND p.status = 'active'
        ORDER BY p.created_at DESC
        LIMIT 1
        """,
        [learner_id]
    ).fetchdf()

    # Get pathway skills if pathway exists
    pathway_skills = []
    if len(pathways) > 0:
        pathway_id = pathways.iloc[0]['id']
        pathway_skills = conn.execute(
            "SELECT * FROM pathway_skills WHERE pathway_id = ? ORDER BY sequence_order",
            [pathway_id]
        ).fetchdf().to_dict('records')

    # Convert DataFrames to dicts, handling NA values
    def safe_to_dict(df):
        """Convert DataFrame to dict, replacing NA with None"""
        if len(df) == 0:
            return []
        records = df.to_dict('records')
        # Replace pandas NA with None in each record
        for record in records:
            for key, val in record.items():
                if pd.isna(val):
                    record[key] = None
        return records

    # Handle pathway dict separately
    active_pathway = None
    if len(pathways) > 0:
        active_pathway = pathways.iloc[0].to_dict()
        for key, val in active_pathway.items():
            if pd.isna(val):
                active_pathway[key] = None

    return {
        "learner": learner,
        "profile": profile,
        "skills": safe_to_dict(skills),
        "goals": safe_to_dict(goals),
        "active_pathway": active_pathway,
        "pathway_skills": pathway_skills
    }


def update_learner_profile(learner_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update learner profile information
    """
    conn = get_connection()

    # Check if profile exists
    existing = conn.execute(
        "SELECT learner_id FROM learner_profiles WHERE learner_id = ?", [learner_id]
    ).fetchdf()

    # Build UPDATE query
    allowed_fields = [
        'current_job_title', 'current_industry', 'years_experience',
        'education_level', 'weekly_study_hours', 'preferred_study_times',
        'has_family_obligations', 'employment_status', 'preferred_format',
        'disposition', 'inferred_riasec_code', 'profile_complete',
        'behavioral_capital_signal', 'social_capital_signal', 'navigation_capital_signal'
    ]

    update_fields = {k: v for k, v in updates.items() if k in allowed_fields}

    if not update_fields:
        return {"error": "No valid fields to update"}

    if len(existing) == 0:
        # Insert new profile
        update_fields['learner_id'] = learner_id
        update_fields['updated_at'] = datetime.now()

        fields = list(update_fields.keys())
        placeholders = ['?' for _ in fields]

        query = f"""
            INSERT INTO learner_profiles ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
        """
        conn.execute(query, list(update_fields.values()))
    else:
        # Update existing profile
        set_clause = ', '.join([f"{k} = ?" for k in update_fields.keys()])
        query = f"""
            UPDATE learner_profiles
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE learner_id = ?
        """
        conn.execute(query, list(update_fields.values()) + [learner_id])

    conn.commit()

    return {"success": True, "learner_id": learner_id, "updated_fields": list(update_fields.keys())}


def add_learner_skill(
    learner_id: str,
    skill_name: str,
    proficiency_level: str,
    evidence_source: str = "self_reported"
) -> Dict[str, Any]:
    """
    Add a skill to learner's profile
    """
    conn = get_connection()

    skill_id = str(uuid.uuid4())

    try:
        conn.execute(
            """
            INSERT INTO learner_skills (id, learner_id, skill_name, proficiency_level, evidence_source, created_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            [skill_id, learner_id, skill_name, proficiency_level, evidence_source]
        )
        conn.commit()

        return {
            "success": True,
            "skill_id": skill_id,
            "skill_name": skill_name,
            "proficiency_level": proficiency_level
        }
    except Exception as e:
        # Likely duplicate skill
        return {"error": f"Could not add skill: {str(e)}"}


def set_learner_goal(
    learner_id: str,
    target_job_title: str,
    status: str = "exploring"
) -> Dict[str, Any]:
    """
    Set or update learner's career goal
    """
    conn = get_connection()

    goal_id = str(uuid.uuid4())

    conn.execute(
        """
        INSERT INTO learner_goals (id, learner_id, target_job_title, status, created_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        [goal_id, learner_id, target_job_title, status]
    )
    conn.commit()

    return {
        "success": True,
        "goal_id": goal_id,
        "target_job_title": target_job_title,
        "status": status
    }


def create_learner(email: str, name: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new learner
    """
    conn = get_connection()

    learner_id = str(uuid.uuid4())

    try:
        conn.execute(
            """
            INSERT INTO learners (id, email, name, status, created_at, updated_at)
            VALUES (?, ?, ?, 'new', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            [learner_id, email, name]
        )
        conn.commit()

        return {
            "success": True,
            "learner_id": learner_id,
            "email": email,
            "name": name
        }
    except Exception as e:
        return {"error": f"Could not create learner: {str(e)}"}
