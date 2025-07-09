#!/usr/bin/env python3
"""
QUICK ACCESS - REAL MADRID 2023-2024 STATISTICS
One-click access to premium Real Madrid statistics
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(__file__))

from scripts.analysis.premium_real_madrid_display import main

if __name__ == "__main__":
    print("🏆 LOADING REAL MADRID 2023-2024 CHAMPIONS LEAGUE WINNERS STATISTICS 🏆")
    print("📊 Premium SportMonks API Integration | Enhanced Database Analysis")
    print()
    main()
