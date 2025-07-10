#!/usr/bin/env python3
"""
Create Match-by-Match Database for Manchester City 2023-2024
Generate individual game records for every player in every match for SQL analysis
"""

import pandas as pd
import numpy as np
import json
import sqlite3
from datetime import datetime, timedelta
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MatchByMatchDatabaseCreator:
    """Create comprehensive match-by-match database for SQL analysis."""
    
    def __init__(self):
        """Initialize the database creator."""
        self.squad_data = None
        self.match_records = []
        self.competitions = {
            'Premier League': 38,
            'UEFA Champions League': 8,
            'FA Cup': 6,
            'EFL Cup': 3
        }
        self.opponents = [
            'Arsenal', 'Liverpool', 'Chelsea', 'Tottenham', 'Newcastle', 'Brighton',
            'Aston Villa', 'West Ham', 'Crystal Palace', 'Bournemouth', 'Wolves',
            'Everton', 'Brentford', 'Nottingham Forest', 'Fulham', 'Sheffield United',
            'Burnley', 'Luton Town', 'Real Madrid', 'Barcelona', 'Bayern Munich',
            'PSG', 'Inter Milan', 'Atletico Madrid', 'Juventus', 'AC Milan'
        ]
        
        # Load squad data
        self.load_squad_data()
    
    def load_squad_data(self):
        """Load Manchester City squad data."""
        logger.info("📊 Loading Manchester City squad data")
        
        try:
            # Load the detailed players data
            data_dir = "data/manchester_city_2023_24_framework"
            files = os.listdir(data_dir)
            detailed_file = [f for f in files if f.startswith('detailed_players_')][0]
            
            self.squad_data = pd.read_csv(f"{data_dir}/{detailed_file}")
            logger.info(f"✅ Loaded {len(self.squad_data)} players")
            
        except Exception as e:
            logger.error(f"❌ Error loading squad data: {e}")
            raise
    
    def generate_season_fixtures(self):
        """Generate realistic season fixtures."""
        logger.info("📅 Generating season fixtures")
        
        fixtures = []
        match_id = 1
        
        # Start date for 2023-24 season
        start_date = datetime(2023, 8, 12)
        current_date = start_date
        
        for competition, num_matches in self.competitions.items():
            logger.info(f"🏆 Creating {num_matches} matches for {competition}")
            
            for match_num in range(1, num_matches + 1):
                # Select random opponent
                opponent = np.random.choice(self.opponents)
                
                # Determine home/away
                home_away = np.random.choice(['Home', 'Away'])
                
                # Generate match result
                man_city_goals = np.random.randint(0, 6)
                opponent_goals = np.random.randint(0, 4)
                
                if man_city_goals > opponent_goals:
                    result = 'Win'
                elif man_city_goals < opponent_goals:
                    result = 'Loss'
                else:
                    result = 'Draw'
                
                fixture = {
                    'match_id': match_id,
                    'match_date': current_date.strftime('%Y-%m-%d'),
                    'competition': competition,
                    'opponent': opponent,
                    'home_away': home_away,
                    'man_city_goals': man_city_goals,
                    'opponent_goals': opponent_goals,
                    'result': result,
                    'match_name': f"Manchester City vs {opponent}" if home_away == 'Home' else f"{opponent} vs Manchester City"
                }
                
                fixtures.append(fixture)
                match_id += 1
                
                # Increment date (matches every 3-7 days)
                current_date += timedelta(days=np.random.randint(3, 8))
        
        logger.info(f"✅ Generated {len(fixtures)} fixtures")
        return fixtures
    
    def generate_player_match_performance(self, player_data, fixture, season_stats):
        """Generate realistic match performance for a player."""
        player_id = player_data['player_id']
        position_id = player_data['position_id']
        
        # Determine if player played (based on position and rotation)
        play_probability = {
            24: 0.7,  # Goalkeeper
            25: 0.8,  # Defender
            26: 0.85, # Midfielder
            27: 0.9   # Forward
        }
        
        # Star players play more often
        star_players = [154421, 1371, 336133, 96353, 1116]  # Haaland, KDB, Foden, Bernardo, Grealish
        if player_id in star_players:
            play_probability[position_id] += 0.1
        
        played = np.random.random() < play_probability.get(position_id, 0.8)
        
        if not played:
            # Player didn't play
            return {
                'match_id': fixture['match_id'],
                'player_id': player_id,
                'player_name': player_data['name'],
                'jersey_number': player_data['jersey_number'],
                'position': self.get_position_name(position_id),
                'match_date': fixture['match_date'],
                'competition': fixture['competition'],
                'opponent': fixture['opponent'],
                'home_away': fixture['home_away'],
                'result': fixture['result'],
                'played': False,
                'started': False,
                'minutes_played': 0,
                'goals': 0,
                'assists': 0,
                'shots': 0,
                'shots_on_target': 0,
                'passes': 0,
                'passes_completed': 0,
                'pass_accuracy': 0,
                'tackles': 0,
                'interceptions': 0,
                'clearances': 0,
                'yellow_cards': 0,
                'red_cards': 0,
                'fouls_committed': 0,
                'fouls_suffered': 0,
                'saves': 0,
                'goals_conceded': 0,
                'clean_sheet': False,
                'rating': 0.0,
                'player_of_match': False
            }
        
        # Player played - generate performance
        started = np.random.random() < 0.8  # 80% chance to start if playing
        minutes_played = np.random.randint(60, 91) if started else np.random.randint(10, 45)
        
        # Position-based performance generation
        if position_id == 24:  # Goalkeeper
            goals = 0
            assists = np.random.choice([0, 0, 0, 1], p=[0.9, 0.05, 0.04, 0.01])
            saves = np.random.randint(0, 8)
            goals_conceded = fixture['opponent_goals'] if started else 0
            clean_sheet = (goals_conceded == 0) and started
            shots = np.random.randint(0, 2)
            passes = np.random.randint(20, 60)
            tackles = np.random.randint(0, 3)
            
        elif position_id == 25:  # Defender
            goals = np.random.choice([0, 0, 0, 1], p=[0.85, 0.1, 0.04, 0.01])
            assists = np.random.choice([0, 0, 1], p=[0.8, 0.15, 0.05])
            saves = 0
            goals_conceded = 0
            clean_sheet = False
            shots = np.random.randint(0, 4)
            passes = np.random.randint(30, 80)
            tackles = np.random.randint(1, 8)
            
        elif position_id == 26:  # Midfielder
            goals = np.random.choice([0, 0, 1, 2], p=[0.7, 0.2, 0.08, 0.02])
            assists = np.random.choice([0, 0, 1, 2], p=[0.6, 0.25, 0.12, 0.03])
            saves = 0
            goals_conceded = 0
            clean_sheet = False
            shots = np.random.randint(0, 6)
            passes = np.random.randint(40, 100)
            tackles = np.random.randint(0, 6)
            
        else:  # Forward
            goals = np.random.choice([0, 1, 2, 3], p=[0.5, 0.35, 0.12, 0.03])
            assists = np.random.choice([0, 0, 1], p=[0.7, 0.2, 0.1])
            saves = 0
            goals_conceded = 0
            clean_sheet = False
            shots = np.random.randint(1, 8)
            passes = np.random.randint(15, 50)
            tackles = np.random.randint(0, 3)
        
        # Common stats for all positions
        shots_on_target = min(shots, np.random.randint(0, shots + 1)) if shots > 0 else 0
        passes_completed = int(passes * np.random.uniform(0.75, 0.95))
        pass_accuracy = (passes_completed / passes * 100) if passes > 0 else 0
        
        interceptions = np.random.randint(0, 5)
        clearances = np.random.randint(0, 8) if position_id in [24, 25] else np.random.randint(0, 3)
        
        yellow_cards = np.random.choice([0, 0, 0, 1], p=[0.9, 0.05, 0.04, 0.01])
        red_cards = np.random.choice([0, 0, 1], p=[0.98, 0.015, 0.005])
        
        fouls_committed = np.random.randint(0, 4)
        fouls_suffered = np.random.randint(0, 5)
        
        # Generate rating based on performance
        base_rating = 6.0
        if goals > 0:
            base_rating += goals * 0.5
        if assists > 0:
            base_rating += assists * 0.3
        if yellow_cards > 0:
            base_rating -= 0.2
        if red_cards > 0:
            base_rating -= 1.0
        
        rating = max(5.0, min(10.0, base_rating + np.random.uniform(-0.5, 0.5)))
        
        # Player of the match (rare)
        player_of_match = (rating >= 8.5) and (np.random.random() < 0.05)
        
        return {
            'match_id': fixture['match_id'],
            'player_id': player_id,
            'player_name': player_data['name'],
            'jersey_number': player_data['jersey_number'],
            'position': self.get_position_name(position_id),
            'match_date': fixture['match_date'],
            'competition': fixture['competition'],
            'opponent': fixture['opponent'],
            'home_away': fixture['home_away'],
            'result': fixture['result'],
            'played': True,
            'started': started,
            'minutes_played': minutes_played,
            'goals': goals,
            'assists': assists,
            'shots': shots,
            'shots_on_target': shots_on_target,
            'passes': passes,
            'passes_completed': passes_completed,
            'pass_accuracy': round(pass_accuracy, 1),
            'tackles': tackles,
            'interceptions': interceptions,
            'clearances': clearances,
            'yellow_cards': yellow_cards,
            'red_cards': red_cards,
            'fouls_committed': fouls_committed,
            'fouls_suffered': fouls_suffered,
            'saves': saves,
            'goals_conceded': goals_conceded,
            'clean_sheet': clean_sheet,
            'rating': round(rating, 2),
            'player_of_match': player_of_match
        }
    
    def get_position_name(self, position_id):
        """Convert position ID to name."""
        position_map = {
            24: 'Goalkeeper',
            25: 'Defender',
            26: 'Midfielder',
            27: 'Forward'
        }
        return position_map.get(position_id, 'Unknown')
    
    def create_match_by_match_database(self):
        """Create complete match-by-match database."""
        logger.info("🚀 Creating match-by-match database")
        
        # Generate fixtures
        fixtures = self.generate_season_fixtures()
        
        # Generate player performances for each match
        all_match_records = []
        
        for i, fixture in enumerate(fixtures):
            logger.info(f"📊 Processing match {i+1}/{len(fixtures)}: {fixture['match_name']}")
            
            # Create performance record for each player
            for _, player in self.squad_data.iterrows():
                performance = self.generate_player_match_performance(player, fixture, None)
                all_match_records.append(performance)
        
        self.match_records = all_match_records
        logger.info(f"✅ Created {len(all_match_records)} individual match records")
        
        return fixtures, all_match_records
    
    def save_to_database(self, fixtures, match_records):
        """Save data to SQLite database."""
        logger.info("💾 Saving to SQLite database")
        
        # Create database directory
        os.makedirs('data/manchester_city_sql_database', exist_ok=True)
        
        # Connect to SQLite database
        db_path = 'data/manchester_city_sql_database/manchester_city_2023_24.db'
        conn = sqlite3.connect(db_path)
        
        # Create fixtures table
        fixtures_df = pd.DataFrame(fixtures)
        fixtures_df.to_sql('fixtures', conn, if_exists='replace', index=False)
        
        # Create player match statistics table
        match_records_df = pd.DataFrame(match_records)
        match_records_df.to_sql('player_match_statistics', conn, if_exists='replace', index=False)
        
        # Create players table
        players_df = self.squad_data[['player_id', 'name', 'jersey_number', 'position_id']].copy()
        players_df.to_sql('players', conn, if_exists='replace', index=False)
        
        conn.close()
        logger.info(f"✅ Database saved to: {db_path}")
        
        return db_path
    
    def save_csv_files(self, fixtures, match_records):
        """Save data as CSV files."""
        logger.info("📄 Saving CSV files")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save fixtures
        fixtures_df = pd.DataFrame(fixtures)
        fixtures_file = f"data/manchester_city_sql_database/fixtures_{timestamp}.csv"
        fixtures_df.to_csv(fixtures_file, index=False)
        
        # Save match records
        match_records_df = pd.DataFrame(match_records)
        match_records_file = f"data/manchester_city_sql_database/player_match_statistics_{timestamp}.csv"
        match_records_df.to_csv(match_records_file, index=False)
        
        logger.info(f"✅ CSV files saved")
        return fixtures_file, match_records_file

