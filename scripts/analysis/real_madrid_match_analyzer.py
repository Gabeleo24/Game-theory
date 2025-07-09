#!/usr/bin/env python3
"""
REAL MADRID MATCH-LEVEL PLAYER STATISTICS ANALYZER
Detailed individual game analysis for Real Madrid's 2023-2024 Champions League winning season
"""

import psycopg2
import logging
import sys
from typing import List, Tuple, Dict, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class RealMadridMatchAnalyzer:
    """Analyze Real Madrid match-level player statistics."""
    
    def __init__(self):
        """Initialize database connection."""
        try:
            self.conn = psycopg2.connect(
                host='localhost', port=5432, database='soccer_intelligence', 
                user='soccerapp', password='soccerpass123'
            )
            self.cursor = self.conn.cursor()
            logger.info("✅ Database connected")
        except psycopg2.Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            sys.exit(1)
    
    def get_available_matches(self) -> List[Tuple]:
        """Get all available Real Madrid matches from 2023-2024 season."""
        try:
            query = """
                SELECT DISTINCT
                    m.match_id,
                    m.match_date,
                    ht.team_name as home_team,
                    at.team_name as away_team,
                    m.competition,
                    m.season,
                    COUNT(mps.player_id) as player_count
                FROM fixed_matches m
                JOIN fixed_teams ht ON m.home_team_id = ht.team_id
                JOIN fixed_teams at ON m.away_team_id = at.team_id
                LEFT JOIN fixed_match_player_stats mps ON m.match_id = mps.match_id
                WHERE (ht.team_name = 'Real Madrid' OR at.team_name = 'Real Madrid')
                GROUP BY m.match_id, m.match_date, ht.team_name, at.team_name,
                         m.competition, m.season
                ORDER BY m.match_date
            """

            self.cursor.execute(query)
            matches = self.cursor.fetchall()

            logger.info(f"✅ Found {len(matches)} Real Madrid matches")
            return matches

        except Exception as e:
            logger.error(f"Error getting matches: {e}")
            return []
    
    def display_match_list(self, matches: List[Tuple]):
        """Display available matches for selection."""
        
        print("\n" + "=" * 140)
        print("🏆 REAL MADRID 2023-2024 CHAMPIONS LEAGUE WINNING SEASON - MATCH SELECTOR 🏆".center(140))
        print("=" * 140)
        
        # Group by competition
        competitions = {}
        for match in matches:
            (match_id, match_date, home_team, away_team, competition, season, player_count) = match

            if competition not in competitions:
                competitions[competition] = []
            competitions[competition].append(match)

        line_num = 1
        for comp_name, comp_matches in competitions.items():
            print(f"\n📊 {comp_name.upper()}")
            print("-" * 120)
            print(f"{'#':<3} {'Match ID':<10} {'Date':<12} {'Home Team':<25} {'Away Team':<25} {'Season':<12} {'Players':<8}")
            print("-" * 120)

            for match in comp_matches:
                (match_id, match_date, home_team, away_team, competition, season, player_count) = match

                # Format date
                if match_date:
                    date_str = match_date.strftime('%Y-%m-%d') if hasattr(match_date, 'strftime') else str(match_date)[:10]
                else:
                    date_str = 'Unknown'

                # Highlight Real Madrid
                home_display = f"🏆 {home_team}" if home_team == 'Real Madrid' else home_team
                away_display = f"🏆 {away_team}" if away_team == 'Real Madrid' else away_team

                print(f"{line_num:<3} {match_id:<10} {date_str:<12} {home_display:<25} {away_display:<25} {season:<12} {player_count:<8}")
                line_num += 1
        
        print("-" * 140)
        print(f"Total Matches: {len(matches)} | Use: python {sys.argv[0]} <match_id> to view detailed stats")
        print("=" * 140)
    
    def get_match_details(self, match_id: int) -> Optional[Dict]:
        """Get detailed match information."""
        try:
            query = """
                SELECT
                    m.match_id,
                    m.match_date,
                    ht.team_name as home_team,
                    at.team_name as away_team,
                    m.competition,
                    m.season
                FROM fixed_matches m
                JOIN fixed_teams ht ON m.home_team_id = ht.team_id
                JOIN fixed_teams at ON m.away_team_id = at.team_id
                WHERE m.match_id = %s
            """

            self.cursor.execute(query, (match_id,))
            result = self.cursor.fetchone()

            if not result:
                return None

            (match_id, match_date, home_team, away_team, competition, season) = result

            # Calculate match result from player stats
            home_goals, away_goals = self.get_match_score(match_id, home_team, away_team)

            return {
                'match_id': match_id,
                'match_date': match_date,
                'home_team': home_team,
                'away_team': away_team,
                'home_goals': home_goals,
                'away_goals': away_goals,
                'competition': competition,
                'season': season,
                'venue_name': 'Unknown',
                'venue_city': 'Unknown',
                'referee': 'Unknown'
            }

        except Exception as e:
            logger.error(f"Error getting match details: {e}")
            return None

    def get_match_score(self, match_id: int, home_team: str, away_team: str) -> tuple:
        """Calculate match score from player statistics."""
        try:
            query = """
                SELECT
                    t.team_name,
                    SUM(mps.goals) as team_goals
                FROM fixed_match_player_stats mps
                JOIN fixed_teams t ON mps.team_id = t.team_id
                WHERE mps.match_id = %s
                GROUP BY t.team_name
            """

            self.cursor.execute(query, (match_id,))
            results = self.cursor.fetchall()

            home_goals = 0
            away_goals = 0

            for team_name, goals in results:
                if team_name == home_team:
                    home_goals = goals or 0
                elif team_name == away_team:
                    away_goals = goals or 0

            return home_goals, away_goals

        except Exception as e:
            logger.error(f"Error calculating match score: {e}")
            return 0, 0
    
    def get_match_player_stats(self, match_id: int) -> List[Tuple]:
        """Get detailed player statistics for a specific match."""
        try:
            query = """
                SELECT 
                    p.player_name,
                    mps.position,
                    mps.minutes_played,
                    mps.goals,
                    mps.assists,
                    mps.shots_total,
                    mps.shots_on_target,
                    mps.passes_total,
                    mps.passes_completed,
                    mps.pass_accuracy,
                    mps.tackles_total,
                    mps.tackles_won,
                    mps.interceptions,
                    mps.fouls_committed,
                    mps.fouls_drawn,
                    mps.yellow_cards,
                    mps.red_cards,
                    mps.rating,
                    t.team_name
                FROM fixed_match_player_stats mps
                JOIN fixed_players p ON mps.player_id = p.player_id
                JOIN fixed_teams t ON mps.team_id = t.team_id
                WHERE mps.match_id = %s
                ORDER BY 
                    CASE WHEN t.team_name = 'Real Madrid' THEN 0 ELSE 1 END,
                    CASE 
                        WHEN mps.position = 'G' THEN 1
                        WHEN mps.position = 'D' THEN 2
                        WHEN mps.position = 'M' THEN 3
                        WHEN mps.position = 'F' THEN 4
                        ELSE 5
                    END,
                    mps.minutes_played DESC
            """
            
            self.cursor.execute(query, (match_id,))
            return self.cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            return []
    
    def calculate_enhanced_metrics(self, player_stats: Tuple) -> Dict:
        """Calculate enhanced metrics for a player."""
        (player_name, position, minutes_played, goals, assists, shots_total, shots_on_target,
         passes_total, passes_completed, pass_accuracy, tackles_total, tackles_won,
         interceptions, fouls_committed, fouls_drawn, yellow_cards, red_cards, rating, team_name) = player_stats
        
        # Enhanced calculations
        touches = int(passes_total * 1.2 + shots_total * 0.5) if passes_total else 0
        blocks = int(interceptions * 0.8 + tackles_total * 0.3)
        
        # Expected stats
        xg = round(shots_on_target * 0.12 + (shots_total - shots_on_target) * 0.03, 2) if shots_total else 0.0
        xag = round(assists * 1.2 + passes_total * 0.02, 2) if passes_total else 0.0
        
        # Shot Creating Actions
        sca = assists + (passes_total // 15) + (shots_total // 2) if passes_total else 0
        gca = goals + assists
        
        # Progressive actions
        progressive_passes = int(passes_total * 0.15) if passes_total else 0
        progressive_carries = int(minutes_played * 0.3) if minutes_played else 0
        
        return {
            'touches': touches,
            'blocks': blocks,
            'xg': xg,
            'xag': xag,
            'sca': sca,
            'gca': gca,
            'progressive_passes': progressive_passes,
            'progressive_carries': progressive_carries
        }
    
    def display_match_analysis(self, match_id: int):
        """Display comprehensive match analysis."""
        
        # Get match details
        match_details = self.get_match_details(match_id)
        if not match_details:
            logger.error(f"❌ Match {match_id} not found!")
            return
        
        # Get player statistics
        player_stats = self.get_match_player_stats(match_id)
        if not player_stats:
            logger.error(f"❌ No player statistics found for match {match_id}!")
            return
        
        # Display match header
        self.display_match_header(match_details)
        
        # Separate Real Madrid and opponent players
        real_madrid_players = []
        opponent_players = []
        
        for player in player_stats:
            if player[18] == 'Real Madrid':  # team_name is at index 18
                real_madrid_players.append(player)
            else:
                opponent_players.append(player)
        
        # Display Real Madrid players by position
        self.display_team_analysis(real_madrid_players, "🏆 REAL MADRID", match_details)
        
        # Display opponent players
        opponent_name = match_details['away_team'] if match_details['home_team'] == 'Real Madrid' else match_details['home_team']
        self.display_team_analysis(opponent_players, f"⚽ {opponent_name.upper()}", match_details)
        
        # Display tactical summary
        self.display_tactical_summary(real_madrid_players, match_details)
    
    def display_match_header(self, match_details: Dict):
        """Display match header information."""
        
        print("\n" + "=" * 160)
        
        # Match title
        home_team = match_details['home_team']
        away_team = match_details['away_team']
        score = f"{match_details['home_goals']}-{match_details['away_goals']}"
        
        if home_team == 'Real Madrid':
            title = f"🏆 REAL MADRID {score} {away_team}"
        else:
            title = f"{home_team} {score} REAL MADRID 🏆"
        
        print(title.center(160))
        print("=" * 160)
        
        # Match information
        date_str = match_details['match_date'].strftime('%Y-%m-%d') if match_details['match_date'] else 'Unknown'
        
        print(f"📅 Date: {date_str}")
        print(f"🏆 Competition: {match_details['competition']}")
        print(f"🎯 Season: {match_details.get('season', 'Unknown')}")
        print(f"🏟️  Venue: {match_details.get('venue_name', 'Unknown')}, {match_details.get('venue_city', 'Unknown')}")
        print(f"👨‍⚖️ Referee: {match_details.get('referee', 'Unknown')}")
        print(f"🆔 Match ID: {match_details['match_id']}")
        
        print("-" * 160)

    def display_team_analysis(self, players: List[Tuple], team_name: str, match_details: Dict):
        """Display detailed team analysis by position."""

        if not players:
            return

        print(f"\n{team_name}")
        print("=" * 160)

        # Group players by position
        positions = {'G': [], 'D': [], 'M': [], 'F': []}
        for player in players:
            pos = player[1] or 'M'  # position is at index 1
            if pos in positions:
                positions[pos].append(player)
            else:
                positions['M'].append(player)  # Default to midfielder

        # Display header
        header = f"{'#':<3} {'Player':<22} {'Pos':<4} {'Min':<4} {'Gls':<4} {'Ast':<4} {'Sh':<3} {'SoT':<4} {'Pass':<5} {'Cmp':<4} {'Acc%':<5} {'Tkl':<4} {'Int':<4} {'Fouls':<6} {'Cards':<6} {'Rating':<7} {'xG':<5} {'xAG':<5} {'SCA':<4} {'Touches':<8}"
        print(header)
        print("-" * 160)

        line_num = 1
        position_names = {'G': 'GOALKEEPERS', 'D': 'DEFENDERS', 'M': 'MIDFIELDERS', 'F': 'FORWARDS'}

        for pos_code, pos_players in positions.items():
            if pos_players:
                print(f"\n📍 {position_names[pos_code]}")
                print("·" * 160)

                for player in pos_players:
                    enhanced = self.calculate_enhanced_metrics(player)

                    (player_name, position, minutes_played, goals, assists, shots_total, shots_on_target,
                     passes_total, passes_completed, pass_accuracy, tackles_total, tackles_won,
                     interceptions, fouls_committed, fouls_drawn, yellow_cards, red_cards, rating, team_name) = player

                    # Format cards
                    cards = f"Y{yellow_cards}" if yellow_cards else ""
                    if red_cards:
                        cards += f"R{red_cards}"
                    cards = cards or "-"

                    # Format fouls
                    fouls = f"{fouls_committed}/{fouls_drawn}"

                    # Safe formatting
                    def safe_val(val, default=0):
                        return val if val is not None else default

                    def safe_float(val, default=0.0):
                        return float(val) if val is not None else default

                    row = f"{line_num:<3} {player_name:<22} {position or 'N/A':<4} {safe_val(minutes_played):<4} {safe_val(goals):<4} {safe_val(assists):<4} {safe_val(shots_total):<3} {safe_val(shots_on_target):<4} {safe_val(passes_total):<5} {safe_val(passes_completed):<4} {safe_float(pass_accuracy):<5.1f} {safe_val(tackles_total):<4} {safe_val(interceptions):<4} {fouls:<6} {cards:<6} {safe_float(rating):<7.2f} {enhanced['xg']:<5.2f} {enhanced['xag']:<5.2f} {safe_val(enhanced['sca']):<4} {safe_val(enhanced['touches']):<8}"
                    print(row)
                    line_num += 1

        print("-" * 160)

    def display_tactical_summary(self, real_madrid_players: List[Tuple], match_details: Dict):
        """Display tactical summary and key insights."""

        print(f"\n🎯 TACTICAL SUMMARY & KEY INSIGHTS")
        print("=" * 160)

        # Calculate team totals
        total_goals = sum(player[3] or 0 for player in real_madrid_players)
        total_assists = sum(player[4] or 0 for player in real_madrid_players)
        total_shots = sum(player[5] or 0 for player in real_madrid_players)
        total_passes = sum(player[7] or 0 for player in real_madrid_players)
        total_completed = sum(player[8] or 0 for player in real_madrid_players)
        total_tackles = sum(player[10] or 0 for player in real_madrid_players)

        # Team pass accuracy
        team_pass_accuracy = (total_completed / total_passes * 100) if total_passes > 0 else 0

        # Find key performers
        top_scorer = max(real_madrid_players, key=lambda x: x[3] or 0)
        top_passer = max(real_madrid_players, key=lambda x: x[7] or 0)
        highest_rated = max(real_madrid_players, key=lambda x: x[17] or 0)

        # Formation analysis
        positions = {}
        starters = [p for p in real_madrid_players if (p[2] or 0) >= 45]  # Players with 45+ minutes

        for player in starters:
            pos = player[1] or 'M'
            positions[pos] = positions.get(pos, 0) + 1

        formation = f"{positions.get('D', 0)}-{positions.get('M', 0)}-{positions.get('F', 0)}"

        print(f"📊 TEAM PERFORMANCE:")
        print(f"   Formation: {formation} | Goals: {total_goals} | Assists: {total_assists} | Shots: {total_shots}")
        print(f"   Pass Accuracy: {team_pass_accuracy:.1f}% ({total_completed}/{total_passes}) | Tackles: {total_tackles}")

        print(f"\n⭐ KEY PERFORMERS:")
        print(f"   🥅 Top Scorer: {top_scorer[0]} ({top_scorer[3]} goals)")
        print(f"   🎯 Most Passes: {top_passer[0]} ({top_passer[7]} passes)")
        print(f"   🌟 Highest Rated: {highest_rated[0]} ({highest_rated[17]:.2f} rating)")

        # Match result context
        home_team = match_details['home_team']
        away_team = match_details['away_team']
        home_goals = match_details['home_goals']
        away_goals = match_details['away_goals']

        if home_team == 'Real Madrid':
            result = "WIN" if home_goals > away_goals else ("DRAW" if home_goals == away_goals else "LOSS")
        else:
            result = "WIN" if away_goals > home_goals else ("DRAW" if away_goals == home_goals else "LOSS")

        result_emoji = "🏆" if result == "WIN" else ("🤝" if result == "DRAW" else "😞")

        print(f"\n🏁 MATCH RESULT: {result} {result_emoji}")
        print(f"   Competition: {match_details['competition']}")
        print(f"   Significance: {'Champions League Winning Season' if '2024' in str(match_details.get('match_date', '')) else 'Season Match'}")

        print("=" * 160)

    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

def main():
    """Main function for match analysis."""
    try:
        analyzer = RealMadridMatchAnalyzer()
        
        if len(sys.argv) > 1:
            # Analyze specific match
            try:
                match_id = int(sys.argv[1])
                analyzer.display_match_analysis(match_id)
            except ValueError:
                logger.error("❌ Please provide a valid match ID number")
        else:
            # Display available matches
            matches = analyzer.get_available_matches()
            if matches:
                analyzer.display_match_list(matches)
            else:
                logger.error("❌ No matches found")
        
        analyzer.close()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
