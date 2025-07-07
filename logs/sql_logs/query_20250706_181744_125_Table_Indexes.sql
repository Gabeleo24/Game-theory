-- SQL Query Log
-- Timestamp: 2025-07-06 18:17:44
-- Description: Table Indexes
-- Results: 23 rows
-- ============================================================

-- ORIGINAL QUERY:
/*

            SELECT 
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM pg_indexes 
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname;
        
*/

-- RESULTS SUMMARY:
-- Total rows: 23
-- Columns: schemaname, tablename, indexname, indexdef

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- schemaname      | tablename       | indexname       | indexdef       
-- --------------------------------------------------------------------------------
-- public          | collection_logs | collection_logs | CREATE UNIQUE I
-- public          | competitions    | competitions_pk | CREATE UNIQUE I
-- public          | matches         | idx_matches_com | CREATE INDEX id
-- public          | matches         | idx_matches_dat | CREATE INDEX id
-- public          | matches         | idx_matches_tea | CREATE INDEX id
-- public          | matches         | matches_pkey    | CREATE UNIQUE I
-- public          | player_statisti | idx_player_stat | CREATE INDEX id
-- public          | player_statisti | idx_player_stat | CREATE INDEX id
-- public          | player_statisti | idx_player_stat | CREATE INDEX id
-- public          | player_statisti | player_statisti | CREATE UNIQUE I
-- public          | players         | idx_players_nam | CREATE INDEX id
-- public          | players         | idx_players_nat | CREATE INDEX id
-- public          | players         | players_pkey    | CREATE UNIQUE I
-- public          | seasons         | seasons_pkey    | CREATE UNIQUE I
-- public          | shapley_analysi | idx_shapley_pla | CREATE INDEX id
-- public          | shapley_analysi | idx_shapley_tea | CREATE INDEX id
-- public          | shapley_analysi | shapley_analysi | CREATE UNIQUE I
-- public          | team_statistics | idx_team_stats_ | CREATE INDEX id
-- public          | team_statistics | idx_team_stats_ | CREATE INDEX id
-- public          | team_statistics | team_statistics | CREATE UNIQUE I
-- public          | teams           | idx_teams_count | CREATE INDEX id
-- public          | teams           | idx_teams_name  | CREATE INDEX id
-- public          | teams           | teams_pkey      | CREATE UNIQUE I
-- --------------------------------------------------------------------------------

-- RESULTS AS INSERT STATEMENTS:
-- (For backup/recreation purposes)

-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'collection_logs', 'collection_logs_pkey', 'CREATE UNIQUE INDEX collection_logs_pkey ON public.collection_logs USING btree (log_id)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'competitions', 'competitions_pkey', 'CREATE UNIQUE INDEX competitions_pkey ON public.competitions USING btree (competition_id)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'matches', 'idx_matches_competition_season', 'CREATE INDEX idx_matches_competition_season ON public.matches USING btree (competition_id, season_year)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'matches', 'idx_matches_date', 'CREATE INDEX idx_matches_date ON public.matches USING btree (match_date)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'matches', 'idx_matches_teams', 'CREATE INDEX idx_matches_teams ON public.matches USING btree (home_team_id, away_team_id)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'matches', 'matches_pkey', 'CREATE UNIQUE INDEX matches_pkey ON public.matches USING btree (match_id)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'player_statistics', 'idx_player_stats_match', 'CREATE INDEX idx_player_stats_match ON public.player_statistics USING btree (match_id)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'player_statistics', 'idx_player_stats_player_season', 'CREATE INDEX idx_player_stats_player_season ON public.player_statistics USING btree (player_id, season_year)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'player_statistics', 'idx_player_stats_team_season', 'CREATE INDEX idx_player_stats_team_season ON public.player_statistics USING btree (team_id, season_year)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'player_statistics', 'player_statistics_pkey', 'CREATE UNIQUE INDEX player_statistics_pkey ON public.player_statistics USING btree (stat_id)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'players', 'idx_players_name', 'CREATE INDEX idx_players_name ON public.players USING btree (player_name)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'players', 'idx_players_nationality', 'CREATE INDEX idx_players_nationality ON public.players USING btree (nationality)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'players', 'players_pkey', 'CREATE UNIQUE INDEX players_pkey ON public.players USING btree (player_id)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'seasons', 'seasons_pkey', 'CREATE UNIQUE INDEX seasons_pkey ON public.seasons USING btree (season_id)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'shapley_analysis', 'idx_shapley_player_season', 'CREATE INDEX idx_shapley_player_season ON public.shapley_analysis USING btree (player_id, season_year)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'shapley_analysis', 'idx_shapley_team_season', 'CREATE INDEX idx_shapley_team_season ON public.shapley_analysis USING btree (team_id, season_year)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'shapley_analysis', 'shapley_analysis_pkey', 'CREATE UNIQUE INDEX shapley_analysis_pkey ON public.shapley_analysis USING btree (analysis_id)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'team_statistics', 'idx_team_stats_competition', 'CREATE INDEX idx_team_stats_competition ON public.team_statistics USING btree (competition_id, season_year)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'team_statistics', 'idx_team_stats_team_season', 'CREATE INDEX idx_team_stats_team_season ON public.team_statistics USING btree (team_id, season_year)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'team_statistics', 'team_statistics_pkey', 'CREATE UNIQUE INDEX team_statistics_pkey ON public.team_statistics USING btree (stat_id)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'teams', 'idx_teams_country', 'CREATE INDEX idx_teams_country ON public.teams USING btree (country)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'teams', 'idx_teams_name', 'CREATE INDEX idx_teams_name ON public.teams USING btree (team_name)');
-- INSERT INTO PG_INDEXES (schemaname, tablename, indexname, indexdef) VALUES ('public', 'teams', 'teams_pkey', 'CREATE UNIQUE INDEX teams_pkey ON public.teams USING btree (team_id)');
