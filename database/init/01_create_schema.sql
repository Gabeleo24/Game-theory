-- ADS599 Capstone Soccer Intelligence System - Unified Database Schema
-- Supports both SportMonks and API-Football APIs for comprehensive data collection
-- Covers 67 UEFA Champions League teams across 2019-2024 seasons
-- Created: 2025-07-09

-- ============================================================================
-- TEAMS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS teams (
    team_id SERIAL PRIMARY KEY,
    sportmonks_team_id INTEGER UNIQUE,
    team_name VARCHAR(255) NOT NULL,
    short_name VARCHAR(50),
    country VARCHAR(100),
    founded_year INTEGER,
    venue_name VARCHAR(255),
    venue_city VARCHAR(255),
    logo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- COMPETITIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS competitions (
    competition_id SERIAL PRIMARY KEY,
    sportmonks_competition_id INTEGER UNIQUE,
    competition_name VARCHAR(255) NOT NULL,
    competition_type VARCHAR(100),
    country VARCHAR(100),
    season VARCHAR(20),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SEASONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS seasons (
    season_id SERIAL PRIMARY KEY,
    sportmonks_season_id INTEGER UNIQUE,
    season_name VARCHAR(100) NOT NULL,
    competition_id INTEGER REFERENCES competitions(competition_id),
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PLAYERS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS players (
    player_id SERIAL PRIMARY KEY,
    sportmonks_player_id INTEGER UNIQUE,
    player_name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    birth_date DATE,
    nationality VARCHAR(100),
    height INTEGER,
    weight INTEGER,
    position VARCHAR(50),
    jersey_number INTEGER,
    team_id INTEGER REFERENCES teams(team_id),
    market_value BIGINT,
    contract_until DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MATCHES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS matches (
    match_id SERIAL PRIMARY KEY,
    sportmonks_match_id INTEGER UNIQUE,
    season_id INTEGER REFERENCES seasons(season_id),
    competition_id INTEGER REFERENCES competitions(competition_id),
    home_team_id INTEGER REFERENCES teams(team_id),
    away_team_id INTEGER REFERENCES teams(team_id),
    match_date TIMESTAMP,
    match_week INTEGER,
    round_name VARCHAR(100),
    home_goals INTEGER DEFAULT 0,
    away_goals INTEGER DEFAULT 0,
    home_goals_ht INTEGER DEFAULT 0,
    away_goals_ht INTEGER DEFAULT 0,
    match_status VARCHAR(50),
    venue_name VARCHAR(255),
    venue_city VARCHAR(255),
    referee_name VARCHAR(255),
    attendance INTEGER,
    weather_conditions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MATCH PLAYER STATISTICS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS match_player_stats (
    stat_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id),
    player_id INTEGER REFERENCES players(player_id),
    team_id INTEGER REFERENCES teams(team_id),
    position VARCHAR(10),
    jersey_number INTEGER,
    is_starter BOOLEAN DEFAULT FALSE,
    minutes_played INTEGER DEFAULT 0,
    
    -- Offensive Statistics
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    shots_total INTEGER DEFAULT 0,
    shots_on_target INTEGER DEFAULT 0,
    shots_off_target INTEGER DEFAULT 0,
    shots_blocked INTEGER DEFAULT 0,
    penalty_goals INTEGER DEFAULT 0,
    penalty_attempts INTEGER DEFAULT 0,
    penalty_missed INTEGER DEFAULT 0,
    
    -- Passing Statistics
    passes_total INTEGER DEFAULT 0,
    passes_completed INTEGER DEFAULT 0,
    pass_accuracy DECIMAL(5,2) DEFAULT 0.0,
    passes_key INTEGER DEFAULT 0,
    passes_long INTEGER DEFAULT 0,
    passes_long_completed INTEGER DEFAULT 0,
    passes_short INTEGER DEFAULT 0,
    passes_short_completed INTEGER DEFAULT 0,
    passes_cross INTEGER DEFAULT 0,
    passes_cross_completed INTEGER DEFAULT 0,
    
    -- Defensive Statistics
    tackles_total INTEGER DEFAULT 0,
    tackles_won INTEGER DEFAULT 0,
    tackles_lost INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    clearances INTEGER DEFAULT 0,
    blocks INTEGER DEFAULT 0,
    duels_total INTEGER DEFAULT 0,
    duels_won INTEGER DEFAULT 0,
    duels_lost INTEGER DEFAULT 0,
    duels_aerial_total INTEGER DEFAULT 0,
    duels_aerial_won INTEGER DEFAULT 0,
    
    -- Disciplinary
    fouls_committed INTEGER DEFAULT 0,
    fouls_drawn INTEGER DEFAULT 0,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    
    -- Advanced Metrics
    rating DECIMAL(4,2) DEFAULT 0.0,
    expected_goals DECIMAL(5,2) DEFAULT 0.0,
    expected_assists DECIMAL(5,2) DEFAULT 0.0,
    touches INTEGER DEFAULT 0,
    touches_penalty_area INTEGER DEFAULT 0,
    dribbles_attempted INTEGER DEFAULT 0,
    dribbles_successful INTEGER DEFAULT 0,
    offsides INTEGER DEFAULT 0,
    
    -- Goalkeeper Specific
    saves INTEGER DEFAULT 0,
    saves_inside_box INTEGER DEFAULT 0,
    saves_outside_box INTEGER DEFAULT 0,
    goals_conceded INTEGER DEFAULT 0,
    clean_sheet BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    data_source VARCHAR(50) DEFAULT 'SportMonks',
    data_quality_score INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(match_id, player_id)
);

-- ============================================================================
-- TEAM FORMATIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS team_formations (
    formation_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id),
    team_id INTEGER REFERENCES teams(team_id),
    formation VARCHAR(20),
    formation_positions JSONB,
    is_home_team BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- API COLLECTION METADATA TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_collection_metadata (
    collection_id SERIAL PRIMARY KEY,
    collection_type VARCHAR(100) NOT NULL,
    api_source VARCHAR(50) DEFAULT 'SportMonks',
    collection_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    records_collected INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    api_rate_limit_remaining INTEGER,
    collection_status VARCHAR(50) DEFAULT 'IN_PROGRESS',
    error_messages TEXT,
    collection_duration_seconds INTEGER,
    data_quality_score DECIMAL(5,2) DEFAULT 100.0,
    notes TEXT
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================================

-- Teams indexes
CREATE INDEX IF NOT EXISTS idx_teams_sportmonks_id ON teams(sportmonks_team_id);
CREATE INDEX IF NOT EXISTS idx_teams_name ON teams(team_name);

-- Players indexes
CREATE INDEX IF NOT EXISTS idx_players_sportmonks_id ON players(sportmonks_player_id);
CREATE INDEX IF NOT EXISTS idx_players_name ON players(player_name);
CREATE INDEX IF NOT EXISTS idx_players_team ON players(team_id);
CREATE INDEX IF NOT EXISTS idx_players_position ON players(position);

-- Matches indexes
CREATE INDEX IF NOT EXISTS idx_matches_sportmonks_id ON matches(sportmonks_match_id);
CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date);
CREATE INDEX IF NOT EXISTS idx_matches_teams ON matches(home_team_id, away_team_id);
CREATE INDEX IF NOT EXISTS idx_matches_season ON matches(season_id);
CREATE INDEX IF NOT EXISTS idx_matches_competition ON matches(competition_id);

-- Match player stats indexes
CREATE INDEX IF NOT EXISTS idx_match_stats_match ON match_player_stats(match_id);
CREATE INDEX IF NOT EXISTS idx_match_stats_player ON match_player_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_match_stats_team ON match_player_stats(team_id);
CREATE INDEX IF NOT EXISTS idx_match_stats_minutes ON match_player_stats(minutes_played);
CREATE INDEX IF NOT EXISTS idx_match_stats_goals ON match_player_stats(goals);
CREATE INDEX IF NOT EXISTS idx_match_stats_assists ON match_player_stats(assists);
CREATE INDEX IF NOT EXISTS idx_match_stats_rating ON match_player_stats(rating);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_match_stats_composite ON match_player_stats(match_id, team_id, minutes_played);
CREATE INDEX IF NOT EXISTS idx_players_team_position ON players(team_id, position);

-- ============================================================================
-- CONSTRAINTS AND TRIGGERS
-- ============================================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers
CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_players_updated_at BEFORE UPDATE ON players
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_matches_updated_at BEFORE UPDATE ON matches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_match_stats_updated_at BEFORE UPDATE ON match_player_stats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA SETUP
-- ============================================================================

-- Insert Real Madrid team record
INSERT INTO teams (sportmonks_team_id, team_name, short_name, country, venue_name, venue_city)
VALUES (53, 'Real Madrid', 'Real Madrid', 'Spain', 'Santiago Bernabéu', 'Madrid')
ON CONFLICT (sportmonks_team_id) DO NOTHING;

-- Insert major competitions
INSERT INTO competitions (sportmonks_competition_id, competition_name, competition_type, country, season)
VALUES 
    (8, 'UEFA Champions League', 'International', 'Europe', '2023-2024'),
    (271, 'La Liga', 'Domestic League', 'Spain', '2023-2024'),
    (75, 'Copa del Rey', 'Domestic Cup', 'Spain', '2023-2024')
ON CONFLICT (sportmonks_competition_id) DO NOTHING;

-- Log schema creation
INSERT INTO api_collection_metadata (collection_type, collection_status, notes)
VALUES ('SCHEMA_CREATION', 'COMPLETED', 'Database schema created successfully for Real Madrid 2023-2024 season analysis');

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO soccerapp;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO soccerapp;
