-- PostgreSQL Performance Tuning for Real Madrid Analysis System
-- Optimized for SportMonks API data and large-scale match analysis
-- Created: 2025-07-08

-- ============================================================================
-- CONNECTION POOLING AND MEMORY SETTINGS
-- ============================================================================

-- Increase shared buffers for better caching (25% of available RAM)
ALTER SYSTEM SET shared_buffers = '512MB';

-- Increase work memory for complex queries
ALTER SYSTEM SET work_mem = '16MB';

-- Increase maintenance work memory for index creation
ALTER SYSTEM SET maintenance_work_mem = '128MB';

-- Optimize checkpoint settings for write-heavy workloads
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';

-- Increase connection limits for API data collection
ALTER SYSTEM SET max_connections = 200;

-- ============================================================================
-- QUERY OPTIMIZATION SETTINGS
-- ============================================================================

-- Enable parallel query execution
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 8;
ALTER SYSTEM SET max_parallel_maintenance_workers = 4;

-- Optimize random page cost for SSD storage
ALTER SYSTEM SET random_page_cost = 1.1;

-- Increase effective cache size (75% of available RAM)
ALTER SYSTEM SET effective_cache_size = '1536MB';

-- ============================================================================
-- LOGGING AND MONITORING SETTINGS
-- ============================================================================

-- Enable query logging for slow queries (>1 second)
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- Log lock waits for debugging
ALTER SYSTEM SET log_lock_waits = on;

-- Enable statement statistics
ALTER SYSTEM SET track_activities = on;
ALTER SYSTEM SET track_counts = on;
ALTER SYSTEM SET track_io_timing = on;

-- ============================================================================
-- AUTOVACUUM OPTIMIZATION
-- ============================================================================

-- Optimize autovacuum for frequent updates
ALTER SYSTEM SET autovacuum_vacuum_scale_factor = 0.1;
ALTER SYSTEM SET autovacuum_analyze_scale_factor = 0.05;

-- Increase autovacuum workers for parallel processing
ALTER SYSTEM SET autovacuum_max_workers = 6;

-- ============================================================================
-- SPECIALIZED INDEXES FOR REAL MADRID ANALYSIS
-- ============================================================================

-- Partial index for Real Madrid matches only
CREATE INDEX IF NOT EXISTS idx_real_madrid_matches 
ON matches(match_date, competition_id) 
WHERE home_team_id = (SELECT team_id FROM teams WHERE team_name = 'Real Madrid')
   OR away_team_id = (SELECT team_id FROM teams WHERE team_name = 'Real Madrid');

-- Partial index for Real Madrid player stats
CREATE INDEX IF NOT EXISTS idx_real_madrid_player_stats 
ON match_player_stats(match_id, minutes_played, goals, assists)
WHERE team_id = (SELECT team_id FROM teams WHERE team_name = 'Real Madrid');

-- Index for high-performing players (rating > 7.0)
CREATE INDEX IF NOT EXISTS idx_high_rated_players 
ON match_player_stats(player_id, rating, match_id)
WHERE rating >= 7.0;

-- Index for goal scorers and assist providers
CREATE INDEX IF NOT EXISTS idx_goal_assist_contributors 
ON match_player_stats(player_id, goals, assists, match_id)
WHERE goals > 0 OR assists > 0;

-- ============================================================================
-- MATERIALIZED VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Real Madrid season summary view
CREATE MATERIALIZED VIEW IF NOT EXISTS real_madrid_season_summary AS
SELECT 
    p.player_name,
    p.position,
    p.jersey_number,
    COUNT(*) as appearances,
    SUM(mps.minutes_played) as total_minutes,
    SUM(mps.goals) as total_goals,
    SUM(mps.assists) as total_assists,
    SUM(mps.shots_total) as total_shots,
    SUM(mps.shots_on_target) as total_shots_on_target,
    SUM(mps.passes_total) as total_passes,
    SUM(mps.passes_completed) as total_passes_completed,
    ROUND(AVG(mps.pass_accuracy), 2) as avg_pass_accuracy,
    SUM(mps.tackles_total) as total_tackles,
    SUM(mps.interceptions) as total_interceptions,
    SUM(mps.yellow_cards) as total_yellow_cards,
    SUM(mps.red_cards) as total_red_cards,
    ROUND(AVG(CASE WHEN mps.rating > 0 THEN mps.rating END), 2) as avg_rating,
    ROUND(SUM(mps.expected_goals), 2) as total_xg,
    ROUND(SUM(mps.expected_assists), 2) as total_xag
FROM match_player_stats mps
JOIN players p ON mps.player_id = p.player_id
JOIN teams t ON mps.team_id = t.team_id
WHERE t.team_name = 'Real Madrid'
  AND mps.minutes_played > 0
GROUP BY p.player_id, p.player_name, p.position, p.jersey_number
ORDER BY SUM(mps.minutes_played) DESC;

