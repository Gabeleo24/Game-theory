-- SQL Query Log
-- Timestamp: 2025-07-06 18:17:44
-- Description: Data Connection Analysis: player_statistics -> matches
-- Results: 1 rows
-- ============================================================

-- ORIGINAL QUERY:
/*

                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT f.match_id) as unique_foreign_keys,
                    COUNT(DISTINCT t.match_id) as unique_primary_keys,
                    COUNT(CASE WHEN t.match_id IS NOT NULL THEN 1 END) as connected_records
                FROM player_statistics f
                LEFT JOIN matches t ON f.match_id = t.match_id;
            
*/

-- RESULTS SUMMARY:
-- Total rows: 1
-- Columns: total_records, unique_foreign_keys, unique_primary_keys, connected_records

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- total_records   | unique_foreign_keys | unique_primary_keys | connected_records
-- --------------------------------------------------------------------------------
-- 8080            | 0               | 0               | 0              
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO PLAYER_STATISTICS (total_records, unique_foreign_keys, unique_primary_keys, connected_records) VALUES (8080, 0, 0, 0);
