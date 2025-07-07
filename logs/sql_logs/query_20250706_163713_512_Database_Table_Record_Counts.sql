-- SQL Query Log
-- Timestamp: 2025-07-06 16:37:13
-- Description: Database Table Record Counts
-- Results: 4 rows
-- ============================================================

-- ORIGINAL QUERY:
/*

            SELECT 
                'teams' as table_name, COUNT(*) as record_count FROM teams
            UNION ALL
            SELECT 
                'players' as table_name, COUNT(*) as record_count FROM players
            UNION ALL
            SELECT 
                'matches' as table_name, COUNT(*) as record_count FROM matches
            UNION ALL
            SELECT 
                'player_statistics' as table_name, COUNT(*) as record_count FROM player_statistics
            ORDER BY record_count DESC;
        
*/

-- RESULTS SUMMARY:
-- Total rows: 4
-- Columns: table_name, record_count

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- table_name      | record_count   
-- --------------------------------------------------------------------------------
-- player_statisti | 8080           
-- players         | 3980           
-- matches         | 98             
-- teams           | 67             
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO TEAMS (table_name, record_count) VALUES ('player_statistics', 8080);
-- INSERT INTO TEAMS (table_name, record_count) VALUES ('players', 3980);
-- INSERT INTO TEAMS (table_name, record_count) VALUES ('matches', 98);
-- INSERT INTO TEAMS (table_name, record_count) VALUES ('teams', 67);
