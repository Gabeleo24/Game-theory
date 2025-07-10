-- =====================================================
-- DATA VALIDATION FUNCTIONS AND TRIGGERS
-- Prevents team confusion and ensures data integrity
-- =====================================================

-- Function to validate Manchester City team identification
CREATE OR REPLACE FUNCTION validate_manchester_city_team()
RETURNS TRIGGER AS $$
BEGIN
    -- Ensure Manchester City is properly identified
    IF NEW.name ILIKE '%manchester city%' OR NEW.name ILIKE '%man city%' THEN
        -- Standardize the name
        NEW.name := 'Manchester City';
        NEW.official_name := 'Manchester City Football Club';
        NEW.city := 'Manchester';
        NEW.country := 'England';
        
        -- Prevent confusion with Manchester United
        IF NEW.name ILIKE '%manchester united%' OR NEW.name ILIKE '%man united%' THEN
            RAISE EXCEPTION 'Team name confusion detected: Cannot mix Manchester City and Manchester United data';
        END IF;
    END IF;
    
    -- Validate Manchester United separately
    IF NEW.name ILIKE '%manchester united%' OR NEW.name ILIKE '%man united%' THEN
        NEW.name := 'Manchester United';
        NEW.official_name := 'Manchester United Football Club';
        NEW.city := 'Manchester';
        NEW.country := 'England';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for team validation
CREATE TRIGGER trigger_validate_manchester_city
    BEFORE INSERT OR UPDATE ON teams
    FOR EACH ROW
    EXECUTE FUNCTION validate_manchester_city_team();

-- Function to validate key Manchester City players
CREATE OR REPLACE FUNCTION validate_key_players()
RETURNS TRIGGER AS $$
DECLARE
    team_record RECORD;
    is_manchester_city BOOLEAN := FALSE;
BEGIN
    -- Check if this is a Manchester City player assignment
    SELECT INTO team_record * FROM teams WHERE id = NEW.team_id;
    
    IF team_record.name = 'Manchester City' THEN
        is_manchester_city := TRUE;
    END IF;
    
    -- Validate key players are assigned to correct team
    IF is_manchester_city THEN
        -- Get player name
        DECLARE
            player_name VARCHAR(100);
        BEGIN
            SELECT full_name INTO player_name FROM players WHERE id = NEW.player_id;
            
            -- Validate key players
            IF player_name ILIKE '%haaland%' THEN
                -- Ensure Haaland is properly identified
                UPDATE players 
                SET first_name = 'Erling', 
                    last_name = 'Haaland',
                    nationality = 'NOR'
                WHERE id = NEW.player_id;
            END IF;
            
            IF player_name ILIKE '%de bruyne%' OR player_name ILIKE '%debruyne%' THEN
                UPDATE players 
                SET first_name = 'Kevin', 
                    last_name = 'De Bruyne',
                    nationality = 'BEL'
                WHERE id = NEW.player_id;
            END IF;
            
            IF player_name ILIKE '%foden%' THEN
                UPDATE players 
                SET first_name = 'Phil', 
                    last_name = 'Foden',
                    nationality = 'ENG'
                WHERE id = NEW.player_id;
            END IF;
        END;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for key player validation
CREATE TRIGGER trigger_validate_key_players
    BEFORE INSERT OR UPDATE ON team_squads
    FOR EACH ROW
    EXECUTE FUNCTION validate_key_players();

-- Function to validate player match performance data integrity
CREATE OR REPLACE FUNCTION validate_player_performance()
RETURNS TRIGGER AS $$
DECLARE
    match_record RECORD;
    team_record RECORD;
    player_record RECORD;
BEGIN
    -- Get match and team information
    SELECT INTO match_record * FROM matches WHERE id = NEW.match_id;
    SELECT INTO team_record * FROM teams WHERE id = NEW.team_id;
    SELECT INTO player_record * FROM players WHERE id = NEW.player_id;
    
    -- Ensure team is actually playing in this match
    IF NEW.team_id != match_record.home_team_id AND NEW.team_id != match_record.away_team_id THEN
        RAISE EXCEPTION 'Player team % is not playing in match %', team_record.name, NEW.match_id;
    END IF;
    
    -- Validate minutes played against match context
    IF NEW.minutes_played > 120 THEN
        RAISE EXCEPTION 'Invalid minutes played: % exceeds maximum possible (120)', NEW.minutes_played;
    END IF;
    
    -- Validate substitution logic
    IF NEW.started = TRUE AND NEW.substituted_in IS NOT NULL THEN
        RAISE EXCEPTION 'Player cannot both start and be substituted in';
    END IF;
    
    IF NEW.started = FALSE AND NEW.substituted_in IS NULL AND NEW.minutes_played > 0 THEN
        RAISE EXCEPTION 'Non-starting player must have substitution time if they played';
    END IF;
    
    -- Validate performance metrics consistency
    IF NEW.shots_on_target > NEW.shots_total THEN
        RAISE EXCEPTION 'Shots on target (%) cannot exceed total shots (%)', NEW.shots_on_target, NEW.shots_total;
    END IF;
    
    IF NEW.passes_completed > NEW.passes_total THEN
        RAISE EXCEPTION 'Completed passes (%) cannot exceed total passes (%)', NEW.passes_completed, NEW.passes_total;
    END IF;
    
    IF NEW.tackles_won > NEW.tackles_total THEN
        RAISE EXCEPTION 'Tackles won (%) cannot exceed total tackles (%)', NEW.tackles_won, NEW.tackles_total;
    END IF;
    
    -- Validate rating range
    IF NEW.rating IS NOT NULL AND (NEW.rating < 0 OR NEW.rating > 10) THEN
        RAISE EXCEPTION 'Player rating must be between 0 and 10, got %', NEW.rating;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for player performance validation
