-- PostgreSQL Initialization Script for ADS599 Capstone Soccer Intelligence System
-- Creates database schema for storing processed match/player statistics

-- ============================================================================
-- Database Setup
-- ============================================================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- Teams Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY,
    team_name VARCHAR(255) NOT NULL,
    team_code VARCHAR(10),
    country VARCHAR(100),
    founded INTEGER,
    venue_name VARCHAR(255),
    venue_capacity INTEGER,
    logo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Players Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    player_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    age INTEGER,
    birth_date DATE,
    birth_place VARCHAR(255),
    birth_country VARCHAR(100),
    nationality VARCHAR(100),
    height VARCHAR(10),
    weight VARCHAR(10),
    photo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Competitions Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS competitions (
    competition_id INTEGER PRIMARY KEY,
    competition_name VARCHAR(255) NOT NULL,
    competition_type VARCHAR(50),
    country VARCHAR(100),
    logo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Seasons Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS seasons (
    season_id SERIAL PRIMARY KEY,
    season_year INTEGER NOT NULL,
    start_date DATE,
    end_date DATE,
    current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Matches Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY,
    competition_id INTEGER REFERENCES competitions(competition_id),
    season_year INTEGER,
    match_date TIMESTAMP,
    round VARCHAR(100),
    home_team_id INTEGER REFERENCES teams(team_id),
    away_team_id INTEGER REFERENCES teams(team_id),
    home_goals INTEGER,
    away_goals INTEGER,
    home_goals_halftime INTEGER,
    away_goals_halftime INTEGER,
    match_status VARCHAR(50),
    venue_name VARCHAR(255),
    venue_city VARCHAR(255),
    referee VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Player Statistics Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS player_statistics (
    stat_id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(player_id),
    team_id INTEGER REFERENCES teams(team_id),
    competition_id INTEGER REFERENCES competitions(competition_id),
    season_year INTEGER,
    match_id INTEGER REFERENCES matches(match_id),
    position VARCHAR(50),
    minutes_played INTEGER,
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    expected_goals DECIMAL(5,3) DEFAULT 0.0,
    expected_assists DECIMAL(5,3) DEFAULT 0.0,
    shots_total INTEGER DEFAULT 0,
    shots_on_target INTEGER DEFAULT 0,
    passes_total INTEGER DEFAULT 0,
    passes_completed INTEGER DEFAULT 0,
    passes_accuracy DECIMAL(5,2),
    tackles_total INTEGER DEFAULT 0,
    tackles_won INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    fouls_drawn INTEGER DEFAULT 0,
    fouls_committed INTEGER DEFAULT 0,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    rating DECIMAL(3,1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Team Statistics Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS team_statistics (
    stat_id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(team_id),
    competition_id INTEGER REFERENCES competitions(competition_id),
    season_year INTEGER,
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    goals_for INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    goal_difference INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    position INTEGER,
    clean_sheets INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Shapley Analysis Results Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS shapley_analysis (
    analysis_id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(player_id),
    team_id INTEGER REFERENCES teams(team_id),
    season_year INTEGER,
    shapley_value DECIMAL(10,6),
    contribution_rank INTEGER,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analysis_type VARCHAR(50),
    confidence_level DECIMAL(5,2),
    iterations INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Data Collection Logs Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS collection_logs (
    log_id SERIAL PRIMARY KEY,
    collection_type VARCHAR(50),
    team_id INTEGER,
    season_year INTEGER,
    status VARCHAR(20),
    records_collected INTEGER,
    api_requests INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Teams indexes
CREATE INDEX IF NOT EXISTS idx_teams_name ON teams(team_name);
CREATE INDEX IF NOT EXISTS idx_teams_country ON teams(country);

-- Players indexes
CREATE INDEX IF NOT EXISTS idx_players_name ON players(player_name);
CREATE INDEX IF NOT EXISTS idx_players_nationality ON players(nationality);

-- Matches indexes
CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date);
CREATE INDEX IF NOT EXISTS idx_matches_teams ON matches(home_team_id, away_team_id);
CREATE INDEX IF NOT EXISTS idx_matches_competition_season ON matches(competition_id, season_year);

-- Player statistics indexes
CREATE INDEX IF NOT EXISTS idx_player_stats_player_season ON player_statistics(player_id, season_year);
CREATE INDEX IF NOT EXISTS idx_player_stats_team_season ON player_statistics(team_id, season_year);
CREATE INDEX IF NOT EXISTS idx_player_stats_match ON player_statistics(match_id);

-- Team statistics indexes
CREATE INDEX IF NOT EXISTS idx_team_stats_team_season ON team_statistics(team_id, season_year);
CREATE INDEX IF NOT EXISTS idx_team_stats_competition ON team_statistics(competition_id, season_year);

-- Shapley analysis indexes
CREATE INDEX IF NOT EXISTS idx_shapley_player_season ON shapley_analysis(player_id, season_year);
CREATE INDEX IF NOT EXISTS idx_shapley_team_season ON shapley_analysis(team_id, season_year);

-- ============================================================================
-- Insert Initial Data
-- ============================================================================

-- Insert core competitions
INSERT INTO competitions (competition_id, competition_name, competition_type, country) VALUES
(2, 'UEFA Champions League', 'champions_league', 'Europe'),
(39, 'Premier League', 'domestic_league', 'England'),
(140, 'La Liga', 'domestic_league', 'Spain'),
(135, 'Serie A', 'domestic_league', 'Italy'),
(78, 'Bundesliga', 'domestic_league', 'Germany'),
(61, 'Ligue 1', 'domestic_league', 'France'),
(3, 'UEFA Europa League', 'europa_league', 'Europe')
ON CONFLICT (competition_id) DO NOTHING;

-- Insert target seasons
INSERT INTO seasons (season_year, current) VALUES
(2019, FALSE),
(2020, FALSE),
(2021, FALSE),
(2022, FALSE),
(2023, FALSE),
(2024, TRUE)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Functions and Triggers
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_players_updated_at BEFORE UPDATE ON players FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_matches_updated_at BEFORE UPDATE ON matches FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_player_statistics_updated_at BEFORE UPDATE ON player_statistics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_team_statistics_updated_at BEFORE UPDATE ON team_statistics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SAMPLE ANALYSIS QUERIES
-- ============================================================================

/*
-- Query 1: Players who outperform expected goals the most
-- This identifies players with the best goal conversion efficiency vs expected

SELECT 
    p.player_name,
    p.nationality,
    t.team_name,
    c.competition_name,
    ps.season_year,
    SUM(ps.goals) as actual_goals,
    ROUND(SUM(ps.expected_goals)::DECIMAL, 2) as total_expected_goals,
    ROUND(SUM(ps.goals) - SUM(ps.expected_goals), 2) as goals_over_expected,
    ROUND(
        CASE 
            WHEN SUM(ps.expected_goals) > 0 
            THEN (SUM(ps.goals)::DECIMAL / SUM(ps.expected_goals) - 1) * 100 
            ELSE 0 
        END, 2
    ) as outperformance_percentage,
    COUNT(ps.match_id) as matches_played,
    SUM(ps.minutes_played) as total_minutes,
    ROUND(SUM(ps.goals)::DECIMAL / (SUM(ps.minutes_played) / 90.0), 2) as goals_per_90min
FROM player_statistics ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams t ON ps.team_id = t.team_id
JOIN competitions c ON ps.competition_id = c.competition_id
WHERE ps.goals IS NOT NULL 
    AND ps.expected_goals IS NOT NULL
    AND ps.expected_goals > 0
    AND ps.minutes_played > 0
GROUP BY p.player_id, p.player_name, p.nationality, t.team_name, c.competition_name, ps.season_year
HAVING SUM(ps.expected_goals) >= 2.0  -- Only include players with meaningful xG sample
    AND SUM(ps.minutes_played) >= 450  -- At least 5 full matches worth
ORDER BY goals_over_expected DESC, outperformance_percentage DESC
LIMIT 25;

-- Query 2: Season-over-season xG outperformance consistency
-- Identifies players who consistently outperform their expected goals

WITH player_season_performance AS (
    SELECT 
        ps.player_id,
        p.player_name,
        ps.season_year,
        SUM(ps.goals) as goals,
        SUM(ps.expected_goals) as xg,
        SUM(ps.goals) - SUM(ps.expected_goals) as goals_over_expected
    FROM player_statistics ps
    JOIN players p ON ps.player_id = p.player_id
    WHERE ps.expected_goals > 0
    GROUP BY ps.player_id, p.player_name, ps.season_year
    HAVING SUM(ps.expected_goals) >= 2.0
),
consistency_stats AS (
    SELECT 
        player_id,
        player_name,
        COUNT(*) as seasons_played,
        AVG(goals_over_expected) as avg_goals_over_expected,
        COUNT(CASE WHEN goals_over_expected > 0 THEN 1 END) as seasons_outperformed,
        STDDEV(goals_over_expected) as consistency_score
    FROM player_season_performance
    GROUP BY player_id, player_name
    HAVING COUNT(*) >= 2  -- At least 2 seasons of data
)
SELECT 
    player_name,
    seasons_played,
    ROUND(avg_goals_over_expected, 2) as avg_goals_over_expected,
    seasons_outperformed,
    ROUND((seasons_outperformed::DECIMAL / seasons_played) * 100, 1) as outperformance_rate_pct,
    ROUND(consistency_score, 2) as consistency_score
FROM consistency_stats
ORDER BY avg_goals_over_expected DESC, outperformance_rate_pct DESC;

-- Query 3: Expected goals vs actual goals by position and competition
-- Analyzes xG performance by playing position

SELECT 
    ps.position,
    c.competition_name,
    COUNT(DISTINCT ps.player_id) as unique_players,
    SUM(ps.goals) as total_goals,
    ROUND(SUM(ps.expected_goals), 2) as total_expected_goals,
    ROUND(SUM(ps.goals) - SUM(ps.expected_goals), 2) as total_difference,
    ROUND(AVG(ps.goals), 2) as avg_goals_per_player,
    ROUND(AVG(ps.expected_goals), 2) as avg_xg_per_player,
    ROUND(
        CASE 
            WHEN SUM(ps.expected_goals) > 0 
            THEN SUM(ps.goals)::DECIMAL / SUM(ps.expected_goals) 
            ELSE 0 
        END, 3
    ) as conversion_ratio
FROM player_statistics ps
JOIN competitions c ON ps.competition_id = c.competition_id
WHERE ps.position IS NOT NULL 
    AND ps.expected_goals > 0
    AND ps.position IN ('Forward', 'Midfielder', 'Defender', 'Goalkeeper')
GROUP BY ps.position, c.competition_name
ORDER BY total_difference DESC;
*/
