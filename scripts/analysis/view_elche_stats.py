#!/usr/bin/env python3
"""
ELCHE STATS VIEWER - Quick launcher for Elche-style statistics
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scripts.analysis.elche_style_professional import main

if __name__ == "__main__":
    print("🏆 REAL MADRID 2023-2024 ELCHE-STYLE STATISTICS 🏆")
    print("Loading comprehensive player statistics...")
    print()
    main()
