-- =====================================================
-- DATABASE REVERSE ENGINEERING - SIMPLE ANALYSIS
-- Shows table connections, relationships, and order
-- =====================================================

-- 1. DATABASE OVERVIEW
SELECT 
    'DATABASE OVERVIEW' as analysis_section,
    '==================' as separator;

SELECT 
    schemaname as schema_name,
    COUNT(*) as total_tables
FROM pg_tables 
WHERE schemaname = 'public'
GROUP BY schemaname;

-- 2. TABLE STRUCTURE WITH RELATIONSHIPS
SELECT 
    'TABLE STRUCTURE & RELATIONSHIPS' as analysis_section,
    '================================' as separator;

SELECT 
    t.table_name,
    (SELECT COUNT(*) FROM information_schema.columns 
     WHERE table_name = t.table_name AND table_schema = 'public') as total_columns,
    COALESCE(fk_out.outgoing_fks, 0) as outgoing_foreign_keys,
    COALESCE(fk_in.incoming_fks, 0) as incoming_foreign_keys,
    CASE 
        WHEN COALESCE(fk_out.outgoing_fks, 0) = 0 AND COALESCE(fk_in.incoming_fks, 0) > 0 THEN 'ROOT TABLE (Referenced by others)'
        WHEN COALESCE(fk_out.outgoing_fks, 0) > 0 AND COALESCE(fk_in.incoming_fks, 0) = 0 THEN 'LEAF TABLE (References others)'
        WHEN COALESCE(fk_out.outgoing_fks, 0) > 0 AND COALESCE(fk_in.incoming_fks, 0) > 0 THEN 'JUNCTION TABLE (Both)'
        ELSE 'STANDALONE TABLE'
    END as table_role,
    -- Get actual row count
    CASE t.table_name
        WHEN 'teams' THEN (SELECT COUNT(*) FROM teams)
        WHEN 'players' THEN (SELECT COUNT(*) FROM players)
        WHEN 'matches' THEN (SELECT COUNT(*) FROM matches)
        WHEN 'player_statistics' THEN (SELECT COUNT(*) FROM player_statistics)
        WHEN 'competitions' THEN (SELECT COUNT(*) FROM competitions)
        WHEN 'seasons' THEN (SELECT COUNT(*) FROM seasons)
        WHEN 'team_statistics' THEN (SELECT COUNT(*) FROM team_statistics)
        WHEN 'shapley_analysis' THEN (SELECT COUNT(*) FROM shapley_analysis)
        WHEN 'collection_logs' THEN (SELECT COUNT(*) FROM collection_logs)
        ELSE 0
    END as current_row_count
FROM information_schema.tables t
LEFT JOIN (
    SELECT 
        tc.table_name,
        COUNT(*) as outgoing_fks
    FROM information_schema.table_constraints tc
    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
    GROUP BY tc.table_name
) fk_out ON t.table_name = fk_out.table_name
LEFT JOIN (
    SELECT 
        ccu.table_name,
        COUNT(*) as incoming_fks
    FROM information_schema.table_constraints tc
    JOIN information_schema.constraint_column_usage ccu 
        ON tc.constraint_name = ccu.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
    GROUP BY ccu.table_name
) fk_in ON t.table_name = fk_in.table_name
WHERE t.table_schema = 'public'
ORDER BY 
    CASE 
        WHEN COALESCE(fk_out.outgoing_fks, 0) = 0 AND COALESCE(fk_in.incoming_fks, 0) > 0 THEN 1
        WHEN COALESCE(fk_out.outgoing_fks, 0) > 0 AND COALESCE(fk_in.incoming_fks, 0) > 0 THEN 2
        WHEN COALESCE(fk_out.outgoing_fks, 0) > 0 AND COALESCE(fk_in.incoming_fks, 0) = 0 THEN 3
        ELSE 4
    END,
    t.table_name;

-- 3. FOREIGN KEY RELATIONSHIPS (THE CONNECTIONS)
SELECT 
    'FOREIGN KEY RELATIONSHIPS' as analysis_section,
    '==========================' as separator;

SELECT 
    tc.table_name as source_table,
    kcu.column_name as source_column,
    ccu.table_name as target_table,
    ccu.column_name as target_column,
    tc.constraint_name,
    CONCAT(tc.table_name, '.', kcu.column_name, ' -> ', ccu.table_name, '.', ccu.column_name) as relationship_chain
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu 
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.column_name;

