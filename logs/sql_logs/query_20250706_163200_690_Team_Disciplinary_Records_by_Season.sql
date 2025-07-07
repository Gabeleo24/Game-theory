-- SQL Query Log
-- Timestamp: 2025-07-06 16:32:00
-- Description: Team Disciplinary Records by Season
-- Results: 20 rows
-- ============================================================

-- ORIGINAL QUERY:
/*

            SELECT 
                t.team_name,
                t.country,
                ps.season_year,
                COUNT(*) as players_with_cards,
                SUM(ps.yellow_cards) as total_yellow_cards,
                SUM(ps.red_cards) as total_red_cards,
                ROUND(AVG(ps.yellow_cards::numeric), 2) as avg_yellow_per_player,
                ROUND(AVG(ps.red_cards::numeric), 2) as avg_red_per_player
            FROM player_statistics ps
            JOIN teams t ON ps.team_id = t.team_id
            WHERE ps.yellow_cards > 0 OR ps.red_cards > 0
            GROUP BY t.team_id, t.team_name, t.country, ps.season_year
            ORDER BY total_yellow_cards DESC, total_red_cards DESC
            LIMIT 20;
        
*/

-- RESULTS SUMMARY:
-- Total rows: 20
-- Columns: team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- team_name       | country         | season_year     | players_with_cards | total_yellow_cards | total_red_cards | avg_yellow_per_player | avg_red_per_player
-- --------------------------------------------------------------------------------
-- Maccabi Haifa   | Israel          | 2021            | 13              | 93              | 2               | 7.15            | 0.15           
-- Sporting CP     | Portugal        | 2021            | 14              | 89              | 5               | 6.36            | 0.36           
-- Inter           | Italy           | 2019            | 15              | 79              | 3               | 5.27            | 0.20           
-- FC Porto        | Portugal        | 2019            | 12              | 78              | 2               | 6.50            | 0.17           
-- FK Crvena Zvezd | Serbia          | 2021            | 14              | 78              | 1               | 5.57            | 0.07           
-- SC Braga        | Portugal        | 2019            | 18              | 75              | 2               | 4.17            | 0.11           
-- Atletico Madrid | Spain           | 2020            | 12              | 72              | 0               | 6.00            | 0.00           
-- Sevilla         | Spain           | 2022            | 14              | 71              | 3               | 5.07            | 0.21           
-- Benfica         | Portugal        | 2021            | 14              | 70              | 1               | 5.00            | 0.07           
-- Valencia        | Spain           | 2019            | 15              | 69              | 4               | 4.60            | 0.27           
-- RB Leipzig      | Germany         | 2020            | 13              | 66              | 0               | 5.08            | 0.00           
-- Genk            | Belgium         | 2023            | 9               | 65              | 3               | 7.22            | 0.33           
-- Rennes          | France          | 2020            | 16              | 65              | 3               | 4.06            | 0.19           
-- Atalanta        | Italy           | 2019            | 11              | 64              | 1               | 5.82            | 0.09           
-- Villarreal      | Spain           | 2020            | 13              | 62              | 1               | 4.77            | 0.08           
-- Villarreal      | Spain           | 2021            | 14              | 61              | 0               | 4.36            | 0.00           
-- Bayer Leverkuse | Germany         | 2019            | 13              | 60              | 2               | 4.62            | 0.15           
-- Plzen           | Czech-Republic  | 2019            | 13              | 60              | 2               | 4.62            | 0.15           
-- Maccabi Haifa   | Israel          | 2022            | 14              | 60              | 1               | 4.29            | 0.07           
-- Marseille       | France          | 2019            | 12              | 60              | 1               | 5.00            | 0.08           
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('Maccabi Haifa', 'Israel', 2021, 13, 93, 2, 7.15, 0.15);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('Sporting CP', 'Portugal', 2021, 14, 89, 5, 6.36, 0.36);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('Inter', 'Italy', 2019, 15, 79, 3, 5.27, 0.20);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('FC Porto', 'Portugal', 2019, 12, 78, 2, 6.50, 0.17);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('FK Crvena Zvezda', 'Serbia', 2021, 14, 78, 1, 5.57, 0.07);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('SC Braga', 'Portugal', 2019, 18, 75, 2, 4.17, 0.11);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('Atletico Madrid', 'Spain', 2020, 12, 72, 0, 6.00, 0.00);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('Sevilla', 'Spain', 2022, 14, 71, 3, 5.07, 0.21);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('Benfica', 'Portugal', 2021, 14, 70, 1, 5.00, 0.07);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('Valencia', 'Spain', 2019, 15, 69, 4, 4.60, 0.27);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('RB Leipzig', 'Germany', 2020, 13, 66, 0, 5.08, 0.00);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('Genk', 'Belgium', 2023, 9, 65, 3, 7.22, 0.33);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('Rennes', 'France', 2020, 16, 65, 3, 4.06, 0.19);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('Atalanta', 'Italy', 2019, 11, 64, 1, 5.82, 0.09);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('Villarreal', 'Spain', 2020, 13, 62, 1, 4.77, 0.08);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('Villarreal', 'Spain', 2021, 14, 61, 0, 4.36, 0.00);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('Bayer Leverkusen', 'Germany', 2019, 13, 60, 2, 4.62, 0.15);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('Plzen', 'Czech-Republic', 2019, 13, 60, 2, 4.62, 0.15);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('Maccabi Haifa', 'Israel', 2022, 14, 60, 1, 4.29, 0.07);
-- INSERT INTO PLAYER_STATISTICS (team_name, country, season_year, players_with_cards, total_yellow_cards, total_red_cards, avg_yellow_per_player, avg_red_per_player) VALUES ('Marseille', 'France', 2019, 12, 60, 1, 5.00, 0.08);
