#!/usr/bin/env python3
"""
Comparative League Analysis for Soccer Intelligence
Establishes league benchmarks and analyzes Manchester City's distinctive characteristics
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComparativeLeagueAnalysis:
    """
    Comparative analysis across the entire league to establish benchmarks
    and identify Manchester City's unique performance characteristics
    """
    
    def __init__(self):
        """Initialize comparative analysis framework."""
        self.league_benchmarks = {}
        self.man_city_characteristics = {}
        self.performance_clusters = {}
        
    def generate_league_dataset(self) -> pd.DataFrame:
        """
        Generate comprehensive league dataset for comparative analysis.
        In production, this would pull from all Premier League teams.
        """
        logger.info("🏆 Generating comprehensive league dataset...")
        
        np.random.seed(42)
        
        # Premier League teams
        teams = [
            'Manchester City', 'Arsenal', 'Liverpool', 'Chelsea', 'Tottenham',
            'Newcastle', 'Brighton', 'Aston Villa', 'West Ham', 'Crystal Palace',
            'Bournemouth', 'Fulham', 'Wolves', 'Everton', 'Brentford',
            'Nottingham Forest', 'Sheffield United', 'Burnley', 'Luton Town', 'Manchester United'
        ]
        
        league_players = []
        player_id = 1
        
        for team in teams:
            # Generate squad for each team
            team_quality_modifier = self.get_team_quality_modifier(team)
            
            # Goalkeepers (2-3 per team)
            for i in range(np.random.randint(2, 4)):
                league_players.append(self.generate_player_data(
                    player_id, f"{team}_GK_{i+1}", 'Goalkeeper', team, team_quality_modifier
                ))
                player_id += 1
            
            # Defenders (6-8 per team)
            for i in range(np.random.randint(6, 9)):
                league_players.append(self.generate_player_data(
                    player_id, f"{team}_DEF_{i+1}", 'Defender', team, team_quality_modifier
                ))
                player_id += 1
            
            # Midfielders (6-10 per team)
            for i in range(np.random.randint(6, 11)):
                league_players.append(self.generate_player_data(
                    player_id, f"{team}_MID_{i+1}", 'Midfielder', team, team_quality_modifier
                ))
                player_id += 1
            
            # Attackers (4-6 per team)
            for i in range(np.random.randint(4, 7)):
                league_players.append(self.generate_player_data(
                    player_id, f"{team}_ATT_{i+1}", 'Attacker', team, team_quality_modifier
                ))
                player_id += 1
        
        df = pd.DataFrame(league_players)
        logger.info(f"✅ Generated league dataset with {len(df)} players from {len(teams)} teams")
        return df
    
    def get_team_quality_modifier(self, team: str) -> float:
        """Get team quality modifier for realistic performance distribution."""
        quality_tiers = {
            # Top 6
            'Manchester City': 1.3,
            'Arsenal': 1.25,
            'Liverpool': 1.25,
            'Chelsea': 1.2,
            'Tottenham': 1.15,
            'Newcastle': 1.1,
            
            # Mid-table
            'Brighton': 1.0,
            'Aston Villa': 1.0,
            'West Ham': 0.95,
            'Crystal Palace': 0.9,
            'Bournemouth': 0.9,
            'Fulham': 0.9,
            'Wolves': 0.85,
            'Everton': 0.85,
            'Brentford': 0.85,
            'Manchester United': 1.05,
            
            # Bottom teams
            'Nottingham Forest': 0.8,
            'Sheffield United': 0.75,
            'Burnley': 0.75,
            'Luton Town': 0.7
        }
        return quality_tiers.get(team, 0.85)
    
    def generate_player_data(self, player_id: int, name: str, position: str, team: str, quality_modifier: float) -> Dict:
        """Generate realistic player data based on position and team quality."""
        
        base_stats = {
            'player_id': player_id,
            'player_name': name,
            'position': position,
            'team': team,
            'matches_played': np.random.randint(15, 40),
            'minutes_played': np.random.randint(1000, 3500)
        }
        
        # Position-specific stat generation with team quality modifier
        if position == 'Goalkeeper':
            base_stats.update({
                'goals': 0,
                'assists': np.random.randint(0, 2),
                'saves': int(np.random.normal(80, 20) * quality_modifier),
                'clean_sheets': int(np.random.normal(8, 4) * quality_modifier),
                'goals_conceded': int(np.random.normal(25, 10) / quality_modifier),
                'pass_accuracy': np.random.normal(75, 10) * quality_modifier,
                'average_rating': np.random.normal(6.5, 0.8) * quality_modifier
            })
        
        elif position == 'Defender':
            base_stats.update({
                'goals': int(np.random.poisson(2) * quality_modifier),
                'assists': int(np.random.poisson(3) * quality_modifier),
                'tackles_total': int(np.random.normal(60, 20) * quality_modifier),
                'tackles_won': int(np.random.normal(40, 15) * quality_modifier),
                'interceptions': int(np.random.normal(45, 15) * quality_modifier),
                'clearances': int(np.random.normal(80, 25) * quality_modifier),
                'pass_accuracy': np.random.normal(88, 5) * quality_modifier,
                'average_rating': np.random.normal(6.8, 0.7) * quality_modifier
            })
        
        elif position == 'Midfielder':
            base_stats.update({
                'goals': int(np.random.poisson(5) * quality_modifier),
                'assists': int(np.random.poisson(7) * quality_modifier),
                'key_passes': int(np.random.normal(40, 15) * quality_modifier),
                'passes_total': int(np.random.normal(1800, 500) * quality_modifier),
                'pass_accuracy': np.random.normal(85, 8) * quality_modifier,
                'tackles_total': int(np.random.normal(45, 15) * quality_modifier),
                'distance_covered': np.random.normal(300, 50) * quality_modifier,
                'average_rating': np.random.normal(7.0, 0.8) * quality_modifier
            })
        
        else:  # Attacker
            base_stats.update({
                'goals': int(np.random.poisson(12) * quality_modifier),
                'assists': int(np.random.poisson(6) * quality_modifier),
                'shots_total': int(np.random.normal(80, 25) * quality_modifier),
                'shots_on_target': int(np.random.normal(35, 12) * quality_modifier),
                'key_passes': int(np.random.normal(30, 10) * quality_modifier),
                'dribbles_successful': int(np.random.normal(40, 15) * quality_modifier),
                'pass_accuracy': np.random.normal(78, 10) * quality_modifier,
                'average_rating': np.random.normal(7.2, 0.9) * quality_modifier
            })
        
        # Ensure realistic bounds
        for key, value in base_stats.items():
            if isinstance(value, (int, float)) and key != 'player_id':
                if key == 'pass_accuracy' or key == 'average_rating':
                    base_stats[key] = max(0, min(100 if 'accuracy' in key else 10, value))
                else:
                    base_stats[key] = max(0, value)
        
        return base_stats
    
    def establish_league_benchmarks(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Establish league benchmarks for each position.
        Calculate percentiles and statistical measures across the league.
        """
        logger.info("📊 Establishing league benchmarks by position...")
        
        benchmarks = {}
        
        for position in df['position'].unique():
            position_data = df[df['position'] == position]
            
            # Calculate key statistics for this position
            if position == 'Goalkeeper':
                metrics = ['saves', 'clean_sheets', 'goals_conceded', 'pass_accuracy', 'average_rating']
            elif position == 'Defender':
                metrics = ['goals', 'assists', 'tackles_total', 'interceptions', 'clearances', 'pass_accuracy', 'average_rating']
            elif position == 'Midfielder':
                metrics = ['goals', 'assists', 'key_passes', 'passes_total', 'pass_accuracy', 'tackles_total', 'average_rating']
            else:  # Attacker
                metrics = ['goals', 'assists', 'shots_total', 'shots_on_target', 'key_passes', 'dribbles_successful', 'average_rating']
            
            position_benchmarks = {}
            
            for metric in metrics:
                if metric in position_data.columns:
                    position_benchmarks[metric] = {
                        'mean': position_data[metric].mean(),
                        'median': position_data[metric].median(),
                        'std': position_data[metric].std(),
                        'p25': position_data[metric].quantile(0.25),
                        'p75': position_data[metric].quantile(0.75),
                        'p90': position_data[metric].quantile(0.90),
                        'p95': position_data[metric].quantile(0.95),
                        'min': position_data[metric].min(),
                        'max': position_data[metric].max()
                    }
            
            benchmarks[position] = position_benchmarks
        
        self.league_benchmarks = benchmarks
        logger.info("✅ League benchmarks established")
        return benchmarks
    
    def analyze_manchester_city_characteristics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze Manchester City's unique performance characteristics
        compared to league averages and identify distinctive patterns.
        """
        logger.info("🔵 Analyzing Manchester City's distinctive characteristics...")
        
        man_city_data = df[df['team'] == 'Manchester City']
        league_data = df[df['team'] != 'Manchester City']
        
        characteristics = {
            'team_comparison': {},
            'position_analysis': {},
            'unique_patterns': [],
            'competitive_advantages': []
        }
        
        # Overall team comparison
        for metric in ['goals', 'assists', 'pass_accuracy', 'average_rating']:
            if metric in man_city_data.columns and metric in league_data.columns:
                man_city_avg = man_city_data[metric].mean()
                league_avg = league_data[metric].mean()
                difference = ((man_city_avg - league_avg) / league_avg) * 100
                
                characteristics['team_comparison'][metric] = {
                    'man_city_avg': man_city_avg,
                    'league_avg': league_avg,
                    'difference_percent': difference,
                    'advantage': difference > 5  # 5% threshold for significant advantage
                }
        
        # Position-specific analysis
        for position in man_city_data['position'].unique():
            man_city_position = man_city_data[man_city_data['position'] == position]
            league_position = league_data[league_data['position'] == position]
            
            position_comparison = {}
            
            # Get relevant metrics for position
            if position == 'Goalkeeper':
                metrics = ['saves', 'clean_sheets', 'pass_accuracy']
            elif position == 'Defender':
                metrics = ['tackles_total', 'interceptions', 'pass_accuracy']
            elif position == 'Midfielder':
                metrics = ['key_passes', 'pass_accuracy', 'assists']
            else:  # Attacker
                metrics = ['goals', 'shots_on_target', 'dribbles_successful']
            
            for metric in metrics:
                if metric in man_city_position.columns and metric in league_position.columns:
                    man_city_avg = man_city_position[metric].mean()
                    league_avg = league_position[metric].mean()
                    
                    if league_avg > 0:
                        difference = ((man_city_avg - league_avg) / league_avg) * 100
                        position_comparison[metric] = {
                            'man_city_avg': man_city_avg,
                            'league_avg': league_avg,
                            'difference_percent': difference
                        }
            
            characteristics['position_analysis'][position] = position_comparison
        
        # Identify unique patterns
        characteristics['unique_patterns'] = self.identify_unique_patterns(man_city_data, league_data)
        
        # Competitive advantages
        characteristics['competitive_advantages'] = self.identify_competitive_advantages(characteristics)
        
        self.man_city_characteristics = characteristics
        logger.info("✅ Manchester City characteristics analyzed")
        return characteristics
    
    def identify_unique_patterns(self, man_city_data: pd.DataFrame, league_data: pd.DataFrame) -> List[str]:
        """Identify unique performance patterns for Manchester City."""
        patterns = []
        
        # High pass accuracy across all positions
        man_city_pass_acc = man_city_data['pass_accuracy'].mean()
        league_pass_acc = league_data['pass_accuracy'].mean()
        
        if man_city_pass_acc > league_pass_acc * 1.05:
            patterns.append(f"Superior passing accuracy: {man_city_pass_acc:.1f}% vs league {league_pass_acc:.1f}%")
        
        # Goal distribution analysis
        man_city_goals = man_city_data.groupby('position')['goals'].sum()
        league_goals = league_data.groupby('position')['goals'].mean()
        
        if 'Midfielder' in man_city_goals.index and man_city_goals['Midfielder'] > league_goals.get('Midfielder', 0) * 1.2:
            patterns.append("High goal contribution from midfielders - tactical advantage")
        
        # Defensive solidity
        if 'Defender' in man_city_data['position'].values:
            man_city_def_rating = man_city_data[man_city_data['position'] == 'Defender']['average_rating'].mean()
            league_def_rating = league_data[league_data['position'] == 'Defender']['average_rating'].mean()
            
            if man_city_def_rating > league_def_rating * 1.1:
                patterns.append("Exceptional defensive performance ratings")
        
        return patterns
    
    def identify_competitive_advantages(self, characteristics: Dict[str, Any]) -> List[str]:
        """Identify key competitive advantages based on analysis."""
        advantages = []
        
        team_comparison = characteristics['team_comparison']
        
        # Check for significant advantages
        for metric, data in team_comparison.items():
            if data.get('advantage', False):
                advantage_text = f"{metric.replace('_', ' ').title()}: {data['difference_percent']:.1f}% above league average"
                advantages.append(advantage_text)
        
        # Position-specific advantages
        position_analysis = characteristics['position_analysis']
        for position, metrics in position_analysis.items():
            strong_metrics = [metric for metric, data in metrics.items() 
                            if data['difference_percent'] > 10]
            
            if strong_metrics:
                advantages.append(f"{position}s excel in: {', '.join(strong_metrics)}")
        
        return advantages
    
    def generate_comparative_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive comparative analysis report."""
        logger.info("📋 Generating comprehensive comparative report...")
        
        # Establish benchmarks
        benchmarks = self.establish_league_benchmarks(df)
        
        # Analyze Manchester City
        man_city_analysis = self.analyze_manchester_city_characteristics(df)
        
        # Performance clustering
        clusters = self.perform_performance_clustering(df)
        
        report = {
            'league_benchmarks': benchmarks,
            'manchester_city_analysis': man_city_analysis,
            'performance_clusters': clusters,
            'summary_insights': self.generate_summary_insights(df, man_city_analysis)
        }
        
        return report
    
    def perform_performance_clustering(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform clustering analysis to identify performance groups."""
        logger.info("🎯 Performing performance clustering analysis...")
        
        # Select features for clustering
        features = ['goals', 'assists', 'pass_accuracy', 'average_rating']
        
        # Prepare data
        cluster_data = df[features].fillna(0)
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(cluster_data)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=4, random_state=42)
        clusters = kmeans.fit_predict(scaled_data)
        
        df_clustered = df.copy()
        df_clustered['performance_cluster'] = clusters
        
        # Analyze clusters
        cluster_analysis = {}
        for cluster_id in range(4):
            cluster_players = df_clustered[df_clustered['performance_cluster'] == cluster_id]
            
            cluster_analysis[f'cluster_{cluster_id}'] = {
                'size': len(cluster_players),
                'avg_goals': cluster_players['goals'].mean(),
                'avg_assists': cluster_players['assists'].mean(),
                'avg_rating': cluster_players['average_rating'].mean(),
                'dominant_positions': cluster_players['position'].value_counts().to_dict(),
                'teams': cluster_players['team'].value_counts().head(3).to_dict()
            }
        
        # Manchester City cluster distribution
        man_city_clusters = df_clustered[df_clustered['team'] == 'Manchester City']['performance_cluster'].value_counts()
        
        return {
            'cluster_analysis': cluster_analysis,
            'man_city_distribution': man_city_clusters.to_dict(),
            'total_clusters': 4
        }
    
    def generate_summary_insights(self, df: pd.DataFrame, man_city_analysis: Dict[str, Any]) -> List[str]:
        """Generate key summary insights from the analysis."""
        insights = []
        
        # League position
        team_ratings = df.groupby('team')['average_rating'].mean().sort_values(ascending=False)
        man_city_rank = list(team_ratings.index).index('Manchester City') + 1
        insights.append(f"Manchester City ranks #{man_city_rank} in average player ratings league-wide")
        
        # Key advantages
        advantages = man_city_analysis['competitive_advantages']
        if advantages:
            insights.append(f"Primary competitive advantages: {', '.join(advantages[:2])}")
        
        # Unique patterns
        patterns = man_city_analysis['unique_patterns']
        if patterns:
            insights.append(f"Distinctive characteristic: {patterns[0]}")
        
        return insights

def main():
    """Main execution function for comparative league analysis."""
    
    # Initialize analysis
    analysis = ComparativeLeagueAnalysis()
    
    # Generate league dataset
    league_data = analysis.generate_league_dataset()
    
    # Generate comprehensive report
    report = analysis.generate_comparative_report(league_data)
    
    # Display results
    print("\n" + "="*100)
    print("🏆 COMPARATIVE LEAGUE ANALYSIS REPORT")
    print("="*100)
    
    # League overview
    print(f"\n📊 LEAGUE OVERVIEW:")
    print(f"  • Total players analyzed: {len(league_data)}")
    print(f"  • Teams covered: {league_data['team'].nunique()}")
    print(f"  • Positions analyzed: {', '.join(league_data['position'].unique())}")
    
    # Manchester City analysis
    man_city_analysis = report['manchester_city_analysis']
    print(f"\n🔵 MANCHESTER CITY DISTINCTIVE CHARACTERISTICS:")
    
    for pattern in man_city_analysis['unique_patterns']:
        print(f"  • {pattern}")
    
    print(f"\n🎯 COMPETITIVE ADVANTAGES:")
    for advantage in man_city_analysis['competitive_advantages']:
        print(f"  • {advantage}")
    
    # Performance clusters
    clusters = report['performance_clusters']
    print(f"\n🎪 PERFORMANCE CLUSTERING:")
    print(f"  • Total performance clusters identified: {clusters['total_clusters']}")
    print(f"  • Manchester City cluster distribution: {clusters['man_city_distribution']}")
    
    # Summary insights
    print(f"\n💡 KEY INSIGHTS:")
    for insight in report['summary_insights']:
        print(f"  • {insight}")
    
    print("\n" + "="*100)
    print("🎉 Comparative League Analysis completed successfully!")
    print("="*100)
    
    return report

if __name__ == "__main__":
    comparative_report = main()