-- 4. DATA RELATIONSHIP ANALYSIS (ACTUAL CONNECTIONS)
SELECT 
    'DATA RELATIONSHIP ANALYSIS' as analysis_section,
    '===========================' as separator;

-- Teams to Players connection
SELECT 
    'teams -> players' as relationship,
    COUNT(DISTINCT t.team_id) as unique_teams,
    COUNT(DISTINCT p.player_id) as unique_players,
    COUNT(*) as total_connections
FROM teams t
LEFT JOIN players p ON t.team_id = p.team_id;

-- Teams to Matches connection (home team)
SELECT 
    'teams -> matches (home)' as relationship,
    COUNT(DISTINCT t.team_id) as unique_teams,
    COUNT(DISTINCT m.match_id) as unique_matches,
    COUNT(*) as total_connections
FROM teams t
LEFT JOIN matches m ON t.team_id = m.home_team_id;

-- Teams to Matches connection (away team)
SELECT 
    'teams -> matches (away)' as relationship,
    COUNT(DISTINCT t.team_id) as unique_teams,
    COUNT(DISTINCT m.match_id) as unique_matches,
    COUNT(*) as total_connections
FROM teams t
LEFT JOIN matches m ON t.team_id = m.away_team_id;

-- Players to Player Statistics connection
SELECT 
    'players -> player_statistics' as relationship,
    COUNT(DISTINCT p.player_id) as unique_players,
    COUNT(DISTINCT ps.player_id) as players_with_stats,
    COUNT(*) as total_stat_records
FROM players p
LEFT JOIN player_statistics ps ON p.player_id = ps.player_id;

-- Teams to Player Statistics connection
SELECT 
    'teams -> player_statistics' as relationship,
    COUNT(DISTINCT t.team_id) as unique_teams,
    COUNT(DISTINCT ps.team_id) as teams_with_stats,
    COUNT(*) as total_stat_records
FROM teams t
LEFT JOIN player_statistics ps ON t.team_id = ps.team_id;

-- 5. OPERATION ORDER (INSERT/DELETE SEQUENCE)
SELECT 
    'OPERATION ORDER' as analysis_section,
    '===============' as separator;

SELECT 
    'INSERT ORDER (Dependencies First)' as operation_type,
    '1. teams (ROOT - no dependencies)' as step_1,
    '2. competitions (ROOT - no dependencies)' as step_2,
    '3. players (depends on teams)' as step_3,
    '4. matches (depends on teams for home/away)' as step_4,
    '5. player_statistics (depends on teams and players)' as step_5;

SELECT 
    'DELETE ORDER (Reverse Dependencies)' as operation_type,
    '1. player_statistics (remove dependent data first)' as step_1,
    '2. matches (remove match records)' as step_2,
    '3. players (remove player records)' as step_3,
    '4. teams (remove root records)' as step_4,
    '5. competitions (remove root records last)' as step_5;

-- 6. SAMPLE DATA CONNECTIONS (SHOW ACTUAL RELATIONSHIPS)
SELECT 
    'SAMPLE DATA CONNECTIONS' as analysis_section,
    '=======================' as separator;

-- Show sample team-player connections
SELECT 
    'TEAM-PLAYER CONNECTIONS (Sample)' as connection_type,
    t.team_name,
    COUNT(p.player_id) as player_count
FROM teams t
LEFT JOIN players p ON t.team_id = p.team_id
GROUP BY t.team_id, t.team_name
HAVING COUNT(p.player_id) > 0
ORDER BY player_count DESC
LIMIT 10;

-- Show sample match connections
SELECT 
    'MATCH CONNECTIONS (Sample)' as connection_type,
    ht.team_name as home_team,
    at.team_name as away_team,
    m.home_goals || '-' || m.away_goals as score,
    m.match_date::date as match_date
FROM matches m
JOIN teams ht ON m.home_team_id = ht.team_id
JOIN teams at ON m.away_team_id = at.team_id
WHERE m.home_goals IS NOT NULL AND m.away_goals IS NOT NULL
ORDER BY m.match_date DESC
LIMIT 10;

-- Show sample player statistics connections
SELECT 
    'PLAYER STATISTICS CONNECTIONS (Sample)' as connection_type,
    p.player_name,
    t.team_name,
    ps.season_year,
    ps.goals,
    ps.assists,
    ps.yellow_cards,
    ps.red_cards
FROM player_statistics ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams t ON ps.team_id = t.team_id
WHERE ps.goals > 0 OR ps.assists > 0
ORDER BY (ps.goals + ps.assists) DESC
LIMIT 10;
