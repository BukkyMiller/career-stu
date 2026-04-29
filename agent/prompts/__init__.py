"""
Multi-agent prompt system for Career STU.

Provides prompt loading utilities for the four specialized agents:
  - Agent 1: Orchestrator & Intake (orchestrator_intake.md)
  - Agent 2: Career Explorer & Goal Setting (career_explorer_goal_setting.md)
  - Agent 3: Career Path (career_path.md)
  - Agent 4: Course Creation & Learning (course_creation_learning.md)

Usage:
    from agent.prompts import load_agent_prompt, get_all_agent_prompts

    # Load a single agent prompt
    orchestrator_prompt = load_agent_prompt("orchestrator_intake")

    # Load all agent prompts as a dict
    all_prompts = get_all_agent_prompts()
"""

import os
from pathlib import Path
from typing import Dict, Optional

# Directory containing the prompt markdown files
PROMPTS_DIR = Path(__file__).parent

# Agent prompt file mapping
AGENT_PROMPT_FILES = {
    "orchestrator_intake": "orchestrator_intake.md",
    "career_explorer_goal_setting": "career_explorer_goal_setting.md",
    "career_path": "career_path.md",
    "course_creation_learning": "course_creation_learning.md",
}

# Maps the new multi-agent modes to the correct prompt file
MODE_TO_AGENT = {
    # Orchestrator handles intake directly
    "INTAKE": "orchestrator_intake",
    # Agent 2 handles both exploratory and goal setting
    "CAREER_EXPLORATORY": "career_explorer_goal_setting",
    "CAREER_GOAL_SETTING": "career_explorer_goal_setting",
    # Legacy mode name maps to Agent 2
    "GOAL_DISCOVERY": "career_explorer_goal_setting",
    # Agent 3
    "PATHWAY": "career_path",
    # Agent 4
    "LEARNING": "course_creation_learning",
}


def load_agent_prompt(agent_name: str) -> str:
    """
    Load a single agent's system prompt from its markdown file.

    Args:
        agent_name: One of the keys in AGENT_PROMPT_FILES:
            - "orchestrator_intake"
            - "career_explorer_goal_setting"
            - "career_path"
            - "course_creation_learning"

    Returns:
        The full text content of the agent's prompt file.

    Raises:
        FileNotFoundError: If the prompt file doesn't exist.
        ValueError: If the agent_name is not recognized.
    """
    if agent_name not in AGENT_PROMPT_FILES:
        raise ValueError(
            f"Unknown agent: '{agent_name}'. "
            f"Valid agents: {list(AGENT_PROMPT_FILES.keys())}"
        )

    filepath = PROMPTS_DIR / AGENT_PROMPT_FILES[agent_name]

    if not filepath.exists():
        raise FileNotFoundError(f"Prompt file not found: {filepath}")

    return filepath.read_text(encoding="utf-8")


def load_prompt_for_mode(mode: str) -> str:
    """
    Load the appropriate agent prompt for a given mode.

    Args:
        mode: One of INTAKE, CAREER_EXPLORATORY, CAREER_GOAL_SETTING,
              GOAL_DISCOVERY, PATHWAY, LEARNING

    Returns:
        The full text content of the corresponding agent's prompt.

    Raises:
        ValueError: If the mode is not recognized.
    """
    if mode not in MODE_TO_AGENT:
        raise ValueError(
            f"Unknown mode: '{mode}'. "
            f"Valid modes: {list(MODE_TO_AGENT.keys())}"
        )

    agent_name = MODE_TO_AGENT[mode]
    return load_agent_prompt(agent_name)


def get_all_agent_prompts() -> Dict[str, str]:
    """
    Load all agent prompts and return as a dictionary.

    Returns:
        Dict mapping agent names to their prompt content.
    """
    return {
        name: load_agent_prompt(name)
        for name in AGENT_PROMPT_FILES
    }


def load_orchestration_overview() -> str:
    """
    Load the orchestration architecture overview document.

    Returns:
        The full text of ORCHESTRATION_OVERVIEW.md
    """
    filepath = PROMPTS_DIR / "ORCHESTRATION_OVERVIEW.md"
    if not filepath.exists():
        raise FileNotFoundError(f"Overview file not found: {filepath}")
    return filepath.read_text(encoding="utf-8")
