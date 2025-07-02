"""
Data Integration Module

Combines data from multiple sources (API-Football, FBref, etc.) to create
comprehensive datasets for the Soccer Performance Intelligence System.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from pathlib import Path
import json
from datetime import datetime

from ..data_collection.api_football import APIFootballClient
from ..data_collection.fbref import FBrefCollector
from ..utils.logger import get_logger


class DataIntegrator:
    """
    Integrates data from multiple sources to create comprehensive datasets
    """
    
    def __init__(self, cache_dir: str = "data/processed/integrated"):
        """
        Initialize the data integrator
        
        Args:
            cache_dir: Directory to store integrated data
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(__name__)
        
        # League mappings between API-Football and FBref
        self.league_mappings = {
            "Premier League": {
                "api_football_id": 39,
                "fbref_url": "/en/comps/9/Premier-League-Stats",
                "country": "England"
            },
            "La Liga": {
                "api_football_id": 140,
                "fbref_url": "/en/comps/12/La-Liga-Stats", 
                "country": "Spain"
            },
            "Serie A": {
                "api_football_id": 135,
                "fbref_url": "/en/comps/11/Serie-A-Stats",
                "country": "Italy"
            },
            "Bundesliga": {
                "api_football_id": 78,
                "fbref_url": "/en/comps/20/Bundesliga-Stats",
                "country": "Germany"
            },
            "Ligue 1": {
                "api_football_id": 61,
                "fbref_url": "/en/comps/13/Ligue-1-Stats",
                "country": "France"
            }
        }
    
    def integrate_league_data(self, league_name: str, season: int = 2024) -> Dict[str, pd.DataFrame]:
        """
        Integrate league data from API-Football and FBref
        
        Args:
            league_name: Name of the league
            season: Season year
            
        Returns:
            Dictionary containing integrated datasets
        """
        if league_name not in self.league_mappings:
            raise ValueError(f"League {league_name} not supported. Available: {list(self.league_mappings.keys())}")
        
        league_info = self.league_mappings[league_name]
        self.logger.info(f"Integrating data for {league_name} season {season}")
        
        # Initialize collectors
        api_client = APIFootballClient()
        fbref_collector = FBrefCollector()
        
        integrated_data = {}
        
        try:
            # Get API-Football data
            self.logger.info("Collecting API-Football data...")
            api_teams = api_client.get_teams(league_info["api_football_id"], season)
            api_standings = api_client.get_standings(league_info["api_football_id"], season)
            
            # Get FBref data
            self.logger.info("Collecting FBref data...")
            fbref_table = fbref_collector.get_league_table(league_info["fbref_url"])
            fbref_player_stats = fbref_collector.get_player_stats(league_info["fbref_url"], "stats")
            fbref_team_stats = fbref_collector.get_team_stats(league_info["fbref_url"], "stats")
            
            # Integrate team data
            integrated_teams = self._integrate_team_data(api_teams, api_standings, fbref_table, fbref_team_stats)
            if integrated_teams is not None:
                integrated_data['teams'] = integrated_teams
            
            # Process player data
            if fbref_player_stats is not None:
                integrated_data['players'] = self._process_player_data(fbref_player_stats, league_name)
            
            # Add metadata
            integrated_data['metadata'] = {
                'league': league_name,
                'season': season,
                'integration_date': datetime.now().isoformat(),
                'sources': ['API-Football', 'FBref'],
                'api_football_league_id': league_info["api_football_id"],
                'fbref_url': league_info["fbref_url"]
            }
            
            # Save integrated data
            self._save_integrated_data(integrated_data, league_name, season)
            
            self.logger.info(f"Successfully integrated {league_name} data")
            return integrated_data
            
        except Exception as e:
            self.logger.error(f"Error integrating {league_name} data: {e}")
            raise
        finally:
            fbref_collector.close()
    
    def _integrate_team_data(self, api_teams: List[Dict], api_standings: List[Dict], 
                           fbref_table: pd.DataFrame, fbref_team_stats: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Integrate team data from multiple sources
        """
        try:
            # Convert API-Football data to DataFrames
            if api_teams:
                api_teams_df = pd.json_normalize(api_teams)
            else:
                api_teams_df = pd.DataFrame()
            
            if api_standings:
                # API-Football standings are nested
                standings_data = []
                for standing in api_standings:
                    if 'league' in standing and 'standings' in standing['league']:
                        for group in standing['league']['standings']:
                            standings_data.extend(group)
                api_standings_df = pd.json_normalize(standings_data) if standings_data else pd.DataFrame()
            else:
                api_standings_df = pd.DataFrame()
            
            # Start with FBref table as base (most comprehensive)
            if fbref_table is None or fbref_table.empty:
                self.logger.warning("No FBref table data available")
                return None
            
            integrated_df = fbref_table.copy()
            
            # Add API-Football team information
            if not api_teams_df.empty and 'team.name' in api_teams_df.columns:
                # Create mapping between team names
                team_mapping = self._create_team_name_mapping(
                    fbref_table['Squad'].tolist(),
                    api_teams_df['team.name'].tolist()
                )
                
                # Add API-Football team IDs and additional info
                for fbref_name, api_name in team_mapping.items():
                    api_team_info = api_teams_df[api_teams_df['team.name'] == api_name]
                    if not api_team_info.empty:
                        team_row = api_team_info.iloc[0]
                        mask = integrated_df['Squad'] == fbref_name
                        integrated_df.loc[mask, 'api_football_team_id'] = team_row.get('team.id', '')
                        integrated_df.loc[mask, 'team_founded'] = team_row.get('team.founded', '')
                        integrated_df.loc[mask, 'venue_name'] = team_row.get('venue.name', '')
                        integrated_df.loc[mask, 'venue_capacity'] = team_row.get('venue.capacity', '')
            
            # Add API-Football standings data
            if not api_standings_df.empty and 'team.name' in api_standings_df.columns:
                team_mapping = self._create_team_name_mapping(
                    fbref_table['Squad'].tolist(),
                    api_standings_df['team.name'].tolist()
                )
                
                for fbref_name, api_name in team_mapping.items():
                    api_standing = api_standings_df[api_standings_df['team.name'] == api_name]
                    if not api_standing.empty:
                        standing_row = api_standing.iloc[0]
                        mask = integrated_df['Squad'] == fbref_name
                        integrated_df.loc[mask, 'form'] = standing_row.get('form', '')
                        integrated_df.loc[mask, 'status'] = standing_row.get('status', '')
                        integrated_df.loc[mask, 'description'] = standing_row.get('description', '')
            
            return integrated_df
            
        except Exception as e:
            self.logger.error(f"Error integrating team data: {e}")
            return None
    
    def _process_player_data(self, fbref_players: pd.DataFrame, league_name: str) -> pd.DataFrame:
        """
        Process and enhance player data from FBref
        """
        try:
            processed_df = fbref_players.copy()
            processed_df['league'] = league_name
            processed_df['data_source'] = 'FBref'
            
            # Add calculated metrics for Shapley analysis
            if 'Gls' in processed_df.columns and 'Ast' in processed_df.columns:
                # Convert to numeric, handling non-numeric values
                processed_df['Gls_numeric'] = pd.to_numeric(processed_df['Gls'], errors='coerce').fillna(0)
                processed_df['Ast_numeric'] = pd.to_numeric(processed_df['Ast'], errors='coerce').fillna(0)
                processed_df['goal_contribution'] = processed_df['Gls_numeric'] + processed_df['Ast_numeric']
            
            # Add xG and xA if available
            if 'xG' in processed_df.columns:
                processed_df['xG_numeric'] = pd.to_numeric(processed_df['xG'], errors='coerce').fillna(0)
            
            if 'xAG' in processed_df.columns:
                processed_df['xAG_numeric'] = pd.to_numeric(processed_df['xAG'], errors='coerce').fillna(0)
                if 'xG_numeric' in processed_df.columns:
                    processed_df['expected_contribution'] = processed_df['xG_numeric'] + processed_df['xAG_numeric']
            
            return processed_df
            
        except Exception as e:
            self.logger.error(f"Error processing player data: {e}")
            return fbref_players
    
    def _create_team_name_mapping(self, fbref_names: List[str], api_names: List[str]) -> Dict[str, str]:
        """
        Create mapping between FBref and API-Football team names
        """
        mapping = {}
        
        # Common name variations
        name_variations = {
            'Manchester Utd': 'Manchester United',
            'Newcastle Utd': 'Newcastle United',
            'Nott\'ham Forest': 'Nottingham Forest',
            'Brighton': 'Brighton & Hove Albion',
            'Wolves': 'Wolverhampton Wanderers',
            'Tottenham': 'Tottenham Hotspur',
            'West Ham': 'West Ham United'
        }
        
        for fbref_name in fbref_names:
            # Try exact match first
            if fbref_name in api_names:
                mapping[fbref_name] = fbref_name
                continue
            
            # Try known variations
            if fbref_name in name_variations and name_variations[fbref_name] in api_names:
                mapping[fbref_name] = name_variations[fbref_name]
                continue
            
            # Try partial matching
            for api_name in api_names:
                if fbref_name.lower() in api_name.lower() or api_name.lower() in fbref_name.lower():
                    mapping[fbref_name] = api_name
                    break
        
        return mapping
    
    def _save_integrated_data(self, data: Dict[str, Any], league_name: str, season: int):
        """
        Save integrated data to files
        """
        try:
            league_dir = self.cache_dir / league_name.lower().replace(' ', '_')
            league_dir.mkdir(exist_ok=True)
            
            # Save DataFrames as CSV
            for key, df in data.items():
                if isinstance(df, pd.DataFrame):
                    filename = f"{league_name.lower().replace(' ', '_')}_{key}_{season}.csv"
                    df.to_csv(league_dir / filename, index=False)
                    self.logger.info(f"Saved {key} data to {filename}")
            
            # Save metadata as JSON
            if 'metadata' in data:
                metadata_file = league_dir / f"{league_name.lower().replace(' ', '_')}_metadata_{season}.json"
                with open(metadata_file, 'w') as f:
                    json.dump(data['metadata'], f, indent=2)
                self.logger.info(f"Saved metadata to {metadata_file}")
                
        except Exception as e:
            self.logger.error(f"Error saving integrated data: {e}")
    
    def get_integrated_data(self, league_name: str, season: int) -> Optional[Dict[str, pd.DataFrame]]:
        """
        Load previously integrated data
        
        Args:
            league_name: Name of the league
            season: Season year
            
        Returns:
            Dictionary containing integrated datasets or None if not found
        """
        try:
            league_dir = self.cache_dir / league_name.lower().replace(' ', '_')
            
            if not league_dir.exists():
                return None
            
            data = {}
            
            # Load CSV files
            for csv_file in league_dir.glob(f"*_{season}.csv"):
                key = csv_file.stem.replace(f"{league_name.lower().replace(' ', '_')}_", "").replace(f"_{season}", "")
                data[key] = pd.read_csv(csv_file)
            
            # Load metadata
            metadata_file = league_dir / f"{league_name.lower().replace(' ', '_')}_metadata_{season}.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    data['metadata'] = json.load(f)
            
            return data if data else None
            
        except Exception as e:
            self.logger.error(f"Error loading integrated data: {e}")
            return None
