-- =====================================================
-- FOOTBALL DATABASE SCHEMA FOR POSTGRESQL
-- Optimized for Manchester City and Football Analytics
-- =====================================================

-- Enable UUID extension for unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- CORE ENTITIES
-- =====================================================

-- Leagues/Competitions table
CREATE TABLE competitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    country VARCHAR(50),
    tier INTEGER DEFAULT 1,
    season_format VARCHAR(20) DEFAULT 'Aug-May', -- Aug-May, Jan-Dec, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Teams table with validation constraints
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    short_name VARCHAR(20),
    official_name VARCHAR(150), -- For disambiguation (e.g., "Manchester City Football Club")
    city VARCHAR(50),
    country VARCHAR(50),
    founded_year INTEGER,
    stadium_name VARCHAR(100),
    stadium_capacity INTEGER,
    primary_color VARCHAR(7), -- Hex color code
    secondary_color VARCHAR(7),
    fbref_url TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint to prevent team name confusion
    CONSTRAINT unique_team_name_country UNIQUE (name, country),
    CONSTRAINT valid_founded_year CHECK (founded_year > 1800 AND founded_year <= EXTRACT(YEAR FROM CURRENT_DATE))
);

-- Players table with comprehensive information
CREATE TABLE players (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    full_name VARCHAR(100) GENERATED ALWAYS AS (first_name || ' ' || last_name) STORED,
    date_of_birth DATE,
    nationality VARCHAR(3), -- ISO 3-letter country code
    height_cm INTEGER,
    weight_kg INTEGER,
    preferred_foot VARCHAR(5) CHECK (preferred_foot IN ('Left', 'Right', 'Both')),
    fbref_url TEXT UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Validation constraints
    CONSTRAINT valid_height CHECK (height_cm BETWEEN 150 AND 220),
    CONSTRAINT valid_weight CHECK (weight_kg BETWEEN 50 AND 120)
);

-- Player positions (many-to-many relationship)
CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(3) NOT NULL UNIQUE, -- GK, DF, MF, FW
    name VARCHAR(20) NOT NULL UNIQUE, -- Goalkeeper, Defender, Midfielder, Forward
    description TEXT
);

-- Player-Position mapping
CREATE TABLE player_positions (
    player_id UUID REFERENCES players(id) ON DELETE CASCADE,
    position_id UUID REFERENCES positions(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (player_id, position_id)
);

-- Team squads (players in teams for specific seasons)
CREATE TABLE team_squads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    season VARCHAR(10) NOT NULL, -- e.g., "2023-24"
    jersey_number INTEGER,
    join_date DATE,
    leave_date DATE,
    transfer_fee_millions DECIMAL(10,2),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_player_team_season UNIQUE (team_id, player_id, season),
    CONSTRAINT unique_jersey_number_team_season UNIQUE (team_id, jersey_number, season),
    CONSTRAINT valid_jersey_number CHECK (jersey_number BETWEEN 1 AND 99),
    CONSTRAINT valid_dates CHECK (leave_date IS NULL OR leave_date >= join_date)
);

-- =====================================================
-- MATCH DATA
-- =====================================================

-- Matches table
CREATE TABLE matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    season VARCHAR(10) NOT NULL,
    match_date DATE NOT NULL,
    competition_id UUID NOT NULL REFERENCES competitions(id),
    matchday INTEGER,
    home_team_id UUID NOT NULL REFERENCES teams(id),
    away_team_id UUID NOT NULL REFERENCES teams(id),
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    match_status VARCHAR(20) DEFAULT 'Scheduled', -- Scheduled, Live, Finished, Postponed, Cancelled
    venue VARCHAR(100),
    attendance INTEGER,
    referee VARCHAR(100),
    weather_conditions TEXT,
    
    -- Match statistics
    home_possession_pct DECIMAL(5,2),
    away_possession_pct DECIMAL(5,2),
    
    -- Timestamps
    kickoff_time TIME,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT different_teams CHECK (home_team_id != away_team_id),
    CONSTRAINT valid_scores CHECK (home_score >= 0 AND away_score >= 0),
    CONSTRAINT valid_possession CHECK (
        (home_possession_pct IS NULL AND away_possession_pct IS NULL) OR
        (home_possession_pct + away_possession_pct = 100)
    ),
    CONSTRAINT valid_attendance CHECK (attendance >= 0)
);

