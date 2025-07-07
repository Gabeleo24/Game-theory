-- SQL Query Log
-- Timestamp: 2025-07-06 18:17:43
-- Description: Table Structure: matches
-- Results: 17 rows
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
                AND table_name = 'matches'
                ORDER BY ordinal_position;
            
*/

-- RESULTS SUMMARY:
-- Total rows: 17
-- Columns: column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- column_name     | data_type       | is_nullable     | column_default  | character_maximum_length | numeric_precision | numeric_scale   | ordinal_position
-- --------------------------------------------------------------------------------
-- match_id        | integer         | NO              | None            | None            | 32              | 0               | 1              
-- competition_id  | integer         | YES             | None            | None            | 32              | 0               | 2              
-- season_year     | integer         | YES             | None            | None            | 32              | 0               | 3              
-- match_date      | timestamp witho | YES             | None            | None            | None            | None            | 4              
-- round           | character varyi | YES             | None            | 100             | None            | None            | 5              
-- home_team_id    | integer         | YES             | None            | None            | 32              | 0               | 6              
-- away_team_id    | integer         | YES             | None            | None            | 32              | 0               | 7              
-- home_goals      | integer         | YES             | None            | None            | 32              | 0               | 8              
-- away_goals      | integer         | YES             | None            | None            | 32              | 0               | 9              
-- home_goals_half | integer         | YES             | None            | None            | 32              | 0               | 10             
-- away_goals_half | integer         | YES             | None            | None            | 32              | 0               | 11             
-- match_status    | character varyi | YES             | None            | 50              | None            | None            | 12             
-- venue_name      | character varyi | YES             | None            | 255             | None            | None            | 13             
-- venue_city      | character varyi | YES             | None            | 255             | None            | None            | 14             
-- referee         | character varyi | YES             | None            | 255             | None            | None            | 15             
-- created_at      | timestamp witho | YES             | CURRENT_TIMESTA | None            | None            | None            | 16             
-- updated_at      | timestamp witho | YES             | CURRENT_TIMESTA | None            | None            | None            | 17             
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('match_id', 'integer', 'NO', NULL, NULL, 32, 0, 1);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('competition_id', 'integer', 'YES', NULL, NULL, 32, 0, 2);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('season_year', 'integer', 'YES', NULL, NULL, 32, 0, 3);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('match_date', 'timestamp without time zone', 'YES', NULL, NULL, NULL, NULL, 4);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('round', 'character varying', 'YES', NULL, 100, NULL, NULL, 5);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('home_team_id', 'integer', 'YES', NULL, NULL, 32, 0, 6);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('away_team_id', 'integer', 'YES', NULL, NULL, 32, 0, 7);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('home_goals', 'integer', 'YES', NULL, NULL, 32, 0, 8);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('away_goals', 'integer', 'YES', NULL, NULL, 32, 0, 9);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('home_goals_halftime', 'integer', 'YES', NULL, NULL, 32, 0, 10);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('away_goals_halftime', 'integer', 'YES', NULL, NULL, 32, 0, 11);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('match_status', 'character varying', 'YES', NULL, 50, NULL, NULL, 12);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('venue_name', 'character varying', 'YES', NULL, 255, NULL, NULL, 13);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('venue_city', 'character varying', 'YES', NULL, 255, NULL, NULL, 14);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('referee', 'character varying', 'YES', NULL, 255, NULL, NULL, 15);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('created_at', 'timestamp without time zone', 'YES', 'CURRENT_TIMESTAMP', NULL, NULL, NULL, 16);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('updated_at', 'timestamp without time zone', 'YES', 'CURRENT_TIMESTAMP', NULL, NULL, NULL, 17);
