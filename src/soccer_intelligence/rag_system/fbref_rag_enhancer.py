"""
FBref RAG Enhancer

Enhances the RAG system with rich statistical content from FBref data
for more comprehensive soccer intelligence queries.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
import json

from ..utils.logger import get_logger
from ..data_collection.fbref import FBrefCollector
from ..data_processing.data_integrator import DataIntegrator


class FBrefRAGEnhancer:
    """
    Enhances RAG system with FBref statistical content
    """
    
    def __init__(self, cache_dir: str = "data/processed/rag_enhanced"):
        """
        Initialize the FBref RAG enhancer
        
        Args:
            cache_dir: Directory to store enhanced RAG content
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(__name__)
        
        # Initialize data sources
        self.fbref_collector = FBrefCollector()
        self.data_integrator = DataIntegrator()
        
        # Content templates for different query types
        self.content_templates = {
            'player_profile': self._create_player_profile_content,
            'team_analysis': self._create_team_analysis_content,
            'tactical_insights': self._create_tactical_insights_content,
            'performance_comparison': self._create_performance_comparison_content,
            'statistical_summary': self._create_statistical_summary_content
        }
    
    def enhance_rag_knowledge_base(self, leagues: List[str] = None) -> Dict[str, List[Dict]]:
        """
        Create enhanced knowledge base with FBref statistical content
        
        Args:
            leagues: List of leagues to process (default: major European leagues)
            
        Returns:
            Dictionary containing enhanced content for RAG system
        """
        if leagues is None:
            leagues = ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
        
        enhanced_content = {
            'player_profiles': [],
            'team_analyses': [],
            'tactical_insights': [],
            'performance_comparisons': [],
            'statistical_summaries': []
        }
        
        self.logger.info(f"Enhancing RAG knowledge base for {len(leagues)} leagues")
        
        for league in leagues:
            try:
                self.logger.info(f"Processing {league}...")
                
                # Get integrated data
                integrated_data = self.data_integrator.get_integrated_data(league, 2024)
                if not integrated_data:
                    # Try to integrate if not available
                    integrated_data = self.data_integrator.integrate_league_data(league, 2024)
                
                if integrated_data:
                    league_content = self._process_league_for_rag(league, integrated_data)
                    
                    # Merge league content into enhanced content
                    for content_type, items in league_content.items():
                        if content_type in enhanced_content:
                            enhanced_content[content_type].extend(items)
                
            except Exception as e:
                self.logger.error(f"Error processing {league}: {e}")
                continue
        
        # Save enhanced content
        self._save_enhanced_content(enhanced_content)
        
        self.logger.info(f"Enhanced knowledge base created with {sum(len(items) for items in enhanced_content.values())} items")
        return enhanced_content
    
    def _process_league_for_rag(self, league: str, integrated_data: Dict) -> Dict[str, List[Dict]]:
        """
        Process league data to create RAG-friendly content
        """
        content = {
            'player_profiles': [],
            'team_analyses': [],
            'tactical_insights': [],
            'performance_comparisons': [],
            'statistical_summaries': []
        }
        
        # Process team data
        if 'teams' in integrated_data:
            teams_df = integrated_data['teams']
            
            # Create team analyses
            for _, team in teams_df.iterrows():
                team_content = self._create_team_analysis_content(team, league)
                content['team_analyses'].append(team_content)
            
            # Create league statistical summary
            league_summary = self._create_league_statistical_summary(teams_df, league)
            content['statistical_summaries'].append(league_summary)
            
            # Create tactical insights
            tactical_content = self._create_league_tactical_insights(teams_df, league)
            content['tactical_insights'].append(tactical_content)
        
        # Process player data
        if 'players' in integrated_data:
            players_df = integrated_data['players']
            
            # Create player profiles for top performers
            top_players = self._identify_top_players(players_df)
            for _, player in top_players.iterrows():
                player_content = self._create_player_profile_content(player, league)
                content['player_profiles'].append(player_content)
            
            # Create performance comparisons
            comparison_content = self._create_performance_comparison_content(players_df, league)
            content['performance_comparisons'].append(comparison_content)
        
        return content
    
    def _create_player_profile_content(self, player_data: pd.Series, league: str) -> Dict:
        """Create comprehensive player profile content"""
        content = {
            'type': 'player_profile',
            'league': league,
            'player_name': player_data.get('Player', 'Unknown'),
            'team': player_data.get('Squad', 'Unknown'),
            'content': f"""
Player Profile: {player_data.get('Player', 'Unknown')} ({player_data.get('Squad', 'Unknown')})

League: {league}
Position: {player_data.get('Pos', 'Unknown')}
Age: {player_data.get('Age', 'Unknown')}

Performance Statistics:
- Goals: {player_data.get('Gls', 0)}
- Assists: {player_data.get('Ast', 0)}
- Expected Goals (xG): {player_data.get('xG', 'N/A')}
- Expected Assists (xAG): {player_data.get('xAG', 'N/A')}
- Minutes Played: {player_data.get('Min', 'N/A')}
- Matches Played: {player_data.get('MP', 'N/A')}

Goal Contribution: {player_data.get('goal_contribution', 'N/A')}
Expected Contribution: {player_data.get('expected_contribution', 'N/A')}

This player's performance data is valuable for tactical analysis, formation planning, and player comparison studies in the {league}.
            """.strip(),
            'metadata': {
                'goals': player_data.get('Gls', 0),
                'assists': player_data.get('Ast', 0),
                'xg': player_data.get('xG', 0),
                'xag': player_data.get('xAG', 0),
                'position': player_data.get('Pos', 'Unknown'),
                'age': player_data.get('Age', 0)
            }
        }
        return content
    
    def _create_team_analysis_content(self, team_data: pd.Series, league: str) -> Dict:
        """Create comprehensive team analysis content"""
        content = {
            'type': 'team_analysis',
            'league': league,
            'team_name': team_data.get('Squad', 'Unknown'),
            'content': f"""
Team Analysis: {team_data.get('Squad', 'Unknown')} - {league}

League Position: {team_data.get('Rk', 'Unknown')}
Points: {team_data.get('Pts', 'Unknown')}
Matches Played: {team_data.get('MP', 'Unknown')}

Performance Record:
- Wins: {team_data.get('W', 'Unknown')}
- Draws: {team_data.get('D', 'Unknown')}
- Losses: {team_data.get('L', 'Unknown')}

Goal Statistics:
- Goals For: {team_data.get('GF', 'Unknown')}
- Goals Against: {team_data.get('GA', 'Unknown')}
- Goal Difference: {team_data.get('GD', 'Unknown')}

Advanced Metrics:
- Expected Goals (xG): {team_data.get('xG', 'N/A')}
- Expected Goals Against (xGA): {team_data.get('xGA', 'N/A')}
- Expected Goal Difference: {team_data.get('xGD', 'N/A')}

Venue Information:
- Stadium: {team_data.get('venue_name', 'Unknown')}
- Capacity: {team_data.get('venue_capacity', 'Unknown')}
- Average Attendance: {team_data.get('Attendance', 'Unknown')}

Top Scorer: {team_data.get('Top Team Scorer', 'Unknown')}
Goalkeeper: {team_data.get('Goalkeeper', 'Unknown')}

This team's performance data provides insights into their tactical approach, attacking efficiency, and defensive solidity in the {league}.
            """.strip(),
            'metadata': {
                'position': team_data.get('Rk', 0),
                'points': team_data.get('Pts', 0),
                'goals_for': team_data.get('GF', 0),
                'goals_against': team_data.get('GA', 0),
                'xg': team_data.get('xG', 0),
                'xga': team_data.get('xGA', 0)
            }
        }
        return content
    
    def _create_tactical_insights_content(self, teams_df: pd.DataFrame, league: str) -> Dict:
        """Create tactical insights from league data"""
        
        # Calculate league averages and trends
        avg_goals = teams_df['GF'].astype(float).mean() if 'GF' in teams_df.columns else 0
        avg_xg = teams_df['xG'].astype(float).mean() if 'xG' in teams_df.columns else 0
        
        # Identify tactical trends
        high_scoring_teams = teams_df.nlargest(3, 'GF')['Squad'].tolist() if 'GF' in teams_df.columns else []
        defensive_teams = teams_df.nsmallest(3, 'GA')['Squad'].tolist() if 'GA' in teams_df.columns else []
        
        content = {
            'type': 'tactical_insights',
            'league': league,
            'content': f"""
Tactical Insights: {league} Analysis

League Tactical Trends:
- Average Goals per Team: {avg_goals:.1f}
- Average Expected Goals (xG): {avg_xg:.1f}

Attacking Patterns:
- Highest Scoring Teams: {', '.join(high_scoring_teams)}
- These teams demonstrate effective attacking formations and player positioning

Defensive Strategies:
- Most Defensively Solid Teams: {', '.join(defensive_teams)}
- These teams show strong defensive organization and tactical discipline

Formation Analysis:
The {league} shows diverse tactical approaches with teams adapting their formations based on opponent analysis and player strengths. Expected Goals (xG) data reveals the quality of chances created, indicating tactical effectiveness beyond just goal tallies.

Key Tactical Considerations:
- Teams with higher xG than actual goals may need better finishing
- Teams with lower xGA than actual goals conceded have strong goalkeeping
- Goal difference vs xG difference shows tactical efficiency vs chance quality
            """.strip(),
            'metadata': {
                'avg_goals': avg_goals,
                'avg_xg': avg_xg,
                'high_scoring_teams': high_scoring_teams,
                'defensive_teams': defensive_teams
            }
        }
        return content
    
    def _create_performance_comparison_content(self, players_df: pd.DataFrame, league: str) -> Dict:
        """Create performance comparison content"""
        
        # Get top performers in different categories
        top_scorers = players_df.nlargest(5, 'Gls_numeric')['Player'].tolist() if 'Gls_numeric' in players_df.columns else []
        top_assisters = players_df.nlargest(5, 'Ast_numeric')['Player'].tolist() if 'Ast_numeric' in players_df.columns else []
        
        content = {
            'type': 'performance_comparison',
            'league': league,
            'content': f"""
Performance Comparison Analysis: {league}

Top Goal Scorers:
{', '.join(top_scorers[:3])}

Top Assist Providers:
{', '.join(top_assisters[:3])}

Performance Metrics for Player Comparison:
- Goal Contribution (Goals + Assists) provides overall attacking impact
- Expected Goals (xG) shows quality of chances created for the player
- Expected Assists (xAG) indicates creative contribution quality

Shapley Value Analysis Applications:
This data is ideal for calculating individual player contributions to team success using Shapley values, considering:
- Direct goal contributions
- Expected performance metrics
- Positional responsibilities
- Team tactical system fit

Formation-Specific Insights:
Players can be analyzed within their tactical roles to understand optimal formations and player combinations for maximum team effectiveness.
            """.strip(),
            'metadata': {
                'top_scorers': top_scorers,
                'top_assisters': top_assisters,
                'total_players': len(players_df)
            }
        }
        return content
    
    def _create_league_statistical_summary(self, teams_df: pd.DataFrame, league: str) -> Dict:
        """Create statistical summary for the league"""
        
        total_goals = teams_df['GF'].astype(float).sum() if 'GF' in teams_df.columns else 0
        total_matches = teams_df['MP'].astype(float).sum() / 2 if 'MP' in teams_df.columns else 0  # Divide by 2 as each match involves 2 teams
        
        content = {
            'type': 'statistical_summary',
            'league': league,
            'content': f"""
Statistical Summary: {league} Season Analysis

League Overview:
- Total Teams: {len(teams_df)}
- Total Goals Scored: {total_goals:.0f}
- Total Matches: {total_matches:.0f}
- Average Goals per Match: {(total_goals / total_matches) if total_matches > 0 else 0:.2f}

Competitive Balance:
- Point Spread: {teams_df['Pts'].max() - teams_df['Pts'].min() if 'Pts' in teams_df.columns else 'N/A'} points
- Goal Difference Range: {teams_df['GD'].max() - teams_df['GD'].min() if 'GD' in teams_df.columns else 'N/A'}

Advanced Analytics:
- Expected Goals accuracy shows tactical execution quality
- Attendance figures indicate fan engagement and market size
- Venue capacity affects home advantage and tactical approaches

This statistical foundation supports comprehensive analysis for formation optimization, player valuation, and tactical decision-making in the {league}.
            """.strip(),
            'metadata': {
                'total_teams': len(teams_df),
                'total_goals': total_goals,
                'total_matches': total_matches,
                'avg_goals_per_match': (total_goals / total_matches) if total_matches > 0 else 0
            }
        }
        return content
    
    def _identify_top_players(self, players_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """Identify top players for profile creation"""
        if 'goal_contribution' in players_df.columns:
            return players_df.nlargest(top_n, 'goal_contribution')
        elif 'Gls_numeric' in players_df.columns:
            return players_df.nlargest(top_n, 'Gls_numeric')
        else:
            return players_df.head(top_n)
    
    def _save_enhanced_content(self, content: Dict[str, List[Dict]]):
        """Save enhanced content to files"""
        try:
            # Save as JSON for easy loading
            content_file = self.cache_dir / "enhanced_rag_content.json"
            with open(content_file, 'w') as f:
                json.dump(content, f, indent=2, default=str)
            
            # Save individual content types
            for content_type, items in content.items():
                type_file = self.cache_dir / f"{content_type}.json"
                with open(type_file, 'w') as f:
                    json.dump(items, f, indent=2, default=str)
            
            self.logger.info(f"Enhanced RAG content saved to {self.cache_dir}")
            
        except Exception as e:
            self.logger.error(f"Error saving enhanced content: {e}")
    
    def load_enhanced_content(self) -> Optional[Dict[str, List[Dict]]]:
        """Load previously created enhanced content"""
        try:
            content_file = self.cache_dir / "enhanced_rag_content.json"
            if content_file.exists():
                with open(content_file, 'r') as f:
                    return json.load(f)
            return None
            
        except Exception as e:
            self.logger.error(f"Error loading enhanced content: {e}")
            return None
    
    def close(self):
        """Close collectors"""
        self.fbref_collector.close()
