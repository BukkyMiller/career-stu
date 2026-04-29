"""
Career STU - Main agent implementation
Orchestrates the four modes: INTAKE, GOAL_DISCOVERY, PATHWAY, LEARNING
"""
import os
import time
from typing import Dict, Any, List
from anthropic import Anthropic, APIError
from dotenv import load_dotenv

from agent.system_prompt import build_system_prompt, determine_mode
from agent.context_builder import ContextBuilder
from tools.definitions import ALL_TOOLS

# Tool implementations
from tools.job_search_tools import search_jobs, search_jobs_by_riasec, get_job_details
from tools.riasec_tools import infer_riasec_from_skills, get_riasec_description, compare_riasec_codes
from tools.salary_tools import get_salary_info, get_comprehensive_market_data, get_high_demand_jobs, get_market_insights
from tools.skills_tools import calculate_skill_gap, find_jobs_by_skill_match, suggest_next_skills
from tools.learner_tools import (
    get_learner_context,
    update_learner_profile,
    add_learner_skill,
    set_learner_goal,
    create_learner
)
from tools.pathway_tools import create_pathway, update_pathway_progress, get_pathway_details, get_current_skill

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
        # Use claude-3-haiku (only model available with current API key tier)
        # To use Sonnet, upgrade API access at console.anthropic.com
        self.model = "claude-3-haiku-20240307"

        # Tool registry (22 tools)
        self.tool_functions = {
            # Job Search (3)
            "search_jobs": search_jobs,
            "search_jobs_by_riasec": search_jobs_by_riasec,
            "get_job_details": get_job_details,
            # RIASEC (3)
            "infer_riasec_from_skills": infer_riasec_from_skills,
            "get_riasec_description": get_riasec_description,
            "compare_riasec_codes": compare_riasec_codes,
            # Salary & Market (4)
            "get_salary_info": get_salary_info,
            "get_comprehensive_market_data": get_comprehensive_market_data,
            "get_high_demand_jobs": get_high_demand_jobs,
            "get_market_insights": get_market_insights,
            # Skills (3)
            "calculate_skill_gap": calculate_skill_gap,
            "find_jobs_by_skill_match": find_jobs_by_skill_match,
            "suggest_next_skills": suggest_next_skills,
            # Learner (5)
            "get_learner_context": get_learner_context,
            "update_learner_profile": update_learner_profile,
            "add_learner_skill": add_learner_skill,
            "set_learner_goal": set_learner_goal,
            "create_learner": create_learner,
            # Pathway (4)
            "create_pathway": create_pathway,
            "update_pathway_progress": update_pathway_progress,
            "get_pathway_details": get_pathway_details,
            "get_current_skill": get_current_skill,
        }

    def _call_with_retry(self, call_func, max_retries=3):
        """
        Retry wrapper for API calls with exponential backoff
        Handles overloaded errors gracefully
        """
        for attempt in range(max_retries):
            try:
                return call_func()
            except APIError as e:
                # Check if it's an overloaded error
                if 'overloaded' in str(e).lower() and attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    print(f"⚠ API overloaded. Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    # Out of retries or different error
                    raise

    def chat(self, user_message: str) -> str:
        """
        Main chat interface with proper multi-turn tool use.
        Handles user message and returns assistant response.
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

        # Multi-turn tool use loop
        max_tool_rounds = 10  # Safety limit
        tool_round = 0
        final_text_parts = []

        while tool_round < max_tool_rounds:
            tool_round += 1

            # Call Claude with tools (with retry for overloaded errors)
            response = self._call_with_retry(lambda: self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
                tools=ALL_TOOLS
            ))

            # Check if we have tool calls
            tool_calls = [block for block in response.content if block.type == "tool_use"]
            text_blocks = [block for block in response.content if block.type == "text"]

            # Collect any text from this response
            for block in text_blocks:
                final_text_parts.append(block.text)

            # If no tool calls, we're done
            if not tool_calls:
                break

            # Execute tools and prepare tool results
            tool_results = []
            for tool_call in tool_calls:
                tool_name = tool_call.name
                tool_input = tool_call.input
                tool_use_id = tool_call.id

                try:
                    tool_function = self.tool_functions.get(tool_name)
                    if not tool_function:
                        result = {"error": f"Tool not found: {tool_name}"}
                    else:
                        result = tool_function(**tool_input)

                    # Convert result to string if needed
                    if not isinstance(result, str):
                        import json
                        result = json.dumps(result, default=str, indent=2)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": result
                    })

                except Exception as e:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": f"Error: {str(e)}",
                        "is_error": True
                    })

            # Add assistant message with tool calls to conversation
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            # Add tool results to conversation
            messages.append({
                "role": "user",
                "content": tool_results
            })

        # Combine all text parts
        assistant_message = " ".join(final_text_parts).strip()

        # Add final assistant message to history
        self.context_builder.add_message("assistant", assistant_message)

        return assistant_message

    def chat_stream(self, user_message: str):
        """
        Streaming chat interface with proper multi-turn tool use.
        Yields text chunks as they arrive from Claude.
        """
        import json

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

        # Multi-turn tool use loop with streaming
        max_tool_rounds = 10
        tool_round = 0
        full_response_text = []

        while tool_round < max_tool_rounds:
            tool_round += 1

            # Stream response from Claude
            with self.client.messages.stream(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
                tools=ALL_TOOLS
            ) as stream:
                # Collect the full response for tool processing
                current_text = []
                tool_calls = []

                for event in stream:
                    # Handle text delta events
                    if hasattr(event, 'type'):
                        if event.type == 'content_block_delta':
                            if hasattr(event.delta, 'text'):
                                text_chunk = event.delta.text
                                current_text.append(text_chunk)
                                yield text_chunk
                        elif event.type == 'content_block_start':
                            if hasattr(event.content_block, 'type') and event.content_block.type == 'tool_use':
                                # Tool call starting - collect it
                                tool_calls.append({
                                    'id': event.content_block.id,
                                    'name': event.content_block.name,
                                    'input': {}
                                })
                        elif event.type == 'content_block_delta':
                            if hasattr(event.delta, 'partial_json') and tool_calls:
                                # Accumulate tool input JSON (handled by SDK)
                                pass

                # Get the final message for tool calls
                final_message = stream.get_final_message()

            # Collect text from this round
            round_text = "".join(current_text)
            if round_text:
                full_response_text.append(round_text)

            # Check for tool calls in final message
            tool_use_blocks = [block for block in final_message.content if block.type == "tool_use"]

            # If no tool calls, we're done
            if not tool_use_blocks:
                break

            # Execute tools
            tool_results = []
            for tool_call in tool_use_blocks:
                tool_name = tool_call.name
                tool_input = tool_call.input
                tool_use_id = tool_call.id

                try:
                    tool_function = self.tool_functions.get(tool_name)
                    if not tool_function:
                        result = {"error": f"Tool not found: {tool_name}"}
                    else:
                        result = tool_function(**tool_input)

                    if not isinstance(result, str):
                        result = json.dumps(result, default=str, indent=2)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": result
                    })

                except Exception as e:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": f"Error: {str(e)}",
                        "is_error": True
                    })

            # Add assistant message with tool calls to conversation
            messages.append({
                "role": "assistant",
                "content": final_message.content
            })

            # Add tool results to conversation
            messages.append({
                "role": "user",
                "content": tool_results
            })

        # Save full response to history
        assistant_message = " ".join(full_response_text).strip()
        self.context_builder.add_message("assistant", assistant_message)

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