-- Match team statistics (team-level stats for each match)
CREATE TABLE match_team_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES teams(id),
    is_home BOOLEAN NOT NULL,
    
    -- Shooting statistics
    shots_total INTEGER DEFAULT 0,
    shots_on_target INTEGER DEFAULT 0,
    shots_off_target INTEGER DEFAULT 0,
    shots_blocked INTEGER DEFAULT 0,
    
    -- Passing statistics
    passes_total INTEGER DEFAULT 0,
    passes_completed INTEGER DEFAULT 0,
    pass_accuracy DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN passes_total > 0 THEN (passes_completed::DECIMAL / passes_total * 100) ELSE 0 END
    ) STORED,
    
    -- Defensive statistics
    tackles_total INTEGER DEFAULT 0,
    tackles_won INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    clearances INTEGER DEFAULT 0,
    blocks INTEGER DEFAULT 0,
    
    -- Disciplinary
    fouls_committed INTEGER DEFAULT 0,
    fouls_suffered INTEGER DEFAULT 0,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    
    -- Set pieces
    corners INTEGER DEFAULT 0,
    offsides INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_match_team UNIQUE (match_id, team_id),
    CONSTRAINT valid_shots CHECK (shots_total >= shots_on_target + shots_off_target + shots_blocked),
    CONSTRAINT valid_passes CHECK (passes_total >= passes_completed),
    CONSTRAINT valid_tackles CHECK (tackles_total >= tackles_won)
);

-- =====================================================
-- PLAYER PERFORMANCE DATA
-- =====================================================

-- Player match performances (individual player stats per match)
CREATE TABLE player_match_performances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES teams(id),

    -- Playing time
    started BOOLEAN DEFAULT false,
    minutes_played INTEGER DEFAULT 0,
    position_played VARCHAR(10),
    formation_position VARCHAR(10),
    substituted_in INTEGER, -- Minute substituted in
    substituted_out INTEGER, -- Minute substituted out

    -- Performance metrics
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    shots_total INTEGER DEFAULT 0,
    shots_on_target INTEGER DEFAULT 0,

    -- Passing
    passes_total INTEGER DEFAULT 0,
    passes_completed INTEGER DEFAULT 0,
    pass_accuracy DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN passes_total > 0 THEN (passes_completed::DECIMAL / passes_total * 100) ELSE 0 END
    ) STORED,

    -- Defensive actions
    tackles_total INTEGER DEFAULT 0,
    tackles_won INTEGER DEFAULT 0,
    tackle_success_rate DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN tackles_total > 0 THEN (tackles_won::DECIMAL / tackles_total * 100) ELSE 0 END
    ) STORED,
    interceptions INTEGER DEFAULT 0,
    clearances INTEGER DEFAULT 0,
    blocks INTEGER DEFAULT 0,

    -- Disciplinary
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    fouls_committed INTEGER DEFAULT 0,
    fouls_suffered INTEGER DEFAULT 0,

    -- Advanced metrics
    touches INTEGER DEFAULT 0,
    rating DECIMAL(3,1), -- Match rating (e.g., 7.5)
    distance_covered_km DECIMAL(4,1),

    -- Per 90 minute statistics
    goals_per_90 DECIMAL(4,2) GENERATED ALWAYS AS (
        CASE WHEN minutes_played > 0 THEN (goals::DECIMAL / minutes_played * 90) ELSE 0 END
    ) STORED,
    assists_per_90 DECIMAL(4,2) GENERATED ALWAYS AS (
        CASE WHEN minutes_played > 0 THEN (assists::DECIMAL / minutes_played * 90) ELSE 0 END
    ) STORED,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT unique_player_match UNIQUE (match_id, player_id),
    CONSTRAINT valid_minutes CHECK (minutes_played BETWEEN 0 AND 120),
    CONSTRAINT valid_substitution CHECK (
        (substituted_in IS NULL AND substituted_out IS NULL) OR
        (substituted_in IS NOT NULL AND substituted_out IS NULL AND NOT started) OR
        (substituted_in IS NULL AND substituted_out IS NOT NULL AND started) OR
        (substituted_in IS NOT NULL AND substituted_out IS NOT NULL AND substituted_out > substituted_in)
    ),
    CONSTRAINT valid_shots CHECK (shots_total >= shots_on_target),
    CONSTRAINT valid_passes_perf CHECK (passes_total >= passes_completed),
    CONSTRAINT valid_tackles_perf CHECK (tackles_total >= tackles_won),
    CONSTRAINT valid_rating CHECK (rating BETWEEN 0 AND 10)
);

