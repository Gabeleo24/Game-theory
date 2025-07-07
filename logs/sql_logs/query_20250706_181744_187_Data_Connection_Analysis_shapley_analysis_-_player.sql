-- SQL Query Log
-- Timestamp: 2025-07-06 18:17:44
-- Description: Data Connection Analysis: shapley_analysis -> players
-- Results: 1 rows
-- ============================================================

-- ORIGINAL QUERY:
/*

                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT f.player_id) as unique_foreign_keys,
                    COUNT(DISTINCT t.player_id) as unique_primary_keys,
                    COUNT(CASE WHEN t.player_id IS NOT NULL THEN 1 END) as connected_records
                FROM shapley_analysis f
                LEFT JOIN players t ON f.player_id = t.player_id;
            
*/

-- RESULTS SUMMARY:
-- Total rows: 1
-- Columns: total_records, unique_foreign_keys, unique_primary_keys, connected_records

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- total_records   | unique_foreign_keys | unique_primary_keys | connected_records
-- --------------------------------------------------------------------------------
-- 0               | 0               | 0               | 0              
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO SHAPLEY_ANALYSIS (total_records, unique_foreign_keys, unique_primary_keys, connected_records) VALUES (0, 0, 0, 0);
