-- ADS599 Capstone Soccer Intelligence System - Unified Database Schema
-- Comprehensive schema supporting both SportMonks and API-Football APIs
-- Covers 67 UEFA Champions League teams across 2019-2024 seasons
-- Created: 2025-07-09

-- ============================================================================
-- EXTENSIONS AND SETUP
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- SEASONS TABLE - Track multiple seasons across years
-- ============================================================================
CREATE TABLE IF NOT EXISTS seasons (
    season_id SERIAL PRIMARY KEY,
    season_name VARCHAR(100) NOT NULL UNIQUE,
    sportmonks_season_id INTEGER UNIQUE,
    api_football_season_id INTEGER UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- COMPETITIONS TABLE - Track all competitions
-- ============================================================================
CREATE TABLE IF NOT EXISTS competitions (
    competition_id SERIAL PRIMARY KEY,
    competition_name VARCHAR(255) NOT NULL,
    sportmonks_competition_id INTEGER UNIQUE,
    api_football_competition_id INTEGER UNIQUE,
    competition_type VARCHAR(50) NOT NULL, -- 'international', 'domestic_league', 'domestic_cup'
    country VARCHAR(100),
    priority INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TEAMS TABLE - Unified team information from both APIs
-- ============================================================================
CREATE TABLE IF NOT EXISTS teams (
    team_id SERIAL PRIMARY KEY,
    team_name VARCHAR(255) NOT NULL,
    short_name VARCHAR(50),
    team_code VARCHAR(10),
    
    -- API IDs for cross-reference
    sportmonks_team_id INTEGER UNIQUE,
    api_football_team_id INTEGER UNIQUE,
    
    -- Team details
    country VARCHAR(100),
    founded_year INTEGER,
    venue_name VARCHAR(255),
    venue_city VARCHAR(255),
    venue_capacity INTEGER,
    
    -- Visual assets
    logo_url TEXT,
    colors JSONB,
    
    -- Status and metadata
    is_active BOOLEAN DEFAULT TRUE,
    data_source VARCHAR(50) DEFAULT 'unified',
    data_quality_score DECIMAL(5,2) DEFAULT 100.0,
    last_updated_sportmonks TIMESTAMP,
    last_updated_api_football TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PLAYERS TABLE - Comprehensive player information
-- ============================================================================
CREATE TABLE IF NOT EXISTS players (
    player_id SERIAL PRIMARY KEY,
    player_name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    
    -- API IDs for cross-reference
    sportmonks_player_id INTEGER UNIQUE,
    api_football_player_id INTEGER UNIQUE,
    
    -- Personal information
    birth_date DATE,
    birth_place VARCHAR(255),
    nationality VARCHAR(100),
    height INTEGER, -- in cm
    weight INTEGER, -- in kg
    
    -- Playing information
    position VARCHAR(50),
    preferred_foot VARCHAR(10),
    jersey_number INTEGER,
    
    -- Current team association
    current_team_id INTEGER REFERENCES teams(team_id),
    
    -- Contract and market information
    market_value BIGINT,
    contract_until DATE,
    
    -- Status and metadata
    is_active BOOLEAN DEFAULT TRUE,
    data_source VARCHAR(50) DEFAULT 'unified',
    data_quality_score DECIMAL(5,2) DEFAULT 100.0,
    last_updated_sportmonks TIMESTAMP,
    last_updated_api_football TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MATCHES TABLE - Comprehensive match information
-- ============================================================================
CREATE TABLE IF NOT EXISTS matches (
    match_id SERIAL PRIMARY KEY,
    
    -- API IDs for cross-reference
    sportmonks_match_id INTEGER UNIQUE,
    api_football_match_id INTEGER UNIQUE,
    
    -- Match details
    competition_id INTEGER REFERENCES competitions(competition_id),
    season_id INTEGER REFERENCES seasons(season_id),
    match_date TIMESTAMP NOT NULL,
    match_week INTEGER,
    round_name VARCHAR(100),
    
    -- Teams
    home_team_id INTEGER REFERENCES teams(team_id) NOT NULL,
    away_team_id INTEGER REFERENCES teams(team_id) NOT NULL,
    
    -- Scores
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    home_score_ht INTEGER DEFAULT 0, -- halftime
    away_score_ht INTEGER DEFAULT 0,
    home_score_et INTEGER, -- extra time
    away_score_et INTEGER,
    home_score_penalty INTEGER, -- penalty shootout
    away_score_penalty INTEGER,
    
    -- Match status
    match_status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, live, finished, postponed, cancelled
    match_minute INTEGER,
    
    -- Venue information
    venue_name VARCHAR(255),
    venue_city VARCHAR(255),
    attendance INTEGER,
    
    -- Weather conditions
    weather_condition VARCHAR(100),
    temperature INTEGER,
    
    -- Officials
    referee_name VARCHAR(255),
    
    -- Additional match data
    match_data JSONB, -- Store additional API-specific data
    
    -- Status and metadata
    data_source VARCHAR(50) DEFAULT 'unified',
    data_quality_score DECIMAL(5,2) DEFAULT 100.0,
    last_updated_sportmonks TIMESTAMP,
    last_updated_api_football TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PLAYER_STATISTICS TABLE - Comprehensive match-level player statistics
-- ============================================================================
CREATE TABLE IF NOT EXISTS player_statistics (
    stat_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id) NOT NULL,
    player_id INTEGER REFERENCES players(player_id) NOT NULL,
    team_id INTEGER REFERENCES teams(team_id) NOT NULL,
    
    -- Basic playing information
    position_played VARCHAR(50),
    jersey_number INTEGER,
    minutes_played INTEGER DEFAULT 0,
    is_starter BOOLEAN DEFAULT FALSE,
    is_substitute BOOLEAN DEFAULT FALSE,
    substitution_minute INTEGER,
    
    -- Offensive statistics
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    shots_total INTEGER DEFAULT 0,
    shots_on_target INTEGER DEFAULT 0,
    shots_off_target INTEGER DEFAULT 0,
    shots_blocked INTEGER DEFAULT 0,
    
    -- Passing statistics
    passes_total INTEGER DEFAULT 0,
    passes_completed INTEGER DEFAULT 0,
    passes_accuracy DECIMAL(5,2) DEFAULT 0.0,
    passes_key INTEGER DEFAULT 0,
    crosses_total INTEGER DEFAULT 0,
    crosses_completed INTEGER DEFAULT 0,
    
    -- Defensive statistics
    tackles_total INTEGER DEFAULT 0,
    tackles_successful INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    clearances INTEGER DEFAULT 0,
    blocks INTEGER DEFAULT 0,
    
    -- Disciplinary
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    fouls_committed INTEGER DEFAULT 0,
    fouls_suffered INTEGER DEFAULT 0,
    
    -- Advanced metrics
    rating DECIMAL(4,2) DEFAULT 0.0,
    expected_goals DECIMAL(5,2) DEFAULT 0.0,
    expected_assists DECIMAL(5,2) DEFAULT 0.0,
    touches INTEGER DEFAULT 0,
    touches_penalty_area INTEGER DEFAULT 0,
    dribbles_attempted INTEGER DEFAULT 0,
    dribbles_successful INTEGER DEFAULT 0,
    offsides INTEGER DEFAULT 0,
    
    -- Goalkeeper specific statistics
    saves INTEGER DEFAULT 0,
    saves_inside_box INTEGER DEFAULT 0,
    saves_outside_box INTEGER DEFAULT 0,
    goals_conceded INTEGER DEFAULT 0,
    clean_sheet BOOLEAN DEFAULT FALSE,
    
    -- Additional statistics from APIs
    additional_stats JSONB,
    
    -- Metadata
    data_source VARCHAR(50) DEFAULT 'unified',
    data_quality_score DECIMAL(5,2) DEFAULT 100.0,
    last_updated_sportmonks TIMESTAMP,
    last_updated_api_football TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(match_id, player_id)
);

-- ============================================================================
-- TEAM_STATISTICS TABLE - Team-level match statistics
-- ============================================================================
CREATE TABLE IF NOT EXISTS team_statistics (
    team_stat_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id) NOT NULL,
    team_id INTEGER REFERENCES teams(team_id) NOT NULL,
    is_home_team BOOLEAN NOT NULL,
    
    -- Possession and passing
    possession_percentage DECIMAL(5,2) DEFAULT 0.0,
    passes_total INTEGER DEFAULT 0,
    passes_completed INTEGER DEFAULT 0,
    passes_accuracy DECIMAL(5,2) DEFAULT 0.0,
    
    -- Attacking statistics
    shots_total INTEGER DEFAULT 0,
    shots_on_target INTEGER DEFAULT 0,
    shots_off_target INTEGER DEFAULT 0,
    shots_blocked INTEGER DEFAULT 0,
    corners INTEGER DEFAULT 0,
    offsides INTEGER DEFAULT 0,
    
    -- Defensive statistics
    tackles_total INTEGER DEFAULT 0,
    tackles_successful INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    clearances INTEGER DEFAULT 0,
    blocks INTEGER DEFAULT 0,
    
    -- Disciplinary
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    fouls_committed INTEGER DEFAULT 0,
    
    -- Additional team statistics
    additional_stats JSONB,
    
    -- Metadata
    data_source VARCHAR(50) DEFAULT 'unified',
    data_quality_score DECIMAL(5,2) DEFAULT 100.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(match_id, team_id)
);

-- ============================================================================
-- MATCH_EVENTS TABLE - Detailed match events
-- ============================================================================
CREATE TABLE IF NOT EXISTS match_events (
    event_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id) NOT NULL,
    
    -- Event details
    event_type VARCHAR(50) NOT NULL, -- goal, card, substitution, etc.
    event_minute INTEGER NOT NULL,
    event_second INTEGER DEFAULT 0,
    period VARCHAR(20) DEFAULT '1H', -- 1H, 2H, ET, P
    
    -- Players involved
    player_id INTEGER REFERENCES players(player_id),
    assist_player_id INTEGER REFERENCES players(player_id),
    team_id INTEGER REFERENCES teams(team_id) NOT NULL,
    
    -- Event specific data
    event_data JSONB,
    
    -- Coordinates (if available)
    coordinate_x INTEGER,
    coordinate_y INTEGER,
    
    -- Metadata
    data_source VARCHAR(50) DEFAULT 'unified',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- API_COLLECTION_METADATA TABLE - Track data collection operations
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_collection_metadata (
    collection_id SERIAL PRIMARY KEY,
    collection_type VARCHAR(100) NOT NULL,
    api_source VARCHAR(50) NOT NULL,
    collection_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Collection metrics
    records_collected INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    
    -- API metrics
    api_requests_made INTEGER DEFAULT 0,
    api_rate_limit_remaining INTEGER,
    api_response_time_avg DECIMAL(8,3),
    
    -- Collection status
    collection_status VARCHAR(50) DEFAULT 'IN_PROGRESS',
    error_messages TEXT,
    collection_duration_seconds INTEGER,
    
    -- Data quality
    data_quality_score DECIMAL(5,2) DEFAULT 100.0,
    data_completeness_score DECIMAL(5,2) DEFAULT 100.0,
    
    -- Additional metadata
    notes TEXT,
    collection_config JSONB
);

-- ============================================================================
-- DATA_QUALITY_CHECKS TABLE - Track data quality issues
-- ============================================================================
CREATE TABLE IF NOT EXISTS data_quality_checks (
    check_id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER,
    check_type VARCHAR(100) NOT NULL,
    check_status VARCHAR(50) NOT NULL, -- passed, failed, warning
    check_message TEXT,
    check_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_timestamp TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================================

-- Teams indexes
CREATE INDEX IF NOT EXISTS idx_teams_sportmonks_id ON teams(sportmonks_team_id);
CREATE INDEX IF NOT EXISTS idx_teams_api_football_id ON teams(api_football_team_id);
CREATE INDEX IF NOT EXISTS idx_teams_name ON teams(team_name);
CREATE INDEX IF NOT EXISTS idx_teams_country ON teams(country);

-- Players indexes
CREATE INDEX IF NOT EXISTS idx_players_sportmonks_id ON players(sportmonks_player_id);
CREATE INDEX IF NOT EXISTS idx_players_api_football_id ON players(api_football_player_id);
CREATE INDEX IF NOT EXISTS idx_players_name ON players(player_name);
CREATE INDEX IF NOT EXISTS idx_players_team ON players(current_team_id);
CREATE INDEX IF NOT EXISTS idx_players_position ON players(position);

-- Matches indexes
CREATE INDEX IF NOT EXISTS idx_matches_sportmonks_id ON matches(sportmonks_match_id);
CREATE INDEX IF NOT EXISTS idx_matches_api_football_id ON matches(api_football_match_id);
CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date);
CREATE INDEX IF NOT EXISTS idx_matches_competition ON matches(competition_id);
CREATE INDEX IF NOT EXISTS idx_matches_season ON matches(season_id);
CREATE INDEX IF NOT EXISTS idx_matches_home_team ON matches(home_team_id);
CREATE INDEX IF NOT EXISTS idx_matches_away_team ON matches(away_team_id);
CREATE INDEX IF NOT EXISTS idx_matches_status ON matches(match_status);

-- Player statistics indexes
CREATE INDEX IF NOT EXISTS idx_player_stats_match ON player_statistics(match_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_player ON player_statistics(player_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_team ON player_statistics(team_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_minutes ON player_statistics(minutes_played);
CREATE INDEX IF NOT EXISTS idx_player_stats_goals ON player_statistics(goals);
CREATE INDEX IF NOT EXISTS idx_player_stats_assists ON player_statistics(assists);

-- Team statistics indexes
CREATE INDEX IF NOT EXISTS idx_team_stats_match ON team_statistics(match_id);
CREATE INDEX IF NOT EXISTS idx_team_stats_team ON team_statistics(team_id);

-- Match events indexes
CREATE INDEX IF NOT EXISTS idx_match_events_match ON match_events(match_id);
CREATE INDEX IF NOT EXISTS idx_match_events_player ON match_events(player_id);
CREATE INDEX IF NOT EXISTS idx_match_events_type ON match_events(event_type);
CREATE INDEX IF NOT EXISTS idx_match_events_minute ON match_events(event_minute);

-- API collection metadata indexes
CREATE INDEX IF NOT EXISTS idx_api_collection_type ON api_collection_metadata(collection_type);
CREATE INDEX IF NOT EXISTS idx_api_collection_source ON api_collection_metadata(api_source);
CREATE INDEX IF NOT EXISTS idx_api_collection_timestamp ON api_collection_metadata(collection_timestamp);
CREATE INDEX IF NOT EXISTS idx_api_collection_status ON api_collection_metadata(collection_status);

-- Data quality checks indexes
CREATE INDEX IF NOT EXISTS idx_data_quality_table ON data_quality_checks(table_name);
CREATE INDEX IF NOT EXISTS idx_data_quality_status ON data_quality_checks(check_status);
CREATE INDEX IF NOT EXISTS idx_data_quality_timestamp ON data_quality_checks(check_timestamp);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- ============================================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers to all tables with updated_at column
CREATE TRIGGER update_seasons_updated_at BEFORE UPDATE ON seasons
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_competitions_updated_at BEFORE UPDATE ON competitions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_players_updated_at BEFORE UPDATE ON players
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_matches_updated_at BEFORE UPDATE ON matches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_player_statistics_updated_at BEFORE UPDATE ON player_statistics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_team_statistics_updated_at BEFORE UPDATE ON team_statistics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA SETUP
-- ============================================================================

-- Insert seasons (2019-2024)
INSERT INTO seasons (season_name, sportmonks_season_id, api_football_season_id, start_date, end_date, is_current) VALUES
('2019-2020', 17141, 2019, '2019-08-01', '2020-07-31', FALSE),
('2020-2021', 18378, 2020, '2020-08-01', '2021-07-31', FALSE),
('2021-2022', 19686, 2021, '2021-08-01', '2022-07-31', FALSE),
('2022-2023', 21646, 2022, '2022-08-01', '2023-07-31', FALSE),
('2023-2024', 23087, 2023, '2023-08-01', '2024-07-31', FALSE),
('2024-2025', 24644, 2024, '2024-08-01', '2025-07-31', TRUE)
ON CONFLICT (season_name) DO NOTHING;

-- Insert major competitions
INSERT INTO competitions (competition_name, sportmonks_competition_id, api_football_competition_id, competition_type, country, priority) VALUES
('UEFA Champions League', 8, 2, 'international', 'Europe', 1),
('Premier League', 8, 39, 'domestic_league', 'England', 2),
('La Liga', 271, 140, 'domestic_league', 'Spain', 2),
('Bundesliga', 82, 78, 'domestic_league', 'Germany', 2),
('Serie A', 384, 135, 'domestic_league', 'Italy', 2),
('Ligue 1', 301, 61, 'domestic_league', 'France', 2),
('Copa del Rey', 75, 143, 'domestic_cup', 'Spain', 3),
('FA Cup', 65, 45, 'domestic_cup', 'England', 3),
('DFB-Pokal', 73, 81, 'domestic_cup', 'Germany', 3),
('Coppa Italia', 74, 137, 'domestic_cup', 'Italy', 3),
('Coupe de France', 76, 66, 'domestic_cup', 'France', 3)
ON CONFLICT (sportmonks_competition_id) DO NOTHING;

-- Log schema creation
INSERT INTO api_collection_metadata (collection_type, api_source, collection_status, notes, records_collected)
VALUES ('SCHEMA_CREATION', 'system', 'COMPLETED', 'Unified database schema created successfully for ADS599 Capstone project', 1)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View for team performance summary
CREATE OR REPLACE VIEW team_performance_summary AS
SELECT
    t.team_name,
    t.country,
    COUNT(DISTINCT m.match_id) as total_matches,
    SUM(CASE WHEN (m.home_team_id = t.team_id AND m.home_score > m.away_score)
              OR (m.away_team_id = t.team_id AND m.away_score > m.home_score)
         THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN m.home_score = m.away_score THEN 1 ELSE 0 END) as draws,
    SUM(CASE WHEN (m.home_team_id = t.team_id AND m.home_score < m.away_score)
              OR (m.away_team_id = t.team_id AND m.away_score < m.home_score)
         THEN 1 ELSE 0 END) as losses,
    SUM(CASE WHEN m.home_team_id = t.team_id THEN m.home_score ELSE m.away_score END) as goals_for,
    SUM(CASE WHEN m.home_team_id = t.team_id THEN m.away_score ELSE m.home_score END) as goals_against
FROM teams t
LEFT JOIN matches m ON (m.home_team_id = t.team_id OR m.away_team_id = t.team_id)
WHERE m.match_status = 'finished'
GROUP BY t.team_id, t.team_name, t.country;

-- View for player performance summary
CREATE OR REPLACE VIEW player_performance_summary AS
SELECT
    p.player_name,
    p.position,
    t.team_name,
    COUNT(ps.stat_id) as matches_played,
    SUM(ps.minutes_played) as total_minutes,
    SUM(ps.goals) as total_goals,
    SUM(ps.assists) as total_assists,
    AVG(ps.rating) as avg_rating,
    SUM(ps.yellow_cards) as yellow_cards,
    SUM(ps.red_cards) as red_cards
FROM players p
LEFT JOIN player_statistics ps ON p.player_id = ps.player_id
LEFT JOIN teams t ON p.current_team_id = t.team_id
WHERE ps.minutes_played > 0
GROUP BY p.player_id, p.player_name, p.position, t.team_name;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO soccerapp;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO soccerapp;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO soccerapp;