-- Player season statistics (aggregated stats per season)
CREATE TABLE player_season_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES teams(id),
    season VARCHAR(10) NOT NULL,
    competition_id UUID REFERENCES competitions(id),

    -- Appearance data
    matches_played INTEGER DEFAULT 0,
    starts INTEGER DEFAULT 0,
    minutes_played INTEGER DEFAULT 0,

    -- Goal statistics
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    shots_total INTEGER DEFAULT 0,
    shots_on_target INTEGER DEFAULT 0,
    shot_accuracy DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN shots_total > 0 THEN (shots_on_target::DECIMAL / shots_total * 100) ELSE 0 END
    ) STORED,

    -- Passing statistics
    passes_completed INTEGER DEFAULT 0,
    passes_attempted INTEGER DEFAULT 0,
    pass_accuracy DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN passes_attempted > 0 THEN (passes_completed::DECIMAL / passes_attempted * 100) ELSE 0 END
    ) STORED,

    -- Defensive statistics
    tackles INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    blocks INTEGER DEFAULT 0,
    clearances INTEGER DEFAULT 0,

    -- Disciplinary
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    fouls_committed INTEGER DEFAULT 0,
    fouls_drawn INTEGER DEFAULT 0,

    -- Advanced metrics
    average_rating DECIMAL(3,1),
    total_distance_km DECIMAL(6,1),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT unique_player_season_competition UNIQUE (player_id, team_id, season, competition_id),
    CONSTRAINT valid_appearances CHECK (matches_played >= starts),
    CONSTRAINT valid_season_shots CHECK (shots_total >= shots_on_target),
    CONSTRAINT valid_season_passes CHECK (passes_attempted >= passes_completed)
);

-- =====================================================
-- DATA VALIDATION AND INTEGRITY
-- =====================================================

-- Key players validation table (for Manchester City focus)
CREATE TABLE key_players_validation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_name VARCHAR(100) NOT NULL,
    team_name VARCHAR(100) NOT NULL,
    expected_position VARCHAR(10),
    nationality VARCHAR(3),
    is_active BOOLEAN DEFAULT true,
    validation_priority INTEGER DEFAULT 1, -- 1 = highest priority
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert key Manchester City players for validation
INSERT INTO key_players_validation (player_name, team_name, expected_position, nationality, validation_priority) VALUES
('Erling Haaland', 'Manchester City', 'FW', 'NOR', 1),
('Kevin De Bruyne', 'Manchester City', 'MF', 'BEL', 1),
('Phil Foden', 'Manchester City', 'MF', 'ENG', 1),
('Bernardo Silva', 'Manchester City', 'MF', 'POR', 2),
('Rodri', 'Manchester City', 'MF', 'ESP', 2),
('Rúben Dias', 'Manchester City', 'DF', 'POR', 2);

-- Team validation to prevent confusion
CREATE TABLE team_aliases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    official_team_id UUID NOT NULL REFERENCES teams(id),
    alias VARCHAR(100) NOT NULL,
    is_common_confusion BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_alias UNIQUE (alias)
);

-- =====================================================
-- PERFORMANCE INDEXES
-- =====================================================

-- Teams indexes
CREATE INDEX idx_teams_name ON teams(name);
CREATE INDEX idx_teams_country ON teams(country);
CREATE INDEX idx_teams_active ON teams(is_active);

