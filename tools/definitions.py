"""
Tool definitions for Career STU agent
Anthropic-compatible tool schemas
"""

# Job Search Tools
SEARCH_JOBS = {
    "name": "search_jobs",
    "description": "Search jobs by title, skills, location, or level in the unified_jobs database",
    "input_schema": {
        "type": "object",
        "properties": {
            "job_title": {
                "type": "string",
                "description": "Job title to search for (partial match supported)"
            },
            "skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of skills to match"
            },
            "location": {
                "type": "string",
                "description": "Job location (city, state, or remote)"
            },
            "job_level": {
                "type": "string",
                "description": "Job level (e.g., Entry, Mid-Senior, Director, Associate)"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 10
            }
        }
    }
}

SEARCH_JOBS_BY_RIASEC = {
    "name": "search_jobs_by_riasec",
    "description": "Find jobs matching a RIASEC code (e.g., 'SRI', 'IRA')",
    "input_schema": {
        "type": "object",
        "properties": {
            "riasec_code": {
                "type": "string",
                "description": "RIASEC code to match (e.g., 'SRI', 'IRA')"
            },
            "primary_type_only": {
                "type": "boolean",
                "description": "Only match primary RIASEC type (first letter)",
                "default": False
            },
            "job_level": {
                "type": "string",
                "description": "Filter by job level"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results",
                "default": 10
            }
        },
        "required": ["riasec_code"]
    }
}

GET_JOB_DETAILS = {
    "name": "get_job_details",
    "description": "Get full details for a specific job using its job_link",
    "input_schema": {
        "type": "object",
        "properties": {
            "job_link": {
                "type": "string",
                "description": "The job_link identifier from search results"
            }
        },
        "required": ["job_link"]
    }
}

# RIASEC Tools
INFER_RIASEC_FROM_SKILLS = {
    "name": "infer_riasec_from_skills",
    "description": "Given a list of skills, predict the most likely RIASEC code",
    "input_schema": {
        "type": "object",
        "properties": {
            "skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of skills to analyze"
            }
        },
        "required": ["skills"]
    }
}

GET_RIASEC_DESCRIPTION = {
    "name": "get_riasec_description",
    "description": "Get description and career themes for a RIASEC code",
    "input_schema": {
        "type": "object",
        "properties": {
            "riasec_code": {
                "type": "string",
                "description": "RIASEC code (e.g., 'SRI')"
            }
        },
        "required": ["riasec_code"]
    }
}

COMPARE_RIASEC_CODES = {
    "name": "compare_riasec_codes",
    "description": "Compare learner's RIASEC code to a target job's RIASEC code to assess fit",
    "input_schema": {
        "type": "object",
        "properties": {
            "learner_riasec": {
                "type": "string",
                "description": "Learner's RIASEC code"
            },
            "job_riasec": {
                "type": "string",
                "description": "Job's RIASEC code"
            }
        },
        "required": ["learner_riasec", "job_riasec"]
    }
}

# Salary & Market Tools
GET_SALARY_INFO = {
    "name": "get_salary_info",
    "description": "Look up salary and market demand for a job title",
    "input_schema": {
        "type": "object",
        "properties": {
            "job_title": {
                "type": "string",
                "description": "Job title to look up"
            }
        },
        "required": ["job_title"]
    }
}

GET_HIGH_DEMAND_JOBS = {
    "name": "get_high_demand_jobs",
    "description": "Find jobs with labor shortages (good career prospects)",
    "input_schema": {
        "type": "object",
        "properties": {
            "riasec_type": {
                "type": "string",
                "description": "Filter by RIASEC primary type (S, I, R, A, E, C)"
            },
            "min_salary": {
                "type": "integer",
                "description": "Minimum salary threshold"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results",
                "default": 10
            }
        }
    }
}

# Skills Gap Tools
CALCULATE_SKILL_GAP = {
    "name": "calculate_skill_gap",
    "description": "Compare learner's skills to a target job's requirements",
    "input_schema": {
        "type": "object",
        "properties": {
            "learner_skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of skills the learner has"
            },
            "target_job_link": {
                "type": "string",
                "description": "job_link of the target job"
            }
        },
        "required": ["learner_skills", "target_job_link"]
    }
}

