-- Clean Match Analysis Queries (No Emojis)
-- Professional soccer intelligence analysis for highest-scoring matches

-- =====================================================
-- TOP 5 HIGHEST SCORING MATCHES WITH FULL DETAILS
-- =====================================================

SELECT 
  'MATCH ' || ROW_NUMBER() OVER (ORDER BY (m.home_goals + m.away_goals) DESC, m.match_date DESC) as rank,
  ht.team_name || ' vs ' || at.team_name as fixture,
  m.home_goals || '-' || m.away_goals as score,
  (m.home_goals + m.away_goals) as total_goals,
  CASE 
    WHEN m.home_goals > m.away_goals THEN ht.team_name || ' (HOME WIN)'
    WHEN m.home_goals < m.away_goals THEN at.team_name || ' (AWAY WIN)'
    ELSE 'DRAW'
  END as result,
  ABS(m.home_goals - m.away_goals) as margin,
  m.match_date::date as date,
  TO_CHAR(m.match_date, 'Day') as day_of_week,
  EXTRACT(year from m.match_date) as season,
  m.venue_name as stadium,
  ht.country as country,
  CASE
    WHEN ABS(m.home_goals - m.away_goals) >= 4 THEN 'DEMOLITION'
    WHEN ABS(m.home_goals - m.away_goals) = 3 THEN 'THRASHING' 
    WHEN ABS(m.home_goals - m.away_goals) = 2 THEN 'COMFORTABLE'
    WHEN ABS(m.home_goals - m.away_goals) = 1 THEN 'TIGHT BATTLE'
    ELSE 'DEADLOCK'
  END as match_intensity,
  CASE 
    WHEN (m.home_goals + m.away_goals) >= 7 THEN 'EPIC'
    WHEN (m.home_goals + m.away_goals) = 6 THEN 'THRILLER'
    WHEN (m.home_goals + m.away_goals) = 5 THEN 'HIGH-SCORING'
    ELSE 'NORMAL'
  END as goal_fest_level
FROM matches m
JOIN teams ht ON m.home_team_id = ht.team_id
JOIN teams at ON m.away_team_id = at.team_id
WHERE m.home_goals IS NOT NULL AND m.away_goals IS NOT NULL
ORDER BY (m.home_goals + m.away_goals) DESC, m.match_date DESC
LIMIT 5;

-- =====================================================
-- TEAM PERFORMANCE IN EPIC MATCHES (7+ GOALS)
-- =====================================================

WITH epic_matches AS (
  SELECT m.*, ht.team_name as home_team, at.team_name as away_team
  FROM matches m
  JOIN teams ht ON m.home_team_id = ht.team_id
  JOIN teams at ON m.away_team_id = at.team_id
  WHERE (m.home_goals + m.away_goals) >= 7
)
SELECT 
  ROW_NUMBER() OVER (ORDER BY goals_scored DESC, team_name) as rank,
  team_name as team,
  goals_scored as scored,
  goals_conceded as conceded,
  (goals_scored - goals_conceded) as goal_difference,
  CASE WHEN goals_scored > goals_conceded THEN 'WIN'
       WHEN goals_scored < goals_conceded THEN 'LOSS'
       ELSE 'DRAW' END as result,
  CASE WHEN venue_type = 'HOME' THEN 'Home' ELSE 'Away' END as venue,
  opponent,
  match_date::date as date,
  stadium,
  CASE 
    WHEN goals_scored >= 5 THEN 'EXPLOSIVE'
    WHEN goals_scored = 4 THEN 'CLINICAL'
    WHEN goals_scored = 3 THEN 'SOLID'
    WHEN goals_scored = 2 THEN 'MODEST'
    ELSE 'DEFENSIVE'
  END as attack_rating,
  CASE
    WHEN goals_conceded <= 1 THEN 'ROCK SOLID'
    WHEN goals_conceded = 2 THEN 'SHAKY'
    WHEN goals_conceded = 3 THEN 'LEAKY'
    ELSE 'POROUS'
  END as defense_rating
FROM (
  SELECT home_team as team_name, home_goals as goals_scored, away_goals as goals_conceded,
         away_team as opponent, 'HOME' as venue_type, match_date, venue_name as stadium
  FROM epic_matches
  UNION ALL
  SELECT away_team as team_name, away_goals as goals_scored, home_goals as goals_conceded,
         home_team as opponent, 'AWAY' as venue_type, match_date, venue_name as stadium
  FROM epic_matches
) combined
ORDER BY goals_scored DESC, goal_difference DESC;

-- =====================================================
-- MATCH STATISTICS SUMMARY
-- =====================================================

SELECT 
  'EPIC MATCH STATISTICS' as analysis_type,
  '=====================' as separator;

SELECT 
  'Total epic matches (7+ goals)' as metric,
  COUNT(*)::text as value
FROM matches 
WHERE (home_goals + away_goals) >= 7
UNION ALL
SELECT 
  'Countries represented',
  COUNT(DISTINCT ht.country)::text
