#!/usr/bin/env python3
"""
nWave IDE Bundle Builder - Simple Entry Point

Simple entry point that loads configuration and runs the main builder.
This provides a clean interface for running the build system.
"""

import sys
from pathlib import Path

# Add the tools directory to the Python path
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

# Import and run the main builder
from build_ide_bundle import main

if __name__ == "__main__":
    main()