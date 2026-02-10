#!/bin/bash
# Career STU Launcher Script

echo "🚀 Launching Career STU..."
echo ""

# Set Python path
export PYTHONPATH=/Users/bukola.awodumila/career-explorer:$PYTHONPATH
export PATH="/Users/bukola.awodumila/Library/Python/3.9/bin:$PATH"

# Change to project directory
cd /Users/bukola.awodumila/career-explorer

# Run Streamlit
echo "Starting Streamlit on http://localhost:8501"
echo "Press Ctrl+C to stop"
echo ""

streamlit run ui/streamlit_app.py