-- Players indexes
CREATE INDEX idx_players_full_name ON players(full_name);
CREATE INDEX idx_players_nationality ON players(nationality);
CREATE INDEX idx_players_fbref_url ON players(fbref_url);

-- Team squads indexes
CREATE INDEX idx_team_squads_team_season ON team_squads(team_id, season);
CREATE INDEX idx_team_squads_player_season ON team_squads(player_id, season);
CREATE INDEX idx_team_squads_active ON team_squads(is_active);

-- Matches indexes
CREATE INDEX idx_matches_date ON matches(match_date);
CREATE INDEX idx_matches_season ON matches(season);
CREATE INDEX idx_matches_competition ON matches(competition_id);
CREATE INDEX idx_matches_home_team ON matches(home_team_id);
CREATE INDEX idx_matches_away_team ON matches(away_team_id);
CREATE INDEX idx_matches_teams ON matches(home_team_id, away_team_id);
CREATE INDEX idx_matches_season_competition ON matches(season, competition_id);

-- Player match performances indexes (critical for analytics)
CREATE INDEX idx_player_performances_match ON player_match_performances(match_id);
CREATE INDEX idx_player_performances_player ON player_match_performances(player_id);
CREATE INDEX idx_player_performances_team ON player_match_performances(team_id);
CREATE INDEX idx_player_performances_player_season ON player_match_performances(player_id, match_id);
CREATE INDEX idx_player_performances_goals ON player_match_performances(goals) WHERE goals > 0;
CREATE INDEX idx_player_performances_assists ON player_match_performances(assists) WHERE assists > 0;
CREATE INDEX idx_player_performances_rating ON player_match_performances(rating) WHERE rating IS NOT NULL;
CREATE INDEX idx_player_performances_minutes ON player_match_performances(minutes_played);

-- Player season stats indexes
CREATE INDEX idx_player_season_stats_player ON player_season_stats(player_id);
CREATE INDEX idx_player_season_stats_team ON player_season_stats(team_id);
CREATE INDEX idx_player_season_stats_season ON player_season_stats(season);
CREATE INDEX idx_player_season_stats_competition ON player_season_stats(competition_id);
CREATE INDEX idx_player_season_stats_goals ON player_season_stats(goals) WHERE goals > 0;

-- Match team stats indexes
CREATE INDEX idx_match_team_stats_match ON match_team_stats(match_id);
CREATE INDEX idx_match_team_stats_team ON match_team_stats(team_id);

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Manchester City focused view
CREATE VIEW manchester_city_squad AS
SELECT
    p.id as player_id,
    p.full_name,
    p.nationality,
    ts.jersey_number,
    ts.season,
    pos.code as position_code,
    pos.name as position_name,
    pp.is_primary as is_primary_position
FROM players p
JOIN team_squads ts ON p.id = ts.player_id
JOIN teams t ON ts.team_id = t.id
LEFT JOIN player_positions pp ON p.id = pp.player_id
LEFT JOIN positions pos ON pp.position_id = pos.id
WHERE t.name = 'Manchester City'
  AND ts.is_active = true;

-- Player performance summary view
CREATE VIEW player_performance_summary AS
SELECT
    p.full_name,
    t.name as team_name,
    m.season,
    COUNT(pmp.id) as matches_played,
    SUM(pmp.minutes_played) as total_minutes,
    SUM(pmp.goals) as total_goals,
    SUM(pmp.assists) as total_assists,
    AVG(pmp.rating) as average_rating,
    SUM(pmp.goals)::DECIMAL / NULLIF(SUM(pmp.minutes_played), 0) * 90 as goals_per_90,
    SUM(pmp.assists)::DECIMAL / NULLIF(SUM(pmp.minutes_played), 0) * 90 as assists_per_90
FROM players p
JOIN player_match_performances pmp ON p.id = pmp.player_id
JOIN matches m ON pmp.match_id = m.id
JOIN teams t ON pmp.team_id = t.id
GROUP BY p.id, p.full_name, t.name, m.season;
