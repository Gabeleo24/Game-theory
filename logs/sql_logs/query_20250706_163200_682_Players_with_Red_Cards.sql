-- SQL Query Log
-- Timestamp: 2025-07-06 16:32:00
-- Description: Players with Red Cards
-- Results: 20 rows
-- ============================================================

-- ORIGINAL QUERY:
/*

            SELECT 
                p.player_name,
                t.team_name,
                t.country,
                ps.season_year,
                ps.red_cards,
                ps.yellow_cards,
                ps.minutes_played,
                ps.goals,
                ps.assists,
                ps.position
            FROM player_statistics ps
            JOIN players p ON ps.player_id = p.player_id
            JOIN teams t ON ps.team_id = t.team_id
            WHERE ps.red_cards > 0
            ORDER BY ps.red_cards DESC, ps.yellow_cards DESC
            LIMIT 20;
        
*/

-- RESULTS SUMMARY:
-- Total rows: 20
-- Columns: player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- player_name     | team_name       | country         | season_year     | red_cards       | yellow_cards    | minutes_played  | goals           | assists         | position       
-- --------------------------------------------------------------------------------
-- G. Xhaka        | Arsenal         | England         | 2021            | 2               | 11              | 2587            | 2               | 2               | Midfielder     
-- M. Tekdemir     | Istanbul Basaks | Turkey          | 2022            | 2               | 11              | 2970            | 0               | 0               | Midfielder     
-- Felipe          | Atletico Madrid | Spain           | 2021            | 2               | 8               | 2147            | 2               | 1               | Defender       
-- Pepe            | FC Porto        | Portugal        | 2023            | 2               | 6               | 2905            | 3               | 1               | Defender       
-- F. Kaša         | Plzen           | Czech-Republic  | 2020            | 2               | 4               | 1682            | 1               | 0               | Defender       
-- Tabata          | Sporting CP     | Portugal        | 2021            | 2               | 4               | 996             | 6               | 2               | Attacker       
-- A. Adli         | Bayer Leverkuse | Germany         | 2022            | 2               | 3               | 1838            | 7               | 4               | Attacker       
-- A. Marchesín    | FC Porto        | Portugal        | 2021            | 2               | 2               | 723             | 0               | 0               | Goalkeeper     
-- Lee Kang-In     | Valencia        | Spain           | 2019            | 2               | 2               | 707             | 2               | 0               | Midfielder     
-- Son Heung-Min   | Tottenham       | England         | 2019            | 2               | 0               | 3289            | 18              | 11              | Attacker       
-- T. Berni        | Inter           | Italy           | 2019            | 2               | 0               | 0               | 0               | 0               | Unknown        
-- P. Hincapié     | Bayer Leverkuse | Germany         | 2022            | 1               | 16              | 3656            | 1               | 1               | Defender       
-- Vinícius Júnior | Real Madrid     | Spain           | 2022            | 1               | 16              | 4727            | 23              | 17              | Attacker       
-- M. Verratti     | Paris Saint Ger | France          | 2022            | 1               | 15              | 3113            | 0               | 1               | Midfielder     
-- Rúben Semedo    | Olympiakos Pira | Greece          | 2019            | 1               | 14              | 3881            | 5               | 0               | Defender       
-- Fransérgio      | SC Braga        | Portugal        | 2019            | 1               | 13              | 3276            | 7               | 3               | Midfielder     
-- Alex Telles     | FC Porto        | Portugal        | 2019            | 1               | 12              | 4102            | 13              | 10              | Defender       
-- Fernandinho     | Manchester City | England         | 2019            | 1               | 12              | 3234            | 0               | 1               | Midfielder     
-- Paulo Otávio    | VfL Wolfsburg   | Germany         | 2020            | 1               | 11              | 2298            | 0               | 2               | Defender       
-- Welinton        | Besiktas        | Turkey          | 2021            | 1               | 11              | 2263            | 0               | 0               | Defender       
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('G. Xhaka', 'Arsenal', 'England', 2021, 2, 11, 2587, 2, 2, 'Midfielder');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('M. Tekdemir', 'Istanbul Basaksehir', 'Turkey', 2022, 2, 11, 2970, 0, 0, 'Midfielder');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('Felipe', 'Atletico Madrid', 'Spain', 2021, 2, 8, 2147, 2, 1, 'Defender');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('Pepe', 'FC Porto', 'Portugal', 2023, 2, 6, 2905, 3, 1, 'Defender');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('F. Kaša', 'Plzen', 'Czech-Republic', 2020, 2, 4, 1682, 1, 0, 'Defender');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('Tabata', 'Sporting CP', 'Portugal', 2021, 2, 4, 996, 6, 2, 'Attacker');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('A. Adli', 'Bayer Leverkusen', 'Germany', 2022, 2, 3, 1838, 7, 4, 'Attacker');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('A. Marchesín', 'FC Porto', 'Portugal', 2021, 2, 2, 723, 0, 0, 'Goalkeeper');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('Lee Kang-In', 'Valencia', 'Spain', 2019, 2, 2, 707, 2, 0, 'Midfielder');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('Son Heung-Min', 'Tottenham', 'England', 2019, 2, 0, 3289, 18, 11, 'Attacker');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('T. Berni', 'Inter', 'Italy', 2019, 2, 0, 0, 0, 0, 'Unknown');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('P. Hincapié', 'Bayer Leverkusen', 'Germany', 2022, 1, 16, 3656, 1, 1, 'Defender');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('Vinícius Júnior', 'Real Madrid', 'Spain', 2022, 1, 16, 4727, 23, 17, 'Attacker');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('M. Verratti', 'Paris Saint Germain', 'France', 2022, 1, 15, 3113, 0, 1, 'Midfielder');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('Rúben Semedo', 'Olympiakos Piraeus', 'Greece', 2019, 1, 14, 3881, 5, 0, 'Defender');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('Fransérgio', 'SC Braga', 'Portugal', 2019, 1, 13, 3276, 7, 3, 'Midfielder');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('Alex Telles', 'FC Porto', 'Portugal', 2019, 1, 12, 4102, 13, 10, 'Defender');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('Fernandinho', 'Manchester City', 'England', 2019, 1, 12, 3234, 0, 1, 'Midfielder');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('Paulo Otávio', 'VfL Wolfsburg', 'Germany', 2020, 1, 11, 2298, 0, 2, 'Defender');
-- INSERT INTO PLAYER_STATISTICS (player_name, team_name, country, season_year, red_cards, yellow_cards, minutes_played, goals, assists, position) VALUES ('Welinton', 'Besiktas', 'Turkey', 2021, 1, 11, 2263, 0, 0, 'Defender');
