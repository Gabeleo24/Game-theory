#!/usr/bin/env python3
"""
Generate Manchester City Match Schedule and Results
Creates realistic match schedule for 2023-24 season across all competitions
with team-level statistics and results
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MatchScheduleGenerator:
    """Generate comprehensive match schedule and results for Manchester City 2023-24."""
    
    def __init__(self, db_path="data/fbref_scraped/fbref_data.db"):
        """Initialize with database path."""
        self.db_path = db_path
        self.season = "2023-24"
        
        # Set random seed for reproducible results
        random.seed(42)
        
    def generate_premier_league_fixtures(self):
        """Generate all 38 Premier League fixtures with realistic results."""
        
        logger.info("⚽ Generating Premier League fixtures")
        
        # Premier League opponents (19 teams x 2 = 38 matches)
        opponents = [
            'Arsenal', 'Liverpool', 'Chelsea', 'Tottenham', 'Newcastle United',
            'Brighton & Hove Albion', 'Aston Villa', 'West Ham United', 'Crystal Palace',
            'Bournemouth', 'Fulham', 'Wolverhampton Wanderers', 'Everton', 'Brentford',
            'Nottingham Forest', 'Sheffield United', 'Burnley', 'Luton Town', 'Manchester United'
        ]
        
        fixtures = []
        match_date = datetime(2023, 8, 12)  # Season start
        
        # Generate home and away fixtures
        for round_num in range(2):  # Two rounds (home and away)
            for i, opponent in enumerate(opponents):
                # Alternate home/away and add some randomness
                is_home = (round_num + i) % 2 == 0
                
                # Add realistic date progression
                match_date += timedelta(days=random.randint(3, 14))
                
                # Generate realistic result based on opponent strength
                city_score, opp_score, result = self._generate_realistic_result(opponent, is_home)
                
                fixture = {
                    'match_date': match_date.strftime('%Y-%m-%d'),
                    'competition': 'Premier League',
                    'matchday': (round_num * 19) + i + 1,
                    'home_away': 'Home' if is_home else 'Away',
                    'opponent': opponent,
                    'manchester_city_score': city_score,
                    'opponent_score': opp_score,
                    'result': result
                }
                
                # Add team statistics
                fixture.update(self._generate_team_stats(city_score, opp_score, is_home))
                
                fixtures.append(fixture)
        
        logger.info(f"✅ Generated {len(fixtures)} Premier League fixtures")
        return fixtures
    
    def generate_champions_league_fixtures(self):
        """Generate Champions League fixtures."""
        
        logger.info("🏆 Generating Champions League fixtures")
        
        fixtures = []
        match_date = datetime(2023, 9, 19)  # CL start
        
        # Group stage opponents (6 matches)
        group_opponents = ['RB Leipzig', 'Young Boys', 'Red Star Belgrade']
        
        for round_num in range(2):  # Home and away
            for opponent in group_opponents:
                is_home = round_num == 0
                match_date += timedelta(days=random.randint(14, 21))
                
                city_score, opp_score, result = self._generate_realistic_result(opponent, is_home, 'Champions League')
                
                fixture = {
                    'match_date': match_date.strftime('%Y-%m-%d'),
                    'competition': 'Champions League',
                    'matchday': (round_num * 3) + group_opponents.index(opponent) + 1,
                    'home_away': 'Home' if is_home else 'Away',
                    'opponent': opponent,
                    'manchester_city_score': city_score,
                    'opponent_score': opp_score,
                    'result': result
                }
                
                fixture.update(self._generate_team_stats(city_score, opp_score, is_home))
                fixtures.append(fixture)
        
        # Knockout stage (Round of 16, Quarter-finals)
        knockout_opponents = ['FC Copenhagen', 'Real Madrid']
        knockout_stages = ['Round of 16', 'Quarter-finals']
        
        for stage, opponent in zip(knockout_stages, knockout_opponents):
            for leg in range(2):  # Two legs
                is_home = leg == 0
                match_date += timedelta(days=random.randint(14, 28))
                
                city_score, opp_score, result = self._generate_realistic_result(opponent, is_home, 'Champions League')
                
                fixture = {
                    'match_date': match_date.strftime('%Y-%m-%d'),
                    'competition': 'Champions League',
                    'matchday': 7 + (knockout_stages.index(stage) * 2) + leg,
                    'home_away': 'Home' if is_home else 'Away',
                    'opponent': opponent,
                    'manchester_city_score': city_score,
                    'opponent_score': opp_score,
                    'result': result
                }
                
                fixture.update(self._generate_team_stats(city_score, opp_score, is_home))
                fixtures.append(fixture)
        
        logger.info(f"✅ Generated {len(fixtures)} Champions League fixtures")
        return fixtures
    
    def generate_fa_cup_fixtures(self):
        """Generate FA Cup fixtures."""
        
        logger.info("🏆 Generating FA Cup fixtures")
        
        fixtures = []
        match_date = datetime(2024, 1, 6)  # FA Cup start
        
        # FA Cup run to final
        opponents = ['Huddersfield Town', 'Tottenham', 'Luton Town', 'Newcastle United', 'Chelsea', 'Manchester United']
        rounds = ['Third Round', 'Fourth Round', 'Fifth Round', 'Quarter-final', 'Semi-final', 'Final']
        
        for i, (round_name, opponent) in enumerate(zip(rounds, opponents)):
            # Most matches at neutral venues or away for cup competitions
            is_home = i < 3  # Early rounds more likely at home
            match_date += timedelta(days=random.randint(14, 28))
            
            city_score, opp_score, result = self._generate_realistic_result(opponent, is_home, 'FA Cup')
            
            fixture = {
                'match_date': match_date.strftime('%Y-%m-%d'),
                'competition': 'FA Cup',
                'matchday': i + 1,
                'home_away': 'Home' if is_home else 'Away',
                'opponent': opponent,
                'manchester_city_score': city_score,
                'opponent_score': opp_score,
                'result': result
            }
            
            fixture.update(self._generate_team_stats(city_score, opp_score, is_home))
            fixtures.append(fixture)
        
        logger.info(f"✅ Generated {len(fixtures)} FA Cup fixtures")
        return fixtures
    
    def generate_efl_cup_fixtures(self):
        """Generate EFL Cup fixtures."""
        
        logger.info("🏆 Generating EFL Cup fixtures")
        
        fixtures = []
        match_date = datetime(2023, 9, 27)  # EFL Cup start
        
        # EFL Cup run (knocked out in 4th round)
        opponents = ['Newcastle United', 'Leicester City', 'Newcastle United']
        rounds = ['Third Round', 'Fourth Round', 'Fourth Round Replay']
        
        for i, (round_name, opponent) in enumerate(zip(rounds, opponents)):
            is_home = i % 2 == 0
            match_date += timedelta(days=random.randint(14, 21))
            
            # Lost in 4th round
            if i == 2:  # Final match - loss
                city_score, opp_score, result = 0, 1, 'Loss'
            else:
                city_score, opp_score, result = self._generate_realistic_result(opponent, is_home, 'EFL Cup')
            
            fixture = {
                'match_date': match_date.strftime('%Y-%m-%d'),
                'competition': 'EFL Cup',
                'matchday': i + 1,
                'home_away': 'Home' if is_home else 'Away',
                'opponent': opponent,
                'manchester_city_score': city_score,
                'opponent_score': opp_score,
                'result': result
            }
            
            fixture.update(self._generate_team_stats(city_score, opp_score, is_home))
            fixtures.append(fixture)
        
        logger.info(f"✅ Generated {len(fixtures)} EFL Cup fixtures")
        return fixtures
    
    def _generate_realistic_result(self, opponent, is_home, competition='Premier League'):
        """Generate realistic match result based on opponent and context."""
        
        # Base scoring probabilities
        base_city_goals = 2.5 if is_home else 2.0
        base_opp_goals = 0.8 if is_home else 1.2
        
        # Adjust based on opponent strength
        strong_opponents = ['Arsenal', 'Liverpool', 'Chelsea', 'Tottenham', 'Newcastle United', 
                          'Real Madrid', 'Manchester United']
        
        if opponent in strong_opponents:
            base_city_goals *= 0.8
            base_opp_goals *= 1.5
        elif opponent in ['Sheffield United', 'Burnley', 'Luton Town']:
            base_city_goals *= 1.3
            base_opp_goals *= 0.6
        
        # Generate scores using Poisson distribution
        city_score = max(0, int(random.gauss(base_city_goals, 1.2)))
        opp_score = max(0, int(random.gauss(base_opp_goals, 1.0)))
        
        # Determine result
        if city_score > opp_score:
            result = 'Win'
        elif city_score < opp_score:
            result = 'Loss'
        else:
            result = 'Draw'
        
        return city_score, opp_score, result
    
    def _generate_team_stats(self, city_score, opp_score, is_home):
        """Generate realistic team statistics for a match."""
        
        # Base stats influenced by score and home advantage
        possession_base = 65 if is_home else 60
        possession = max(45, min(80, possession_base + random.randint(-10, 15)))
        
        # Shots based on goals scored
        shots_base = 12 + (city_score * 3)
        shots = max(5, shots_base + random.randint(-3, 8))
        shots_on_target = max(2, min(shots, 3 + city_score + random.randint(0, 4)))
        
        # Other statistics
        corners = random.randint(3, 12)
        fouls_committed = random.randint(8, 18)
        fouls_suffered = random.randint(6, 16)
        yellow_cards = random.randint(0, 4)
        red_cards = 1 if random.random() < 0.05 else 0
        
        # Passing stats
        passes_total = int(possession * 8 + random.randint(-50, 100))
        pass_accuracy = max(75, min(95, 85 + random.randint(-8, 8)))
        passes_completed = int(passes_total * pass_accuracy / 100)
        
        # Defensive stats
        tackles_total = random.randint(12, 25)
        tackles_won = int(tackles_total * random.uniform(0.6, 0.8))
        interceptions = random.randint(8, 18)
        clearances = random.randint(10, 25)
        blocks = random.randint(2, 8)
        
        return {
            'possession_percentage': round(possession, 1),
            'shots_total': shots,
            'shots_on_target': shots_on_target,
            'shots_off_target': shots - shots_on_target - random.randint(0, 2),
            'shots_blocked': random.randint(0, 3),
            'corners': corners,
            'offsides': random.randint(0, 5),
            'fouls_committed': fouls_committed,
            'fouls_suffered': fouls_suffered,
            'yellow_cards': yellow_cards,
            'red_cards': red_cards,
            'passes_total': passes_total,
            'passes_completed': passes_completed,
            'pass_accuracy': round(pass_accuracy, 1),
            'tackles_total': tackles_total,
            'tackles_won': tackles_won,
            'interceptions': interceptions,
            'clearances': clearances,
            'blocks': blocks,
            'attendance': random.randint(45000, 55000) if is_home else random.randint(35000, 75000),
            'venue': 'Etihad Stadium' if is_home else f'{random.choice(["Stadium", "Arena", "Park", "Ground"])}',
            'referee': f'Referee {random.randint(1, 20)}'
        }

    def save_fixtures_to_database(self, all_fixtures):
        """Save all fixtures to the database."""

        logger.info(f"💾 Saving {len(all_fixtures)} fixtures to database")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clear existing match data for this season
        cursor.execute("DELETE FROM match_results WHERE season = ?", (self.season,))

        for fixture in all_fixtures:
            cursor.execute('''
                INSERT INTO match_results (
                    season, match_date, competition, matchday, home_away, opponent,
                    manchester_city_score, opponent_score, result,
                    possession_percentage, shots_total, shots_on_target, shots_off_target,
                    shots_blocked, corners, offsides, fouls_committed, fouls_suffered,
                    yellow_cards, red_cards, passes_total, passes_completed, pass_accuracy,
                    tackles_total, tackles_won, interceptions, clearances, blocks,
                    attendance, venue, referee
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.season, fixture['match_date'], fixture['competition'], fixture['matchday'],
                fixture['home_away'], fixture['opponent'], fixture['manchester_city_score'],
                fixture['opponent_score'], fixture['result'], fixture['possession_percentage'],
                fixture['shots_total'], fixture['shots_on_target'], fixture['shots_off_target'],
                fixture['shots_blocked'], fixture['corners'], fixture['offsides'],
                fixture['fouls_committed'], fixture['fouls_suffered'], fixture['yellow_cards'],
                fixture['red_cards'], fixture['passes_total'], fixture['passes_completed'],
                fixture['pass_accuracy'], fixture['tackles_total'], fixture['tackles_won'],
                fixture['interceptions'], fixture['clearances'], fixture['blocks'],
                fixture['attendance'], fixture['venue'], fixture['referee']
            ))

        conn.commit()
        conn.close()

        logger.info("✅ All fixtures saved to database")

    def generate_all_fixtures(self):
        """Generate fixtures for all competitions."""

        logger.info("🏆 Generating complete Manchester City 2023-24 fixture list")

        all_fixtures = []

        # Generate fixtures for each competition
        all_fixtures.extend(self.generate_premier_league_fixtures())
        all_fixtures.extend(self.generate_champions_league_fixtures())
        all_fixtures.extend(self.generate_fa_cup_fixtures())
        all_fixtures.extend(self.generate_efl_cup_fixtures())

        # Sort by date
        all_fixtures.sort(key=lambda x: x['match_date'])

        logger.info(f"✅ Generated {len(all_fixtures)} total fixtures")

        # Save to database
        self.save_fixtures_to_database(all_fixtures)

        return all_fixtures

    def export_fixtures_summary(self):
        """Export fixtures summary and statistics."""

        logger.info("📊 Generating fixtures summary")

        conn = sqlite3.connect(self.db_path)

        # Get match summary by competition
        summary_query = """
        SELECT
            competition,
            COUNT(*) as total_matches,
            SUM(CASE WHEN result = 'Win' THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN result = 'Draw' THEN 1 ELSE 0 END) as draws,
            SUM(CASE WHEN result = 'Loss' THEN 1 ELSE 0 END) as losses,
            SUM(manchester_city_score) as goals_for,
            SUM(opponent_score) as goals_against,
            ROUND(AVG(possession_percentage), 1) as avg_possession,
            ROUND(AVG(shots_total), 1) as avg_shots
        FROM match_results
        WHERE season = ?
        GROUP BY competition
        ORDER BY total_matches DESC
        """

        summary_df = pd.read_sql_query(summary_query, conn, params=(self.season,))

        print("\n🏆 MANCHESTER CITY 2023-24 SEASON SUMMARY")
        print("=" * 60)

        total_matches = 0
        total_wins = 0
        total_goals_for = 0

        for _, row in summary_df.iterrows():
            print(f"\n📊 {row['competition']}:")
            print(f"   Matches: {row['total_matches']} | W:{row['wins']} D:{row['draws']} L:{row['losses']}")
            print(f"   Goals: {row['goals_for']}-{row['goals_against']} | Possession: {row['avg_possession']}% | Shots: {row['avg_shots']}")

            total_matches += row['total_matches']
            total_wins += row['wins']
            total_goals_for += row['goals_for']

        print(f"\n🎯 OVERALL SEASON:")
        print(f"   Total Matches: {total_matches}")
        print(f"   Win Rate: {round(total_wins/total_matches*100, 1)}%")
        print(f"   Goals Scored: {total_goals_for}")

        # Export to CSV
        all_matches_df = pd.read_sql_query("SELECT * FROM match_results WHERE season = ? ORDER BY match_date", conn, params=(self.season,))

        output_file = "data/fbref_scraped/manchester_city_matches_2023_24.csv"
        all_matches_df.to_csv(output_file, index=False)

        conn.close()

        logger.info(f"📄 Exported {len(all_matches_df)} matches to {output_file}")

        return summary_df

def main():
    """Main execution function."""

    print("⚽ Generating Manchester City 2023-24 Match Schedule")
    print("=" * 60)

    generator = MatchScheduleGenerator()

    # Generate all fixtures
    fixtures = generator.generate_all_fixtures()

    # Export summary
    summary = generator.export_fixtures_summary()

    print(f"\n✅ Complete! Generated {len(fixtures)} matches across all competitions")
    print("📊 Next step: Generate individual player match performances")

if __name__ == "__main__":
    main()
