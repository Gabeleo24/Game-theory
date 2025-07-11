#!/usr/bin/env python3
"""
Real Madrid vs Manchester City Dataset Compatibility Validator

This script validates that the Real Madrid dataset structure is compatible
with the Manchester City dataset, ensuring they can be used for comparative analysis.
"""

import pandas as pd
import os
import logging
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatasetCompatibilityValidator:
    """Validate compatibility between Real Madrid and Manchester City datasets."""
    
    def __init__(self):
        """Initialize validator with dataset paths."""
        self.man_city_path = "data/fbref_scraped/final_exports"
        self.real_madrid_path = "data/real_madrid_scraped/final_exports"
        
        # Expected file mappings
        self.file_mappings = {
            "match_results": {
                "man_city": "manchester_city_match_results_2023_24.csv",
                "real_madrid": "real_madrid_match_results_2023_24.csv"
            },
            "player_performances": {
                "man_city": "manchester_city_player_match_performances_2023_24.csv",
                "real_madrid": "real_madrid_player_match_performances_2023_24.csv"
            },
            "season_stats": {
                "man_city": "manchester_city_player_season_aggregates_2023_24.csv",
                "real_madrid": "real_madrid_player_season_aggregates_2023_24.csv"
            },
            "competition_summary": {
                "man_city": "manchester_city_competition_summary_2023_24.csv",
                "real_madrid": "real_madrid_competition_summary_2023_24.csv"
            }
        }
    
    def validate_file_structure(self) -> bool:
        """Validate that all required files exist for both teams."""
        logger.info("🔍 Validating file structure...")
        
        missing_files = []
        
        for file_type, files in self.file_mappings.items():
            # Check Manchester City files
            man_city_file = os.path.join(self.man_city_path, files["man_city"])
            if not os.path.exists(man_city_file):
                missing_files.append(f"Manchester City: {files['man_city']}")
            
            # Check Real Madrid files
            real_madrid_file = os.path.join(self.real_madrid_path, files["real_madrid"])
            if not os.path.exists(real_madrid_file):
                missing_files.append(f"Real Madrid: {files['real_madrid']}")
        
        if missing_files:
            logger.error("❌ Missing files:")
            for file in missing_files:
                logger.error(f"   • {file}")
            return False
        
        logger.info("✅ All required files exist")
        return True
    
    def validate_column_compatibility(self) -> Dict[str, bool]:
        """Validate that column structures are compatible between datasets."""
        logger.info("📊 Validating column compatibility...")
        
        compatibility_results = {}
        
        for file_type, files in self.file_mappings.items():
            logger.info(f"   Checking {file_type}...")
            
            # Load both datasets
            man_city_file = os.path.join(self.man_city_path, files["man_city"])
            real_madrid_file = os.path.join(self.real_madrid_path, files["real_madrid"])
            
            try:
                man_city_df = pd.read_csv(man_city_file)
                real_madrid_df = pd.read_csv(real_madrid_file)
                
                # Compare column structures
                man_city_cols = set(man_city_df.columns)
                real_madrid_cols = set(real_madrid_df.columns)
                
                # Check for missing columns
                missing_in_real_madrid = man_city_cols - real_madrid_cols
                missing_in_man_city = real_madrid_cols - man_city_cols
                
                if missing_in_real_madrid or missing_in_man_city:
                    logger.warning(f"⚠️ Column differences in {file_type}:")
                    if missing_in_real_madrid:
                        logger.warning(f"   Missing in Real Madrid: {missing_in_real_madrid}")
                    if missing_in_man_city:
                        logger.warning(f"   Missing in Manchester City: {missing_in_man_city}")
                    compatibility_results[file_type] = False
                else:
                    logger.info(f"   ✅ {file_type} columns compatible")
                    compatibility_results[file_type] = True
                
            except Exception as e:
                logger.error(f"❌ Error validating {file_type}: {str(e)}")
                compatibility_results[file_type] = False
        
        return compatibility_results
    
    def validate_data_quality(self) -> Dict[str, Dict]:
        """Validate data quality and realistic ranges for both datasets."""
        logger.info("🎯 Validating data quality...")
        
        quality_results = {}
        
        for team in ["man_city", "real_madrid"]:
            team_name = "Manchester City" if team == "man_city" else "Real Madrid"
            logger.info(f"   Checking {team_name}...")
            
            # Load season stats for quality checks
            season_file = os.path.join(
                self.man_city_path if team == "man_city" else self.real_madrid_path,
                self.file_mappings["season_stats"][team]
            )
            
            try:
                df = pd.read_csv(season_file)
                
                # Quality metrics
                quality_metrics = {
                    "total_players": len(df),
                    "avg_goals_per_90": df["goals_per_90"].mean(),
                    "avg_assists_per_90": df["assists_per_90"].mean(),
                    "avg_rating": df["avg_rating"].mean(),
                    "realistic_goals": (df["goals_per_90"] <= 2.0).all(),
                    "realistic_assists": (df["assists_per_90"] <= 1.5).all(),
                    "realistic_ratings": ((df["avg_rating"] >= 5.0) & (df["avg_rating"] <= 10.0)).all(),
                    "has_key_players": len(df[df["goals"] > 5]) >= 3  # At least 3 players with 5+ goals
                }
                
                quality_results[team_name] = quality_metrics
                
                # Log key metrics
                logger.info(f"     Players: {quality_metrics['total_players']}")
                logger.info(f"     Avg Goals/90: {quality_metrics['avg_goals_per_90']:.3f}")
                logger.info(f"     Avg Rating: {quality_metrics['avg_rating']:.2f}")
                
            except Exception as e:
                logger.error(f"❌ Error validating {team_name} quality: {str(e)}")
                quality_results[team_name] = {"error": str(e)}
        
        return quality_results
    
    def compare_team_statistics(self) -> Dict:
        """Compare key statistics between the two teams."""
        logger.info("⚖️ Comparing team statistics...")
        
        comparison = {}
        
        try:
            # Load season stats for both teams
            man_city_df = pd.read_csv(os.path.join(
                self.man_city_path, self.file_mappings["season_stats"]["man_city"]
            ))
            real_madrid_df = pd.read_csv(os.path.join(
                self.real_madrid_path, self.file_mappings["season_stats"]["real_madrid"]
            ))
            
            # Calculate team totals
            comparison = {
                "Manchester City": {
                    "total_goals": man_city_df["goals"].sum(),
                    "total_assists": man_city_df["assists"].sum(),
                    "avg_team_rating": man_city_df["avg_rating"].mean(),
                    "top_scorer_goals": man_city_df["goals"].max(),
                    "top_assister_assists": man_city_df["assists"].max()
                },
                "Real Madrid": {
                    "total_goals": real_madrid_df["goals"].sum(),
                    "total_assists": real_madrid_df["assists"].sum(),
                    "avg_team_rating": real_madrid_df["avg_rating"].mean(),
                    "top_scorer_goals": real_madrid_df["goals"].max(),
                    "top_assister_assists": real_madrid_df["assists"].max()
                }
            }
            
            # Log comparison
            for team, stats in comparison.items():
                logger.info(f"   {team}:")
                logger.info(f"     Total Goals: {stats['total_goals']}")
                logger.info(f"     Total Assists: {stats['total_assists']}")
                logger.info(f"     Avg Rating: {stats['avg_team_rating']:.2f}")
                logger.info(f"     Top Scorer: {stats['top_scorer_goals']} goals")
                logger.info(f"     Top Assister: {stats['top_assister_assists']} assists")
            
        except Exception as e:
            logger.error(f"❌ Error comparing statistics: {str(e)}")
            comparison = {"error": str(e)}
        
        return comparison
    
    def run_full_validation(self) -> Dict:
        """Run complete validation suite."""
        logger.info("🚀 Starting comprehensive dataset compatibility validation")
        
        results = {
            "file_structure_valid": False,
            "column_compatibility": {},
            "data_quality": {},
            "team_comparison": {},
            "overall_compatible": False
        }
        
        # Step 1: File structure validation
        results["file_structure_valid"] = self.validate_file_structure()
        
        if not results["file_structure_valid"]:
            logger.error("❌ Cannot proceed - missing required files")
            return results
        
        # Step 2: Column compatibility
        results["column_compatibility"] = self.validate_column_compatibility()
        
        # Step 3: Data quality validation
        results["data_quality"] = self.validate_data_quality()
        
        # Step 4: Team comparison
        results["team_comparison"] = self.compare_team_statistics()
        
        # Overall compatibility assessment
        column_compatibility_score = sum(results["column_compatibility"].values())
        total_file_types = len(self.file_mappings)
        
        results["overall_compatible"] = (
            results["file_structure_valid"] and
            column_compatibility_score >= total_file_types * 0.8  # 80% compatibility threshold
        )
        
        # Final assessment
        if results["overall_compatible"]:
            logger.info("🎉 VALIDATION PASSED: Datasets are compatible for comparative analysis!")
        else:
            logger.error("❌ VALIDATION FAILED: Datasets have compatibility issues")
        
        return results


def main():
    """Main execution function."""
    print("=" * 80)
    print("🔍 REAL MADRID vs MANCHESTER CITY DATASET COMPATIBILITY VALIDATION")
    print("=" * 80)
    
    validator = DatasetCompatibilityValidator()
    results = validator.run_full_validation()
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)
    
    print(f"📁 File Structure: {'✅ VALID' if results['file_structure_valid'] else '❌ INVALID'}")
    
    print(f"\n📋 Column Compatibility:")
    for file_type, compatible in results["column_compatibility"].items():
        status = "✅ COMPATIBLE" if compatible else "❌ INCOMPATIBLE"
        print(f"   • {file_type.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 Overall Compatibility: {'✅ COMPATIBLE' if results['overall_compatible'] else '❌ INCOMPATIBLE'}")
    
    if results["overall_compatible"]:
        print(f"\n🚀 Ready for comparative analysis between Manchester City and Real Madrid!")
    else:
        print(f"\n⚠️ Datasets require fixes before comparative analysis")
    
    print("=" * 80)
    
    return results


if __name__ == "__main__":
    main()
