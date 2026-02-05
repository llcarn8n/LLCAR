#!/usr/bin/env python3
"""
LLCAR Interactive Console Launcher

Quick launcher for the interactive console mode.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from main import main

if __name__ == "__main__":
    # Force interactive mode
    sys.argv.append("--interactive")
    sys.exit(main())
