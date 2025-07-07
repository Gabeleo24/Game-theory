-- SQL Query Log
-- Timestamp: 2025-07-06 18:17:43
-- Description: Table Structure: competitions
-- Results: 6 rows
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
                AND table_name = 'competitions'
                ORDER BY ordinal_position;
            
*/

-- RESULTS SUMMARY:
-- Total rows: 6
-- Columns: column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- column_name     | data_type       | is_nullable     | column_default  | character_maximum_length | numeric_precision | numeric_scale   | ordinal_position
-- --------------------------------------------------------------------------------
-- competition_id  | integer         | NO              | None            | None            | 32              | 0               | 1              
-- competition_nam | character varyi | NO              | None            | 255             | None            | None            | 2              
-- competition_typ | character varyi | YES             | None            | 50              | None            | None            | 3              
-- country         | character varyi | YES             | None            | 100             | None            | None            | 4              
-- logo_url        | text            | YES             | None            | None            | None            | None            | 5              
-- created_at      | timestamp witho | YES             | CURRENT_TIMESTA | None            | None            | None            | 6              
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('competition_id', 'integer', 'NO', NULL, NULL, 32, 0, 1);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('competition_name', 'character varying', 'NO', NULL, 255, NULL, NULL, 2);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('competition_type', 'character varying', 'YES', NULL, 50, NULL, NULL, 3);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('country', 'character varying', 'YES', NULL, 100, NULL, NULL, 4);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('logo_url', 'text', 'YES', NULL, NULL, NULL, NULL, 5);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('created_at', 'timestamp without time zone', 'YES', 'CURRENT_TIMESTAMP', NULL, NULL, NULL, 6);
