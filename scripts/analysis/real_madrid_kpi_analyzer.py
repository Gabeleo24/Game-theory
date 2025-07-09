#!/usr/bin/env python3
"""
Real Madrid KPI Analyzer - Advanced Soccer Intelligence System
Specialized service for analyzing Real Madrid performance metrics and KPIs
Optimized for containerized deployment with Redis caching and PostgreSQL storage
"""

import asyncio
import json
import logging
import time
import redis
import psycopg2
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from psycopg2.extras import RealDictCursor
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class KPIMetric:
    """KPI metric data structure."""
    name: str
    value: float
    category: str
    importance: float
    trend: str
    last_updated: datetime

@dataclass
class PlayerKPI:
    """Player KPI analysis result."""
    player_id: int
    player_name: str
    position: str
    kpis: List[KPIMetric]
    overall_rating: float
    performance_trend: str

class RealMadridKPIAnalyzer:
    """Advanced KPI analyzer for Real Madrid soccer intelligence."""
    
    def __init__(self):
        """Initialize the KPI analyzer."""
        self.setup_connections()
        self.kpi_weights = self.load_kpi_weights()
        self.analysis_cache = {}
        
    def setup_connections(self):
        """Setup database and cache connections."""
        try:
            # PostgreSQL connection
            self.db_conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                port=os.getenv('POSTGRES_PORT', 5432),
                database=os.getenv('POSTGRES_DB', 'soccer_intelligence'),
                user=os.getenv('POSTGRES_USER', 'soccerapp'),
                password=os.getenv('POSTGRES_PASSWORD', 'soccerpass123')
            )
            self.db_cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            
            # Redis connection
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                password=os.getenv('REDIS_PASSWORD', 'redispass123'),
                db=0,
                decode_responses=True
            )
            
            # Test connections
            self.db_cursor.execute("SELECT 1")
            self.redis_client.ping()
            
            logger.info("✅ Database and Redis connections established")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup connections: {e}")
            raise
    
    def load_kpi_weights(self) -> Dict[str, float]:
        """Load KPI weights for different positions and metrics."""
        return {
            # Offensive KPIs
            'goals_per_match': 0.25,
            'assists_per_match': 0.20,
            'shots_on_target_ratio': 0.15,
            'key_passes_per_match': 0.12,
            'dribbles_success_rate': 0.10,
            
            # Defensive KPIs
            'tackles_success_rate': 0.18,
            'interceptions_per_match': 0.15,
            'clearances_per_match': 0.12,
            'blocks_per_match': 0.10,
            
            # Midfield KPIs
            'pass_accuracy': 0.20,
            'long_passes_accuracy': 0.15,
            'through_balls_per_match': 0.12,
            'ball_recovery_rate': 0.15,
            
            # Goalkeeper KPIs
            'save_percentage': 0.30,
            'clean_sheets_ratio': 0.25,
            'distribution_accuracy': 0.15,
            'goals_conceded_per_match': 0.20,
            
            # General Performance KPIs
            'match_rating_average': 0.25,
            'minutes_played_consistency': 0.10,
            'disciplinary_record': 0.08,
            'injury_resistance': 0.07
        }
    
    async def analyze_team_kpis(self, season: str = "2023-2024") -> Dict:
        """Analyze comprehensive team KPIs for Real Madrid."""
        logger.info(f"🔄 Analyzing Real Madrid team KPIs for {season}")
        
        cache_key = f"real_madrid_team_kpis_{season}"
        
        # Check cache first
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            logger.info("📋 Retrieved team KPIs from cache")
            return json.loads(cached_result)
        
        try:
            # Get team performance data
            team_stats = await self.get_team_statistics(season)
            player_stats = await self.get_player_statistics(season)
            match_results = await self.get_match_results(season)
            
            # Calculate comprehensive KPIs
            kpi_analysis = {
                'team_overview': {
                    'season': season,
                    'total_matches': len(match_results),
                    'wins': sum(1 for m in match_results if m['result'] == 'W'),
                    'draws': sum(1 for m in match_results if m['result'] == 'D'),
                    'losses': sum(1 for m in match_results if m['result'] == 'L'),
                    'goals_scored': sum(m['goals_for'] for m in match_results),
                    'goals_conceded': sum(m['goals_against'] for m in match_results),
                    'analysis_timestamp': datetime.now().isoformat()
                },
                
                'offensive_kpis': await self.calculate_offensive_kpis(team_stats, match_results),
                'defensive_kpis': await self.calculate_defensive_kpis(team_stats, match_results),
                'tactical_kpis': await self.calculate_tactical_kpis(team_stats, match_results),
                'player_kpis': await self.calculate_player_kpis(player_stats),
                'performance_trends': await self.calculate_performance_trends(match_results),
                'competition_analysis': await self.analyze_by_competition(match_results),
                
                'top_performers': await self.identify_top_performers(player_stats),
                'improvement_areas': await self.identify_improvement_areas(team_stats, player_stats),
                'kpi_recommendations': await self.generate_kpi_recommendations(team_stats, player_stats)
            }
            
            # Cache the results
            self.redis_client.setex(
                cache_key, 
                3600,  # 1 hour cache
                json.dumps(kpi_analysis, default=str)
            )
            
            logger.info("✅ Team KPI analysis completed successfully")
            return kpi_analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze team KPIs: {e}")
            raise
    
    async def get_team_statistics(self, season: str) -> Dict:
        """Get team-level statistics from database."""
        query = """
        SELECT 
            AVG(possession) as avg_possession,
            AVG(shots) as avg_shots,
            AVG(shots_on_target) as avg_shots_on_target,
            AVG(passes) as avg_passes,
            AVG(pass_accuracy) as avg_pass_accuracy,
            AVG(tackles) as avg_tackles,
            AVG(interceptions) as avg_interceptions,
            AVG(fouls) as avg_fouls,
            AVG(corners) as avg_corners,
            AVG(offsides) as avg_offsides,
            COUNT(*) as total_matches
        FROM match_statistics ms
        JOIN matches m ON ms.match_id = m.match_id
        WHERE m.season = %s AND (m.home_team_id = 53 OR m.away_team_id = 53)
        """
        
        self.db_cursor.execute(query, (season,))
        result = self.db_cursor.fetchone()
        return dict(result) if result else {}
    
    async def get_player_statistics(self, season: str) -> List[Dict]:
        """Get player-level statistics from database."""
        query = """
        SELECT 
            p.player_id,
            p.name as player_name,
            p.position,
            AVG(ps.rating) as avg_rating,
            SUM(ps.goals) as total_goals,
            SUM(ps.assists) as total_assists,
            SUM(ps.minutes_played) as total_minutes,
            AVG(ps.shots) as avg_shots,
            AVG(ps.shots_on_target) as avg_shots_on_target,
            AVG(ps.passes) as avg_passes,
            AVG(ps.pass_accuracy) as avg_pass_accuracy,
            AVG(ps.tackles) as avg_tackles,
            AVG(ps.interceptions) as avg_interceptions,
            SUM(ps.yellow_cards) as total_yellow_cards,
            SUM(ps.red_cards) as total_red_cards,
            COUNT(*) as matches_played
        FROM player_statistics ps
        JOIN players p ON ps.player_id = p.player_id
        JOIN matches m ON ps.match_id = m.match_id
        WHERE m.season = %s AND p.team_id = 53
        GROUP BY p.player_id, p.name, p.position
        HAVING COUNT(*) >= 5  -- Minimum 5 matches
        ORDER BY AVG(ps.rating) DESC
        """
        
        self.db_cursor.execute(query, (season,))
        return [dict(row) for row in self.db_cursor.fetchall()]
    
    async def get_match_results(self, season: str) -> List[Dict]:
        """Get match results for Real Madrid."""
        query = """
        SELECT 
            m.match_id,
            m.match_date,
            m.competition,
            m.home_team_id,
            m.away_team_id,
            m.home_score,
            m.away_score,
            CASE 
                WHEN (m.home_team_id = 53 AND m.home_score > m.away_score) OR 
                     (m.away_team_id = 53 AND m.away_score > m.home_score) THEN 'W'
                WHEN m.home_score = m.away_score THEN 'D'
                ELSE 'L'
            END as result,
            CASE 
                WHEN m.home_team_id = 53 THEN m.home_score
                ELSE m.away_score
            END as goals_for,
            CASE 
                WHEN m.home_team_id = 53 THEN m.away_score
                ELSE m.home_score
            END as goals_against
        FROM matches m
        WHERE m.season = %s AND (m.home_team_id = 53 OR m.away_team_id = 53)
        ORDER BY m.match_date
        """
        
        self.db_cursor.execute(query, (season,))
        return [dict(row) for row in self.db_cursor.fetchall()]
    
    async def calculate_offensive_kpis(self, team_stats: Dict, match_results: List[Dict]) -> Dict:
        """Calculate offensive KPIs."""
        total_goals = sum(m['goals_for'] for m in match_results)
        total_matches = len(match_results)
        
        return {
            'goals_per_match': round(total_goals / max(total_matches, 1), 2),
            'shots_per_match': round(team_stats.get('avg_shots', 0), 2),
            'shots_on_target_ratio': round(
                (team_stats.get('avg_shots_on_target', 0) / max(team_stats.get('avg_shots', 1), 1)) * 100, 2
            ),
            'scoring_efficiency': round((total_goals / max(team_stats.get('avg_shots', 1) * total_matches, 1)) * 100, 2),
            'possession_percentage': round(team_stats.get('avg_possession', 0), 2),
            'corners_per_match': round(team_stats.get('avg_corners', 0), 2)
        }
    
    async def calculate_defensive_kpis(self, team_stats: Dict, match_results: List[Dict]) -> Dict:
        """Calculate defensive KPIs."""
        total_goals_conceded = sum(m['goals_against'] for m in match_results)
        total_matches = len(match_results)
        clean_sheets = sum(1 for m in match_results if m['goals_against'] == 0)
        
        return {
            'goals_conceded_per_match': round(total_goals_conceded / max(total_matches, 1), 2),
            'clean_sheets_percentage': round((clean_sheets / max(total_matches, 1)) * 100, 2),
            'tackles_per_match': round(team_stats.get('avg_tackles', 0), 2),
            'interceptions_per_match': round(team_stats.get('avg_interceptions', 0), 2),
            'defensive_actions_per_match': round(
                team_stats.get('avg_tackles', 0) + team_stats.get('avg_interceptions', 0), 2
            )
        }
    
    async def calculate_tactical_kpis(self, team_stats: Dict, match_results: List[Dict]) -> Dict:
        """Calculate tactical KPIs."""
        return {
            'pass_accuracy': round(team_stats.get('avg_pass_accuracy', 0), 2),
            'passes_per_match': round(team_stats.get('avg_passes', 0), 2),
            'fouls_per_match': round(team_stats.get('avg_fouls', 0), 2),
            'offsides_per_match': round(team_stats.get('avg_offsides', 0), 2),
            'discipline_score': round(100 - (team_stats.get('avg_fouls', 0) * 2), 2)
        }
    
    async def calculate_player_kpis(self, player_stats: List[Dict]) -> List[Dict]:
        """Calculate individual player KPIs."""
        player_kpis = []
        
        for player in player_stats:
            matches_played = player['matches_played']
            minutes_per_match = player['total_minutes'] / max(matches_played, 1)
            
            kpi_data = {
                'player_id': player['player_id'],
                'player_name': player['player_name'],
                'position': player['position'],
                'matches_played': matches_played,
                'average_rating': round(player['avg_rating'] or 0, 2),
                'goals_per_match': round(player['total_goals'] / max(matches_played, 1), 2),
                'assists_per_match': round(player['total_assists'] / max(matches_played, 1), 2),
                'minutes_per_match': round(minutes_per_match, 0),
                'pass_accuracy': round(player['avg_pass_accuracy'] or 0, 2),
                'disciplinary_score': round(100 - ((player['total_yellow_cards'] * 2 + player['total_red_cards'] * 10) / max(matches_played, 1)), 2)
            }
            
            player_kpis.append(kpi_data)
        
        return sorted(player_kpis, key=lambda x: x['average_rating'], reverse=True)
    
    async def calculate_performance_trends(self, match_results: List[Dict]) -> Dict:
        """Calculate performance trends over time."""
        if len(match_results) < 5:
            return {'trend': 'insufficient_data'}
        
        recent_matches = match_results[-10:]  # Last 10 matches
        recent_wins = sum(1 for m in recent_matches if m['result'] == 'W')
        recent_goals_for = sum(m['goals_for'] for m in recent_matches)
        recent_goals_against = sum(m['goals_against'] for m in recent_matches)
        
        return {
            'recent_form': f"{recent_wins}W out of {len(recent_matches)} matches",
            'recent_win_percentage': round((recent_wins / len(recent_matches)) * 100, 2),
            'recent_goals_per_match': round(recent_goals_for / len(recent_matches), 2),
            'recent_goals_conceded_per_match': round(recent_goals_against / len(recent_matches), 2),
            'form_trend': 'improving' if recent_wins >= len(recent_matches) * 0.6 else 'declining'
        }
    
    async def analyze_by_competition(self, match_results: List[Dict]) -> Dict:
        """Analyze performance by competition."""
        competitions = {}
        
        for match in match_results:
            comp = match['competition']
            if comp not in competitions:
                competitions[comp] = {'matches': 0, 'wins': 0, 'goals_for': 0, 'goals_against': 0}
            
            competitions[comp]['matches'] += 1
            if match['result'] == 'W':
                competitions[comp]['wins'] += 1
            competitions[comp]['goals_for'] += match['goals_for']
            competitions[comp]['goals_against'] += match['goals_against']
        
        # Calculate win percentages
        for comp_data in competitions.values():
            comp_data['win_percentage'] = round((comp_data['wins'] / max(comp_data['matches'], 1)) * 100, 2)
            comp_data['goals_per_match'] = round(comp_data['goals_for'] / max(comp_data['matches'], 1), 2)
        
        return competitions
    
    async def identify_top_performers(self, player_stats: List[Dict]) -> Dict:
        """Identify top performers in different categories."""
        if not player_stats:
            return {}
        
        return {
            'highest_rated': max(player_stats, key=lambda x: x['avg_rating'] or 0),
            'top_scorer': max(player_stats, key=lambda x: x['total_goals']),
            'most_assists': max(player_stats, key=lambda x: x['total_assists']),
            'most_consistent': min(player_stats, key=lambda x: abs((x['avg_rating'] or 0) - 7.0)),
            'most_minutes': max(player_stats, key=lambda x: x['total_minutes'])
        }
    
    async def identify_improvement_areas(self, team_stats: Dict, player_stats: List[Dict]) -> List[str]:
        """Identify areas for improvement."""
        improvements = []
        
        # Check pass accuracy
        if team_stats.get('avg_pass_accuracy', 0) < 85:
            improvements.append("Improve passing accuracy - currently below 85%")
        
        # Check defensive stability
        if team_stats.get('avg_tackles', 0) < 15:
            improvements.append("Increase defensive pressure - low tackle count")
        
        # Check player consistency
        inconsistent_players = [p for p in player_stats if (p['avg_rating'] or 0) < 6.5 and p['matches_played'] >= 10]
        if inconsistent_players:
            improvements.append(f"Address performance consistency for {len(inconsistent_players)} players")
        
        return improvements
    
    async def generate_kpi_recommendations(self, team_stats: Dict, player_stats: List[Dict]) -> List[str]:
        """Generate KPI-based recommendations."""
        recommendations = []
        
        # Offensive recommendations
        goals_per_match = sum(p['total_goals'] for p in player_stats) / max(len(player_stats), 1)
        if goals_per_match < 1.5:
            recommendations.append("Focus on improving goal conversion rate and creating more scoring opportunities")
        
        # Defensive recommendations
        avg_rating = sum(p['avg_rating'] or 0 for p in player_stats) / max(len(player_stats), 1)
        if avg_rating < 7.0:
            recommendations.append("Work on overall team performance consistency")
        
        # Tactical recommendations
        if team_stats.get('avg_possession', 0) > 65 and goals_per_match < 2.0:
            recommendations.append("Improve efficiency in converting possession into goals")
        
        return recommendations

