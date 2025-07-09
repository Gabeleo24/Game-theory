#!/usr/bin/env python3
"""
QUICK ACCESS - REAL MADRID MATCH ANALYZER
One-click access to Real Madrid's 2023-2024 match-level player statistics
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(__file__))

from scripts.analysis.real_madrid_match_analyzer import main

if __name__ == "__main__":
    print("🏆 REAL MADRID 2023-2024 CHAMPIONS LEAGUE WINNING SEASON 🏆")
    print("📊 Match-Level Player Statistics Analyzer")
    print("🎯 52 Games Available | Individual Player Performance Analysis")
    print()
    
    if len(sys.argv) > 1:
        print(f"🔍 Analyzing Match ID: {sys.argv[1]}")
        print()
    else:
        print("📋 Available Commands:")
        print("   python view_real_madrid_matches.py          # Show all matches")
        print("   python view_real_madrid_matches.py 4        # Champions League Final")
        print("   python view_real_madrid_matches.py 51       # El Clasico vs Barcelona")
        print("   python view_real_madrid_matches.py 15       # vs Manchester City")
        print()
    
    main()
