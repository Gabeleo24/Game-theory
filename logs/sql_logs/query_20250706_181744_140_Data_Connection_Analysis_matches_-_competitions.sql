-- SQL Query Log
-- Timestamp: 2025-07-06 18:17:44
-- Description: Data Connection Analysis: matches -> competitions
-- Results: 1 rows
-- ============================================================

-- ORIGINAL QUERY:
/*

                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT f.competition_id) as unique_foreign_keys,
                    COUNT(DISTINCT t.competition_id) as unique_primary_keys,
                    COUNT(CASE WHEN t.competition_id IS NOT NULL THEN 1 END) as connected_records
                FROM matches f
                LEFT JOIN competitions t ON f.competition_id = t.competition_id;
            
*/

-- RESULTS SUMMARY:
-- Total rows: 1
-- Columns: total_records, unique_foreign_keys, unique_primary_keys, connected_records

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- total_records   | unique_foreign_keys | unique_primary_keys | connected_records
-- --------------------------------------------------------------------------------
-- 98              | 2               | 2               | 98             
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO MATCHES (total_records, unique_foreign_keys, unique_primary_keys, connected_records) VALUES (98, 2, 2, 98);