async def main():
    """Main function to run the KPI analyzer."""
    analyzer = RealMadridKPIAnalyzer()
    
    try:
        logger.info("🚀 Starting Real Madrid KPI Analysis")
        
        # Run comprehensive KPI analysis
        kpi_results = await analyzer.analyze_team_kpis("2023-2024")
        
        # Save results to file
        output_file = f"/app/logs/kpi/real_madrid_kpi_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(kpi_results, f, indent=2, default=str)
        
        logger.info(f"✅ KPI analysis completed and saved to {output_file}")
        
        # Print summary
        print("\n" + "="*80)
        print("REAL MADRID KPI ANALYSIS SUMMARY")
        print("="*80)
        
        overview = kpi_results['team_overview']
        print(f"Season: {overview['season']}")
        print(f"Matches Played: {overview['total_matches']}")
        print(f"Record: {overview['wins']}W-{overview['draws']}D-{overview['losses']}L")
        print(f"Goals: {overview['goals_scored']} scored, {overview['goals_conceded']} conceded")
        
        print(f"\nTop Performer: {kpi_results['top_performers']['highest_rated']['player_name']} "
              f"(Rating: {kpi_results['top_performers']['highest_rated']['avg_rating']:.2f})")
        
        print(f"\nKey KPIs:")
        offensive = kpi_results['offensive_kpis']
        print(f"  • Goals per match: {offensive['goals_per_match']}")
        print(f"  • Shots on target: {offensive['shots_on_target_ratio']}%")
        print(f"  • Possession: {offensive['possession_percentage']}%")
        
        defensive = kpi_results['defensive_kpis']
        print(f"  • Goals conceded per match: {defensive['goals_conceded_per_match']}")
        print(f"  • Clean sheets: {defensive['clean_sheets_percentage']}%")
        
        print("\n" + "="*80)
        
    except Exception as e:
        logger.error(f"❌ KPI analysis failed: {e}")
        raise
    finally:
        if hasattr(analyzer, 'db_conn'):
            analyzer.db_conn.close()
        if hasattr(analyzer, 'redis_client'):
            analyzer.redis_client.close()

if __name__ == "__main__":
    asyncio.run(main())
