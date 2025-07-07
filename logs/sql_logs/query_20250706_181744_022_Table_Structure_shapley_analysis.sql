-- SQL Query Log
-- Timestamp: 2025-07-06 18:17:44
-- Description: Table Structure: shapley_analysis
-- Results: 11 rows
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
                AND table_name = 'shapley_analysis'
                ORDER BY ordinal_position;
            
*/

-- RESULTS SUMMARY:
-- Total rows: 11
-- Columns: column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- column_name     | data_type       | is_nullable     | column_default  | character_maximum_length | numeric_precision | numeric_scale   | ordinal_position
-- --------------------------------------------------------------------------------
-- analysis_id     | integer         | NO              | nextval('shaple | None            | 32              | 0               | 1              
-- player_id       | integer         | YES             | None            | None            | 32              | 0               | 2              
-- team_id         | integer         | YES             | None            | None            | 32              | 0               | 3              
-- season_year     | integer         | YES             | None            | None            | 32              | 0               | 4              
-- shapley_value   | numeric         | YES             | None            | None            | 10              | 6               | 5              
-- contribution_ra | integer         | YES             | None            | None            | 32              | 0               | 6              
-- analysis_date   | timestamp witho | YES             | CURRENT_TIMESTA | None            | None            | None            | 7              
-- analysis_type   | character varyi | YES             | None            | 50              | None            | None            | 8              
-- confidence_leve | numeric         | YES             | None            | None            | 5               | 2               | 9              
-- iterations      | integer         | YES             | None            | None            | 32              | 0               | 10             
-- created_at      | timestamp witho | YES             | CURRENT_TIMESTA | None            | None            | None            | 11             
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('analysis_id', 'integer', 'NO', 'nextval(''shapley_analysis_analysis_id_seq''::regclass)', NULL, 32, 0, 1);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('player_id', 'integer', 'YES', NULL, NULL, 32, 0, 2);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('team_id', 'integer', 'YES', NULL, NULL, 32, 0, 3);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('season_year', 'integer', 'YES', NULL, NULL, 32, 0, 4);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('shapley_value', 'numeric', 'YES', NULL, NULL, 10, 6, 5);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('contribution_rank', 'integer', 'YES', NULL, NULL, 32, 0, 6);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('analysis_date', 'timestamp without time zone', 'YES', 'CURRENT_TIMESTAMP', NULL, NULL, NULL, 7);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('analysis_type', 'character varying', 'YES', NULL, 50, NULL, NULL, 8);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('confidence_level', 'numeric', 'YES', NULL, NULL, 5, 2, 9);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('iterations', 'integer', 'YES', NULL, NULL, 32, 0, 10);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('created_at', 'timestamp without time zone', 'YES', 'CURRENT_TIMESTAMP', NULL, NULL, NULL, 11);
