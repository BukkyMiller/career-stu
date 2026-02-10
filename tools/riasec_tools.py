"""
RIASEC tools - Classification and matching logic
Imports from scripts/riasec_classifier.py
"""
import json
from typing import List, Dict, Any
from scripts.riasec_classifier import classify_job, FRAMEWORK, RIASEC_TYPES, COMBINATIONS


def infer_riasec_from_skills(skills: List[str]) -> Dict[str, Any]:
    """
    Given a list of skills, predict the most likely RIASEC code
    Uses the riasec_classifier from scripts/
    """
    # Join skills into a comma-separated string
    skills_text = ", ".join(skills)

    # Classify using the existing classifier
    result = classify_job(skills_text)

    return {
        "riasec_code": result["riasec_code"],
        "primary_type": result["primary_type"],
        "confidence": result["confidence"],
        "description": result["description"],
        "scores": result["scores"],
        "matched_indicators": result["matched_indicators"]
    }


def get_riasec_description(riasec_code: str) -> Dict[str, Any]:
    """
    Get description and career themes for a RIASEC code
    """
    code = riasec_code.upper()

    # Get combination description
    combo_info = COMBINATIONS.get(code, {})

    if isinstance(combo_info, dict):
        description = combo_info.get('description', 'No description available')
        gift = combo_info.get('gift', '')
        themes = combo_info.get('career_themes', [])
    else:
        description = combo_info if combo_info else 'No description available'
        gift = ''
        themes = []

    # Get individual type names
    types_breakdown = []
    for letter in code:
        if letter in RIASEC_TYPES:
            type_info = RIASEC_TYPES[letter]
            types_breakdown.append({
                "letter": letter,
                "name": type_info.get("name", ""),
                "title": type_info.get("title", "")
            })

    return {
        "riasec_code": code,
        "description": description,
        "gift": gift,
        "career_themes": themes,
        "types_breakdown": types_breakdown
    }


def compare_riasec_codes(learner_riasec: str, job_riasec: str) -> Dict[str, Any]:
    """
    Compare learner's RIASEC code to a target job's RIASEC code to assess fit
    """
    learner = learner_riasec.upper()
    job = job_riasec.upper()

    # Calculate match score
    # Primary type match (position 1) is most important
    primary_match = learner[0] == job[0]

    # Secondary match (position 2)
    secondary_match = len(learner) > 1 and len(job) > 1 and learner[1] == job[1]

    # Tertiary match (position 3)
    tertiary_match = len(learner) > 2 and len(job) > 2 and learner[2] == job[2]

    # Any letter appears in the other code
    learner_letters = set(learner)
    job_letters = set(job)
    overlap_count = len(learner_letters & job_letters)

    # Calculate overall fit score (0-100)
    fit_score = 0
    if primary_match:
        fit_score += 50
    if secondary_match:
        fit_score += 30
    if tertiary_match:
        fit_score += 20
    elif overlap_count > 1:
        # Partial credit for shared letters
        fit_score += (overlap_count - 1) * 10

    # Determine fit level
    if fit_score >= 80:
        fit_level = "Excellent"
        recommendation = "Strong match - your interests align very well with this role"
    elif fit_score >= 50:
        fit_level = "Good"
        recommendation = "Good match - your primary interests align with this role"
    elif fit_score >= 30:
        fit_level = "Moderate"
        recommendation = "Moderate match - some shared interests but significant differences"
    else:
        fit_level = "Low"
        recommendation = "Limited match - this role may be quite different from your natural preferences"

    return {
        "learner_riasec": learner,
        "job_riasec": job,
        "fit_score": fit_score,
        "fit_level": fit_level,
        "recommendation": recommendation,
        "primary_match": primary_match,
        "secondary_match": secondary_match,
        "tertiary_match": tertiary_match,
        "shared_types": list(learner_letters & job_letters)
    }
