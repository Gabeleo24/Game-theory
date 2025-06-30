"""
Tactical analysis module for soccer formations and team strategies.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging

from ..utils.config import Config


class TacticalAnalyzer:
    """Analyzes tactical formations and team strategies."""
    
    def __init__(self):
        """Initialize the tactical analyzer."""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        # Formation templates
        self.formations = {
            '4-4-2': {
                'defenders': 4,
                'midfielders': 4,
                'forwards': 2,
                'style': 'balanced',
                'strengths': ['defensive stability', 'wide play', 'crossing'],
                'weaknesses': ['midfield overload', 'lack of creativity']
            },
            '4-3-3': {
                'defenders': 4,
                'midfielders': 3,
                'forwards': 3,
                'style': 'attacking',
                'strengths': ['wing play', 'pressing', 'attacking width'],
                'weaknesses': ['defensive vulnerability', 'midfield gaps']
            },
            '3-5-2': {
                'defenders': 3,
                'midfielders': 5,
                'forwards': 2,
                'style': 'possession',
                'strengths': ['midfield control', 'wing-back play', 'flexibility'],
                'weaknesses': ['wide defensive areas', 'requires fit wing-backs']
            },
            '4-5-1': {
                'defenders': 4,
                'midfielders': 5,
                'forwards': 1,
                'style': 'defensive',
                'strengths': ['defensive solidity', 'counter-attacking', 'midfield numbers'],
                'weaknesses': ['lack of attacking threat', 'isolated striker']
            }
        }
    
    def analyze_team_formation(self, player_data: pd.DataFrame, team_id: int) -> Dict[str, Any]:
        """
        Analyze a team's formation based on player positions.
        
        Args:
            player_data: Player statistics DataFrame
            team_id: Team ID to analyze
            
        Returns:
            Formation analysis results
        """
        self.logger.info(f"Analyzing formation for team {team_id}")
        
        team_players = player_data[player_data['team_id'] == team_id]
        
        if team_players.empty:
            return {'error': f'No players found for team {team_id}'}
        
        # Count players by position
        position_counts = team_players['games_position'].value_counts()
        
        # Determine likely formation
        formation = self._determine_formation(position_counts)
        
        # Analyze formation effectiveness
        effectiveness = self._analyze_formation_effectiveness(team_players, formation)
        
        return {
            'team_id': team_id,
            'formation': formation,
            'position_counts': position_counts.to_dict(),
            'effectiveness': effectiveness,
            'recommendations': self._get_formation_recommendations(team_players, formation)
        }
    
    def _determine_formation(self, position_counts: pd.Series) -> str:
        """Determine formation from position counts."""
        # Simplified formation detection
        defenders = position_counts.get('Defender', 0)
        midfielders = position_counts.get('Midfielder', 0)
        forwards = position_counts.get('Attacker', 0) + position_counts.get('Forward', 0)
        
        formation_key = f"{defenders}-{midfielders}-{forwards}"
        
        if formation_key in self.formations:
            return formation_key
        else:
            return 'Unknown'
    
    def _analyze_formation_effectiveness(self, team_players: pd.DataFrame, formation: str) -> Dict[str, Any]:
        """Analyze how effective the formation is for the team."""
        if formation == 'Unknown':
            return {'overall_rating': 0, 'analysis': 'Formation not recognized'}
        
        formation_info = self.formations[formation]
        
        # Calculate effectiveness based on player performance
        avg_rating = team_players['games_rating'].mean() if 'games_rating' in team_players.columns else 0
        total_goals = team_players['goals_total'].sum() if 'goals_total' in team_players.columns else 0
        total_assists = team_players['goals_assists'].sum() if 'goals_assists' in team_players.columns else 0
        
        effectiveness_score = min(10, (avg_rating + total_goals * 0.1 + total_assists * 0.05))
        
        return {
            'overall_rating': round(effectiveness_score, 2),
            'formation_style': formation_info['style'],
            'strengths': formation_info['strengths'],
            'weaknesses': formation_info['weaknesses'],
            'avg_player_rating': round(avg_rating, 2),
            'total_goals': total_goals,
            'total_assists': total_assists
        }
    
    def _get_formation_recommendations(self, team_players: pd.DataFrame, current_formation: str) -> List[str]:
        """Get recommendations for formation improvements."""
        recommendations = []
        
        if current_formation == 'Unknown':
            recommendations.append("Consider adopting a standard formation like 4-4-2 or 4-3-3")
            return recommendations
        
        # Analyze player strengths
        if 'goals_total' in team_players.columns:
            high_scorers = len(team_players[team_players['goals_total'] > 5])
            if high_scorers >= 2:
                recommendations.append("Consider more attacking formations like 4-3-3 with multiple goal threats")
        
        if 'tackles_total' in team_players.columns:
            strong_defenders = len(team_players[team_players['tackles_total'] > 20])
            if strong_defenders >= 3:
                recommendations.append("Strong defensive players suggest 3-5-2 could work well")
        
        return recommendations
    
    def compare_formations(self, formation1: str, formation2: str) -> Dict[str, Any]:
        """
        Compare two formations.
        
        Args:
            formation1: First formation to compare
            formation2: Second formation to compare
            
        Returns:
            Comparison analysis
        """
        if formation1 not in self.formations or formation2 not in self.formations:
            return {'error': 'One or both formations not recognized'}
        
        f1_info = self.formations[formation1]
        f2_info = self.formations[formation2]
        
        comparison = {
            'formation_1': {
                'name': formation1,
                'style': f1_info['style'],
                'strengths': f1_info['strengths'],
                'weaknesses': f1_info['weaknesses']
            },
            'formation_2': {
                'name': formation2,
                'style': f2_info['style'],
                'strengths': f2_info['strengths'],
                'weaknesses': f2_info['weaknesses']
            },
            'recommendations': self._get_formation_comparison_recommendations(f1_info, f2_info)
        }
        
        return comparison
    
    def _get_formation_comparison_recommendations(self, f1_info: Dict, f2_info: Dict) -> List[str]:
        """Get recommendations from formation comparison."""
        recommendations = []
        
        if f1_info['style'] == 'attacking' and f2_info['style'] == 'defensive':
            recommendations.append(f"Choose {f1_info} for offensive games, {f2_info} for defensive games")
        
        if 'midfield control' in f1_info['strengths'] and 'midfield control' not in f2_info['strengths']:
            recommendations.append("First formation offers better midfield control")
        
        return recommendations
    
    def get_formation_for_opponent(self, opponent_style: str, team_strengths: List[str]) -> Dict[str, Any]:
        """
        Recommend formation based on opponent style and team strengths.
        
        Args:
            opponent_style: Style of the opponent ('attacking', 'defensive', 'possession')
            team_strengths: List of team's key strengths
            
        Returns:
            Formation recommendation
        """
        recommendations = []
        
        # Counter-formation logic
        if opponent_style == 'attacking':
            recommendations.append({
                'formation': '4-5-1',
                'reason': 'Defensive solidity to counter attacking opponents',
                'tactics': ['Deep defensive line', 'Quick counter-attacks', 'Compact midfield']
            })
        
        elif opponent_style == 'defensive':
            recommendations.append({
                'formation': '4-3-3',
                'reason': 'Width and creativity to break down defensive teams',
                'tactics': ['Wide attacking play', 'High pressing', 'Quick passing']
            })
        
        elif opponent_style == 'possession':
            recommendations.append({
                'formation': '3-5-2',
                'reason': 'Midfield numbers to compete for possession',
                'tactics': ['High pressing', 'Quick transitions', 'Wing-back overlaps']
            })
        
        # Consider team strengths
        if 'pace' in team_strengths:
            recommendations.append({
                'formation': '4-3-3',
                'reason': 'Utilize pace with wide forwards',
                'tactics': ['Counter-attacking', 'Direct play', 'Through balls']
            })
        
        return {
            'opponent_style': opponent_style,
            'team_strengths': team_strengths,
            'recommendations': recommendations
        }
