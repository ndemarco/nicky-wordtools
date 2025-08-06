# conftest.py
# Global pytest config or fixtures can go here if needed in future

import pytest
import sys
import os

# Add the utilities/ folder to sys.path so tests can import local modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# No shared fixtures yet, but keeping this for consistency and future use

# Example placeholder fixture (remove when unused)
# @pytest.fixture
# def sample_wordlist():
#     return "wordA 10\nwordB 20\n"
