-- SQL Query Log
-- Timestamp: 2025-07-06 18:17:43
-- Description: Database Tables Overview
-- Results: 9 rows
-- ============================================================

-- ORIGINAL QUERY:
/*

            SELECT 
                table_name,
                table_type,
                table_schema
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        
*/

-- RESULTS SUMMARY:
-- Total rows: 9
-- Columns: table_name, table_type, table_schema

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- table_name      | table_type      | table_schema   
-- --------------------------------------------------------------------------------
-- collection_logs | BASE TABLE      | public         
-- competitions    | BASE TABLE      | public         
-- matches         | BASE TABLE      | public         
-- player_statisti | BASE TABLE      | public         
-- players         | BASE TABLE      | public         
-- seasons         | BASE TABLE      | public         
-- shapley_analysi | BASE TABLE      | public         
-- team_statistics | BASE TABLE      | public         
-- teams           | BASE TABLE      | public         
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO INFORMATION_SCHEMA.TABLES (table_name, table_type, table_schema) VALUES ('collection_logs', 'BASE TABLE', 'public');
-- INSERT INTO INFORMATION_SCHEMA.TABLES (table_name, table_type, table_schema) VALUES ('competitions', 'BASE TABLE', 'public');
-- INSERT INTO INFORMATION_SCHEMA.TABLES (table_name, table_type, table_schema) VALUES ('matches', 'BASE TABLE', 'public');
-- INSERT INTO INFORMATION_SCHEMA.TABLES (table_name, table_type, table_schema) VALUES ('player_statistics', 'BASE TABLE', 'public');
-- INSERT INTO INFORMATION_SCHEMA.TABLES (table_name, table_type, table_schema) VALUES ('players', 'BASE TABLE', 'public');
-- INSERT INTO INFORMATION_SCHEMA.TABLES (table_name, table_type, table_schema) VALUES ('seasons', 'BASE TABLE', 'public');
-- INSERT INTO INFORMATION_SCHEMA.TABLES (table_name, table_type, table_schema) VALUES ('shapley_analysis', 'BASE TABLE', 'public');
-- INSERT INTO INFORMATION_SCHEMA.TABLES (table_name, table_type, table_schema) VALUES ('team_statistics', 'BASE TABLE', 'public');
-- INSERT INTO INFORMATION_SCHEMA.TABLES (table_name, table_type, table_schema) VALUES ('teams', 'BASE TABLE', 'public');
