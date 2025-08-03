#!/usr/bin/env python3
"""
Create Unified Data Views
Create PostgreSQL views that combine both data sources for comprehensive analysis
"""

import psycopg2
import psycopg2.extras
import yaml
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UnifiedViewCreator:
    """Create unified views combining SportMonks and FBRef data."""
    
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
    
    def create_unified_team_view(self):
        """Create unified view for team information."""
        
        logger.info("🏟️ Creating unified team view")
        
        self.cursor.execute("DROP VIEW IF EXISTS unified_teams CASCADE")
        
        self.cursor.execute("""
            CREATE VIEW unified_teams AS
            SELECT 
                id,
                name,
                short_name,
                country,
                'SportMonks' as data_source,
                sportmonks_id as external_id,
                api_football_id as secondary_id,
                created_at,
                updated_at
            FROM teams
            WHERE teams.id IS NOT NULL
            
            UNION ALL
            
            SELECT 
                NULL as id,
                'Manchester City' as name,
                'MCI' as short_name,
                'England' as country,
                'FBRef' as data_source,
                NULL as external_id,
                NULL as secondary_id,
                CURRENT_TIMESTAMP as created_at,
                CURRENT_TIMESTAMP as updated_at
            WHERE NOT EXISTS (
                SELECT 1 FROM teams WHERE LOWER(name) LIKE '%manchester city%'
            )
        """)
        
        logger.info("✅ Unified team view created")
    
    def create_unified_match_view(self):
        """Create unified view for match data."""
        
        logger.info("📅 Creating unified match view")
        
        self.cursor.execute("DROP VIEW IF EXISTS unified_matches CASCADE")
        
        self.cursor.execute("""
            CREATE VIEW unified_matches AS
            -- SportMonks fixtures (when available)
            SELECT 
                f.id,
                f.match_date,
                ht.name as home_team,
                at.name as away_team,
                f.home_score,
                f.away_score,
                CASE 
                    WHEN f.home_score > f.away_score THEN 'Home Win'
                    WHEN f.home_score < f.away_score THEN 'Away Win'
                    WHEN f.home_score = f.away_score THEN 'Draw'
                    ELSE 'TBD'
                END as result,
                c.name as competition,
                'SportMonks' as data_source,
                f.created_at,
                f.updated_at
            FROM fixtures f
            LEFT JOIN teams ht ON f.home_team_id = ht.id
            LEFT JOIN teams at ON f.away_team_id = at.id
            LEFT JOIN competitions c ON f.competition_id = c.id
            WHERE f.id IS NOT NULL
            
            UNION ALL
            
            -- FBRef matches (when available)
            SELECT 
                mr.id,
                mr.match_date::date,
                CASE WHEN mr.home_away = 'Home' THEN 'Manchester City' ELSE mr.opponent END as home_team,
                CASE WHEN mr.home_away = 'Away' THEN 'Manchester City' ELSE mr.opponent END as away_team,
                CASE WHEN mr.home_away = 'Home' THEN mr.manchester_city_score ELSE mr.opponent_score END as home_score,
                CASE WHEN mr.home_away = 'Away' THEN mr.manchester_city_score ELSE mr.opponent_score END as away_score,
                mr.result,
                mr.competition,
                'FBRef' as data_source,
                mr.created_at,
                mr.updated_at
            FROM fbref.fbref_match_results mr
            WHERE mr.id IS NOT NULL
        """)
        
        logger.info("✅ Unified match view created")
    
    def create_unified_player_view(self):
        """Create unified view for player data."""
        
        logger.info("👥 Creating unified player view")
        
        self.cursor.execute("DROP VIEW IF EXISTS unified_players CASCADE")
        
        # First check if players table exists and has data
        try:
            self.cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'players' LIMIT 5")
            player_columns = [row[0] for row in self.cursor.fetchall()]

            self.cursor.execute("SELECT COUNT(*) FROM players")
            player_count = self.cursor.fetchone()[0]

            if player_count > 0 and 'name' in player_columns:
                # Include SportMonks players if available
                sportmonks_players_query = """
                    SELECT
                        p.id,
                        p.name as player_name,
                        p.position,
                        p.nationality,
                        p.age,
                        t.name as team_name,
                        'SportMonks' as data_source,
                        p.sportmonks_id as external_id,
                        p.api_football_id as secondary_id,
                        p.created_at,
                        p.updated_at
                    FROM players p
                    LEFT JOIN squad_members sm ON p.id = sm.player_id
                    LEFT JOIN teams t ON sm.team_id = t.id
                    WHERE p.id IS NOT NULL

                    UNION ALL
                """
            else:
                # No SportMonks players available
                sportmonks_players_query = ""

        except:
            # Table doesn't exist or has issues
            sportmonks_players_query = ""

        self.cursor.execute(f"""
            CREATE VIEW unified_players AS
            {sportmonks_players_query}
            -- FBRef players (when available)
            SELECT
                NULL as id,
                fps.player_name,
                fps.position,
                fps.nationality,
                fps.age,
                fps.team_name,
                'FBRef' as data_source,
                NULL as external_id,
                NULL as secondary_id,
                fps.created_at,
                fps.updated_at
            FROM fbref.fbref_player_season_stats fps
            WHERE fps.player_name IS NOT NULL
        """)
        
        logger.info("✅ Unified player view created")
    
    def create_manchester_city_dashboard_view(self):
        """Create specialized view for Manchester City analytics dashboard."""
        
        logger.info("🏆 Creating Manchester City dashboard view")
        
        self.cursor.execute("DROP VIEW IF EXISTS manchester_city_dashboard CASCADE")
        
        self.cursor.execute("""
            CREATE VIEW manchester_city_dashboard AS
            SELECT 
                -- Player Information
                fps.player_name,
                fps.position,
                fps.nationality,
                fps.age,
                
                -- Season Statistics
                fps.matches_played,
                fps.total_minutes,
                fps.goals,
                fps.assists,
                fps.goals + fps.assists as goal_contributions,
                fps.goals_per_90,
                fps.assists_per_90,
                
                -- Performance Metrics
                fps.avg_rating,
                fps.shots,
                fps.shots_on_target,
                fps.shot_accuracy,
                fps.avg_pass_accuracy,
                fps.tackles,
                fps.interceptions,
                
                -- Disciplinary
                fps.yellow_cards,
                fps.red_cards,
                
                -- Calculated Fields
                CASE 
                    WHEN fps.total_minutes > 0 THEN ROUND((fps.goals + fps.assists) * 90.0 / fps.total_minutes, 2)
                    ELSE 0 
                END as contributions_per_90,
                
                CASE 
                    WHEN fps.position LIKE '%FW%' OR fps.position LIKE '%Forward%' THEN 'Forward'
                    WHEN fps.position LIKE '%MF%' OR fps.position LIKE '%Midfielder%' THEN 'Midfielder'
                    WHEN fps.position LIKE '%DF%' OR fps.position LIKE '%Defender%' THEN 'Defender'
                    WHEN fps.position LIKE '%GK%' OR fps.position LIKE '%Goalkeeper%' THEN 'Goalkeeper'
                    ELSE 'Unknown'
                END as position_group,
                
                -- Data Source
                'FBRef' as data_source,
                fps.created_at,
                fps.updated_at
                
            FROM fbref.fbref_player_season_stats fps
            WHERE fps.team_name = 'Manchester City'
            ORDER BY fps.goals DESC, fps.assists DESC
        """)
        
        logger.info("✅ Manchester City dashboard view created")
    
    def create_match_performance_summary_view(self):
        """Create view summarizing match performance data."""
        
        logger.info("📊 Creating match performance summary view")
        
        self.cursor.execute("DROP VIEW IF EXISTS match_performance_summary CASCADE")
        
        self.cursor.execute("""
            CREATE VIEW match_performance_summary AS
            SELECT 
                mr.id as match_id,
                mr.match_date,
                mr.opponent,
                mr.competition,
                mr.home_away,
                mr.manchester_city_score,
                mr.opponent_score,
                mr.result,
                mr.possession_percentage,
                mr.shots_total,
                mr.shots_on_target,
                mr.pass_accuracy,
                
                -- Match Context
                CASE 
                    WHEN mr.opponent IN ('Arsenal', 'Liverpool', 'Chelsea', 'Tottenham', 'Manchester United') 
                    THEN 'Big Six'
                    WHEN mr.competition = 'Champions League' 
                    THEN 'European'
                    WHEN mr.competition = 'Premier League' 
                    THEN 'Domestic League'
                    ELSE 'Cup Competition'
                END as match_category,
                
                -- Performance Indicators
                CASE 
                    WHEN mr.possession_percentage >= 70 THEN 'Dominant'
                    WHEN mr.possession_percentage >= 55 THEN 'Controlled'
                    WHEN mr.possession_percentage >= 45 THEN 'Balanced'
                    ELSE 'Under Pressure'
                END as possession_category,
                
                CASE 
                    WHEN mr.shots_total >= 20 THEN 'High'
                    WHEN mr.shots_total >= 12 THEN 'Medium'
                    ELSE 'Low'
                END as attacking_intensity,
                
                -- Goal Difference
                mr.manchester_city_score - mr.opponent_score as goal_difference,
                
                -- Points
                CASE 
                    WHEN mr.result = 'Win' THEN 3
                    WHEN mr.result = 'Draw' THEN 1
                    ELSE 0
                END as points,
                
                mr.data_source,
                mr.created_at
                
            FROM fbref.fbref_match_results mr
            ORDER BY mr.match_date
        """)
        
        logger.info("✅ Match performance summary view created")
    
    def create_analytics_summary_view(self):
        """Create high-level analytics summary view."""
        
        logger.info("📈 Creating analytics summary view")
        
        self.cursor.execute("DROP VIEW IF EXISTS analytics_summary CASCADE")
        
        self.cursor.execute("""
            CREATE VIEW analytics_summary AS
            SELECT 
                'Manchester City 2023-24 Season' as summary_title,
                
                -- Match Statistics
                (SELECT COUNT(*) FROM fbref.fbref_match_results) as total_matches,
                (SELECT COUNT(*) FROM fbref.fbref_match_results WHERE result = 'Win') as wins,
                (SELECT COUNT(*) FROM fbref.fbref_match_results WHERE result = 'Draw') as draws,
                (SELECT COUNT(*) FROM fbref.fbref_match_results WHERE result = 'Loss') as losses,
                
                -- Goal Statistics
                (SELECT SUM(manchester_city_score) FROM fbref.fbref_match_results) as goals_scored,
                (SELECT SUM(opponent_score) FROM fbref.fbref_match_results) as goals_conceded,
                (SELECT SUM(manchester_city_score) - SUM(opponent_score) FROM fbref.fbref_match_results) as goal_difference,
                
                -- Player Statistics
                (SELECT COUNT(*) FROM fbref.fbref_player_season_stats) as total_players,
                (SELECT COUNT(*) FROM fbref.fbref_player_season_stats WHERE matches_played > 10) as regular_players,
                (SELECT player_name FROM fbref.fbref_player_season_stats ORDER BY goals DESC LIMIT 1) as top_scorer,
                (SELECT MAX(goals) FROM fbref.fbref_player_season_stats) as top_scorer_goals,
                
                -- Performance Averages
                (SELECT ROUND(AVG(possession_percentage), 1) FROM fbref.fbref_match_results) as avg_possession,
                (SELECT ROUND(AVG(shots_total), 1) FROM fbref.fbref_match_results) as avg_shots,
                (SELECT ROUND(AVG(pass_accuracy), 1) FROM fbref.fbref_match_results) as avg_pass_accuracy,
                
                -- Competition Performance
                (SELECT COUNT(*) FROM fbref.fbref_match_results WHERE competition = 'Premier League') as pl_matches,
                (SELECT COUNT(*) FROM fbref.fbref_match_results WHERE competition = 'Champions League') as cl_matches,
                (SELECT COUNT(*) FROM fbref.fbref_match_results WHERE competition = 'FA Cup') as fa_cup_matches,
                (SELECT COUNT(*) FROM fbref.fbref_match_results WHERE competition = 'EFL Cup') as efl_cup_matches,
                
                -- Data Quality
                'FBRef' as primary_data_source,
                CURRENT_TIMESTAMP as generated_at
        """)
        
        logger.info("✅ Analytics summary view created")
    
    def create_all_unified_views(self):
        """Create all unified views."""
        
        print("🔄 CREATING UNIFIED DATA VIEWS")
        print("=" * 60)
        
        try:
            # Create all views
            self.create_unified_team_view()
            self.create_unified_match_view()
            self.create_unified_player_view()
            self.create_manchester_city_dashboard_view()
            self.create_match_performance_summary_view()
            self.create_analytics_summary_view()
            
            # Commit all changes
            self.conn.commit()
            
            print("\n✅ ALL UNIFIED VIEWS CREATED SUCCESSFULLY!")
            print("📊 Views created:")
            print("   • unified_teams - Combined team data")
            print("   • unified_matches - Combined match data")
            print("   • unified_players - Combined player data")
            print("   • manchester_city_dashboard - MC analytics dashboard")
            print("   • match_performance_summary - Match analysis")
            print("   • analytics_summary - High-level summary")
            
            # Test views
            self.test_views()
            
            return True
            
        except Exception as e:
            print(f"❌ View creation failed: {e}")
            self.conn.rollback()
            return False
        
        finally:
            self.conn.close()
    
    def test_views(self):
        """Test the created views."""
        
        print(f"\n🧪 TESTING UNIFIED VIEWS")
        print("=" * 40)
        
        views_to_test = [
            'unified_teams',
            'unified_matches', 
            'unified_players',
            'manchester_city_dashboard',
            'match_performance_summary',
            'analytics_summary'
        ]
        
        for view in views_to_test:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {view}")
                count = self.cursor.fetchone()[0]
                print(f"   ✅ {view}: {count} records")
            except Exception as e:
                print(f"   ❌ {view}: Error - {e}")
        
        # Show sample data from key views
        print(f"\n📊 SAMPLE DATA:")
        
        try:
            self.cursor.execute("SELECT * FROM analytics_summary")
            summary = self.cursor.fetchone()
            if summary:
                print(f"   🏆 Season Summary:")
                print(f"      • Total Matches: {summary['total_matches']}")
                print(f"      • Record: {summary['wins']}W-{summary['draws']}D-{summary['losses']}L")
                print(f"      • Goals: {summary['goals_scored']}-{summary['goals_conceded']} (+{summary['goal_difference']})")
                print(f"      • Top Scorer: {summary['top_scorer']} ({summary['top_scorer_goals']} goals)")
        except Exception as e:
            print(f"   ⚠️ Could not fetch summary: {e}")

def main():
    """Main execution function."""
    
    creator = UnifiedViewCreator()
    success = creator.create_all_unified_views()
    
    if success:
        print("\n🎉 Unified views ready for comprehensive analysis!")
        print("💡 Use these views to combine SportMonks and FBRef data seamlessly")
    else:
        print("\n💥 View creation failed. Check logs for details.")

if __name__ == "__main__":
    main()
