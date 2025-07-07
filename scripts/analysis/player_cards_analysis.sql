-- Player Cards Analysis Queries
-- Professional analysis of player disciplinary records connected to games and teams

-- =====================================================
-- SAMPLE PLAYERS WITH BASIC INFO
-- =====================================================

SELECT 
  'PLAYER DATABASE OVERVIEW' as analysis_type,
  '========================' as separator;

SELECT 
  COUNT(*) as total_players,
  COUNT(DISTINCT nationality) as countries_represented,
  COUNT(DISTINCT CASE WHEN age IS NOT NULL THEN age END) as age_range_count,
  MIN(age) as youngest_player,
  MAX(age) as oldest_player,
  ROUND(AVG(age::numeric), 1) as average_age
FROM players
WHERE age IS NOT NULL;

-- =====================================================
-- TOP 10 PLAYERS BY NAME (SAMPLE)
-- =====================================================

SELECT 
  'SAMPLE PLAYERS' as section,
  '==============' as separator;

SELECT 
  player_id,
  player_name,
  nationality,
  age,
  height,
  weight
FROM players 
WHERE player_name IS NOT NULL 
ORDER BY player_name 
LIMIT 10;

-- =====================================================
-- PLAYERS BY NATIONALITY (TOP COUNTRIES)
-- =====================================================

SELECT 
  'PLAYERS BY NATIONALITY' as section,
  '======================' as separator;

SELECT 
  nationality,
  COUNT(*) as player_count,
  ROUND(AVG(age::numeric), 1) as avg_age,
  ROUND(AVG(height::numeric), 1) as avg_height_cm,
  ROUND(AVG(weight::numeric), 1) as avg_weight_kg
FROM players 
WHERE nationality IS NOT NULL
GROUP BY nationality
HAVING COUNT(*) >= 10
ORDER BY player_count DESC
LIMIT 15;

-- =====================================================
-- PLAYERS WITH TEAM CONNECTIONS
-- =====================================================

SELECT 
  'PLAYERS WITH TEAM DATA' as section,
  '======================' as separator;

-- This query will show players and their potential team connections
-- Note: We'll need to load player_statistics to see the actual connections
SELECT 
  p.player_name,
  p.nationality,
  p.age,
  'Team data pending statistics load' as team_info
FROM players p
WHERE p.player_name IS NOT NULL
ORDER BY p.player_name
LIMIT 10;

-- =====================================================
-- PREPARE FOR CARD ANALYSIS (WHEN STATS ARE LOADED)
-- =====================================================

SELECT 
  'CARD ANALYSIS PREPARATION' as section,
  '=========================' as separator;

-- Check if player_statistics table has data
SELECT 
  COUNT(*) as player_statistics_count,
  CASE 
    WHEN COUNT(*) > 0 THEN 'Player statistics available for card analysis'
    ELSE 'Player statistics need to be loaded for card analysis'
  END as status
FROM player_statistics;

-- =====================================================
-- FUTURE CARD ANALYSIS QUERIES (WHEN DATA IS LOADED)
-- =====================================================

/*
-- These queries will work once player statistics are loaded:

-- TOP PLAYERS BY YELLOW CARDS
SELECT 
  p.player_name,
  t.team_name,
  ps.season_year,
  ps.yellow_cards,
  ps.red_cards,
  ps.minutes_played,
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

-- PLAYERS WITH RED CARDS
SELECT 
  p.player_name,
  t.team_name,
  ps.season_year,
  ps.red_cards,
  ps.yellow_cards,
  ps.minutes_played,
  ps.goals,
  ps.assists
FROM player_statistics ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams t ON ps.team_id = t.team_id
WHERE ps.red_cards > 0
ORDER BY ps.red_cards DESC, ps.yellow_cards DESC;

-- TEAM DISCIPLINARY RECORDS
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

-- CARDS BY POSITION
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
WHERE ps.position IS NOT NULL AND (ps.yellow_cards > 0 OR ps.red_cards > 0)
GROUP BY ps.position
ORDER BY avg_yellow_per_player DESC;

-- MATCH-LEVEL CARD ANALYSIS (IF MATCH_ID IS AVAILABLE)
SELECT 
  m.match_date,
  ht.team_name as home_team,
  at.team_name as away_team,
  COUNT(ps.player_id) as players_with_cards,
  SUM(ps.yellow_cards) as total_yellow_cards,
  SUM(ps.red_cards) as total_red_cards
FROM player_statistics ps
JOIN matches m ON ps.match_id = m.match_id
JOIN teams ht ON m.home_team_id = ht.team_id
JOIN teams at ON m.away_team_id = at.team_id
WHERE ps.yellow_cards > 0 OR ps.red_cards > 0
GROUP BY m.match_id, m.match_date, ht.team_name, at.team_name
ORDER BY total_yellow_cards DESC, total_red_cards DESC
LIMIT 15;

*/

-- =====================================================
-- CURRENT STATUS SUMMARY
-- =====================================================

SELECT 
  'DATABASE STATUS SUMMARY' as section,
  '=======================' as separator;

SELECT 
  'Players loaded' as metric,
  COUNT(*)::text as value
FROM players
UNION ALL
SELECT 
  'Teams available',
  COUNT(*)::text
FROM teams
UNION ALL
SELECT 
  'Matches available',
  COUNT(*)::text
FROM matches
UNION ALL
SELECT 
  'Player statistics loaded',
  COUNT(*)::text
FROM player_statistics
UNION ALL
SELECT 
  'Ready for card analysis',
  CASE 
    WHEN (SELECT COUNT(*) FROM player_statistics) > 0 THEN 'YES'
    ELSE 'NO - Need to load player statistics'
  END;
