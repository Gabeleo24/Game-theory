-- SQL Query Log
-- Timestamp: 2025-07-06 18:17:44
-- Description: Table Structure: team_statistics
-- Results: 16 rows
-- ============================================================

-- ORIGINAL QUERY:
/*

                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale,
                    ordinal_position
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'team_statistics'
                ORDER BY ordinal_position;
            
*/

-- RESULTS SUMMARY:
-- Total rows: 16
-- Columns: column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- column_name     | data_type       | is_nullable     | column_default  | character_maximum_length | numeric_precision | numeric_scale   | ordinal_position
-- --------------------------------------------------------------------------------
-- stat_id         | integer         | NO              | nextval('team_s | None            | 32              | 0               | 1              
-- team_id         | integer         | YES             | None            | None            | 32              | 0               | 2              
-- competition_id  | integer         | YES             | None            | None            | 32              | 0               | 3              
-- season_year     | integer         | YES             | None            | None            | 32              | 0               | 4              
-- matches_played  | integer         | YES             | 0               | None            | 32              | 0               | 5              
-- wins            | integer         | YES             | 0               | None            | 32              | 0               | 6              
-- draws           | integer         | YES             | 0               | None            | 32              | 0               | 7              
-- losses          | integer         | YES             | 0               | None            | 32              | 0               | 8              
-- goals_for       | integer         | YES             | 0               | None            | 32              | 0               | 9              
-- goals_against   | integer         | YES             | 0               | None            | 32              | 0               | 10             
-- goal_difference | integer         | YES             | 0               | None            | 32              | 0               | 11             
-- points          | integer         | YES             | 0               | None            | 32              | 0               | 12             
-- position        | integer         | YES             | None            | None            | 32              | 0               | 13             
-- clean_sheets    | integer         | YES             | 0               | None            | 32              | 0               | 14             
-- created_at      | timestamp witho | YES             | CURRENT_TIMESTA | None            | None            | None            | 15             
-- updated_at      | timestamp witho | YES             | CURRENT_TIMESTA | None            | None            | None            | 16             
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('stat_id', 'integer', 'NO', 'nextval(''team_statistics_stat_id_seq''::regclass)', NULL, 32, 0, 1);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('team_id', 'integer', 'YES', NULL, NULL, 32, 0, 2);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('competition_id', 'integer', 'YES', NULL, NULL, 32, 0, 3);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('season_year', 'integer', 'YES', NULL, NULL, 32, 0, 4);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('matches_played', 'integer', 'YES', '0', NULL, 32, 0, 5);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('wins', 'integer', 'YES', '0', NULL, 32, 0, 6);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('draws', 'integer', 'YES', '0', NULL, 32, 0, 7);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('losses', 'integer', 'YES', '0', NULL, 32, 0, 8);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('goals_for', 'integer', 'YES', '0', NULL, 32, 0, 9);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('goals_against', 'integer', 'YES', '0', NULL, 32, 0, 10);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('goal_difference', 'integer', 'YES', '0', NULL, 32, 0, 11);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('points', 'integer', 'YES', '0', NULL, 32, 0, 12);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('position', 'integer', 'YES', NULL, NULL, 32, 0, 13);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('clean_sheets', 'integer', 'YES', '0', NULL, 32, 0, 14);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('created_at', 'timestamp without time zone', 'YES', 'CURRENT_TIMESTAMP', NULL, NULL, NULL, 15);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('updated_at', 'timestamp without time zone', 'YES', 'CURRENT_TIMESTAMP', NULL, NULL, NULL, 16);
