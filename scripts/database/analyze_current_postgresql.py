#!/usr/bin/env python3
"""
Analyze Current PostgreSQL Database
Examine existing PostgreSQL structure and SportMonks data before adding FBRef data
"""

import psycopg2
import psycopg2.extras
import pandas as pd
import yaml
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PostgreSQLAnalyzer:
    """Analyze current PostgreSQL database structure and data."""
    
    def __init__(self):
        """Initialize database connection."""
        self.load_config()
        self.setup_connection()
        
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
            
    def setup_connection(self):
        """Setup PostgreSQL connection."""
        try:
            self.conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['name'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            logger.info("✅ PostgreSQL connection established")
        except psycopg2.Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
            
    def analyze_database_structure(self):
        """Analyze current database structure."""
        
        print("🔍 POSTGRESQL DATABASE STRUCTURE ANALYSIS")
        print("=" * 60)
        
        # Get all tables
        self.cursor.execute("""
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = self.cursor.fetchall()
        
        if not tables:
            print("📋 No tables found in database")
            return
        
        print(f"📊 Found {len(tables)} tables:")

        for table in tables:
            table_name = table['table_name']
            table_type = table['table_type']

            # Get row count
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = self.cursor.fetchone()[0]
            except Exception as e:
                row_count = f"Error: {e}"

            # Get column count
            try:
                self.cursor.execute(f"""
                    SELECT COUNT(*)
                    FROM information_schema.columns
                    WHERE table_name = %s
                """, (table_name,))
                col_count = self.cursor.fetchone()[0]
            except Exception as e:
                col_count = f"Error: {e}"

            print(f"   📋 {table_name} ({table_type}): {row_count} rows, {col_count} columns")
        
        return tables
    
    def analyze_manchester_city_data(self):
        """Analyze existing Manchester City data."""
        
        print(f"\n🏆 MANCHESTER CITY DATA ANALYSIS")
        print("=" * 50)
        
        # Check for Manchester City in teams table
        try:
            self.cursor.execute("""
                SELECT id, name, short_name, country, sportmonks_id, api_football_id
                FROM teams 
                WHERE LOWER(name) LIKE '%manchester city%' OR LOWER(name) LIKE '%man city%'
            """)
            
            city_teams = self.cursor.fetchall()
            
            if city_teams:
                print("✅ Manchester City found in teams table:")
                for team in city_teams:
                    print(f"   • ID: {team['id']}, Name: {team['name']}")
                    print(f"     SportMonks ID: {team['sportmonks_id']}, API-Football ID: {team['api_football_id']}")
                
                # Get team ID for further analysis
                team_id = city_teams[0]['id']
                
                # Check fixtures
                self.cursor.execute("""
                    SELECT COUNT(*) as fixture_count
                    FROM fixtures 
                    WHERE home_team_id = %s OR away_team_id = %s
                """, (team_id, team_id))
                
                fixture_count = self.cursor.fetchone()['fixture_count']
                print(f"   📅 Fixtures: {fixture_count}")
                
                # Check players
                self.cursor.execute("""
                    SELECT COUNT(DISTINCT p.id) as player_count
                    FROM players p
                    JOIN squad_members sm ON p.id = sm.player_id
                    WHERE sm.team_id = %s
                """, (team_id,))
                
                try:
                    player_count = self.cursor.fetchone()['player_count']
                    print(f"   👥 Players: {player_count}")
                except:
                    print(f"   👥 Players: 0 (no squad_members data)")
                
                # Check match statistics
                self.cursor.execute("""
                    SELECT COUNT(*) as stats_count
                    FROM team_match_statistics tms
                    JOIN fixtures f ON tms.fixture_id = f.id
                    WHERE f.home_team_id = %s OR f.away_team_id = %s
                """, (team_id, team_id))
                
                try:
                    stats_count = self.cursor.fetchone()['stats_count']
                    print(f"   📊 Team match statistics: {stats_count}")
                except:
                    print(f"   📊 Team match statistics: 0")
                
                return team_id
                
            else:
                print("❌ Manchester City not found in teams table")
                return None
                
        except Exception as e:
            print(f"❌ Error analyzing Manchester City data: {e}")
            return None
    
    def analyze_data_sources(self):
        """Analyze what data sources are currently in the database."""
        
        print(f"\n📡 DATA SOURCES ANALYSIS")
        print("=" * 40)
        
        # Check for SportMonks data
        try:
            self.cursor.execute("SELECT COUNT(*) FROM teams WHERE sportmonks_id IS NOT NULL")
            sportmonks_teams = self.cursor.fetchone()[0]
            print(f"   🏟️ Teams with SportMonks ID: {sportmonks_teams}")
        except:
            print(f"   🏟️ Teams with SportMonks ID: 0")
        
        # Check for API-Football data
        try:
            self.cursor.execute("SELECT COUNT(*) FROM teams WHERE api_football_id IS NOT NULL")
            api_football_teams = self.cursor.fetchone()[0]
            print(f"   ⚽ Teams with API-Football ID: {api_football_teams}")
        except:
            print(f"   ⚽ Teams with API-Football ID: 0")
        
        # Check seasons
        try:
            self.cursor.execute("SELECT season_name, is_current FROM seasons ORDER BY season_name")
            seasons = self.cursor.fetchall()
            print(f"   📅 Seasons: {len(seasons)}")
            for season in seasons:
                current = "✅" if season['is_current'] else "  "
                print(f"      {current} {season['season_name']}")
        except:
            print(f"   📅 Seasons: 0")
        
        # Check competitions
        try:
            self.cursor.execute("SELECT name, country, type FROM competitions ORDER BY name")
            competitions = self.cursor.fetchall()
            print(f"   🏆 Competitions: {len(competitions)}")
            for comp in competitions[:5]:  # Show first 5
                print(f"      • {comp['name']} ({comp['country']}, {comp['type']})")
            if len(competitions) > 5:
                print(f"      ... and {len(competitions) - 5} more")
        except:
            print(f"   🏆 Competitions: 0")
    
    def analyze_recent_activity(self):
        """Analyze recent database activity."""
        
        print(f"\n⏰ RECENT ACTIVITY ANALYSIS")
        print("=" * 40)
        
        # Check recent fixtures
        try:
            self.cursor.execute("""
                SELECT COUNT(*) as recent_fixtures
                FROM fixtures 
                WHERE created_at >= NOW() - INTERVAL '30 days'
            """)
            recent_fixtures = self.cursor.fetchone()['recent_fixtures']
            print(f"   📅 Fixtures added in last 30 days: {recent_fixtures}")
        except:
            print(f"   📅 Recent fixtures: Unable to determine")
        
        # Check data freshness
        try:
            self.cursor.execute("""
                SELECT 
                    MAX(created_at) as latest_fixture,
                    MIN(created_at) as earliest_fixture
                FROM fixtures
            """)
            result = self.cursor.fetchone()
            if result['latest_fixture']:
                print(f"   📊 Latest fixture: {result['latest_fixture']}")
                print(f"   📊 Earliest fixture: {result['earliest_fixture']}")
            else:
                print(f"   📊 No fixture data found")
        except:
            print(f"   📊 Unable to determine data freshness")
    
    def generate_summary_report(self):
        """Generate comprehensive summary report."""
        
        print(f"\n📋 DATABASE SUMMARY REPORT")
        print("=" * 50)
        
        # Database size
        try:
            self.cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as db_size
            """)
            db_size = self.cursor.fetchone()['db_size']
            print(f"   💾 Database size: {db_size}")
        except:
            print(f"   💾 Database size: Unable to determine")
        
        # Total records across main tables
        main_tables = ['teams', 'players', 'fixtures', 'competitions', 'seasons']
        total_records = 0
        
        print(f"   📊 Record counts:")
        for table in main_tables:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                print(f"      • {table}: {count:,}")
                total_records += count
            except:
                print(f"      • {table}: Table not found")
        
        print(f"   📈 Total records: {total_records:,}")
        
        # Connection info
        print(f"   🔗 Connected to: {self.db_config['host']}:{self.db_config['port']}")
        print(f"   🗄️ Database: {self.db_config['name']}")
        print(f"   👤 User: {self.db_config['user']}")
        
    def run_complete_analysis(self):
        """Run complete database analysis."""
        
        print("🔍 POSTGRESQL DATABASE ANALYSIS")
        print("=" * 80)
        print(f"Analysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Analyze structure
            tables = self.analyze_database_structure()
            
            # Analyze Manchester City data
            city_team_id = self.analyze_manchester_city_data()
            
            # Analyze data sources
            self.analyze_data_sources()
            
            # Analyze recent activity
            self.analyze_recent_activity()
            
            # Generate summary
            self.generate_summary_report()
            
            print(f"\n✅ Analysis complete!")
            
            return {
                'tables_found': len(tables) if tables else 0,
                'manchester_city_id': city_team_id,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return None
        
        finally:
            self.conn.close()

def main():
    """Main execution function."""
    
    analyzer = PostgreSQLAnalyzer()
    results = analyzer.run_complete_analysis()
    
    if results:
        print(f"\n🎯 Analysis Results:")
        print(f"   Tables: {results['tables_found']}")
        print(f"   Manchester City ID: {results['manchester_city_id']}")
        print(f"   Timestamp: {results['analysis_timestamp']}")

if __name__ == "__main__":
    main()
