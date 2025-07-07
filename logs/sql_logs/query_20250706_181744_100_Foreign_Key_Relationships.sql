-- SQL Query Log
-- Timestamp: 2025-07-06 18:17:44
-- Description: Foreign Key Relationships
-- Results: 11 rows
-- ============================================================

-- ORIGINAL QUERY:
/*

            SELECT 
                tc.table_name as source_table,
                kcu.column_name as source_column,
                ccu.table_name as target_table,
                ccu.column_name as target_column,
                tc.constraint_name,
                tc.constraint_type
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu 
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name;
        
*/

-- RESULTS SUMMARY:
-- Total rows: 11
-- Columns: source_table, source_column, target_table, target_column, constraint_name, constraint_type

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- source_table    | source_column   | target_table    | target_column   | constraint_name | constraint_type
-- --------------------------------------------------------------------------------
-- matches         | away_team_id    | teams           | team_id         | matches_away_te | FOREIGN KEY    
-- matches         | competition_id  | competitions    | competition_id  | matches_competi | FOREIGN KEY    
-- matches         | home_team_id    | teams           | team_id         | matches_home_te | FOREIGN KEY    
-- player_statisti | competition_id  | competitions    | competition_id  | player_statisti | FOREIGN KEY    
-- player_statisti | match_id        | matches         | match_id        | player_statisti | FOREIGN KEY    
-- player_statisti | player_id       | players         | player_id       | player_statisti | FOREIGN KEY    
-- player_statisti | team_id         | teams           | team_id         | player_statisti | FOREIGN KEY    
-- shapley_analysi | player_id       | players         | player_id       | shapley_analysi | FOREIGN KEY    
-- shapley_analysi | team_id         | teams           | team_id         | shapley_analysi | FOREIGN KEY    
-- team_statistics | competition_id  | competitions    | competition_id  | team_statistics | FOREIGN KEY    
-- team_statistics | team_id         | teams           | team_id         | team_statistics | FOREIGN KEY    
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, constraint_name, constraint_type) VALUES ('matches', 'away_team_id', 'teams', 'team_id', 'matches_away_team_id_fkey', 'FOREIGN KEY');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, constraint_name, constraint_type) VALUES ('matches', 'competition_id', 'competitions', 'competition_id', 'matches_competition_id_fkey', 'FOREIGN KEY');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, constraint_name, constraint_type) VALUES ('matches', 'home_team_id', 'teams', 'team_id', 'matches_home_team_id_fkey', 'FOREIGN KEY');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, constraint_name, constraint_type) VALUES ('player_statistics', 'competition_id', 'competitions', 'competition_id', 'player_statistics_competition_id_fkey', 'FOREIGN KEY');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, constraint_name, constraint_type) VALUES ('player_statistics', 'match_id', 'matches', 'match_id', 'player_statistics_match_id_fkey', 'FOREIGN KEY');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, constraint_name, constraint_type) VALUES ('player_statistics', 'player_id', 'players', 'player_id', 'player_statistics_player_id_fkey', 'FOREIGN KEY');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, constraint_name, constraint_type) VALUES ('player_statistics', 'team_id', 'teams', 'team_id', 'player_statistics_team_id_fkey', 'FOREIGN KEY');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, constraint_name, constraint_type) VALUES ('shapley_analysis', 'player_id', 'players', 'player_id', 'shapley_analysis_player_id_fkey', 'FOREIGN KEY');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, constraint_name, constraint_type) VALUES ('shapley_analysis', 'team_id', 'teams', 'team_id', 'shapley_analysis_team_id_fkey', 'FOREIGN KEY');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, constraint_name, constraint_type) VALUES ('team_statistics', 'competition_id', 'competitions', 'competition_id', 'team_statistics_competition_id_fkey', 'FOREIGN KEY');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (source_table, source_column, target_table, target_column, constraint_name, constraint_type) VALUES ('team_statistics', 'team_id', 'teams', 'team_id', 'team_statistics_team_id_fkey', 'FOREIGN KEY');
