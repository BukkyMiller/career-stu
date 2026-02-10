"""
Career STU - Main agent implementation
Orchestrates the four modes: INTAKE, GOAL_DISCOVERY, PATHWAY, LEARNING
"""
import os
from typing import Dict, Any, List
from anthropic import Anthropic
from dotenv import load_dotenv

from agent.system_prompt import build_system_prompt, determine_mode
from agent.context_builder import ContextBuilder
from tools.definitions import ALL_TOOLS

# Tool implementations
from tools.job_search_tools import search_jobs, search_jobs_by_riasec, get_job_details
from tools.riasec_tools import infer_riasec_from_skills, get_riasec_description, compare_riasec_codes
from tools.salary_tools import get_salary_info, get_high_demand_jobs
from tools.skills_tools import calculate_skill_gap, find_jobs_by_skill_match
from tools.learner_tools import (
    get_learner_context,
    update_learner_profile,
    add_learner_skill,
    set_learner_goal
)
from tools.pathway_tools import create_pathway

load_dotenv()


class CareerSTU:
    """
    Career STU Agent - ONE agent with FOUR modes
    """

    def __init__(self, learner_id: str, api_key: str = None):
        self.learner_id = learner_id
        self.context_builder = ContextBuilder(learner_id)

        # Initialize Anthropic client
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"

        # Tool registry
        self.tool_functions = {
            "search_jobs": search_jobs,
            "search_jobs_by_riasec": search_jobs_by_riasec,
            "get_job_details": get_job_details,
            "infer_riasec_from_skills": infer_riasec_from_skills,
            "get_riasec_description": get_riasec_description,
            "compare_riasec_codes": compare_riasec_codes,
            "get_salary_info": get_salary_info,
            "get_high_demand_jobs": get_high_demand_jobs,
            "calculate_skill_gap": calculate_skill_gap,
            "find_jobs_by_skill_match": find_jobs_by_skill_match,
            "get_learner_context": get_learner_context,
            "update_learner_profile": update_learner_profile,
            "add_learner_skill": add_learner_skill,
            "set_learner_goal": set_learner_goal,
            "create_pathway": create_pathway
        }

    def chat(self, user_message: str) -> str:
        """
        Main chat interface
        Handles user message and returns assistant response
        """
        # Get learner context
        learner_context = self.context_builder.get_learner_context()

        # Determine current mode
        current_mode = determine_mode(learner_context)

        # Build system prompt for current mode
        system_prompt = build_system_prompt(current_mode, learner_context)

        # Add user message to history
        self.context_builder.add_message("user", user_message)

        # Get messages
        messages = self.context_builder.get_messages()

        # Call Claude with tools
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
            tools=ALL_TOOLS
        )

        # Process response
        assistant_message = self._process_response(response)

        # Add assistant message to history
        self.context_builder.add_message("assistant", assistant_message)

        return assistant_message

    def _process_response(self, response) -> str:
        """
        Process Claude's response, handling tool calls
        """
        final_text = []

        for block in response.content:
            if block.type == "text":
                final_text.append(block.text)

            elif block.type == "tool_use":
                # Execute tool
                tool_name = block.name
                tool_input = block.input

                try:
                    tool_function = self.tool_functions.get(tool_name)
                    if not tool_function:
                        result = {"error": f"Tool not found: {tool_name}"}
                    else:
                        result = tool_function(**tool_input)

                    # For multi-turn tool use, we'd need to call Claude again with tool results
                    # For MVP, we'll just include tool result in response
                    final_text.append(f"\n[Tool: {tool_name}]\n{result}\n")

                except Exception as e:
                    final_text.append(f"\n[Error using {tool_name}: {str(e)}]\n")

        return "".join(final_text)

    def get_current_mode(self) -> str:
        """Get the current mode based on learner context"""
        learner_context = self.context_builder.get_learner_context()
        return determine_mode(learner_context)

    def reset_conversation(self):
        """Reset conversation history"""
        self.context_builder.clear_history()


def create_agent(learner_id: str) -> CareerSTU:
    """
    Factory function to create a CareerSTU agent

    Args:
        learner_id: Learner's unique ID

    Returns:
        CareerSTU agent instance
    """
    return CareerSTU(learner_id)