FROM matches m
JOIN teams ht ON m.home_team_id = ht.team_id
WHERE (m.home_goals + m.away_goals) >= 7
UNION ALL
SELECT 
  'Home team wins',
  COUNT(*)::text
FROM matches 
WHERE (home_goals + away_goals) >= 7 AND home_goals > away_goals
UNION ALL
SELECT 
  'Away team wins', 
  COUNT(*)::text
FROM matches
WHERE (home_goals + away_goals) >= 7 AND away_goals > home_goals
UNION ALL
SELECT
  'Average goal difference',
  ROUND(AVG(ABS(home_goals - away_goals))::numeric, 1)::text
FROM matches
WHERE (home_goals + away_goals) >= 7;

-- =====================================================
-- TEAM PERFORMANCE ACROSS ALL MATCHES
-- =====================================================

SELECT 
  t.team_name,
  t.country,
  COUNT(m.match_id) as total_matches,
  SUM(CASE WHEN m.home_team_id = t.team_id THEN m.home_goals ELSE m.away_goals END) as goals_scored,
  SUM(CASE WHEN m.home_team_id = t.team_id THEN m.away_goals ELSE m.home_goals END) as goals_conceded,
  SUM(CASE WHEN m.home_team_id = t.team_id THEN m.home_goals ELSE m.away_goals END) - 
  SUM(CASE WHEN m.home_team_id = t.team_id THEN m.away_goals ELSE m.home_goals END) as goal_difference,
  SUM(CASE 
    WHEN (m.home_team_id = t.team_id AND m.home_goals > m.away_goals) OR 
         (m.away_team_id = t.team_id AND m.away_goals > m.home_goals) 
    THEN 1 ELSE 0 END) as wins,
  SUM(CASE WHEN m.home_goals = m.away_goals THEN 1 ELSE 0 END) as draws,
  SUM(CASE 
    WHEN (m.home_team_id = t.team_id AND m.home_goals < m.away_goals) OR 
         (m.away_team_id = t.team_id AND m.away_goals < m.home_goals) 
    THEN 1 ELSE 0 END) as losses,
  ROUND(
    (SUM(CASE WHEN m.home_goals = m.away_goals THEN 1 ELSE 0 END) + 
     SUM(CASE 
       WHEN (m.home_team_id = t.team_id AND m.home_goals > m.away_goals) OR 
            (m.away_team_id = t.team_id AND m.away_goals > m.home_goals) 
       THEN 3 ELSE 0 END))::numeric / COUNT(m.match_id), 2
  ) as points_per_game
FROM teams t
LEFT JOIN matches m ON t.team_id = m.home_team_id OR t.team_id = m.away_team_id
WHERE m.home_goals IS NOT NULL AND m.away_goals IS NOT NULL
GROUP BY t.team_id, t.team_name, t.country
HAVING COUNT(m.match_id) > 0
ORDER BY points_per_game DESC, goal_difference DESC
LIMIT 20;

-- =====================================================
-- VENUE ANALYSIS
-- =====================================================

SELECT 
  m.venue_name as stadium,
  ht.country,
  COUNT(*) as matches_played,
  ROUND(AVG(m.home_goals + m.away_goals)::numeric, 2) as avg_goals_per_match,
  SUM(CASE WHEN m.home_goals > m.away_goals THEN 1 ELSE 0 END) as home_wins,
  SUM(CASE WHEN m.home_goals = m.away_goals THEN 1 ELSE 0 END) as draws,
  SUM(CASE WHEN m.away_goals > m.home_goals THEN 1 ELSE 0 END) as away_wins,
  ROUND(
    (SUM(CASE WHEN m.home_goals > m.away_goals THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100), 1
  ) as home_win_percentage
FROM matches m
JOIN teams ht ON m.home_team_id = ht.team_id
WHERE m.home_goals IS NOT NULL AND m.away_goals IS NOT NULL AND m.venue_name IS NOT NULL
GROUP BY m.venue_name, ht.country
HAVING COUNT(*) >= 2
ORDER BY avg_goals_per_match DESC, matches_played DESC;

-- =====================================================
-- SEASONAL TRENDS
-- =====================================================

SELECT 
  EXTRACT(year from m.match_date) as season,
  COUNT(*) as total_matches,
  ROUND(AVG(m.home_goals + m.away_goals)::numeric, 2) as avg_goals_per_match,
  SUM(CASE WHEN (m.home_goals + m.away_goals) >= 5 THEN 1 ELSE 0 END) as high_scoring_matches,
  SUM(CASE WHEN (m.home_goals + m.away_goals) >= 7 THEN 1 ELSE 0 END) as epic_matches,
  MAX(m.home_goals + m.away_goals) as highest_scoring_match
FROM matches m
WHERE m.home_goals IS NOT NULL AND m.away_goals IS NOT NULL
GROUP BY EXTRACT(year from m.match_date)
ORDER BY season;