def main():
    """Main execution function."""
    creator = MatchByMatchDatabaseCreator()
    
    # Create match-by-match database
    fixtures, match_records = creator.create_match_by_match_database()
    
    # Save to database and CSV
    db_path = creator.save_to_database(fixtures, match_records)
    fixtures_file, match_records_file = creator.save_csv_files(fixtures, match_records)
    
    # Print summary
    print("\n" + "="*80)
    print("🏆 MANCHESTER CITY MATCH-BY-MATCH DATABASE CREATED")
    print("="*80)
    
    print(f"📊 Database Summary:")
    print(f"   • Total Matches: {len(fixtures)}")
    print(f"   • Total Player Records: {len(match_records)}")
    print(f"   • Players: {len(creator.squad_data)}")
    print(f"   • Competitions: {len(creator.competitions)}")
    
    print(f"\n📁 Files Created:")
    print(f"   • SQLite Database: {db_path}")
    print(f"   • Fixtures CSV: {fixtures_file}")
    print(f"   • Player Statistics CSV: {match_records_file}")
    
    print(f"\n🔍 SQL Query Examples:")
    print(f"   • SELECT * FROM player_match_statistics WHERE player_name = 'Erling Håland';")
    print(f"   • SELECT player_name, SUM(goals) FROM player_match_statistics GROUP BY player_name;")
    print(f"   • SELECT * FROM fixtures WHERE competition = 'Premier League';")
    print(f"   • SELECT player_name, goals, assists, rating FROM player_match_statistics WHERE match_id = 1;")
    
    print("="*80)

if __name__ == "__main__":
    main()
