-- SportMonks Database Schema
-- Generated from API exploration

-- TEAMS TABLES

CREATE TABLE teams_basic (
    id SERIAL PRIMARY KEY,
    id INTEGER NOT NULL,
    sport_id INTEGER NOT NULL,
    country_id INTEGER NOT NULL,
    venue_id INTEGER NOT NULL,
    gender VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    short_code VARCHAR(255) NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    founded INTEGER NOT NULL,
    type VARCHAR(255) NOT NULL,
    placeholder BOOLEAN NOT NULL,
    last_played_at VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Basic team information - core teams table


CREATE TABLE team_squads (
    id SERIAL PRIMARY KEY,
    id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    season_id INTEGER NOT NULL,
    has_values BOOLEAN NOT NULL,
    position_id INTEGER NOT NULL,
    jersey_number INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Team squad data - players table with team relationships

-- SEASONS TABLES

CREATE TABLE seasons (
    id SERIAL PRIMARY KEY,
    id INTEGER NOT NULL,
    sport_id INTEGER NOT NULL,
    league_id INTEGER NOT NULL,
    tie_breaker_rule_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    finished BOOLEAN NOT NULL,
    pending BOOLEAN NOT NULL,
    is_current BOOLEAN NOT NULL,
    starting_at VARCHAR(255) NOT NULL,
    ending_at VARCHAR(255) NOT NULL,
    standings_recalculated_at VARCHAR(255) NOT NULL,
    games_in_current_week BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Seasons data - seasons table

-- FIXTURES TABLES

CREATE TABLE fixtures (
    id SERIAL PRIMARY KEY,
    id INTEGER NOT NULL,
    sport_id INTEGER NOT NULL,
    league_id INTEGER NOT NULL,
    season_id INTEGER NOT NULL,
    stage_id INTEGER NOT NULL,
    group_id TEXT NULL,
    aggregate_id TEXT NULL,
    round_id INTEGER NOT NULL,
    state_id INTEGER NOT NULL,
    venue_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    starting_at VARCHAR(255) NOT NULL,
    result_info VARCHAR(255) NOT NULL,
    leg VARCHAR(255) NOT NULL,
    details TEXT NULL,
    length INTEGER NOT NULL,
    placeholder BOOLEAN NOT NULL,
    has_odds BOOLEAN NOT NULL,
    has_premium_odds BOOLEAN NOT NULL,
    starting_at_timestamp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Fixtures/matches data - matches table

-- PLAYERS TABLES

CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    id INTEGER NOT NULL,
    sport_id INTEGER NOT NULL,
    country_id INTEGER NOT NULL,
    nationality_id INTEGER NOT NULL,
    city_id INTEGER NOT NULL,
    position_id INTEGER NOT NULL,
    detailed_position_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    common_name VARCHAR(255) NOT NULL,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    height INTEGER NOT NULL,
    weight INTEGER NOT NULL,
    date_of_birth VARCHAR(255) NOT NULL,
    gender VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Individual player data - players table

