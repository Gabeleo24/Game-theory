-- SQL Query Log
-- Timestamp: 2025-07-06 18:18:51
-- Description: Foreign Key Relationships Analysis
-- Results: 11 rows
-- ============================================================

-- ORIGINAL QUERY:
/*
SELECT tc.table_name as source_table, kcu.column_name as source_column, ccu.table_name as target_table, ccu.column_name as target_column, CONCAT(tc.table_name, '.', kcu.column_name, ' -> ', ccu.table_name, '.', ccu.column_name) as relationship_chain FROM information_schema.table_constraints tc JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public' ORDER BY tc.table_name, kcu.column_name;
*/

-- RESULTS SUMMARY:
-- Total rows: 11
-- Columns: source_table, source_column, target_table, target_column, relationship_chain

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- source_table    | source_column   | target_table    | target_column   | relationship_chain
-- --------------------------------------------------------------------------------
-- matches         | away_team_id    | teams           | team_id         | matches.away_te
-- matches         | competition_id  | competitions    | competition_id  | matches.competi
-- matches         | home_team_id    | teams           | team_id         | matches.home_te
-- player_statisti | competition_id  | competitions    | competition_id  | player_statisti
-- player_statisti | match_id        | matches         | match_id        | player_statisti
-- player_statisti | player_id       | players         | player_id       | player_statisti
-- player_statisti | team_id         | teams           | team_id         | player_statisti
-- shapley_analysi | player_id       | players         | player_id       | shapley_analysi
-- shapley_analysi | team_id         | teams           | team_id         | shapley_analysi
-- team_statistics | competition_id  | competitions    | competition_id  | team_statistics
-- team_statistics | team_id         | teams           | team_id         | team_statistics
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, relationship_chain) VALUES ('matches', 'away_team_id', 'teams', 'team_id', 'matches.away_team_id -> teams.team_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, relationship_chain) VALUES ('matches', 'competition_id', 'competitions', 'competition_id', 'matches.competition_id -> competitions.competition_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, relationship_chain) VALUES ('matches', 'home_team_id', 'teams', 'team_id', 'matches.home_team_id -> teams.team_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, relationship_chain) VALUES ('player_statistics', 'competition_id', 'competitions', 'competition_id', 'player_statistics.competition_id -> competitions.competition_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, relationship_chain) VALUES ('player_statistics', 'match_id', 'matches', 'match_id', 'player_statistics.match_id -> matches.match_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, relationship_chain) VALUES ('player_statistics', 'player_id', 'players', 'player_id', 'player_statistics.player_id -> players.player_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, relationship_chain) VALUES ('player_statistics', 'team_id', 'teams', 'team_id', 'player_statistics.team_id -> teams.team_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, relationship_chain) VALUES ('shapley_analysis', 'player_id', 'players', 'player_id', 'shapley_analysis.player_id -> players.player_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, relationship_chain) VALUES ('shapley_analysis', 'team_id', 'teams', 'team_id', 'shapley_analysis.team_id -> teams.team_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, relationship_chain) VALUES ('team_statistics', 'competition_id', 'competitions', 'competition_id', 'team_statistics.competition_id -> competitions.competition_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, relationship_chain) VALUES ('team_statistics', 'team_id', 'teams', 'team_id', 'team_statistics.team_id -> teams.team_id');
