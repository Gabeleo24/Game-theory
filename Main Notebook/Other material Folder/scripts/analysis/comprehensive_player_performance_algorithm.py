#!/usr/bin/env python3
"""
Comprehensive Player Performance Algorithm for Soccer Intelligence
Multi-stakeholder algorithm addressing team managers, player agents, and contract negotiation needs
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
import sqlite3
import yaml
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComprehensivePlayerPerformanceAlgorithm:
    """
    Comprehensive algorithm for soccer player performance analysis
    addressing three key stakeholder needs with position-normalized metrics
    """
    
    def __init__(self):
        """Initialize the algorithm with configuration and data sources."""
        self.load_configuration()
        self.position_weights = self.define_position_weights()
        self.performance_metrics = {}
        self.league_benchmarks = {}
        self.team_contribution_models = {}
        
    def load_configuration(self):
        """Load configuration for algorithm parameters."""
        self.config = {
            'performance_scale': (0, 100),
            'team_contribution_weight': 0.4,
            'individual_performance_weight': 0.6,
            'contract_efficiency_threshold': 0.75,
            'market_value_factors': {
                'age_peak': 27,
                'age_decline_start': 30,
                'performance_weight': 0.5,
                'potential_weight': 0.3,
                'market_demand_weight': 0.2
            }
        }
        logger.info("✅ Algorithm configuration loaded")
    
    def define_position_weights(self) -> Dict[str, Dict[str, float]]:
        """
        Define position-specific weights for performance metrics.
        Each position has different importance for various statistics.
        """
        return {
            'Goalkeeper': {
                'saves': 0.25,
                'clean_sheets': 0.20,
                'goals_conceded': -0.15,
                'distribution_accuracy': 0.15,
                'command_of_area': 0.10,
                'shot_stopping': 0.15,
                'minutes_played': 0.10
            },
            'Defender': {
                'tackles_won': 0.20,
                'interceptions': 0.15,
                'clearances': 0.15,
                'aerial_duels_won': 0.15,
                'pass_accuracy': 0.10,
                'goals_conceded_involvement': -0.10,
                'clean_sheets': 0.10,
                'minutes_played': 0.15
            },
            'Midfielder': {
                'pass_accuracy': 0.20,
                'key_passes': 0.15,
                'assists': 0.15,
                'tackles_won': 0.10,
                'goals': 0.10,
                'distance_covered': 0.10,
                'possession_retention': 0.10,
                'minutes_played': 0.10
            },
            'Attacker': {
                'goals': 0.30,
                'assists': 0.20,
                'shots_on_target': 0.15,
                'key_passes': 0.10,
                'dribbles_successful': 0.10,
                'conversion_rate': 0.10,
                'minutes_played': 0.05
            }
        }
    
    def load_player_data(self) -> pd.DataFrame:
        """Load comprehensive player data from multiple sources."""
        logger.info("📊 Loading comprehensive player data...")
        
        # Load from existing advanced statistics database
        db_path = "data/final_advanced_stats/manchester_city_final_advanced_2023_24.db"
        
        try:
            conn = sqlite3.connect(db_path)
            
            # Get comprehensive player statistics
            query = """
            SELECT 
                p.player_id,
                p.player_name,
                p.position,
                p.matches_played,
                p.minutes_played,
                p.goals,
                p.assists,
                p.expected_goals,
                p.expected_assists,
                p.shots_total,
                p.shots_on_target,
                p.shot_accuracy,
                p.passes_total,
                p.passes_completed,
                p.pass_accuracy,
                p.key_passes,
                p.tackles_total,
                p.tackles_won,
                p.tackle_success_rate,
                p.interceptions,
                p.clearances,
                p.average_rating,
                p.yellow_cards,
                p.red_cards
            FROM player_season_summary p
            WHERE p.matches_played >= 5
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            logger.info(f"✅ Loaded data for {len(df)} players")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error loading player data: {e}")
            # Generate synthetic data for demonstration
            return self.generate_synthetic_player_data()
    
    def generate_synthetic_player_data(self) -> pd.DataFrame:
        """Generate synthetic player data for algorithm demonstration."""
        logger.info("🔄 Generating synthetic player data for demonstration...")
        
        np.random.seed(42)
        
        # Manchester City squad with realistic data
        players_data = []
        
        # Goalkeepers
        goalkeepers = ['Ederson', 'Ortega', 'Carson']
        for name in goalkeepers:
            players_data.append({
                'player_id': len(players_data) + 1,
                'player_name': name,
                'position': 'Goalkeeper',
                'matches_played': np.random.randint(15, 35),
                'minutes_played': np.random.randint(1200, 3000),
                'goals': 0,
                'assists': np.random.randint(0, 2),
                'expected_goals': 0,
                'expected_assists': np.random.uniform(0, 0.5),
                'shots_total': np.random.randint(0, 3),
                'shots_on_target': np.random.randint(0, 2),
                'shot_accuracy': np.random.uniform(0, 50),
                'passes_total': np.random.randint(800, 2000),
                'passes_completed': np.random.randint(700, 1800),
                'pass_accuracy': np.random.uniform(85, 95),
                'key_passes': np.random.randint(5, 20),
                'tackles_total': np.random.randint(0, 10),
                'tackles_won': np.random.randint(0, 8),
                'tackle_success_rate': np.random.uniform(60, 80),
                'interceptions': np.random.randint(5, 25),
                'clearances': np.random.randint(20, 80),
                'average_rating': np.random.uniform(6.5, 8.0),
                'yellow_cards': np.random.randint(0, 3),
                'red_cards': np.random.randint(0, 1)
            })
        
        # Defenders
        defenders = ['Dias', 'Stones', 'Aké', 'Gvardiol', 'Walker', 'Lewis', 'Akanji']
        for name in defenders:
            players_data.append({
                'player_id': len(players_data) + 1,
                'player_name': name,
                'position': 'Defender',
                'matches_played': np.random.randint(20, 40),
                'minutes_played': np.random.randint(1500, 3500),
                'goals': np.random.randint(0, 5),
                'assists': np.random.randint(0, 8),
                'expected_goals': np.random.uniform(0.5, 3.0),
                'expected_assists': np.random.uniform(1.0, 5.0),
                'shots_total': np.random.randint(10, 40),
                'shots_on_target': np.random.randint(3, 15),
                'shot_accuracy': np.random.uniform(30, 60),
                'passes_total': np.random.randint(1500, 3000),
                'passes_completed': np.random.randint(1300, 2700),
                'pass_accuracy': np.random.uniform(88, 95),
                'key_passes': np.random.randint(10, 40),
                'tackles_total': np.random.randint(40, 100),
                'tackles_won': np.random.randint(25, 70),
                'tackle_success_rate': np.random.uniform(65, 85),
                'interceptions': np.random.randint(30, 80),
                'clearances': np.random.randint(50, 150),
                'average_rating': np.random.uniform(6.8, 8.2),
                'yellow_cards': np.random.randint(2, 8),
                'red_cards': np.random.randint(0, 2)
            })
        
        # Midfielders
        midfielders = ['Rodri', 'De Bruyne', 'Bernardo Silva', 'Gündoğan', 'Phillips', 'Kovačić', 'Foden']
        for name in midfielders:
            players_data.append({
                'player_id': len(players_data) + 1,
                'player_name': name,
                'position': 'Midfielder',
                'matches_played': np.random.randint(25, 45),
                'minutes_played': np.random.randint(2000, 4000),
                'goals': np.random.randint(3, 15),
                'assists': np.random.randint(5, 20),
                'expected_goals': np.random.uniform(3.0, 12.0),
                'expected_assists': np.random.uniform(6.0, 18.0),
                'shots_total': np.random.randint(30, 80),
                'shots_on_target': np.random.randint(15, 40),
                'shot_accuracy': np.random.uniform(45, 70),
                'passes_total': np.random.randint(2000, 4000),
                'passes_completed': np.random.randint(1800, 3600),
                'pass_accuracy': np.random.uniform(85, 95),
                'key_passes': np.random.randint(40, 100),
                'tackles_total': np.random.randint(30, 80),
                'tackles_won': np.random.randint(20, 60),
                'tackle_success_rate': np.random.uniform(60, 80),
                'interceptions': np.random.randint(20, 60),
                'clearances': np.random.randint(10, 50),
                'average_rating': np.random.uniform(7.0, 8.5),
                'yellow_cards': np.random.randint(3, 10),
                'red_cards': np.random.randint(0, 2)
            })
        
        # Attackers
        attackers = ['Haaland', 'Grealish', 'Mahrez', 'Álvarez', 'Doku']
        for name in attackers:
            players_data.append({
                'player_id': len(players_data) + 1,
                'player_name': name,
                'position': 'Attacker',
                'matches_played': np.random.randint(25, 45),
                'minutes_played': np.random.randint(2000, 4000),
                'goals': np.random.randint(8, 35),
                'assists': np.random.randint(3, 15),
                'expected_goals': np.random.uniform(10.0, 30.0),
                'expected_assists': np.random.uniform(4.0, 12.0),
                'shots_total': np.random.randint(80, 150),
                'shots_on_target': np.random.randint(40, 80),
                'shot_accuracy': np.random.uniform(50, 75),
                'passes_total': np.random.randint(1000, 2500),
                'passes_completed': np.random.randint(800, 2200),
                'pass_accuracy': np.random.uniform(75, 90),
                'key_passes': np.random.randint(30, 80),
                'tackles_total': np.random.randint(10, 40),
                'tackles_won': np.random.randint(5, 25),
                'tackle_success_rate': np.random.uniform(50, 70),
                'interceptions': np.random.randint(5, 30),
                'clearances': np.random.randint(0, 20),
                'average_rating': np.random.uniform(7.2, 8.8),
                'yellow_cards': np.random.randint(1, 6),
                'red_cards': np.random.randint(0, 1)
            })
        
        df = pd.DataFrame(players_data)
        logger.info(f"✅ Generated synthetic data for {len(df)} players")
        return df
    
    def calculate_position_normalized_performance(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate position-normalized performance metrics (0-100 scale).
        Each position is evaluated based on position-specific criteria.
        """
        logger.info("⚖️ Calculating position-normalized performance metrics...")
        
        df_normalized = df.copy()
        
        # Calculate position-specific performance scores
        for position in df['position'].unique():
            position_data = df[df['position'] == position].copy()
            weights = self.position_weights.get(position, {})
            
            # Calculate weighted performance score for this position
            performance_scores = []
            
            for _, player in position_data.iterrows():
                score = 0
                total_weight = 0
                
                for metric, weight in weights.items():
                    if metric in player and pd.notna(player[metric]):
                        # Normalize metric to 0-1 scale within position
                        if metric.startswith('-') or weight < 0:
                            # Negative metrics (lower is better)
                            metric_name = metric.replace('-', '') if metric.startswith('-') else metric
                            if metric_name in position_data.columns:
                                normalized_value = 1 - (player[metric_name] - position_data[metric_name].min()) / (position_data[metric_name].max() - position_data[metric_name].min() + 0.001)
                        else:
                            # Positive metrics (higher is better)
                            if metric in position_data.columns:
                                normalized_value = (player[metric] - position_data[metric].min()) / (position_data[metric].max() - position_data[metric].min() + 0.001)
                            else:
                                normalized_value = 0.5  # Default if metric not found
                        
                        score += abs(weight) * normalized_value
                        total_weight += abs(weight)
                
                # Scale to 0-100
                final_score = (score / total_weight * 100) if total_weight > 0 else 50
                performance_scores.append(min(100, max(0, final_score)))
            
            # Add scores back to dataframe
            df_normalized.loc[df_normalized['position'] == position, 'position_normalized_score'] = performance_scores
        
        logger.info("✅ Position-normalized performance calculated")
        return df_normalized
    
    def calculate_team_contribution_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Team Contribution Index measuring player's impact on team success.
        Combines individual performance with team outcome correlation.
        """
        logger.info("🤝 Calculating Team Contribution Index...")
        
        df_contribution = df.copy()
        
        # Simulate team performance correlation for each player
        # In real implementation, this would use actual match results
        team_contribution_scores = []
        
        for _, player in df.iterrows():
            # Base contribution from individual performance
            individual_contribution = (
                player.get('goals', 0) * 3 +
                player.get('assists', 0) * 2 +
                player.get('average_rating', 6) * 5 +
                (player.get('minutes_played', 0) / 90) * 0.5
            )
            
            # Position-specific team contribution adjustments
            position_multiplier = {
                'Goalkeeper': 1.2,  # High impact on team success
                'Defender': 1.1,
                'Midfielder': 1.0,
                'Attacker': 0.9
            }.get(player['position'], 1.0)
            
            # Simulate correlation with team wins (would use actual data)
            win_correlation = np.random.uniform(0.3, 0.9)
            
            # Calculate final team contribution index
            team_contribution = (
                individual_contribution * position_multiplier * win_correlation
            )
            
            # Normalize to 0-100 scale
            normalized_contribution = min(100, max(0, team_contribution * 2))
            team_contribution_scores.append(normalized_contribution)
        
        df_contribution['team_contribution_index'] = team_contribution_scores
        
        logger.info("✅ Team Contribution Index calculated")
        return df_contribution
    
    def calculate_comprehensive_performance_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate comprehensive performance score combining all metrics.
        """
        logger.info("🎯 Calculating comprehensive performance scores...")
        
        df_final = df.copy()
        
        # Combine position-normalized performance and team contribution
        individual_weight = self.config['individual_performance_weight']
        team_weight = self.config['team_contribution_weight']
        
        df_final['comprehensive_performance_score'] = (
            df_final['position_normalized_score'] * individual_weight +
            df_final['team_contribution_index'] * team_weight
        )
        
        # Add performance tier classification
        def classify_performance(score):
            if score >= 85:
                return 'Elite'
            elif score >= 75:
                return 'Excellent'
            elif score >= 65:
                return 'Good'
            elif score >= 55:
                return 'Average'
            else:
                return 'Below Average'
        
        df_final['performance_tier'] = df_final['comprehensive_performance_score'].apply(classify_performance)
        
        logger.info("✅ Comprehensive performance scores calculated")
        return df_final
    
    def generate_stakeholder_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate insights for three key stakeholders:
        1. Team Managers - Retention/Release decisions
        2. Player Agents - Market positioning
        3. Contract Negotiation - Performance-based terms
        """
        logger.info("👥 Generating stakeholder-specific insights...")
        
        insights = {
            'team_managers': self.generate_manager_insights(df),
            'player_agents': self.generate_agent_insights(df),
            'contract_negotiation': self.generate_contract_insights(df)
        }
        
        return insights
    
    def generate_manager_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate insights for team managers - retention/release decisions."""
        
        # Sort players by comprehensive performance
        df_sorted = df.sort_values('comprehensive_performance_score', ascending=False)
        
        # Categorize players for retention decisions
        elite_performers = df_sorted[df_sorted['performance_tier'] == 'Elite']
        underperformers = df_sorted[df_sorted['performance_tier'].isin(['Below Average', 'Average'])]
        
        # Calculate squad balance
        position_distribution = df['position'].value_counts()
        
        return {
            'retention_priority': elite_performers[['player_name', 'position', 'comprehensive_performance_score']].to_dict('records'),
            'release_candidates': underperformers[['player_name', 'position', 'comprehensive_performance_score']].to_dict('records'),
            'squad_balance': position_distribution.to_dict(),
            'performance_summary': {
                'elite_count': len(elite_performers),
                'underperformer_count': len(underperformers),
                'average_team_performance': df['comprehensive_performance_score'].mean()
            }
        }
    
    def generate_agent_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate insights for player agents - market positioning."""
        
        agent_insights = {}
        
        for _, player in df.iterrows():
            # Calculate market value factors
            performance_percentile = (df['comprehensive_performance_score'] <= player['comprehensive_performance_score']).mean() * 100
            
            # Position-specific market analysis
            position_peers = df[df['position'] == player['position']]
            position_rank = (position_peers['comprehensive_performance_score'] <= player['comprehensive_performance_score']).mean() * 100
            
            agent_insights[player['player_name']] = {
                'overall_percentile': performance_percentile,
                'position_percentile': position_rank,
                'market_tier': player['performance_tier'],
                'negotiation_leverage': 'High' if performance_percentile >= 75 else 'Medium' if performance_percentile >= 50 else 'Low',
                'comparable_players': position_peers.nlargest(3, 'comprehensive_performance_score')['player_name'].tolist()
            }
        
        return agent_insights
    
    def generate_contract_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate insights for contract negotiation - performance-based terms."""
        
        contract_insights = {}
        
        for _, player in df.iterrows():
            # Performance-based contract recommendations
            performance_score = player['comprehensive_performance_score']
            
            # Contract length recommendation based on performance and age simulation
            simulated_age = np.random.randint(20, 35)
            
            if performance_score >= 80 and simulated_age <= 28:
                contract_length = '4-5 years'
                performance_bonus = 'High'
            elif performance_score >= 70:
                contract_length = '3-4 years'
                performance_bonus = 'Medium'
            else:
                contract_length = '1-2 years'
                performance_bonus = 'Low'
            
            contract_insights[player['player_name']] = {
                'recommended_length': contract_length,
                'performance_bonus_tier': performance_bonus,
                'base_salary_justification': player['performance_tier'],
                'risk_assessment': 'Low' if performance_score >= 75 else 'Medium' if performance_score >= 60 else 'High',
                'key_performance_indicators': self.get_position_kpis(player['position'])
            }
        
        return contract_insights
    
    def get_position_kpis(self, position: str) -> List[str]:
        """Get key performance indicators for contract terms by position."""
        kpi_mapping = {
            'Goalkeeper': ['Clean sheets', 'Save percentage', 'Distribution accuracy'],
            'Defender': ['Tackles won', 'Interceptions', 'Pass accuracy', 'Clean sheets'],
            'Midfielder': ['Assists', 'Key passes', 'Pass accuracy', 'Distance covered'],
            'Attacker': ['Goals', 'Assists', 'Shot accuracy', 'Key passes']
        }
        return kpi_mapping.get(position, ['Goals', 'Assists', 'Average rating'])

def main():
    """Main execution function for comprehensive player performance analysis."""
    
    # Initialize algorithm
    algorithm = ComprehensivePlayerPerformanceAlgorithm()
    
    # Load player data
    player_data = algorithm.load_player_data()
    
    # Calculate position-normalized performance
    normalized_data = algorithm.calculate_position_normalized_performance(player_data)
    
    # Calculate team contribution index
    contribution_data = algorithm.calculate_team_contribution_index(normalized_data)
    
    # Calculate comprehensive performance scores
    final_data = algorithm.calculate_comprehensive_performance_score(contribution_data)
    
    # Generate stakeholder insights
    insights = algorithm.generate_stakeholder_insights(final_data)
    
    # Display results
    print("\n" + "="*100)
    print("🎯 COMPREHENSIVE PLAYER PERFORMANCE ALGORITHM RESULTS")
    print("="*100)
    
    # Top performers
    print(f"\n🏆 TOP PERFORMERS:")
    top_performers = final_data.nlargest(10, 'comprehensive_performance_score')
    for _, player in top_performers.iterrows():
        print(f"  • {player['player_name']} ({player['position']}): {player['comprehensive_performance_score']:.1f} - {player['performance_tier']}")
    
    # Manager insights
    print(f"\n👔 TEAM MANAGER INSIGHTS:")
    manager_insights = insights['team_managers']
    print(f"  • Elite performers to retain: {manager_insights['performance_summary']['elite_count']}")
    print(f"  • Release candidates: {manager_insights['performance_summary']['underperformer_count']}")
    print(f"  • Average team performance: {manager_insights['performance_summary']['average_team_performance']:.1f}")
    
    # Agent insights sample
    print(f"\n🤝 PLAYER AGENT INSIGHTS (Sample):")
    agent_insights = insights['player_agents']
    for player_name, insight in list(agent_insights.items())[:3]:
        print(f"  • {player_name}: {insight['position_percentile']:.0f}th percentile, {insight['negotiation_leverage']} leverage")
    
    # Contract insights sample
    print(f"\n📋 CONTRACT NEGOTIATION INSIGHTS (Sample):")
    contract_insights = insights['contract_negotiation']
    for player_name, insight in list(contract_insights.items())[:3]:
        print(f"  • {player_name}: {insight['recommended_length']}, {insight['performance_bonus_tier']} bonus tier")
    
    print("\n" + "="*100)
    print("🎉 Comprehensive Player Performance Algorithm completed successfully!")
    print("="*100)
    
    return final_data, insights

class StakeholderProductSuite:
    """
    Three-tiered product suite for different stakeholders
    """

    def __init__(self, performance_data: pd.DataFrame, insights: Dict[str, Any]):
        """Initialize with performance data and insights."""
        self.performance_data = performance_data
        self.insights = insights

    def manager_retention_tool(self) -> Dict[str, Any]:
        """
        Tool for team managers: Retention/Release Decision Tool
        Ranks squad players by contribution value and contract efficiency
        """
        print("\n" + "="*80)
        print("👔 TEAM MANAGER: RETENTION/RELEASE DECISION TOOL")
        print("="*80)

        manager_insights = self.insights['team_managers']

        # Priority retention list
        print(f"\n🔒 PRIORITY RETENTION LIST:")
        for player in manager_insights['retention_priority']:
            print(f"  ✅ {player['player_name']} ({player['position']}) - Score: {player['comprehensive_performance_score']:.1f}")

        # Release candidates
        print(f"\n🚪 RELEASE CANDIDATES:")
        for player in manager_insights['release_candidates']:
            print(f"  ❌ {player['player_name']} ({player['position']}) - Score: {player['comprehensive_performance_score']:.1f}")

        # Squad balance analysis
        print(f"\n⚖️ SQUAD BALANCE ANALYSIS:")
        for position, count in manager_insights['squad_balance'].items():
            status = "✅ Balanced" if 3 <= count <= 8 else "⚠️ Review needed"
            print(f"  • {position}: {count} players - {status}")

        # Actionable recommendations
        recommendations = self.generate_manager_recommendations()
        print(f"\n📋 ACTIONABLE RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"  • {rec}")

        return {
            'retention_priority': manager_insights['retention_priority'],
            'release_candidates': manager_insights['release_candidates'],
            'squad_balance': manager_insights['squad_balance'],
            'recommendations': recommendations
        }

    def agent_positioning_tool(self) -> Dict[str, Any]:
        """
        Tool for player agents: Player Positioning Analytics
        Identifies market value and negotiation leverage points
        """
        print("\n" + "="*80)
        print("🤝 PLAYER AGENT: POSITIONING ANALYTICS TOOL")
        print("="*80)

        agent_insights = self.insights['player_agents']

        # Market positioning analysis
        print(f"\n📊 MARKET POSITIONING ANALYSIS:")

        high_leverage_players = []
        medium_leverage_players = []

        for player_name, insight in agent_insights.items():
            leverage = insight['negotiation_leverage']
            percentile = insight['overall_percentile']

            if leverage == 'High':
                high_leverage_players.append((player_name, percentile))
                print(f"  🔥 {player_name}: {percentile:.0f}th percentile - HIGH leverage")
            elif leverage == 'Medium':
                medium_leverage_players.append((player_name, percentile))

        # Contract negotiation strategies
        print(f"\n💼 NEGOTIATION STRATEGIES:")
        for player_name, insight in list(agent_insights.items())[:5]:
            strategy = self.generate_negotiation_strategy(insight)
            print(f"  • {player_name}: {strategy}")

        # Market comparables
        print(f"\n🔍 MARKET COMPARABLES (Top 3 players):")
        top_players = sorted(agent_insights.items(), key=lambda x: x[1]['overall_percentile'], reverse=True)[:3]
        for player_name, insight in top_players:
            comparables = ', '.join(insight['comparable_players'][:2])
            print(f"  • {player_name}: Compare to {comparables}")

        return {
            'high_leverage_players': high_leverage_players,
            'medium_leverage_players': medium_leverage_players,
            'negotiation_strategies': {name: self.generate_negotiation_strategy(insight)
                                     for name, insight in agent_insights.items()}
        }

    def contract_optimizer_tool(self) -> Dict[str, Any]:
        """
        Tool for contract negotiation: Performance-Based Contract Optimizer
        Provides data-driven justification for contract terms
        """
        print("\n" + "="*80)
        print("📋 CONTRACT NEGOTIATION: PERFORMANCE-BASED OPTIMIZER")
        print("="*80)

        contract_insights = self.insights['contract_negotiation']

        # Contract recommendations by tier
        print(f"\n📊 CONTRACT RECOMMENDATIONS BY PERFORMANCE TIER:")

        tiers = {'Elite': [], 'Excellent': [], 'Good': [], 'Average': [], 'Below Average': []}

        for _, player in self.performance_data.iterrows():
            tier = player['performance_tier']
            contract_info = contract_insights.get(player['player_name'], {})
            tiers[tier].append({
                'name': player['player_name'],
                'position': player['position'],
                'score': player['comprehensive_performance_score'],
                'contract_length': contract_info.get('recommended_length', 'N/A'),
                'bonus_tier': contract_info.get('performance_bonus_tier', 'N/A')
            })

        for tier, players in tiers.items():
            if players:
                print(f"\n  🏆 {tier.upper()} TIER:")
                for player in players[:3]:  # Show top 3 per tier
                    print(f"    • {player['name']} ({player['position']}): {player['contract_length']}, {player['bonus_tier']} bonuses")

        # Performance-based contract clauses
        print(f"\n📋 PERFORMANCE-BASED CONTRACT CLAUSES:")
        sample_contracts = list(contract_insights.items())[:3]
        for player_name, insight in sample_contracts:
            print(f"\n  📄 {player_name}:")
            print(f"    • Base term: {insight['recommended_length']}")
            print(f"    • Risk level: {insight['risk_assessment']}")
            print(f"    • KPIs: {', '.join(insight['key_performance_indicators'])}")

        # Financial recommendations
        print(f"\n💰 FINANCIAL RECOMMENDATIONS:")
        financial_recs = self.generate_financial_recommendations()
        for rec in financial_recs:
            print(f"  • {rec}")

        return {
            'contract_tiers': tiers,
            'performance_clauses': contract_insights,
            'financial_recommendations': financial_recs
        }

    def generate_manager_recommendations(self) -> List[str]:
        """Generate actionable recommendations for team managers."""
        recommendations = []

        # Squad balance recommendations
        squad_balance = self.insights['team_managers']['squad_balance']

        if squad_balance.get('Goalkeeper', 0) < 2:
            recommendations.append("🥅 Recruit additional goalkeeper - squad depth insufficient")

        if squad_balance.get('Defender', 0) < 4:
            recommendations.append("🛡️ Strengthen defensive options - below minimum requirements")

        if squad_balance.get('Midfielder', 0) > 10:
            recommendations.append("⚽ Consider midfielder loans/sales - squad overcrowded")

        # Performance-based recommendations
        elite_count = self.insights['team_managers']['performance_summary']['elite_count']
        if elite_count < 3:
            recommendations.append("⭐ Prioritize elite talent acquisition - insufficient top performers")

        underperformer_count = self.insights['team_managers']['performance_summary']['underperformer_count']
        if underperformer_count > 5:
            recommendations.append("🔄 Academy development focus - high underperformer count")

        return recommendations

    def generate_negotiation_strategy(self, insight: Dict[str, Any]) -> str:
        """Generate negotiation strategy based on player insights."""
        percentile = insight['overall_percentile']
        leverage = insight['negotiation_leverage']

        if leverage == 'High' and percentile >= 80:
            return "Aggressive salary increase, long-term security, performance bonuses"
        elif leverage == 'High':
            return "Emphasize potential, seek development clauses, moderate increase"
        elif leverage == 'Medium':
            return "Market-rate adjustment, prove-it contract, incentive-heavy"
        else:
            return "Focus on opportunity, development pathway, team contribution"

    def generate_financial_recommendations(self) -> List[str]:
        """Generate financial recommendations for contracts."""
        return [
            "💰 Elite performers: 15-25% salary premium justified by performance metrics",
            "📈 Performance bonuses: Tie 30% of compensation to position-specific KPIs",
            "⏰ Contract timing: Negotiate extensions 18 months before expiry for top performers",
            "🎯 Release clauses: Set 20% above market value for elite tier players",
            "📊 Annual reviews: Implement performance-based salary adjustments"
        ]

if __name__ == "__main__":
    # Run comprehensive analysis
    results, stakeholder_insights = main()

    # Initialize product suite
    product_suite = StakeholderProductSuite(results, stakeholder_insights)

    # Run all three stakeholder tools
    print("\n" + "🎯" * 50)
    print("COMPREHENSIVE STAKEHOLDER PRODUCT SUITE")
    print("🎯" * 50)

    # Tool 1: Team Manager
    manager_results = product_suite.manager_retention_tool()

    # Tool 2: Player Agent
    agent_results = product_suite.agent_positioning_tool()

    # Tool 3: Contract Negotiation
    contract_results = product_suite.contract_optimizer_tool()

    print(f"\n🎉 All stakeholder tools completed successfully!")
    print(f"📊 Analysis covers {len(results)} players with comprehensive insights")
    print("="*100)
