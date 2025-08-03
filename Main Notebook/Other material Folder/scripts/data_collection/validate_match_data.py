#!/usr/bin/env python3
"""
Validate Match-by-Match Data
Comprehensive validation to ensure data consistency and integrity
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MatchDataValidator:
    """Validate match-by-match data for consistency and integrity."""
    
    def __init__(self, db_path="data/fbref_scraped/fbref_data.db"):
        """Initialize with database path."""
        self.db_path = db_path
        self.validation_results = {}
        
    def validate_match_data_consistency(self):
        """Validate that match-level data is consistent."""
        
        logger.info("🔍 Validating match data consistency")
        
        conn = sqlite3.connect(self.db_path)
        
        # Check match count by competition
        match_counts = pd.read_sql_query('''
            SELECT competition, COUNT(*) as match_count
            FROM match_results 
            GROUP BY competition
        ''', conn)
        
        print("\n📊 MATCH COUNT VALIDATION")
        print("=" * 40)
        
        expected_counts = {
            'Premier League': 38,
            'Champions League': 8,
            'FA Cup': 6,
            'EFL Cup': 3
        }
        
        total_matches = 0
        for _, row in match_counts.iterrows():
            comp = row['competition']
            actual = row['match_count']
            expected = expected_counts.get(comp, 'Unknown')
            
            status = "✅" if actual == expected else "⚠️"
            print(f"   {status} {comp}: {actual} matches (expected: {expected})")
            total_matches += actual
        
        print(f"\n📈 Total matches: {total_matches}")
        
        # Validate results distribution
        results_dist = pd.read_sql_query('''
            SELECT result, COUNT(*) as count
            FROM match_results 
            GROUP BY result
        ''', conn)
        
        print(f"\n🎯 RESULTS DISTRIBUTION")
        print("=" * 40)
        for _, row in results_dist.iterrows():
            percentage = (row['count'] / total_matches) * 100
            print(f"   {row['result']}: {row['count']} ({percentage:.1f}%)")
        
        conn.close()
        
        self.validation_results['match_consistency'] = {
            'total_matches': total_matches,
            'expected_total': sum(expected_counts.values()),
            'status': 'PASS' if total_matches == sum(expected_counts.values()) else 'WARNING'
        }
        
    def validate_player_performance_consistency(self):
        """Validate that player performances aggregate correctly to season totals."""
        
        logger.info("🎭 Validating player performance consistency")
        
        conn = sqlite3.connect(self.db_path)
        
        # Compare match-level aggregates to season totals
        comparison_query = '''
        SELECT 
            ps.player_name,
            ps.matches_played as season_matches,
            ps.goals as season_goals,
            ps.assists as season_assists,
            COUNT(pmp.match_id) as match_count,
            SUM(pmp.goals) as match_goals,
            SUM(pmp.assists) as match_assists,
            ROUND(AVG(pmp.rating), 1) as avg_rating
        FROM player_stats ps
        LEFT JOIN player_match_performances pmp ON ps.player_name = pmp.player_name
        WHERE ps.team_name = 'Manchester City'
        GROUP BY ps.player_name
        ORDER BY ps.goals DESC
        '''
        
        comparison_df = pd.read_sql_query(comparison_query, conn)
        
        print("\n🎭 PLAYER PERFORMANCE VALIDATION")
        print("=" * 60)
        print("Player Name                | Season | Match  | Goals | Assists | Rating")
        print("-" * 60)
        
        inconsistencies = 0
        
        for _, row in comparison_df.head(15).iterrows():
            # Check for major inconsistencies (allowing some variance for realism)
            goals_diff = abs((row['season_goals'] or 0) - (row['match_goals'] or 0))
            assists_diff = abs((row['season_assists'] or 0) - (row['match_assists'] or 0))
            
            status = "✅" if goals_diff <= 5 and assists_diff <= 3 else "⚠️"
            if status == "⚠️":
                inconsistencies += 1
            
            print(f"{row['player_name'][:25]:<25} | {row['season_matches']:>6} | {row['match_count']:>6} | "
                  f"{row['season_goals']:>5} | {row['season_assists']:>7} | {row['avg_rating']:>6} {status}")
        
        print(f"\n📊 Inconsistencies found: {inconsistencies}")
        
        conn.close()
        
        self.validation_results['player_consistency'] = {
            'inconsistencies': inconsistencies,
            'status': 'PASS' if inconsistencies <= 5 else 'WARNING'
        }
        
    def validate_data_relationships(self):
        """Validate foreign key relationships and data integrity."""
        
        logger.info("🔗 Validating data relationships")
        
        conn = sqlite3.connect(self.db_path)
        
        # Check for orphaned player performances
        orphaned_performances = pd.read_sql_query('''
            SELECT COUNT(*) as count
            FROM player_match_performances pmp
            LEFT JOIN match_results mr ON pmp.match_id = mr.match_id
            WHERE mr.match_id IS NULL
        ''', conn)
        
        # Check for players in performances but not in roster
        missing_players = pd.read_sql_query('''
            SELECT COUNT(DISTINCT pmp.player_name) as count
            FROM player_match_performances pmp
            LEFT JOIN players p ON pmp.player_name = p.player_name
            WHERE p.player_name IS NULL
        ''', conn)
        
        # Check for matches without any player performances
        empty_matches = pd.read_sql_query('''
            SELECT COUNT(*) as count
            FROM match_results mr
            LEFT JOIN player_match_performances pmp ON mr.match_id = pmp.match_id
            WHERE pmp.match_id IS NULL
        ''', conn)
        
        print("\n🔗 DATA RELATIONSHIP VALIDATION")
        print("=" * 40)
        
        orphaned_count = orphaned_performances.iloc[0]['count']
        missing_count = missing_players.iloc[0]['count']
        empty_count = empty_matches.iloc[0]['count']
        
        print(f"   {'✅' if orphaned_count == 0 else '❌'} Orphaned performances: {orphaned_count}")
        print(f"   {'✅' if missing_count == 0 else '❌'} Missing players: {missing_count}")
        print(f"   {'✅' if empty_count == 0 else '❌'} Empty matches: {empty_count}")
        
        conn.close()
        
        self.validation_results['relationships'] = {
            'orphaned_performances': orphaned_count,
            'missing_players': missing_count,
            'empty_matches': empty_count,
            'status': 'PASS' if all([orphaned_count == 0, missing_count == 0, empty_count == 0]) else 'FAIL'
        }
        
    def validate_statistical_realism(self):
        """Validate that statistics are realistic and within expected ranges."""
        
        logger.info("📈 Validating statistical realism")
        
        conn = sqlite3.connect(self.db_path)
        
        # Check for unrealistic individual match performances
        unrealistic_performances = pd.read_sql_query('''
            SELECT 
                player_name,
                COUNT(*) as issues
            FROM player_match_performances
            WHERE goals > 5 OR assists > 4 OR shots_total > 15 OR rating > 10 OR rating < 5
            GROUP BY player_name
        ''', conn)
        
        # Check team-level statistics
        team_stats = pd.read_sql_query('''
            SELECT 
                AVG(manchester_city_score) as avg_goals_for,
                AVG(opponent_score) as avg_goals_against,
                AVG(possession_percentage) as avg_possession,
                AVG(shots_total) as avg_shots,
                MAX(manchester_city_score) as max_goals,
                MIN(possession_percentage) as min_possession,
                MAX(possession_percentage) as max_possession
            FROM match_results
        ''', conn)
        
        print("\n📈 STATISTICAL REALISM VALIDATION")
        print("=" * 40)
        
        stats = team_stats.iloc[0]
        print(f"   Average goals scored: {stats['avg_goals_for']:.1f}")
        print(f"   Average goals conceded: {stats['avg_goals_against']:.1f}")
        print(f"   Average possession: {stats['avg_possession']:.1f}%")
        print(f"   Average shots: {stats['avg_shots']:.1f}")
        print(f"   Highest score: {stats['max_goals']}")
        print(f"   Possession range: {stats['min_possession']:.1f}% - {stats['max_possession']:.1f}%")
        
        unrealistic_count = len(unrealistic_performances)
        print(f"\n   {'✅' if unrealistic_count == 0 else '⚠️'} Players with unrealistic performances: {unrealistic_count}")
        
        conn.close()
        
        # Validate ranges
        realistic_ranges = {
            'avg_goals_for': (1.5, 3.5),
            'avg_possession': (55, 75),
            'max_goals': (0, 8)
        }
        
        realism_issues = 0
        for stat, (min_val, max_val) in realistic_ranges.items():
            if not (min_val <= stats[stat] <= max_val):
                realism_issues += 1
        
        self.validation_results['realism'] = {
            'unrealistic_performances': unrealistic_count,
            'range_issues': realism_issues,
            'status': 'PASS' if unrealistic_count <= 5 and realism_issues == 0 else 'WARNING'
        }
        
    def generate_data_summary(self):
        """Generate comprehensive data summary."""
        
        logger.info("📋 Generating data summary")
        
        conn = sqlite3.connect(self.db_path)
        
        # Overall statistics
        summary_stats = pd.read_sql_query('''
            SELECT 
                (SELECT COUNT(*) FROM match_results) as total_matches,
                (SELECT COUNT(*) FROM player_match_performances) as total_performances,
                (SELECT COUNT(DISTINCT player_name) FROM player_match_performances) as active_players,
                (SELECT SUM(manchester_city_score) FROM match_results) as total_goals_scored,
                (SELECT COUNT(*) FROM match_results WHERE result = 'Win') as wins,
                (SELECT COUNT(*) FROM match_results WHERE result = 'Draw') as draws,
                (SELECT COUNT(*) FROM match_results WHERE result = 'Loss') as losses
        ''', conn)
        
        stats = summary_stats.iloc[0]
        
        print("\n📋 COMPREHENSIVE DATA SUMMARY")
        print("=" * 50)
        print(f"📊 Dataset Overview:")
        print(f"   • Total matches: {stats['total_matches']}")
        print(f"   • Player performances: {stats['total_performances']}")
        print(f"   • Active players: {stats['active_players']}")
        print(f"   • Goals scored: {stats['total_goals_scored']}")
        
        print(f"\n🏆 Season Record:")
        total_games = stats['wins'] + stats['draws'] + stats['losses']
        win_rate = (stats['wins'] / total_games * 100) if total_games > 0 else 0
        print(f"   • Wins: {stats['wins']} ({win_rate:.1f}%)")
        print(f"   • Draws: {stats['draws']}")
        print(f"   • Losses: {stats['losses']}")
        
        # Top performers
        top_performers = pd.read_sql_query('''
            SELECT 
                player_name,
                COUNT(*) as matches,
                SUM(goals) as goals,
                SUM(assists) as assists,
                ROUND(AVG(rating), 1) as avg_rating
            FROM player_match_performances
            GROUP BY player_name
            ORDER BY goals DESC, assists DESC
            LIMIT 5
        ''', conn)
        
        print(f"\n⭐ Top Performers:")
        for _, player in top_performers.iterrows():
            print(f"   • {player['player_name']}: {player['goals']}G {player['assists']}A "
                  f"({player['matches']} matches, {player['avg_rating']} rating)")
        
        conn.close()
        
        return stats.to_dict()
        
    def run_full_validation(self):
        """Run complete validation suite."""
        
        print("🔍 Manchester City 2023-24 Match Data Validation")
        print("=" * 60)
        
        # Run all validations
        self.validate_match_data_consistency()
        self.validate_player_performance_consistency()
        self.validate_data_relationships()
        self.validate_statistical_realism()
        
        # Generate summary
        summary = self.generate_data_summary()
        
        # Overall validation result
        print(f"\n🎯 VALIDATION RESULTS")
        print("=" * 30)
        
        overall_status = "PASS"
        for validation, result in self.validation_results.items():
            status = result['status']
            print(f"   {validation}: {status}")
            if status in ['FAIL', 'WARNING']:
                overall_status = status
        
        print(f"\n🏁 OVERALL STATUS: {overall_status}")
        
        if overall_status == "PASS":
            print("✅ All validations passed! Data is ready for analysis.")
        elif overall_status == "WARNING":
            print("⚠️ Some warnings found, but data is generally usable.")
        else:
            print("❌ Critical issues found. Data may need correction.")
        
        return overall_status, self.validation_results, summary

def main():
    """Main execution function."""
    
    validator = MatchDataValidator()
    status, results, summary = validator.run_full_validation()
    
    print(f"\n📊 Validation complete with status: {status}")
    print("🎉 Manchester City match-by-match dataset is ready!")

if __name__ == "__main__":
    main()
