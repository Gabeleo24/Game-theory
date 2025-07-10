#!/usr/bin/env python3
"""
Migrate FBRef Data to PostgreSQL
Transfer SQLite FBRef data to PostgreSQL database for comparison with SportMonks data
"""

import sqlite3
import psycopg2
import psycopg2.extras
import pandas as pd
import yaml
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FBRefDataMigrator:
    """Migrate FBRef data from SQLite to PostgreSQL."""
    
    def __init__(self):
        """Initialize database connections."""
        self.sqlite_path = "data/fbref_scraped/fbref_data.db"
        self.load_config()
        self.setup_postgresql_connection()
        self.setup_sqlite_connection()
        
    def load_config(self):
        """Load database configuration."""
        try:
            with open('config/api_keys.yaml', 'r') as f:
                config = yaml.safe_load(f)
            self.db_config = config['database']
            logger.info("✅ Configuration loaded")
        except FileNotFoundError:
            logger.error("❌ Config file not found")
            raise
            
    def setup_postgresql_connection(self):
        """Setup PostgreSQL connection."""
        try:
            self.pg_conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['name'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            self.pg_cursor = self.pg_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            logger.info("✅ PostgreSQL connection established")
        except psycopg2.Error as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            raise
            
    def setup_sqlite_connection(self):
        """Setup SQLite connection."""
        try:
            self.sqlite_conn = sqlite3.connect(self.sqlite_path)
            logger.info("✅ SQLite connection established")
        except sqlite3.Error as e:
            logger.error(f"❌ SQLite connection failed: {e}")
            raise
    
    def migrate_match_results(self):
        """Migrate match results from SQLite to PostgreSQL."""
        
        logger.info("📊 Migrating match results")
        
        # Extract data from SQLite
        matches_df = pd.read_sql_query("""
            SELECT 
                season, match_date, competition, matchday, home_away, opponent,
                manchester_city_score, opponent_score, result,
                possession_percentage, shots_total, shots_on_target, shots_off_target,
                shots_blocked, corners, offsides, fouls_committed, fouls_suffered,
                yellow_cards, red_cards, passes_total, passes_completed, pass_accuracy,
                tackles_total, tackles_won, interceptions, clearances, blocks,
                attendance, venue, referee
            FROM match_results
            ORDER BY match_date
        """, self.sqlite_conn)
        
        if matches_df.empty:
            logger.warning("⚠️ No match results found in SQLite")
            return 0
        
        # Clear existing data
        self.pg_cursor.execute("DELETE FROM fbref.fbref_match_results")
        
        # Insert data into PostgreSQL
        inserted_count = 0
        
        for _, row in matches_df.iterrows():
            try:
                self.pg_cursor.execute("""
                    INSERT INTO fbref.fbref_match_results (
                        season, match_date, competition, matchday, home_away, opponent,
                        manchester_city_score, opponent_score, result,
                        possession_percentage, shots_total, shots_on_target, shots_off_target,
                        shots_blocked, corners, offsides, fouls_committed, fouls_suffered,
                        yellow_cards, red_cards, passes_total, passes_completed, pass_accuracy,
                        tackles_total, tackles_won, interceptions, clearances, blocks,
                        attendance, venue, referee
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    row['season'], row['match_date'], row['competition'], row['matchday'],
                    row['home_away'], row['opponent'], row['manchester_city_score'],
                    row['opponent_score'], row['result'], row['possession_percentage'],
                    row['shots_total'], row['shots_on_target'], row['shots_off_target'],
                    row['shots_blocked'], row['corners'], row['offsides'],
                    row['fouls_committed'], row['fouls_suffered'], row['yellow_cards'],
                    row['red_cards'], row['passes_total'], row['passes_completed'],
                    row['pass_accuracy'], row['tackles_total'], row['tackles_won'],
                    row['interceptions'], row['clearances'], row['blocks'],
                    row['attendance'], row['venue'], row['referee']
                ))
                inserted_count += 1
                
            except Exception as e:
                logger.error(f"❌ Error inserting match: {e}")
                continue
        
        self.pg_conn.commit()
        logger.info(f"✅ Migrated {inserted_count} match results")
        return inserted_count
    
    def migrate_player_performances(self):
        """Migrate player match performances from SQLite to PostgreSQL."""
        
        logger.info("🎭 Migrating player performances")
        
        # Get match IDs mapping
        self.pg_cursor.execute("""
            SELECT id, match_date, opponent, competition 
            FROM fbref.fbref_match_results 
            ORDER BY match_date
        """)
        pg_matches = {(row['match_date'], row['opponent'], row['competition']): row['id'] 
                     for row in self.pg_cursor.fetchall()}
        
        # Extract player performances from SQLite
        performances_df = pd.read_sql_query("""
            SELECT 
                pmp.*,
                mr.match_date,
                mr.opponent,
                mr.competition
            FROM player_match_performances pmp
            JOIN match_results mr ON pmp.match_id = mr.match_id
            ORDER BY mr.match_date, pmp.player_name
        """, self.sqlite_conn)
        
        if performances_df.empty:
            logger.warning("⚠️ No player performances found in SQLite")
            return 0
        
        # Clear existing data
        self.pg_cursor.execute("DELETE FROM fbref.fbref_player_performances")
        
        # Insert data into PostgreSQL
        inserted_count = 0
        
        for _, row in performances_df.iterrows():
            # Find matching PostgreSQL match ID
            match_key = (row['match_date'], row['opponent'], row['competition'])
            pg_match_id = pg_matches.get(match_key)
            
            if not pg_match_id:
                logger.warning(f"⚠️ No matching PostgreSQL match for {match_key}")
                continue
            
            try:
                self.pg_cursor.execute("""
                    INSERT INTO fbref.fbref_player_performances (
                        match_result_id, player_name, team_name, started, minutes_played,
                        position, formation_position, substituted_in, substituted_out,
                        goals, assists, shots_total, shots_on_target, shots_off_target,
                        shots_blocked, big_chances_created, big_chances_missed,
                        passes_total, passes_completed, pass_accuracy, key_passes,
                        through_balls, long_balls, crosses_total, crosses_accurate,
                        tackles_total, tackles_won, tackle_success_rate, interceptions,
                        clearances, blocks, headed_clearances, duels_total, duels_won,
                        duel_success_rate, aerial_duels_total, aerial_duels_won,
                        aerial_success_rate, yellow_cards, red_cards, fouls_committed,
                        fouls_suffered, touches, dribbles_attempted, dribbles_successful,
                        dribble_success_rate, dispossessed, distance_covered, sprints,
                        rating, expected_goals, expected_assists
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                """, (
                    pg_match_id, row['player_name'], row['team_name'], row['started'],
                    row['minutes_played'], row['position'], row.get('formation_position'),
                    row.get('substituted_in'), row.get('substituted_out'), row['goals'],
                    row['assists'], row['shots_total'], row['shots_on_target'],
                    row['shots_off_target'], row.get('shots_blocked', 0),
                    row.get('big_chances_created', 0), row.get('big_chances_missed', 0),
                    row['passes_total'], row['passes_completed'], row['pass_accuracy'],
                    row.get('key_passes', 0), row.get('through_balls', 0),
                    row.get('long_balls', 0), row.get('crosses_total', 0),
                    row.get('crosses_accurate', 0), row['tackles_total'],
                    row['tackles_won'], row.get('tackle_success_rate', 0.0),
                    row['interceptions'], row['clearances'], row.get('blocks', 0),
                    row.get('headed_clearances', 0), row.get('duels_total', 0),
                    row.get('duels_won', 0), row.get('duel_success_rate', 0.0),
                    row.get('aerial_duels_total', 0), row.get('aerial_duels_won', 0),
                    row.get('aerial_success_rate', 0.0), row['yellow_cards'],
                    row['red_cards'], row['fouls_committed'], row['fouls_suffered'],
                    row['touches'], row.get('dribbles_attempted', 0),
                    row.get('dribbles_successful', 0), row.get('dribble_success_rate', 0.0),
                    row.get('dispossessed', 0), row['distance_covered'],
                    row.get('sprints', 0), row['rating'], row.get('expected_goals', 0.0),
                    row.get('expected_assists', 0.0)
                ))
                inserted_count += 1
                
            except Exception as e:
                logger.error(f"❌ Error inserting performance for {row['player_name']}: {e}")
                continue
        
        self.pg_conn.commit()
        logger.info(f"✅ Migrated {inserted_count} player performances")
        return inserted_count
    
    def migrate_player_season_stats(self):
        """Migrate player season statistics from SQLite to PostgreSQL."""
        
        logger.info("📈 Migrating player season stats")
        
        # Extract season stats from SQLite
        season_stats_df = pd.read_sql_query("""
            SELECT 
                ps.player_name,
                p.position,
                p.nationality,
                p.age,
                ps.matches_played,
                ps.starts,
                ps.minutes,
                ps.goals,
                ps.assists,
                ps.shots,
                ps.shots_on_target,
                ps.passes_completed,
                ps.passes_attempted,
                ps.tackles,
                ps.interceptions,
                ps.clearances,
                ps.blocks,
                ps.yellow_cards,
                ps.red_cards,
                ps.fouls_committed,
                ps.fouls_drawn
            FROM player_stats ps
            LEFT JOIN players p ON ps.player_name = p.player_name
            WHERE ps.team_name = 'Manchester City'
        """, self.sqlite_conn)
        
        if season_stats_df.empty:
            logger.warning("⚠️ No player season stats found in SQLite")
            return 0
        
        # Clear existing data
        self.pg_cursor.execute("DELETE FROM fbref.fbref_player_season_stats")
        
        # Insert data into PostgreSQL
        inserted_count = 0
        
        for _, row in season_stats_df.iterrows():
            try:
                # Calculate derived statistics
                shot_accuracy = (row['shots_on_target'] / max(row['shots'], 1)) * 100 if row['shots'] > 0 else 0
                pass_accuracy = (row['passes_completed'] / max(row['passes_attempted'], 1)) * 100 if row['passes_attempted'] > 0 else 0
                goals_per_90 = (row['goals'] * 90 / max(row['minutes'], 1)) if row['minutes'] > 0 else 0
                assists_per_90 = (row['assists'] * 90 / max(row['minutes'], 1)) if row['minutes'] > 0 else 0
                
                self.pg_cursor.execute("""
                    INSERT INTO fbref.fbref_player_season_stats (
                        player_name, position, nationality, age, matches_played, starts,
                        total_minutes, goals, assists, shots, shots_on_target, shot_accuracy,
                        passes_attempted, passes_completed, avg_pass_accuracy, tackles,
                        interceptions, clearances, blocks, yellow_cards, red_cards,
                        fouls_committed, fouls_suffered, goals_per_90, assists_per_90
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    row['player_name'], row['position'], row['nationality'], row['age'],
                    row['matches_played'], row.get('starts', 0), row['minutes'],
                    row['goals'], row['assists'], row['shots'], row['shots_on_target'],
                    shot_accuracy, row['passes_attempted'], row['passes_completed'],
                    pass_accuracy, row['tackles'], row['interceptions'], row['clearances'],
                    row['blocks'], row['yellow_cards'], row['red_cards'],
                    row['fouls_committed'], row.get('fouls_drawn', 0), goals_per_90, assists_per_90
                ))
                inserted_count += 1
                
            except Exception as e:
                logger.error(f"❌ Error inserting season stats for {row['player_name']}: {e}")
                continue
        
        self.pg_conn.commit()
        logger.info(f"✅ Migrated {inserted_count} player season stats")
        return inserted_count
    
    def migrate_competitions(self):
        """Migrate competition data from SQLite to PostgreSQL."""
        
        logger.info("🏆 Migrating competitions")
        
        # Extract competitions from SQLite
        competitions_df = pd.read_sql_query("""
            SELECT 
                competition_name,
                competition_type,
                season,
                total_matches,
                matches_won,
                matches_drawn,
                matches_lost,
                goals_for,
                goals_against,
                final_position,
                trophy_won
            FROM competitions
        """, self.sqlite_conn)
        
        if competitions_df.empty:
            logger.warning("⚠️ No competitions found in SQLite")
            return 0
        
        # Clear existing data
        self.pg_cursor.execute("DELETE FROM fbref.fbref_competitions")
        
        # Insert data into PostgreSQL
        inserted_count = 0
        
        for _, row in competitions_df.iterrows():
            try:
                self.pg_cursor.execute("""
                    INSERT INTO fbref.fbref_competitions (
                        competition_name, competition_type, season, total_matches,
                        matches_won, matches_drawn, matches_lost, goals_for, goals_against,
                        final_position, trophy_won
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    row['competition_name'], row['competition_type'], row['season'],
                    row['total_matches'], row['matches_won'], row['matches_drawn'],
                    row['matches_lost'], row['goals_for'], row['goals_against'],
                    row['final_position'], row['trophy_won']
                ))
                inserted_count += 1
                
            except Exception as e:
                logger.error(f"❌ Error inserting competition {row['competition_name']}: {e}")
                continue
        
        self.pg_conn.commit()
        logger.info(f"✅ Migrated {inserted_count} competitions")
        return inserted_count
    
    def run_complete_migration(self):
        """Run complete data migration."""
        
        print("🚀 MIGRATING FBREF DATA TO POSTGRESQL")
        print("=" * 60)
        print(f"Migration started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Migrate all data
            matches_count = self.migrate_match_results()
            performances_count = self.migrate_player_performances()
            season_stats_count = self.migrate_player_season_stats()
            competitions_count = self.migrate_competitions()
            
            print(f"\n✅ MIGRATION COMPLETE!")
            print(f"📊 Migration Summary:")
            print(f"   • Match Results: {matches_count}")
            print(f"   • Player Performances: {performances_count}")
            print(f"   • Season Statistics: {season_stats_count}")
            print(f"   • Competitions: {competitions_count}")
            print(f"   • Total Records: {matches_count + performances_count + season_stats_count + competitions_count}")
            
            return {
                'matches': matches_count,
                'performances': performances_count,
                'season_stats': season_stats_count,
                'competitions': competitions_count,
                'total': matches_count + performances_count + season_stats_count + competitions_count
            }
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            self.pg_conn.rollback()
            return None
        
        finally:
            self.sqlite_conn.close()
            self.pg_conn.close()

def main():
    """Main execution function."""
    
    migrator = FBRefDataMigrator()
    results = migrator.run_complete_migration()
    
    if results:
        print(f"\n🎯 Migration Results: {results['total']} total records migrated")
        print("🎉 Ready for data comparison analysis!")

if __name__ == "__main__":
    main()
