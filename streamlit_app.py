# Entry point for Streamlit Cloud deployment
# This file imports the AI Resume Builder app from ai_resumes_tool package

import sys
import os

# Add current directory to path for package imports
sys.path.insert(0, os.path.dirname(__file__))

# Import and run the Streamlit app
# This triggers all Streamlit code in ai_resumes_tool/app.py
from ai_resumes_tool import app
