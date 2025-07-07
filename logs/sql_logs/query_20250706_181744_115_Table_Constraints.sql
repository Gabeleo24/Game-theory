-- SQL Query Log
-- Timestamp: 2025-07-06 18:17:44
-- Description: Table Constraints
-- Results: 33 rows
-- ============================================================

-- ORIGINAL QUERY:
/*

            SELECT 
                tc.table_name,
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name
            FROM information_schema.table_constraints tc
            LEFT JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_schema = 'public'
            ORDER BY tc.table_name, tc.constraint_type;
        
*/

-- RESULTS SUMMARY:
-- Total rows: 33
-- Columns: table_name, constraint_name, constraint_type, column_name

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- table_name      | constraint_name | constraint_type | column_name    
-- --------------------------------------------------------------------------------
-- collection_logs | 2200_16626_1_no | CHECK           | None           
-- collection_logs | collection_logs | PRIMARY KEY     | log_id         
-- competitions    | 2200_16495_1_no | CHECK           | None           
-- competitions    | 2200_16495_2_no | CHECK           | None           
-- competitions    | competitions_pk | PRIMARY KEY     | competition_id 
-- matches         | 2200_16512_1_no | CHECK           | None           
-- matches         | matches_away_te | FOREIGN KEY     | away_team_id   
-- matches         | matches_competi | FOREIGN KEY     | competition_id 
-- matches         | matches_home_te | FOREIGN KEY     | home_team_id   
-- matches         | matches_pkey    | PRIMARY KEY     | match_id       
-- player_statisti | 2200_16537_1_no | CHECK           | None           
-- player_statisti | player_statisti | FOREIGN KEY     | competition_id 
-- player_statisti | player_statisti | FOREIGN KEY     | player_id      
-- player_statisti | player_statisti | FOREIGN KEY     | match_id       
-- player_statisti | player_statisti | FOREIGN KEY     | team_id        
-- player_statisti | player_statisti | PRIMARY KEY     | stat_id        
-- players         | 2200_16486_2_no | CHECK           | None           
-- players         | 2200_16486_1_no | CHECK           | None           
-- players         | players_pkey    | PRIMARY KEY     | player_id      
-- seasons         | 2200_16504_1_no | CHECK           | None           
-- seasons         | 2200_16504_2_no | CHECK           | None           
-- seasons         | seasons_pkey    | PRIMARY KEY     | season_id      
-- shapley_analysi | 2200_16607_1_no | CHECK           | None           
-- shapley_analysi | shapley_analysi | FOREIGN KEY     | team_id        
-- shapley_analysi | shapley_analysi | FOREIGN KEY     | player_id      
-- shapley_analysi | shapley_analysi | PRIMARY KEY     | analysis_id    
-- team_statistics | 2200_16579_1_no | CHECK           | None           
-- team_statistics | team_statistics | FOREIGN KEY     | team_id        
-- team_statistics | team_statistics | FOREIGN KEY     | competition_id 
-- team_statistics | team_statistics | PRIMARY KEY     | stat_id        
-- teams           | 2200_16477_2_no | CHECK           | None           
-- teams           | 2200_16477_1_no | CHECK           | None           
-- teams           | teams_pkey      | PRIMARY KEY     | team_id        
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('collection_logs', '2200_16626_1_not_null', 'CHECK', NULL);
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('collection_logs', 'collection_logs_pkey', 'PRIMARY KEY', 'log_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('competitions', '2200_16495_1_not_null', 'CHECK', NULL);
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('competitions', '2200_16495_2_not_null', 'CHECK', NULL);
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('competitions', 'competitions_pkey', 'PRIMARY KEY', 'competition_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('matches', '2200_16512_1_not_null', 'CHECK', NULL);
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('matches', 'matches_away_team_id_fkey', 'FOREIGN KEY', 'away_team_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('matches', 'matches_competition_id_fkey', 'FOREIGN KEY', 'competition_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('matches', 'matches_home_team_id_fkey', 'FOREIGN KEY', 'home_team_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('matches', 'matches_pkey', 'PRIMARY KEY', 'match_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('player_statistics', '2200_16537_1_not_null', 'CHECK', NULL);
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('player_statistics', 'player_statistics_competition_id_fkey', 'FOREIGN KEY', 'competition_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('player_statistics', 'player_statistics_player_id_fkey', 'FOREIGN KEY', 'player_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('player_statistics', 'player_statistics_match_id_fkey', 'FOREIGN KEY', 'match_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('player_statistics', 'player_statistics_team_id_fkey', 'FOREIGN KEY', 'team_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('player_statistics', 'player_statistics_pkey', 'PRIMARY KEY', 'stat_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('players', '2200_16486_2_not_null', 'CHECK', NULL);
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('players', '2200_16486_1_not_null', 'CHECK', NULL);
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('players', 'players_pkey', 'PRIMARY KEY', 'player_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('seasons', '2200_16504_1_not_null', 'CHECK', NULL);
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('seasons', '2200_16504_2_not_null', 'CHECK', NULL);
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('seasons', 'seasons_pkey', 'PRIMARY KEY', 'season_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('shapley_analysis', '2200_16607_1_not_null', 'CHECK', NULL);
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('shapley_analysis', 'shapley_analysis_team_id_fkey', 'FOREIGN KEY', 'team_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('shapley_analysis', 'shapley_analysis_player_id_fkey', 'FOREIGN KEY', 'player_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('shapley_analysis', 'shapley_analysis_pkey', 'PRIMARY KEY', 'analysis_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('team_statistics', '2200_16579_1_not_null', 'CHECK', NULL);
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('team_statistics', 'team_statistics_team_id_fkey', 'FOREIGN KEY', 'team_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('team_statistics', 'team_statistics_competition_id_fkey', 'FOREIGN KEY', 'competition_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('team_statistics', 'team_statistics_pkey', 'PRIMARY KEY', 'stat_id');
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('teams', '2200_16477_2_not_null', 'CHECK', NULL);
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('teams', '2200_16477_1_not_null', 'CHECK', NULL);
-- INSERT INTO INFORMATION_SCHEMA.TABLE_CONSTRAINTS (table_name, constraint_name, constraint_type, column_name) VALUES ('teams', 'teams_pkey', 'PRIMARY KEY', 'team_id');
