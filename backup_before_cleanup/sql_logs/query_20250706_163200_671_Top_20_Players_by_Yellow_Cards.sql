-- SQL Query Log
-- Timestamp: 2025-07-06 16:32:00
-- Description: Top 20 Players by Yellow Cards
-- Results: 20 rows
-- ============================================================

-- ORIGINAL QUERY:
/*

            SELECT 
                p.player_name,
                t.team_name,
                t.country,
                ps.season_year,
                ps.yellow_cards,
                ps.red_cards,
                ps.minutes_played,
                ps.goals,
                ps.assists,
                ps.position,
                CASE 
                    WHEN ps.minutes_played > 0 
                    THEN ROUND((ps.yellow_cards::numeric / ps.minutes_played * 90), 2)
                    ELSE 0 
                END as yellow_cards_per_90min
            FROM player_statistics ps
            JOIN players p ON ps.player_id = p.player_id
            JOIN teams t ON ps.team_id = t.team_id
            WHERE ps.yellow_cards > 0
            ORDER BY ps.yellow_cards DESC, ps.red_cards DESC
            LIMIT 20;
        
*/

-- RESULTS SUMMARY:
-- Total rows: 20
-- Columns: player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- player_name     | team_name       | country         | season_year     | yellow_cards    | red_cards       | minutes_played  | goals           | assists         | position        | yellow_cards_per_90min
-- --------------------------------------------------------------------------------
-- Piqué           | Barcelona       | Spain           | 2019            | 19              | 0               | 4070            | 1               | 0               | Defender        | 0.42           
-- O. Alderete     | Valencia        | Spain           | 2021            | 17              | 0               | 2935            | 2               | 0               | Defender        | 0.52           
-- P. Hincapié     | Bayer Leverkuse | Germany         | 2022            | 16              | 1               | 3656            | 1               | 1               | Defender        | 0.39           
-- Vinícius Júnior | Real Madrid     | Spain           | 2022            | 16              | 1               | 4727            | 23              | 17              | Attacker        | 0.30           
-- João Palhinha   | SC Braga        | Portugal        | 2019            | 16              | 0               | 3562            | 4               | 1               | Midfielder      | 0.40           
-- M. Verratti     | Paris Saint Ger | France          | 2022            | 15              | 1               | 3113            | 0               | 1               | Midfielder      | 0.43           
-- M. de Roon      | Atalanta        | Italy           | 2019            | 15              | 0               | 3572            | 2               | 6               | Midfielder      | 0.38           
-- K. Havertz      | Arsenal         | England         | 2023            | 15              | 0               | 3973            | 16              | 7               | Attacker        | 0.34           
-- Álvaro González | Marseille       | France          | 2020            | 15              | 0               | 3552            | 2               | 3               | Defender        | 0.38           
-- M. Abu Fani     | Maccabi Haifa   | Israel          | 2021            | 15              | 0               | 2996            | 6               | 0               | Midfielder      | 0.45           
-- N. Barella      | Inter           | Italy           | 2019            | 15              | 0               | 3314            | 4               | 6               | Midfielder      | 0.41           
-- D. Haziza       | Maccabi Haifa   | Israel          | 2021            | 15              | 0               | 3685            | 11              | 0               | Midfielder      | 0.37           
-- Rúben Semedo    | Olympiakos Pira | Greece          | 2019            | 14              | 1               | 3881            | 5               | 0               | Defender        | 0.32           
-- C. Gallagher    | Chelsea         | England         | 2022            | 14              | 0               | 2113            | 3               | 1               | Midfielder      | 0.60           
-- Martín Zubimend | Real Sociedad   | Spain           | 2022            | 14              | 0               | 3745            | 1               | 4               | Midfielder      | 0.34           
-- Paulinho        | Sporting CP     | Portugal        | 2021            | 14              | 0               | 3419            | 14              | 5               | Attacker        | 0.37           
-- M. Verratti     | Paris Saint Ger | France          | 2021            | 14              | 0               | 2622            | 2               | 2               | Midfielder      | 0.48           
-- Vladislav Ignat | Lokomotiv       | Russia          | 2019            | 14              | 0               | 2426            | 1               | 1               | Midfielder      | 0.52           
-- M. Rodić        | FK Crvena Zvezd | Serbia          | 2021            | 14              | 0               | 4151            | 4               | 0               | Defender        | 0.30           
-- S. Sanogo       | FK Crvena Zvezd | Serbia          | 2020            | 14              | 0               | 2674            | 1               | 0               | Midfielder      | 0.47           
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('Piqué', 'Barcelona', 'Spain', 2019, 19, 0, 4070, 1, 0, 'Defender', 0.42);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('O. Alderete', 'Valencia', 'Spain', 2021, 17, 0, 2935, 2, 0, 'Defender', 0.52);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('P. Hincapié', 'Bayer Leverkusen', 'Germany', 2022, 16, 1, 3656, 1, 1, 'Defender', 0.39);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('Vinícius Júnior', 'Real Madrid', 'Spain', 2022, 16, 1, 4727, 23, 17, 'Attacker', 0.30);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('João Palhinha', 'SC Braga', 'Portugal', 2019, 16, 0, 3562, 4, 1, 'Midfielder', 0.40);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('M. Verratti', 'Paris Saint Germain', 'France', 2022, 15, 1, 3113, 0, 1, 'Midfielder', 0.43);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('M. de Roon', 'Atalanta', 'Italy', 2019, 15, 0, 3572, 2, 6, 'Midfielder', 0.38);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('K. Havertz', 'Arsenal', 'England', 2023, 15, 0, 3973, 16, 7, 'Attacker', 0.34);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('Álvaro González', 'Marseille', 'France', 2020, 15, 0, 3552, 2, 3, 'Defender', 0.38);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('M. Abu Fani', 'Maccabi Haifa', 'Israel', 2021, 15, 0, 2996, 6, 0, 'Midfielder', 0.45);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('N. Barella', 'Inter', 'Italy', 2019, 15, 0, 3314, 4, 6, 'Midfielder', 0.41);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('D. Haziza', 'Maccabi Haifa', 'Israel', 2021, 15, 0, 3685, 11, 0, 'Midfielder', 0.37);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('Rúben Semedo', 'Olympiakos Piraeus', 'Greece', 2019, 14, 1, 3881, 5, 0, 'Defender', 0.32);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('C. Gallagher', 'Chelsea', 'England', 2022, 14, 0, 2113, 3, 1, 'Midfielder', 0.60);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('Martín Zubimendi', 'Real Sociedad', 'Spain', 2022, 14, 0, 3745, 1, 4, 'Midfielder', 0.34);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('Paulinho', 'Sporting CP', 'Portugal', 2021, 14, 0, 3419, 14, 5, 'Attacker', 0.37);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('M. Verratti', 'Paris Saint Germain', 'France', 2021, 14, 0, 2622, 2, 2, 'Midfielder', 0.48);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('Vladislav Ignatjev', 'Lokomotiv', 'Russia', 2019, 14, 0, 2426, 1, 1, 'Midfielder', 0.52);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('M. Rodić', 'FK Crvena Zvezda', 'Serbia', 2021, 14, 0, 4151, 4, 0, 'Defender', 0.30);
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, yellow_cards, red_cards, minutes_played, goals, assists, position, yellow_cards_per_90min) VALUES ('S. Sanogo', 'FK Crvena Zvezda', 'Serbia', 2020, 14, 0, 2674, 1, 0, 'Midfielder', 0.47);
