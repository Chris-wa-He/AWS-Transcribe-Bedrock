#!/usr/bin/env python3
"""
Development runner script for the Voice Assistant application.
This script can be used as an alternative to running main.py directly.
"""
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

if __name__ == "__main__":
    from voice_assistant.main import main

    main()