CREATE TRIGGER trigger_validate_player_performance
    BEFORE INSERT OR UPDATE ON player_match_performances
    FOR EACH ROW
    EXECUTE FUNCTION validate_player_performance();

-- Function to validate match data consistency
CREATE OR REPLACE FUNCTION validate_match_data()
RETURNS TRIGGER AS $$
BEGIN
    -- Ensure teams are different
    IF NEW.home_team_id = NEW.away_team_id THEN
        RAISE EXCEPTION 'Home and away teams cannot be the same';
    END IF;
    
    -- Validate scores
    IF NEW.home_score < 0 OR NEW.away_score < 0 THEN
        RAISE EXCEPTION 'Match scores cannot be negative';
    END IF;
    
    -- Validate possession percentages
    IF NEW.home_possession_pct IS NOT NULL AND NEW.away_possession_pct IS NOT NULL THEN
        IF ABS((NEW.home_possession_pct + NEW.away_possession_pct) - 100) > 0.1 THEN
            RAISE EXCEPTION 'Possession percentages must sum to 100, got % + % = %', 
                NEW.home_possession_pct, NEW.away_possession_pct, 
                NEW.home_possession_pct + NEW.away_possession_pct;
        END IF;
    END IF;
    
    -- Validate attendance
    IF NEW.attendance IS NOT NULL AND NEW.attendance < 0 THEN
        RAISE EXCEPTION 'Attendance cannot be negative';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for match data validation
CREATE TRIGGER trigger_validate_match_data
    BEFORE INSERT OR UPDATE ON matches
    FOR EACH ROW
    EXECUTE FUNCTION validate_match_data();

-- Function to check for duplicate players
CREATE OR REPLACE FUNCTION check_duplicate_players()
RETURNS TRIGGER AS $$
DECLARE
    existing_count INTEGER;
BEGIN
    -- Check for potential duplicates based on name and nationality
    SELECT COUNT(*) INTO existing_count
    FROM players 
    WHERE full_name = NEW.full_name 
      AND nationality = NEW.nationality 
      AND id != COALESCE(NEW.id, uuid_generate_v4());
    
    IF existing_count > 0 THEN
        RAISE WARNING 'Potential duplicate player detected: % (%)', NEW.full_name, NEW.nationality;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for duplicate player check
CREATE TRIGGER trigger_check_duplicate_players
    BEFORE INSERT OR UPDATE ON players
    FOR EACH ROW
    EXECUTE FUNCTION check_duplicate_players();

-- Function to validate team squad constraints
CREATE OR REPLACE FUNCTION validate_team_squad()
RETURNS TRIGGER AS $$
DECLARE
    existing_jersey INTEGER;
    squad_size INTEGER;
BEGIN
    -- Check jersey number uniqueness within team and season
    IF NEW.jersey_number IS NOT NULL THEN
        SELECT jersey_number INTO existing_jersey
        FROM team_squads 
        WHERE team_id = NEW.team_id 
          AND season = NEW.season 
          AND jersey_number = NEW.jersey_number 
          AND id != COALESCE(NEW.id, uuid_generate_v4())
          AND is_active = TRUE;
        
        IF existing_jersey IS NOT NULL THEN
            RAISE EXCEPTION 'Jersey number % already assigned in team for season %', 
                NEW.jersey_number, NEW.season;
        END IF;
    END IF;
    
    -- Check squad size limits (typical maximum of 25 players)
    SELECT COUNT(*) INTO squad_size
    FROM team_squads 
    WHERE team_id = NEW.team_id 
      AND season = NEW.season 
      AND is_active = TRUE;
    
    IF squad_size >= 30 THEN
        RAISE WARNING 'Squad size exceeds typical limit (30) for team in season %', NEW.season;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for team squad validation
CREATE TRIGGER trigger_validate_team_squad
    BEFORE INSERT OR UPDATE ON team_squads
    FOR EACH ROW
    EXECUTE FUNCTION validate_team_squad();
