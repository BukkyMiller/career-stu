"""
Career STU - OpenAI-compatible agent implementation
Orchestrates the four modes: INTAKE, GOAL_DISCOVERY, PATHWAY, LEARNING
"""
import os
import json
from typing import Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

from agent.system_prompt import build_system_prompt, determine_mode
from agent.context_builder import ContextBuilder

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


def convert_tool_to_openai_format(tool: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Anthropic tool format to OpenAI function format"""
    return {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["input_schema"]
        }
    }


class CareerSTUOpenAI:
    """
    Career STU Agent - ONE agent with FOUR modes (OpenAI version)
    """

    def __init__(self, learner_id: str, api_key: str = None):
        self.learner_id = learner_id
        self.context_builder = ContextBuilder(learner_id)

        # Initialize OpenAI client
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4-turbo-preview"

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

        # Convert tools to OpenAI format
        from tools.definitions import ALL_TOOLS
        self.tools = [convert_tool_to_openai_format(tool) for tool in ALL_TOOLS]

    def chat(self, user_message: str, max_turns: int = 3) -> str:
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
        messages = [{"role": "system", "content": system_prompt}] + self.context_builder.get_messages()

        # Call OpenAI with function calling
        response_text = self._chat_with_tools(messages, max_turns)

        # Add assistant message to history
        self.context_builder.add_message("assistant", response_text)

        return response_text

    def _chat_with_tools(self, messages: List[Dict], max_turns: int) -> str:
        """
        Handle multi-turn conversation with tool calls
        """
        current_messages = messages.copy()

        for turn in range(max_turns):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=current_messages,
                tools=self.tools,
                tool_choice="auto"
            )

            message = response.choices[0].message

            # If no tool calls, return the response
            if not message.tool_calls:
                return message.content or ""

            # Add assistant message with tool calls
            current_messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [tc.model_dump() for tc in message.tool_calls]
            })

            # Execute each tool call
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Execute tool
                try:
                    tool_function = self.tool_functions.get(function_name)
                    if not tool_function:
                        result = {"error": f"Tool not found: {function_name}"}
                    else:
                        result = tool_function(**function_args)
                except Exception as e:
                    result = {"error": f"Error executing {function_name}: {str(e)}"}

                # Add tool result
                current_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

        # Final response after all tool calls
        final_response = self.client.chat.completions.create(
            model=self.model,
            messages=current_messages
        )

        return final_response.choices[0].message.content or ""

    def chat_stream(self, user_message: str):
        """
        Streaming chat interface for better UX
        Yields text chunks as they arrive from OpenAI
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
        messages = [{"role": "system", "content": system_prompt}] + self.context_builder.get_messages()

        # Agentic loop: handle tool calls
        max_iterations = 5
        iteration = 0
        current_messages = messages.copy()

        while iteration < max_iterations:
            iteration += 1

            # Call OpenAI with streaming
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=current_messages,
                tools=self.tools,
                tool_choice="auto",
                stream=True
            )

            # Collect response
            collected_messages = []
            tool_calls_data = []
            current_tool_call = None

            for chunk in stream:
                delta = chunk.choices[0].delta

                # Handle text content
                if delta.content:
                    yield delta.content
                    collected_messages.append(delta.content)

                # Handle tool calls
                if delta.tool_calls:
                    for tool_call_chunk in delta.tool_calls:
                        # Initialize or update tool call data
                        if tool_call_chunk.index >= len(tool_calls_data):
                            tool_calls_data.append({
                                "id": "",
                                "type": "function",
                                "function": {"name": "", "arguments": ""}
                            })

                        if tool_call_chunk.id:
                            tool_calls_data[tool_call_chunk.index]["id"] = tool_call_chunk.id

                        if tool_call_chunk.function:
                            if tool_call_chunk.function.name:
                                tool_calls_data[tool_call_chunk.index]["function"]["name"] = tool_call_chunk.function.name
                            if tool_call_chunk.function.arguments:
                                tool_calls_data[tool_call_chunk.index]["function"]["arguments"] += tool_call_chunk.function.arguments

            # Check if we have tool calls
            if not tool_calls_data:
                # No tool calls, we're done
                full_response = "".join(collected_messages)
                self.context_builder.add_message("assistant", full_response)
                return

            # Process tool calls
            current_messages.append({
                "role": "assistant",
                "content": "".join(collected_messages) if collected_messages else None,
                "tool_calls": tool_calls_data
            })

            # Execute each tool call
            for tool_call in tool_calls_data:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])

                # Execute tool
                try:
                    tool_function = self.tool_functions.get(function_name)
                    if not tool_function:
                        result = {"error": f"Tool not found: {function_name}"}
                    else:
                        result = tool_function(**function_args)
                except Exception as e:
                    result = {"error": f"Error executing {function_name}: {str(e)}"}

                # Add tool result
                current_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result)
                })

        # If we hit max iterations
        yield "\n\n[Reached maximum tool use iterations]"

    def get_current_mode(self) -> str:
        """Get the current mode based on learner context"""
        learner_context = self.context_builder.get_learner_context()
        return determine_mode(learner_context)

    def reset_conversation(self):
        """Reset conversation history"""
        self.context_builder.clear_history()


def create_agent_openai(learner_id: str) -> CareerSTUOpenAI:
    """
    Factory function to create a CareerSTU agent with OpenAI

    Args:
        learner_id: Learner's unique ID

    Returns:
        CareerSTUOpenAI agent instance
    """
    return CareerSTUOpenAI(learner_id)
