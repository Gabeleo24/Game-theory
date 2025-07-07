-- SQL Query Log
-- Timestamp: 2025-07-06 18:17:44
-- Description: Table Structure: players
-- Results: 14 rows
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
                AND table_name = 'players'
                ORDER BY ordinal_position;
            
*/

-- RESULTS SUMMARY:
-- Total rows: 14
-- Columns: column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- column_name     | data_type       | is_nullable     | column_default  | character_maximum_length | numeric_precision | numeric_scale   | ordinal_position
-- --------------------------------------------------------------------------------
-- player_id       | integer         | NO              | None            | None            | 32              | 0               | 1              
-- player_name     | character varyi | NO              | None            | 255             | None            | None            | 2              
-- first_name      | character varyi | YES             | None            | 255             | None            | None            | 3              
-- last_name       | character varyi | YES             | None            | 255             | None            | None            | 4              
-- age             | integer         | YES             | None            | None            | 32              | 0               | 5              
-- birth_date      | date            | YES             | None            | None            | None            | None            | 6              
-- birth_place     | character varyi | YES             | None            | 255             | None            | None            | 7              
-- birth_country   | character varyi | YES             | None            | 100             | None            | None            | 8              
-- nationality     | character varyi | YES             | None            | 100             | None            | None            | 9              
-- height          | character varyi | YES             | None            | 10              | None            | None            | 10             
-- weight          | character varyi | YES             | None            | 10              | None            | None            | 11             
-- photo_url       | text            | YES             | None            | None            | None            | None            | 12             
-- created_at      | timestamp witho | YES             | CURRENT_TIMESTA | None            | None            | None            | 13             
-- updated_at      | timestamp witho | YES             | CURRENT_TIMESTA | None            | None            | None            | 14             
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('player_id', 'integer', 'NO', NULL, NULL, 32, 0, 1);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('player_name', 'character varying', 'NO', NULL, 255, NULL, NULL, 2);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('first_name', 'character varying', 'YES', NULL, 255, NULL, NULL, 3);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('last_name', 'character varying', 'YES', NULL, 255, NULL, NULL, 4);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('age', 'integer', 'YES', NULL, NULL, 32, 0, 5);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('birth_date', 'date', 'YES', NULL, NULL, NULL, NULL, 6);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('birth_place', 'character varying', 'YES', NULL, 255, NULL, NULL, 7);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('birth_country', 'character varying', 'YES', NULL, 100, NULL, NULL, 8);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('nationality', 'character varying', 'YES', NULL, 100, NULL, NULL, 9);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('height', 'character varying', 'YES', NULL, 10, NULL, NULL, 10);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('weight', 'character varying', 'YES', NULL, 10, NULL, NULL, 11);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('photo_url', 'text', 'YES', NULL, NULL, NULL, NULL, 12);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('created_at', 'timestamp without time zone', 'YES', 'CURRENT_TIMESTAMP', NULL, NULL, NULL, 13);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('updated_at', 'timestamp without time zone', 'YES', 'CURRENT_TIMESTAMP', NULL, NULL, NULL, 14);
