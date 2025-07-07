-- SQL Query Log
-- Timestamp: 2025-07-06 16:32:00
-- Description: Cards Analysis by Position
-- Results: 5 rows
-- ============================================================

-- ORIGINAL QUERY:
/*

            SELECT 
                ps.position,
                COUNT(*) as players,
                SUM(ps.yellow_cards) as total_yellow_cards,
                SUM(ps.red_cards) as total_red_cards,
                ROUND(AVG(ps.yellow_cards::numeric), 2) as avg_yellow_per_player,
                ROUND(AVG(ps.red_cards::numeric), 2) as avg_red_per_player,
                ROUND(SUM(ps.yellow_cards)::numeric / NULLIF(SUM(ps.minutes_played), 0) * 90, 3) as yellow_per_90min,
                ROUND(SUM(ps.red_cards)::numeric / NULLIF(SUM(ps.minutes_played), 0) * 90, 3) as red_per_90min
            FROM player_statistics ps
            WHERE ps.position IS NOT NULL AND ps.position != '' AND (ps.yellow_cards > 0 OR ps.red_cards > 0)
            GROUP BY ps.position
            ORDER BY avg_yellow_per_player DESC;
        
*/

-- RESULTS SUMMARY:
-- Total rows: 5
-- Columns: position, players, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player, yellow_per_90min, red_per_90min

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- position        | players         | total_yellow_cards | total_red_cards | avg_yellow_per_player | avg_red_per_player | yellow_per_90min | red_per_90min  
-- --------------------------------------------------------------------------------
-- Midfielder      | 950             | 4037            | 69              | 4.25            | 0.07            | 0.217           | 0.004          
-- Defender        | 987             | 4095            | 113             | 4.15            | 0.11            | 0.200           | 0.006          
-- Attacker        | 725             | 2301            | 52              | 3.17            | 0.07            | 0.170           | 0.004          
-- Goalkeeper      | 112             | 205             | 16              | 1.83            | 0.14            | 0.065           | 0.005          
-- Unknown         | 3               | 2               | 2               | 0.67            | 0.67            | None            | None           
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO PLAYER_STATISTICS (position, players, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player, yellow_per_90min, red_per_90min) VALUES ('Midfielder', 950, 4037, 69, 4.25, 0.07, 0.217, 0.004);
-- INSERT INTO PLAYER_STATISTICS (position, players, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player, yellow_per_90min, red_per_90min) VALUES ('Defender', 987, 4095, 113, 4.15, 0.11, 0.200, 0.006);
-- INSERT INTO PLAYER_STATISTICS (position, players, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player, yellow_per_90min, red_per_90min) VALUES ('Attacker', 725, 2301, 52, 3.17, 0.07, 0.170, 0.004);
-- INSERT INTO PLAYER_STATISTICS (position, players, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player, yellow_per_90min, red_per_90min) VALUES ('Goalkeeper', 112, 205, 16, 1.83, 0.14, 0.065, 0.005);
-- INSERT INTO PLAYER_STATISTICS (position, players, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player, yellow_per_90min, red_per_90min) VALUES ('Unknown', 3, 2, 2, 0.67, 0.67, NULL, NULL);
