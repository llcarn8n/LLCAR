#!/usr/bin/env python3
"""
LLCAR Interactive Console Launcher

Quick launcher for the interactive console mode.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    # Force interactive mode without mutating the global sys.argv
    if "--interactive" not in sys.argv:
        sys.argv.append("--interactive")
    from main import main
    sys.exit(main())
