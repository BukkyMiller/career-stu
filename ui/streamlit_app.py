"""
Streamlit UI for Career STU
Quick test interface for MVP
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
import streamlit as st
import uuid
from dotenv import load_dotenv
from tools.learner_tools import create_learner, get_learner_context
from database.connection import init_db

load_dotenv()

# Import the right agent based on provider
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic").lower()
if LLM_PROVIDER == "openai":
    from agent.career_stu_openai import create_agent_openai as create_agent
else:
    from agent.career_stu import create_agent

st.set_page_config(
    page_title="Career STU",
    page_icon="🎓",
    layout="wide"
)

# Initialize database
try:
    init_db()
except:
    pass  # Already initialized


def initialize_session():
    """Initialize session state"""
    if "learner_id" not in st.session_state:
        st.session_state.learner_id = None
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "messages" not in st.session_state:
        st.session_state.messages = []


def create_new_learner():
    """Create a new learner"""
    email = st.session_state.get("new_email", "")
    name = st.session_state.get("new_name", "")

    if email:
        result = create_learner(email, name)
        if "error" not in result:
            st.session_state.learner_id = result["learner_id"]
            st.session_state.agent = create_agent(result["learner_id"])
            st.success(f"Created learner: {result['learner_id']}")
        else:
            st.error(result["error"])


def main():
    initialize_session()

    st.title("🎓 Career STU")
    st.subheader("AI Career Support Assistant")

    # Sidebar for learner management
    with st.sidebar:
        st.header("Learner")

        if st.session_state.learner_id:
            st.success(f"Active: {st.session_state.learner_id[:8]}...")

            # Show current mode
            if st.session_state.agent:
                current_mode = st.session_state.agent.get_current_mode()
                st.info(f"Mode: **{current_mode}**")

            # Show context
            if st.button("View Context"):
                context = get_learner_context(st.session_state.learner_id)
                st.json(context)

            # Reset conversation
            if st.button("Reset Conversation"):
                st.session_state.messages = []
                if st.session_state.agent:
                    st.session_state.agent.reset_conversation()
                st.success("Conversation reset")

            # New learner
            if st.button("Switch Learner"):
                st.session_state.learner_id = None
                st.session_state.agent = None
                st.session_state.messages = []
                st.rerun()

        else:
            st.write("Create or load a learner")

            # Create new learner
            st.text_input("Email", key="new_email")
            st.text_input("Name (optional)", key="new_name")
            st.button("Create Learner", on_click=create_new_learner)

            st.divider()

            # Load existing learner
            learner_id_input = st.text_input("Or enter Learner ID")
            if st.button("Load Learner"):
                if learner_id_input:
                    try:
                        st.session_state.learner_id = learner_id_input
                        st.session_state.agent = create_agent(learner_id_input)
                        st.success("Learner loaded")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # Main chat interface
    if not st.session_state.learner_id:
        st.info("👈 Create or load a learner to start")
        return

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Message Career STU..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.agent.chat(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})


if __name__ == "__main__":
    main()
