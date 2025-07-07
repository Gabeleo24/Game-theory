-- SQL Query Log
-- Timestamp: 2025-07-06 16:32:00
-- Description: Player Cards Overview Statistics
-- Results: 1 rows
-- ============================================================

-- ORIGINAL QUERY:
/*

            SELECT 
                COUNT(*) as total_player_statistics,
                SUM(yellow_cards) as total_yellow_cards,
                SUM(red_cards) as total_red_cards,
                COUNT(CASE WHEN yellow_cards > 0 THEN 1 END) as players_with_yellow_cards,
                COUNT(CASE WHEN red_cards > 0 THEN 1 END) as players_with_red_cards,
                ROUND(AVG(yellow_cards::numeric), 2) as avg_yellow_per_player,
                ROUND(AVG(red_cards::numeric), 2) as avg_red_per_player
            FROM player_statistics;
        
*/

-- RESULTS SUMMARY:
-- Total rows: 1
-- Columns: total_player_statistics, total_yellow_cards, total_red_cards, players_with_yellow_cards, players_with_red_cards, avg_yellow_per_player, avg_red_per_player

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- total_player_statistics | total_yellow_cards | total_red_cards | players_with_yellow_cards | players_with_red_cards | avg_yellow_per_player | avg_red_per_player
-- --------------------------------------------------------------------------------
-- 8080            | 10640           | 252             | 2762            | 241             | 1.32            | 0.03           
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO PLAYER_STATISTICS; (total_player_statistics, total_yellow_cards, total_red_cards, players_with_yellow_cards, players_with_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES (8080, 10640, 252, 2762, 241, 1.32, 0.03);
