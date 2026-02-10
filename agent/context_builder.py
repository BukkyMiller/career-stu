"""
Context builder for Career STU agent
Manages conversation history and learner context
"""
from typing import List, Dict, Any
from tools.learner_tools import get_learner_context


class ContextBuilder:
    """Builds and manages context for the Career STU agent"""

    def __init__(self, learner_id: str):
        self.learner_id = learner_id
        self.conversation_history: List[Dict[str, Any]] = []

    def get_learner_context(self) -> Dict[str, Any]:
        """Get current learner context from database"""
        return get_learner_context(self.learner_id)

    def add_message(self, role: str, content: str):
        """
        Add a message to conversation history

        Args:
            role: 'user' or 'assistant'
            content: Message content
        """
        self.conversation_history.append({
            "role": role,
            "content": content
        })

    def add_tool_result(self, tool_name: str, tool_input: Dict[str, Any], result: Any):
        """
        Add a tool use to conversation history

        Args:
            tool_name: Name of the tool used
            tool_input: Input parameters to the tool
            result: Tool result
        """
        # For Anthropic format, tool results are added separately
        # This is a simplified version - full implementation would follow Anthropic's format
        pass

    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in Anthropic format"""
        return self.conversation_history

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def summarize_conversation(self) -> str:
        """
        Summarize the conversation so far
        Useful for long conversations
        """
        if not self.conversation_history:
            return "No conversation yet"

        summary_parts = []
        for msg in self.conversation_history[-10:]:  # Last 10 messages
            role = msg["role"]
            content = msg["content"][:100]  # Truncate long messages
            summary_parts.append(f"{role.upper()}: {content}...")

        return "\n".join(summary_parts)
