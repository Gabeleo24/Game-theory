-- SportMonks Real Madrid 2023-2024 Season Database Schema
-- Optimized for match-level player statistics collection
-- Focus: Real Madrid team ID 53, Season ID 23087
-- Created: 2025-07-09

-- ============================================================================
-- DROP EXISTING TABLES (Clean Reset)
-- ============================================================================
DROP TABLE IF EXISTS player_match_statistics CASCADE;
DROP TABLE IF EXISTS match_events CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS teams CASCADE;
DROP TABLE IF EXISTS competitions CASCADE;
DROP TABLE IF EXISTS seasons CASCADE;
DROP TABLE IF EXISTS data_collection_log CASCADE;

-- ============================================================================
-- SEASONS TABLE
-- ============================================================================
CREATE TABLE seasons (
    season_id SERIAL PRIMARY KEY,
    sportmonks_season_id INTEGER UNIQUE NOT NULL,
    season_name VARCHAR(100) NOT NULL,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- COMPETITIONS TABLE
-- ============================================================================
CREATE TABLE competitions (
    competition_id SERIAL PRIMARY KEY,
    sportmonks_competition_id INTEGER UNIQUE NOT NULL,
    competition_name VARCHAR(255) NOT NULL,
    competition_type VARCHAR(100),
    country VARCHAR(100),
    season_id INTEGER REFERENCES seasons(season_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TEAMS TABLE
-- ============================================================================
CREATE TABLE teams (
    team_id SERIAL PRIMARY KEY,
    sportmonks_team_id INTEGER UNIQUE NOT NULL,
    team_name VARCHAR(255) NOT NULL,
    short_name VARCHAR(50),
    country VARCHAR(100),
    founded_year INTEGER,
    venue_name VARCHAR(255),
    venue_city VARCHAR(255),
    logo_url TEXT,
    is_real_madrid BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PLAYERS TABLE
-- ============================================================================
CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    sportmonks_player_id INTEGER UNIQUE NOT NULL,
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MATCHES TABLE
-- ============================================================================
CREATE TABLE matches (
    match_id SERIAL PRIMARY KEY,
    sportmonks_match_id INTEGER UNIQUE NOT NULL,
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
    home_score_ht INTEGER DEFAULT 0,
    away_score_ht INTEGER DEFAULT 0,
    
    -- Match details
    match_status VARCHAR(50) DEFAULT 'finished',
    venue_name VARCHAR(255),
    venue_city VARCHAR(255),
    attendance INTEGER,
    referee_name VARCHAR(255),
    
    -- Real Madrid involvement
    real_madrid_home BOOLEAN DEFAULT FALSE,
    real_madrid_away BOOLEAN DEFAULT FALSE,
    
    -- Collection status
    players_collected BOOLEAN DEFAULT FALSE,
    statistics_collected BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PLAYER_MATCH_STATISTICS TABLE (Core table for individual game performance)
-- ============================================================================
CREATE TABLE player_match_statistics (
    stat_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id) NOT NULL,
    player_id INTEGER REFERENCES players(player_id) NOT NULL,
    team_id INTEGER REFERENCES teams(team_id) NOT NULL,
    
    -- Basic match info
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
    shots_inside_box INTEGER DEFAULT 0,
    shots_outside_box INTEGER DEFAULT 0,
    
    -- Passing statistics
    passes_total INTEGER DEFAULT 0,
    passes_completed INTEGER DEFAULT 0,
    passes_accuracy DECIMAL(5,2) DEFAULT 0.0,
    passes_key INTEGER DEFAULT 0,
    passes_forward INTEGER DEFAULT 0,
    passes_backward INTEGER DEFAULT 0,
    crosses_total INTEGER DEFAULT 0,
    crosses_completed INTEGER DEFAULT 0,
    
    -- Defensive statistics
    tackles_total INTEGER DEFAULT 0,
    tackles_successful INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    clearances INTEGER DEFAULT 0,
    blocks INTEGER DEFAULT 0,
    duels_total INTEGER DEFAULT 0,
    duels_won INTEGER DEFAULT 0,
    aerial_duels_total INTEGER DEFAULT 0,
    aerial_duels_won INTEGER DEFAULT 0,
    
    -- Disciplinary
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    fouls_committed INTEGER DEFAULT 0,
    fouls_suffered INTEGER DEFAULT 0,
    
    -- Advanced metrics
    rating DECIMAL(4,2) DEFAULT 0.0,
    touches INTEGER DEFAULT 0,
    touches_penalty_area INTEGER DEFAULT 0,
    dribbles_attempted INTEGER DEFAULT 0,
    dribbles_successful INTEGER DEFAULT 0,
    offsides INTEGER DEFAULT 0,
    
    -- Goalkeeper specific (for goalkeepers)
    saves INTEGER DEFAULT 0,
    saves_inside_box INTEGER DEFAULT 0,
    saves_outside_box INTEGER DEFAULT 0,
    goals_conceded INTEGER DEFAULT 0,
    clean_sheet BOOLEAN DEFAULT FALSE,
    punches INTEGER DEFAULT 0,
    high_claims INTEGER DEFAULT 0,
    
    -- Distance and speed metrics (if available)
    distance_covered INTEGER DEFAULT 0,
    top_speed DECIMAL(5,2) DEFAULT 0.0,
    sprints INTEGER DEFAULT 0,
    
    -- Collection metadata
    data_source VARCHAR(50) DEFAULT 'SportMonks',
    collection_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure unique player per match
    UNIQUE(match_id, player_id)
);

-- ============================================================================
-- MATCH_EVENTS TABLE (Goals, cards, substitutions, etc.)
-- ============================================================================
CREATE TABLE match_events (
    event_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id) NOT NULL,
    sportmonks_event_id INTEGER UNIQUE,
    
    -- Event details
    event_type VARCHAR(50) NOT NULL, -- goal, card, substitution, etc.
    event_minute INTEGER NOT NULL,
    event_second INTEGER DEFAULT 0,
    period VARCHAR(20) DEFAULT '1H', -- 1H, 2H, ET, P
    
    -- Players involved
    player_id INTEGER REFERENCES players(player_id),
    related_player_id INTEGER REFERENCES players(player_id), -- assist, substitution
    team_id INTEGER REFERENCES teams(team_id) NOT NULL,
    
    -- Event specific details
    event_details JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- DATA_COLLECTION_LOG TABLE (Track collection progress)
-- ============================================================================
CREATE TABLE data_collection_log (
    log_id SERIAL PRIMARY KEY,
    collection_type VARCHAR(100) NOT NULL,
    target_description TEXT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(50) DEFAULT 'IN_PROGRESS',
    records_collected INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    api_requests INTEGER DEFAULT 0,
    error_messages TEXT,
    notes TEXT
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Primary lookup indexes
CREATE INDEX idx_teams_sportmonks_id ON teams(sportmonks_team_id);
CREATE INDEX idx_players_sportmonks_id ON players(sportmonks_player_id);
CREATE INDEX idx_matches_sportmonks_id ON matches(sportmonks_match_id);
CREATE INDEX idx_competitions_sportmonks_id ON competitions(sportmonks_competition_id);

-- Real Madrid specific indexes
CREATE INDEX idx_teams_real_madrid ON teams(is_real_madrid);
CREATE INDEX idx_matches_real_madrid_home ON matches(real_madrid_home);
CREATE INDEX idx_matches_real_madrid_away ON matches(real_madrid_away);

-- Player statistics indexes
CREATE INDEX idx_player_stats_match ON player_match_statistics(match_id);
CREATE INDEX idx_player_stats_player ON player_match_statistics(player_id);
CREATE INDEX idx_player_stats_team ON player_match_statistics(team_id);
CREATE INDEX idx_player_stats_minutes ON player_match_statistics(minutes_played);
CREATE INDEX idx_player_stats_goals ON player_match_statistics(goals);
CREATE INDEX idx_player_stats_assists ON player_match_statistics(assists);
CREATE INDEX idx_player_stats_rating ON player_match_statistics(rating);

-- Match lookup indexes
CREATE INDEX idx_matches_date ON matches(match_date);
CREATE INDEX idx_matches_competition ON matches(competition_id);
CREATE INDEX idx_matches_season ON matches(season_id);
CREATE INDEX idx_matches_home_team ON matches(home_team_id);
CREATE INDEX idx_matches_away_team ON matches(away_team_id);

-- Collection status indexes
CREATE INDEX idx_matches_players_collected ON matches(players_collected);
CREATE INDEX idx_matches_statistics_collected ON matches(statistics_collected);

-- Event indexes
CREATE INDEX idx_events_match ON match_events(match_id);
CREATE INDEX idx_events_player ON match_events(player_id);
CREATE INDEX idx_events_type ON match_events(event_type);

-- ============================================================================
-- INITIAL DATA SETUP
-- ============================================================================

-- Insert 2023-2024 season
INSERT INTO seasons (sportmonks_season_id, season_name, start_date, end_date, is_current)
VALUES (23087, '2023-2024', '2023-08-01', '2024-07-31', FALSE);

-- Insert Real Madrid team
INSERT INTO teams (sportmonks_team_id, team_name, short_name, country, founded_year, 
                  venue_name, venue_city, is_real_madrid)
VALUES (53, 'Real Madrid', 'RMA', 'Spain', 1902, 'Santiago Bernabéu', 'Madrid', TRUE);

-- Insert major competitions (will be populated during collection)
INSERT INTO competitions (sportmonks_competition_id, competition_name, competition_type, country, season_id)
VALUES 
    (8, 'UEFA Champions League', 'International Cup', 'Europe', 1),
    (271, 'La Liga', 'Domestic League', 'Spain', 1),
    (75, 'Copa del Rey', 'Domestic Cup', 'Spain', 1);

-- Log initial setup
INSERT INTO data_collection_log (collection_type, target_description, status, notes)
VALUES ('SCHEMA_SETUP', 'SportMonks Real Madrid 2023-2024 schema initialization', 'COMPLETED', 
        'Clean database schema created for Real Madrid match-level player statistics collection');

-- ============================================================================
-- VIEWS FOR ANALYSIS
-- ============================================================================

-- Real Madrid player performance summary
CREATE VIEW real_madrid_player_summary AS
SELECT 
    p.player_name,
    p.position,
    COUNT(pms.stat_id) as matches_played,
    SUM(pms.minutes_played) as total_minutes,
    ROUND(AVG(pms.minutes_played), 1) as avg_minutes_per_match,
    SUM(pms.goals) as total_goals,
    SUM(pms.assists) as total_assists,
    ROUND(AVG(pms.rating), 2) as avg_rating,
    SUM(pms.shots_total) as total_shots,
    SUM(pms.shots_on_target) as shots_on_target,
    SUM(pms.passes_completed) as passes_completed,
    ROUND(AVG(pms.passes_accuracy), 1) as avg_pass_accuracy,
    SUM(pms.tackles_successful) as tackles_successful,
    SUM(pms.yellow_cards) as yellow_cards,
    SUM(pms.red_cards) as red_cards
FROM players p
JOIN player_match_statistics pms ON p.player_id = pms.player_id
JOIN teams t ON p.team_id = t.team_id
WHERE t.is_real_madrid = TRUE
  AND pms.minutes_played > 0
GROUP BY p.player_id, p.player_name, p.position
ORDER BY total_minutes DESC;

-- Real Madrid match results
CREATE VIEW real_madrid_matches AS
SELECT 
    m.match_date,
    c.competition_name,
    m.round_name,
    CASE 
        WHEN m.real_madrid_home THEN ht.team_name || ' vs ' || at.team_name
        ELSE ht.team_name || ' vs ' || at.team_name
    END as fixture,
    CASE 
        WHEN m.real_madrid_home THEN m.home_score || '-' || m.away_score
        ELSE m.away_score || '-' || m.home_score
    END as score,
    m.venue_name,
    m.players_collected,
    m.statistics_collected
FROM matches m
JOIN teams ht ON m.home_team_id = ht.team_id
JOIN teams at ON m.away_team_id = at.team_id
JOIN competitions c ON m.competition_id = c.competition_id
WHERE m.real_madrid_home = TRUE OR m.real_madrid_away = TRUE
ORDER BY m.match_date;

-- Grant permissions (assuming default user)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO soccerapp;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO soccerapp;
