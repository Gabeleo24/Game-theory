-- Enhanced Database Schema for Comprehensive Soccer Intelligence
-- Supports multiple teams, seasons, and detailed analytics
-- Created: 2025-07-09

-- ============================================================================
-- SEASONS TABLE - Track multiple seasons
-- ============================================================================
CREATE TABLE IF NOT EXISTS seasons (
    season_id SERIAL PRIMARY KEY,
    sportmonks_season_id INTEGER UNIQUE,
    season_name VARCHAR(100) NOT NULL,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ENHANCED COMPETITIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS enhanced_competitions (
    competition_id SERIAL PRIMARY KEY,
    sportmonks_competition_id INTEGER UNIQUE,
    competition_name VARCHAR(255) NOT NULL,
    competition_type VARCHAR(100),
    country VARCHAR(100),
    season_id INTEGER REFERENCES seasons(season_id),
    priority_level INTEGER DEFAULT 1, -- 1=highest priority
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ENHANCED TEAMS TABLE - Support for multiple teams
-- ============================================================================
CREATE TABLE IF NOT EXISTS enhanced_teams (
    team_id SERIAL PRIMARY KEY,
    sportmonks_team_id INTEGER UNIQUE,
    team_name VARCHAR(255) NOT NULL,
    short_name VARCHAR(50),
    country VARCHAR(100),
    founded_year INTEGER,
    venue_name VARCHAR(255),
    venue_city VARCHAR(255),
    venue_capacity INTEGER,
    logo_url TEXT,
    is_champions_league_team BOOLEAN DEFAULT FALSE,
    priority_level INTEGER DEFAULT 1, -- 1=Real Madrid, 2=other UCL teams
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ENHANCED PLAYERS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS enhanced_players (
    player_id SERIAL PRIMARY KEY,
    sportmonks_player_id INTEGER UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    display_name VARCHAR(255),
    date_of_birth DATE,
    nationality VARCHAR(100),
    height INTEGER, -- in cm
    weight INTEGER, -- in kg
    preferred_foot VARCHAR(10),
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PLAYER POSITIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS player_positions (
    position_id SERIAL PRIMARY KEY,
    sportmonks_position_id INTEGER UNIQUE,
    position_name VARCHAR(100) NOT NULL,
    position_code VARCHAR(10),
    position_category VARCHAR(50), -- Goalkeeper, Defender, Midfielder, Forward
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TEAM SEASONS - Track which teams played in which seasons
-- ============================================================================
CREATE TABLE IF NOT EXISTS team_seasons (
    team_season_id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES enhanced_teams(team_id),
    season_id INTEGER REFERENCES seasons(season_id),
    league_position INTEGER,
    points INTEGER,
    games_played INTEGER,
    wins INTEGER,
    draws INTEGER,
    losses INTEGER,
    goals_for INTEGER,
    goals_against INTEGER,
    goal_difference INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, season_id)
);

-- ============================================================================
-- ENHANCED MATCHES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS enhanced_matches (
    match_id SERIAL PRIMARY KEY,
    sportmonks_match_id INTEGER UNIQUE,
    season_id INTEGER REFERENCES seasons(season_id),
    competition_id INTEGER REFERENCES enhanced_competitions(competition_id),
    home_team_id INTEGER REFERENCES enhanced_teams(team_id),
    away_team_id INTEGER REFERENCES enhanced_teams(team_id),
    match_date TIMESTAMP,
    match_week INTEGER,
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    match_status VARCHAR(50),
    venue_name VARCHAR(255),
    attendance INTEGER,
    referee_name VARCHAR(255),
    weather_conditions TEXT,
    match_importance INTEGER DEFAULT 1, -- 1=highest importance
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ENHANCED PLAYER STATISTICS TABLE - Match-level statistics
-- ============================================================================
CREATE TABLE IF NOT EXISTS enhanced_player_statistics (
    stat_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES enhanced_matches(match_id),
    player_id INTEGER REFERENCES enhanced_players(player_id),
    team_id INTEGER REFERENCES enhanced_teams(team_id),
    position_id INTEGER REFERENCES player_positions(position_id),
    
    -- Basic Performance
    minutes_played INTEGER DEFAULT 0,
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    shots INTEGER DEFAULT 0,
    shots_on_target INTEGER DEFAULT 0,
    
    -- Passing
    passes_attempted INTEGER DEFAULT 0,
    passes_completed INTEGER DEFAULT 0,
    pass_accuracy DECIMAL(5,2) DEFAULT 0.0,
    key_passes INTEGER DEFAULT 0,
    crosses_attempted INTEGER DEFAULT 0,
    crosses_completed INTEGER DEFAULT 0,
    
    -- Defensive
    tackles_attempted INTEGER DEFAULT 0,
    tackles_successful INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    clearances INTEGER DEFAULT 0,
    blocks INTEGER DEFAULT 0,
    
    -- Disciplinary
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    fouls_committed INTEGER DEFAULT 0,
    fouls_suffered INTEGER DEFAULT 0,
    
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
-- TEAM PERFORMANCE CACHE - Aggregated team statistics
-- ============================================================================
CREATE TABLE IF NOT EXISTS team_performance_cache (
    cache_id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES enhanced_teams(team_id),
    season_id INTEGER REFERENCES seasons(season_id),
    competition_id INTEGER REFERENCES enhanced_competitions(competition_id),
    
    -- Aggregated Statistics
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    goals_scored INTEGER DEFAULT 0,
    goals_conceded INTEGER DEFAULT 0,
    clean_sheets INTEGER DEFAULT 0,
    
    -- Performance Metrics
    avg_possession DECIMAL(5,2) DEFAULT 0.0,
    avg_shots_per_game DECIMAL(5,2) DEFAULT 0.0,
    avg_shots_on_target DECIMAL(5,2) DEFAULT 0.0,
    avg_pass_accuracy DECIMAL(5,2) DEFAULT 0.0,
    
    -- Cache Metadata
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cache_valid_until TIMESTAMP,
    
    UNIQUE(team_id, season_id, competition_id)
);

-- ============================================================================
-- DATA COLLECTION TRACKING
-- ============================================================================
CREATE TABLE IF NOT EXISTS collection_progress (
    progress_id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES enhanced_teams(team_id),
    season_id INTEGER REFERENCES seasons(season_id),
    collection_type VARCHAR(100), -- 'MATCHES', 'PLAYERS', 'STATISTICS'
    total_expected INTEGER DEFAULT 0,
    total_collected INTEGER DEFAULT 0,
    last_collection_date TIMESTAMP,
    collection_status VARCHAR(50) DEFAULT 'PENDING',
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(team_id, season_id, collection_type)
);

-- ============================================================================
-- INDEXES for Performance Optimization
-- ============================================================================

-- Primary lookup indexes
CREATE INDEX IF NOT EXISTS idx_enhanced_matches_teams ON enhanced_matches(home_team_id, away_team_id);
CREATE INDEX IF NOT EXISTS idx_enhanced_matches_date ON enhanced_matches(match_date);
CREATE INDEX IF NOT EXISTS idx_enhanced_matches_season ON enhanced_matches(season_id);
CREATE INDEX IF NOT EXISTS idx_enhanced_matches_competition ON enhanced_matches(competition_id);

-- Player statistics indexes
CREATE INDEX IF NOT EXISTS idx_player_stats_match ON enhanced_player_statistics(match_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_player ON enhanced_player_statistics(player_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_team ON enhanced_player_statistics(team_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_performance ON enhanced_player_statistics(goals, assists, rating);

-- Team performance indexes
CREATE INDEX IF NOT EXISTS idx_team_seasons_lookup ON team_seasons(team_id, season_id);
CREATE INDEX IF NOT EXISTS idx_team_performance_cache_lookup ON team_performance_cache(team_id, season_id);

-- Collection tracking indexes
CREATE INDEX IF NOT EXISTS idx_collection_progress_status ON collection_progress(collection_status);
CREATE INDEX IF NOT EXISTS idx_collection_progress_team_season ON collection_progress(team_id, season_id);

-- ============================================================================
-- INITIAL DATA SETUP
-- ============================================================================

-- Insert Real Madrid as priority team
INSERT INTO enhanced_teams (
    sportmonks_team_id, team_name, short_name, country, founded_year,
    is_champions_league_team, priority_level
) VALUES (
    53, 'Real Madrid', 'RMA', 'Spain', 1902, TRUE, 1
) ON CONFLICT (sportmonks_team_id) DO UPDATE SET
    is_champions_league_team = TRUE,
    priority_level = 1,
    updated_at = CURRENT_TIMESTAMP;

-- Insert seasons 2019-2024
INSERT INTO seasons (sportmonks_season_id, season_name, start_date, end_date) VALUES
    (19686, '2019-2020', '2019-08-01', '2020-07-31'),
    (19734, '2020-2021', '2020-08-01', '2021-07-31'),
    (21646, '2021-2022', '2021-08-01', '2022-07-31'),
    (21647, '2022-2023', '2022-08-01', '2023-07-31'),
    (21648, '2023-2024', '2023-08-01', '2024-07-31')
ON CONFLICT (sportmonks_season_id) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO soccerapp;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO soccerapp;