-- Match results summary view
CREATE MATERIALIZED VIEW IF NOT EXISTS real_madrid_match_results AS
SELECT 
    m.match_id,
    m.match_date,
    m.competition_id,
    c.competition_name,
    CASE 
        WHEN m.home_team_id = t_rm.team_id THEN t_away.team_name
        ELSE t_home.team_name
    END as opponent,
    CASE 
        WHEN m.home_team_id = t_rm.team_id THEN 'Home'
        ELSE 'Away'
    END as venue,
    CASE 
        WHEN m.home_team_id = t_rm.team_id THEN m.home_goals
        ELSE m.away_goals
    END as real_madrid_goals,
    CASE 
        WHEN m.home_team_id = t_rm.team_id THEN m.away_goals
        ELSE m.home_goals
    END as opponent_goals,
    CASE 
        WHEN (m.home_team_id = t_rm.team_id AND m.home_goals > m.away_goals) OR
             (m.away_team_id = t_rm.team_id AND m.away_goals > m.home_goals) THEN 'Win'
        WHEN m.home_goals = m.away_goals THEN 'Draw'
        ELSE 'Loss'
    END as result
FROM matches m
JOIN teams t_rm ON t_rm.team_name = 'Real Madrid'
JOIN teams t_home ON m.home_team_id = t_home.team_id
JOIN teams t_away ON m.away_team_id = t_away.team_id
JOIN competitions c ON m.competition_id = c.competition_id
WHERE m.home_team_id = t_rm.team_id OR m.away_team_id = t_rm.team_id
ORDER BY m.match_date;

-- ============================================================================
-- FUNCTIONS FOR DATA QUALITY AND VALIDATION
-- ============================================================================

-- Function to validate player statistics
CREATE OR REPLACE FUNCTION validate_player_stats()
RETURNS TABLE(
    validation_type TEXT,
    issue_count BIGINT,
    details TEXT
) AS $$
BEGIN
    -- Check for negative statistics
    RETURN QUERY
    SELECT 
        'Negative Statistics'::TEXT,
        COUNT(*)::BIGINT,
        'Players with negative goals, assists, or minutes'::TEXT
    FROM match_player_stats 
    WHERE goals < 0 OR assists < 0 OR minutes_played < 0;
    
    -- Check for unrealistic ratings
    RETURN QUERY
    SELECT 
        'Invalid Ratings'::TEXT,
        COUNT(*)::BIGINT,
        'Players with ratings outside 0-10 range'::TEXT
    FROM match_player_stats 
    WHERE rating < 0 OR rating > 10;
    
    -- Check for missing player names
    RETURN QUERY
    SELECT 
        'Missing Player Names'::TEXT,
        COUNT(*)::BIGINT,
        'Players without names'::TEXT
    FROM players 
    WHERE player_name IS NULL OR player_name = '';
    
    -- Check for duplicate player stats in same match
    RETURN QUERY
    SELECT 
        'Duplicate Player Stats'::TEXT,
        COUNT(*)::BIGINT,
        'Duplicate player statistics for same match'::TEXT
    FROM (
        SELECT match_id, player_id, COUNT(*) as cnt
        FROM match_player_stats
        GROUP BY match_id, player_id
        HAVING COUNT(*) > 1
    ) duplicates;
END;
$$ LANGUAGE plpgsql;

-- Function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_analysis_views()
RETURNS TEXT AS $$
BEGIN
    REFRESH MATERIALIZED VIEW real_madrid_season_summary;
    REFRESH MATERIALIZED VIEW real_madrid_match_results;
    
    INSERT INTO api_collection_metadata (collection_type, collection_status, notes)
    VALUES ('VIEW_REFRESH', 'COMPLETED', 'Materialized views refreshed successfully');
    
    RETURN 'Analysis views refreshed successfully';
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PERFORMANCE MONITORING VIEWS
-- ============================================================================

-- View for monitoring query performance
CREATE OR REPLACE VIEW query_performance AS
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 20;

-- View for monitoring table sizes
CREATE OR REPLACE VIEW table_sizes AS
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- ============================================================================
-- CLEANUP AND MAINTENANCE PROCEDURES
-- ============================================================================

-- Function to clean old API collection metadata
CREATE OR REPLACE FUNCTION cleanup_old_metadata()
RETURNS TEXT AS $$
BEGIN
    DELETE FROM api_collection_metadata 
    WHERE collection_timestamp < CURRENT_TIMESTAMP - INTERVAL '30 days'
      AND collection_status = 'COMPLETED';
    
    RETURN 'Old metadata cleaned successfully';
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- APPLY CONFIGURATION CHANGES
-- ============================================================================

-- Reload configuration
SELECT pg_reload_conf();

-- Log performance tuning completion
INSERT INTO api_collection_metadata (collection_type, collection_status, notes)
VALUES ('PERFORMANCE_TUNING', 'COMPLETED', 'Database performance optimization applied successfully');

-- Create initial refresh of views
SELECT refresh_analysis_views();
