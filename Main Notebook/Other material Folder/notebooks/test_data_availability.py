#!/usr/bin/env python3
"""
Test script to verify data availability for the EDA notebook.
Run this before executing the Jupyter notebook to ensure all required data files exist.
"""

import os
import pandas as pd

def test_data_availability():
    """Test if all required data files are available."""
    
    print("🔍 Testing Data Availability for EDA Notebook")
    print("=" * 60)
    
    # Define required files
    required_files = {
        "Manchester City": {
            "match_results": "data/fbref_scraped/final_exports/manchester_city_match_results_2023_24.csv",
            "player_performances": "data/fbref_scraped/final_exports/manchester_city_player_match_performances_2023_24.csv",
            "season_stats": "data/fbref_scraped/final_exports/manchester_city_player_season_aggregates_2023_24.csv",
            "competition_summary": "data/fbref_scraped/final_exports/manchester_city_competition_summary_2023_24.csv"
        },
        "Real Madrid": {
            "match_results": "data/real_madrid_scraped/final_exports/real_madrid_match_results_2023_24.csv",
            "player_performances": "data/real_madrid_scraped/final_exports/real_madrid_player_match_performances_2023_24.csv",
            "season_stats": "data/real_madrid_scraped/final_exports/real_madrid_player_season_aggregates_2023_24.csv",
            "competition_summary": "data/real_madrid_scraped/final_exports/real_madrid_competition_summary_2023_24.csv"
        }
    }
    
    all_files_exist = True
    total_files = 0
    found_files = 0
    
    for team, files in required_files.items():
        print(f"\n📊 {team} Data Files:")
        print("-" * 40)
        
        for file_type, file_path in files.items():
            total_files += 1
            if os.path.exists(file_path):
                try:
                    # Try to load the file to verify it's readable
                    df = pd.read_csv(file_path)
                    print(f"✅ {file_type}: {file_path} ({len(df)} records)")
                    found_files += 1
                except Exception as e:
                    print(f"❌ {file_type}: {file_path} (Error: {str(e)})")
                    all_files_exist = False
            else:
                print(f"❌ {file_type}: {file_path} (File not found)")
                all_files_exist = False
    
    print(f"\n📈 SUMMARY")
    print("=" * 60)
    print(f"Files Found: {found_files}/{total_files}")
    print(f"Data Availability: {found_files/total_files*100:.1f}%")
    
    if all_files_exist:
        print("🎉 SUCCESS: All required data files are available!")
        print("✅ You can now run the EDA notebook successfully.")
        
        # Quick data preview
        print(f"\n📋 QUICK DATA PREVIEW")
        print("-" * 40)
        
        try:
            mc_stats = pd.read_csv(required_files["Manchester City"]["season_stats"])
            rm_stats = pd.read_csv(required_files["Real Madrid"]["season_stats"])
            
            print(f"Manchester City Players: {len(mc_stats)}")
            print(f"Real Madrid Players: {len(rm_stats)}")
            
            mc_matches = pd.read_csv(required_files["Manchester City"]["match_results"])
            rm_matches = pd.read_csv(required_files["Real Madrid"]["match_results"])
            
            print(f"Manchester City Matches: {len(mc_matches)}")
            print(f"Real Madrid Matches: {len(rm_matches)}")
            
        except Exception as e:
            print(f"⚠️ Could not load data preview: {str(e)}")
        
    else:
        print("❌ FAILURE: Some required data files are missing!")
        print("⚠️ Please ensure all data collection scripts have been run successfully.")
        print("\nTo generate missing data:")
        print("1. Run Manchester City data collection if MC files are missing")
        print("2. Run Real Madrid data collection if RM files are missing")
        print("3. Check file paths and permissions")
    
    print("=" * 60)
    return all_files_exist

if __name__ == "__main__":
    test_data_availability()
