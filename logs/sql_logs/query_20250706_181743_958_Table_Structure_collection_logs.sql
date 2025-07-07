-- SQL Query Log
-- Timestamp: 2025-07-06 18:17:43
-- Description: Table Structure: collection_logs
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
                AND table_name = 'collection_logs'
                ORDER BY ordinal_position;
            
*/

-- RESULTS SUMMARY:
-- Total rows: 11
-- Columns: column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- column_name     | data_type       | is_nullable     | column_default  | character_maximum_length | numeric_precision | numeric_scale   | ordinal_position
-- --------------------------------------------------------------------------------
-- log_id          | integer         | NO              | nextval('collec | None            | 32              | 0               | 1              
-- collection_type | character varyi | YES             | None            | 50              | None            | None            | 2              
-- team_id         | integer         | YES             | None            | None            | 32              | 0               | 3              
-- season_year     | integer         | YES             | None            | None            | 32              | 0               | 4              
-- status          | character varyi | YES             | None            | 20              | None            | None            | 5              
-- records_collect | integer         | YES             | None            | None            | 32              | 0               | 6              
-- api_requests    | integer         | YES             | None            | None            | 32              | 0               | 7              
-- start_time      | timestamp witho | YES             | None            | None            | None            | None            | 8              
-- end_time        | timestamp witho | YES             | None            | None            | None            | None            | 9              
-- error_message   | text            | YES             | None            | None            | None            | None            | 10             
-- created_at      | timestamp witho | YES             | CURRENT_TIMESTA | None            | None            | None            | 11             
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('log_id', 'integer', 'NO', 'nextval(''collection_logs_log_id_seq''::regclass)', NULL, 32, 0, 1);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('collection_type', 'character varying', 'YES', NULL, 50, NULL, NULL, 2);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('team_id', 'integer', 'YES', NULL, NULL, 32, 0, 3);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('season_year', 'integer', 'YES', NULL, NULL, 32, 0, 4);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('status', 'character varying', 'YES', NULL, 20, NULL, NULL, 5);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('records_collected', 'integer', 'YES', NULL, NULL, 32, 0, 6);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('api_requests', 'integer', 'YES', NULL, NULL, 32, 0, 7);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('start_time', 'timestamp without time zone', 'YES', NULL, NULL, NULL, NULL, 8);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('end_time', 'timestamp without time zone', 'YES', NULL, NULL, NULL, NULL, 9);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('error_message', 'text', 'YES', NULL, NULL, NULL, NULL, 10);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('created_at', 'timestamp without time zone', 'YES', 'CURRENT_TIMESTAMP', NULL, NULL, NULL, 11);
