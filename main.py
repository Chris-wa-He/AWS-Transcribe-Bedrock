#!/usr/bin/env python3
"""
Voice Assistant Application Entry Point

This is the main entry point for the Voice Assistant application.
It imports and runs the main function from the voice_assistant package.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import after path modification
from voice_assistant.main import main  # noqa: E402

if __name__ == "__main__":
    main()
