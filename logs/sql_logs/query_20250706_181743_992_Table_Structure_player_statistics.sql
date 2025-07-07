-- SQL Query Log
-- Timestamp: 2025-07-06 18:17:44
-- Description: Table Structure: player_statistics
-- Results: 25 rows
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
                AND table_name = 'player_statistics'
                ORDER BY ordinal_position;
            
*/

-- RESULTS SUMMARY:
-- Total rows: 25
-- Columns: column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- column_name     | data_type       | is_nullable     | column_default  | character_maximum_length | numeric_precision | numeric_scale   | ordinal_position
-- --------------------------------------------------------------------------------
-- stat_id         | integer         | NO              | nextval('player | None            | 32              | 0               | 1              
-- player_id       | integer         | YES             | None            | None            | 32              | 0               | 2              
-- team_id         | integer         | YES             | None            | None            | 32              | 0               | 3              
-- competition_id  | integer         | YES             | None            | None            | 32              | 0               | 4              
-- season_year     | integer         | YES             | None            | None            | 32              | 0               | 5              
-- match_id        | integer         | YES             | None            | None            | 32              | 0               | 6              
-- position        | character varyi | YES             | None            | 50              | None            | None            | 7              
-- minutes_played  | integer         | YES             | None            | None            | 32              | 0               | 8              
-- goals           | integer         | YES             | 0               | None            | 32              | 0               | 9              
-- assists         | integer         | YES             | 0               | None            | 32              | 0               | 10             
-- shots_total     | integer         | YES             | 0               | None            | 32              | 0               | 11             
-- shots_on_target | integer         | YES             | 0               | None            | 32              | 0               | 12             
-- passes_total    | integer         | YES             | 0               | None            | 32              | 0               | 13             
-- passes_complete | integer         | YES             | 0               | None            | 32              | 0               | 14             
-- passes_accuracy | numeric         | YES             | None            | None            | 5               | 2               | 15             
-- tackles_total   | integer         | YES             | 0               | None            | 32              | 0               | 16             
-- tackles_won     | integer         | YES             | 0               | None            | 32              | 0               | 17             
-- interceptions   | integer         | YES             | 0               | None            | 32              | 0               | 18             
-- fouls_drawn     | integer         | YES             | 0               | None            | 32              | 0               | 19             
-- fouls_committed | integer         | YES             | 0               | None            | 32              | 0               | 20             
-- yellow_cards    | integer         | YES             | 0               | None            | 32              | 0               | 21             
-- red_cards       | integer         | YES             | 0               | None            | 32              | 0               | 22             
-- rating          | numeric         | YES             | None            | None            | 3               | 1               | 23             
-- created_at      | timestamp witho | YES             | CURRENT_TIMESTA | None            | None            | None            | 24             
-- updated_at      | timestamp witho | YES             | CURRENT_TIMESTA | None            | None            | None            | 25             
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('stat_id', 'integer', 'NO', 'nextval(''player_statistics_stat_id_seq''::regclass)', NULL, 32, 0, 1);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('player_id', 'integer', 'YES', NULL, NULL, 32, 0, 2);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('team_id', 'integer', 'YES', NULL, NULL, 32, 0, 3);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('competition_id', 'integer', 'YES', NULL, NULL, 32, 0, 4);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('season_year', 'integer', 'YES', NULL, NULL, 32, 0, 5);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('match_id', 'integer', 'YES', NULL, NULL, 32, 0, 6);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('position', 'character varying', 'YES', NULL, 50, NULL, NULL, 7);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('minutes_played', 'integer', 'YES', NULL, NULL, 32, 0, 8);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('goals', 'integer', 'YES', '0', NULL, 32, 0, 9);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('assists', 'integer', 'YES', '0', NULL, 32, 0, 10);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('shots_total', 'integer', 'YES', '0', NULL, 32, 0, 11);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('shots_on_target', 'integer', 'YES', '0', NULL, 32, 0, 12);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('passes_total', 'integer', 'YES', '0', NULL, 32, 0, 13);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('passes_completed', 'integer', 'YES', '0', NULL, 32, 0, 14);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('passes_accuracy', 'numeric', 'YES', NULL, NULL, 5, 2, 15);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('tackles_total', 'integer', 'YES', '0', NULL, 32, 0, 16);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('tackles_won', 'integer', 'YES', '0', NULL, 32, 0, 17);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('interceptions', 'integer', 'YES', '0', NULL, 32, 0, 18);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('fouls_drawn', 'integer', 'YES', '0', NULL, 32, 0, 19);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('fouls_committed', 'integer', 'YES', '0', NULL, 32, 0, 20);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('yellow_cards', 'integer', 'YES', '0', NULL, 32, 0, 21);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('red_cards', 'integer', 'YES', '0', NULL, 32, 0, 22);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('rating', 'numeric', 'YES', NULL, NULL, 3, 1, 23);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('created_at', 'timestamp without time zone', 'YES', 'CURRENT_TIMESTAMP', NULL, NULL, NULL, 24);
-- INSERT INTO INFORMATION_SCHEMA.COLUMNS (column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale, ordinal_position) VALUES ('updated_at', 'timestamp without time zone', 'YES', 'CURRENT_TIMESTAMP', NULL, NULL, NULL, 25);
