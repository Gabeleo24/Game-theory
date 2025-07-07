-- SQL Query Log
-- Timestamp: 2025-07-06 18:17:44
-- Description: Table Structure: teams
-- Results: 10 rows
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
                AND table_name = 'teams'
                ORDER BY ordinal_position;
            
*/

-- RESULTS SUMMARY:
-- Total rows: 10
-- Columns: column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- column_name     | data_type       | is_nullable     | column_default  | character_maximum_length | numeric_precision | numeric_scale   | ordinal_position
-- --------------------------------------------------------------------------------
-- team_id         | integer         | NO              | None            | None            | 32              | 0               | 1              
-- team_name       | character varyi | NO              | None            | 255             | None            | None            | 2              
-- team_code       | character varyi | YES             | None            | 10              | None            | None            | 3              
-- country         | character varyi | YES             | None            | 100             | None            | None            | 4              
-- founded         | integer         | YES             | None            | None            | 32              | 0               | 5              
-- venue_name      | character varyi | YES             | None            | 255             | None            | None            | 6              
-- venue_capacity  | integer         | YES             | None            | None            | 32              | 0               | 7              
-- logo_url        | text            | YES             | None            | None            | None            | None            | 8              
-- created_at      | timestamp witho | YES             | CURRENT_TIMESTA | None            | None            | None            | 9              
-- updated_at      | timestamp witho | YES             | CURRENT_TIMESTA | None            | None            | None            | 10             
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('team_id', 'integer', 'NO', NULL, NULL, 32, 0, 1);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('team_name', 'character varying', 'NO', NULL, 255, NULL, NULL, 2);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('team_code', 'character varying', 'YES', NULL, 10, NULL, NULL, 3);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('country', 'character varying', 'YES', NULL, 100, NULL, NULL, 4);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('founded', 'integer', 'YES', NULL, NULL, 32, 0, 5);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('venue_name', 'character varying', 'YES', NULL, 255, NULL, NULL, 6);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('venue_capacity', 'integer', 'YES', NULL, NULL, 32, 0, 7);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('logo_url', 'text', 'YES', NULL, NULL, NULL, NULL, 8);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('created_at', 'timestamp without time zone', 'YES', 'CURRENT_TIMESTAMP', NULL, NULL, NULL, 9);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('updated_at', 'timestamp without time zone', 'YES', 'CURRENT_TIMESTAMP', NULL, NULL, NULL, 10);