FIND_JOBS_BY_SKILL_MATCH = {
    "name": "find_jobs_by_skill_match",
    "description": "Find jobs where learner has the highest skill match percentage",
    "input_schema": {
        "type": "object",
        "properties": {
            "learner_skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of skills the learner has"
            },
            "min_match_percent": {
                "type": "number",
                "description": "Minimum match percentage (0-100)",
                "default": 50
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results",
                "default": 10
            }
        },
        "required": ["learner_skills"]
    }
}

# Learner Management Tools
GET_LEARNER_CONTEXT = {
    "name": "get_learner_context",
    "description": "Get full learner profile, skills, goals, and pathway progress",
    "input_schema": {
        "type": "object",
        "properties": {
            "learner_id": {
                "type": "string",
                "description": "Learner's unique ID"
            }
        },
        "required": ["learner_id"]
    }
}

UPDATE_LEARNER_PROFILE = {
    "name": "update_learner_profile",
    "description": "Update learner profile information",
    "input_schema": {
        "type": "object",
        "properties": {
            "learner_id": {
                "type": "string",
                "description": "Learner's unique ID"
            },
            "updates": {
                "type": "object",
                "description": "Fields to update (e.g., current_job_title, years_experience)"
            }
        },
        "required": ["learner_id", "updates"]
    }
}

ADD_LEARNER_SKILL = {
    "name": "add_learner_skill",
    "description": "Add a skill to learner's profile",
    "input_schema": {
        "type": "object",
        "properties": {
            "learner_id": {
                "type": "string",
                "description": "Learner's unique ID"
            },
            "skill_name": {
                "type": "string",
                "description": "Name of the skill"
            },
            "proficiency_level": {
                "type": "string",
                "description": "Proficiency: none, beginner, intermediate, advanced, expert"
            },
            "evidence_source": {
                "type": "string",
                "description": "Source: self_reported, validated, credential",
                "default": "self_reported"
            }
        },
        "required": ["learner_id", "skill_name", "proficiency_level"]
    }
}

SET_LEARNER_GOAL = {
    "name": "set_learner_goal",
    "description": "Set or update learner's career goal",
    "input_schema": {
        "type": "object",
        "properties": {
            "learner_id": {
                "type": "string",
                "description": "Learner's unique ID"
            },
            "target_job_title": {
                "type": "string",
                "description": "Target job title"
            },
            "status": {
                "type": "string",
                "description": "Goal status: exploring, committed, achieved, changed",
                "default": "exploring"
            }
        },
        "required": ["learner_id", "target_job_title"]
    }
}

CREATE_PATHWAY = {
    "name": "create_pathway",
    "description": "Create a learning pathway for the learner",
    "input_schema": {
        "type": "object",
        "properties": {
            "learner_id": {
                "type": "string",
                "description": "Learner's unique ID"
            },
            "goal_id": {
                "type": "string",
                "description": "Goal ID to create pathway for"
            },
            "skills_to_learn": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Ordered list of skills to learn"
            }
        },
        "required": ["learner_id", "goal_id", "skills_to_learn"]
    }
}

# All tools list
ALL_TOOLS = [
    # Job search
    SEARCH_JOBS,
    SEARCH_JOBS_BY_RIASEC,
    GET_JOB_DETAILS,
    # RIASEC
    INFER_RIASEC_FROM_SKILLS,
    GET_RIASEC_DESCRIPTION,
    COMPARE_RIASEC_CODES,
    # Salary
    GET_SALARY_INFO,
    GET_HIGH_DEMAND_JOBS,
    # Skills
    CALCULATE_SKILL_GAP,
    FIND_JOBS_BY_SKILL_MATCH,
    # Learner
    GET_LEARNER_CONTEXT,
    UPDATE_LEARNER_PROFILE,
    ADD_LEARNER_SKILL,
    SET_LEARNER_GOAL,
    CREATE_PATHWAY
]
