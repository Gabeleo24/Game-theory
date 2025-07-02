#!/usr/bin/env python3
"""
FBref Data Collection Example

Working example of collecting data from FBref.com for the Soccer Intelligence System.
This demonstrates successful data collection from Premier League and other major leagues.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
from pathlib import Path
from datetime import datetime


def create_session():
    """Create a session with proper headers for FBref"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    })
    return session


def collect_league_table(session, league_url, league_name):
    """Collect league table data"""
    print(f"Collecting {league_name} table...")
    
    try:
        # Add delay for respectful scraping
        time.sleep(3)
        
        response = session.get(league_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the league table
        table = soup.find('table', {'class': 'stats_table'})
        
        if not table:
            print(f"✗ No table found for {league_name}")
            return None
        
        # Extract headers
        thead = table.find('thead')
        if not thead:
            print(f"✗ No table header found for {league_name}")
            return None
            
        headers = [th.get_text(strip=True) for th in thead.find_all('th')]
        
        # Extract data rows
        rows = []
        tbody = table.find('tbody')
        if tbody:
            for tr in tbody.find_all('tr'):
                row_data = []
                for td in tr.find_all(['td', 'th']):
                    text = td.get_text(strip=True)
                    row_data.append(text)
                if row_data and len(row_data) == len(headers):
                    rows.append(row_data)
        
        if not rows:
            print(f"✗ No data rows found for {league_name}")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        df['league'] = league_name
        df['scraped_at'] = datetime.now().isoformat()
        
        print(f"✓ {league_name} table collected: {len(df)} teams")
        return df
        
    except Exception as e:
        print(f"✗ Error collecting {league_name} table: {e}")
        return None


def collect_player_stats(session, league_url, league_name, stat_type="stats"):
    """Collect player statistics"""
    print(f"Collecting {league_name} player {stat_type}...")
    
    try:
        # Construct stats URL
        base_url = league_url.rstrip('/')
        if stat_type == "stats":
            stats_url = base_url
        else:
            stats_url = f"{base_url}/{stat_type}/{base_url.split('/')[-1]}"
        
        # Add delay for respectful scraping
        time.sleep(3)
        
        response = session.get(stats_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the stats table - try different approaches
        table = soup.find('table', {'id': f'stats_{stat_type}'})
        if not table:
            table = soup.find('table', {'class': 'stats_table'})
        
        if not table:
            print(f"✗ No {stat_type} table found for {league_name}")
            return None
        
        # Extract headers
        thead = table.find('thead')
        if not thead:
            print(f"✗ No table header found for {league_name} {stat_type}")
            return None
        
        # Handle multi-level headers
        header_rows = thead.find_all('tr')
        if len(header_rows) > 1:
            # Use the last row for column names
            headers = [th.get_text(strip=True) for th in header_rows[-1].find_all('th')]
        else:
            headers = [th.get_text(strip=True) for th in header_rows[0].find_all('th')]
        
        # Extract data rows
        rows = []
        tbody = table.find('tbody')
        if tbody:
            for tr in tbody.find_all('tr'):
                # Skip header rows within tbody
                if tr.find('th', {'class': 'thead'}):
                    continue
                
                row_data = []
                for td in tr.find_all(['td', 'th']):
                    text = td.get_text(strip=True)
                    row_data.append(text)
                
                if row_data and len(row_data) == len(headers):
                    rows.append(row_data)
        
        if not rows:
            print(f"✗ No data rows found for {league_name} {stat_type}")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        df['league'] = league_name
        df['stat_type'] = stat_type
        df['scraped_at'] = datetime.now().isoformat()
        
        print(f"✓ {league_name} {stat_type} collected: {len(df)} players")
        return df
        
    except Exception as e:
        print(f"✗ Error collecting {league_name} {stat_type}: {e}")
        return None


def main():
    """Main data collection example"""
    print("FBref Data Collection Example")
    print("=" * 50)
    
    # Create output directory
    output_dir = Path("data/raw/fbref_example")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create session
    session = create_session()
    
    # Major leagues to collect
    leagues = {
        "Premier League": "https://fbref.com/en/comps/9/Premier-League-Stats",
        "La Liga": "https://fbref.com/en/comps/12/La-Liga-Stats",
        "Serie A": "https://fbref.com/en/comps/11/Serie-A-Stats",
        "Bundesliga": "https://fbref.com/en/comps/20/Bundesliga-Stats",
        "Ligue 1": "https://fbref.com/en/comps/13/Ligue-1-Stats"
    }
    
    collected_data = {}
    
    try:
        for league_name, league_url in leagues.items():
            print(f"\n=== {league_name} ===")
            
            # Collect league table
            table_df = collect_league_table(session, league_url, league_name)
            if table_df is not None:
                filename = f"{league_name.lower().replace(' ', '_')}_table.csv"
                table_df.to_csv(output_dir / filename, index=False)
                collected_data[f"{league_name}_table"] = len(table_df)
            
            # Collect player stats
            player_df = collect_player_stats(session, league_url, league_name, "stats")
            if player_df is not None:
                filename = f"{league_name.lower().replace(' ', '_')}_players.csv"
                player_df.to_csv(output_dir / filename, index=False)
                collected_data[f"{league_name}_players"] = len(player_df)
                
                # Show top scorers if goals column exists
                if 'Gls' in player_df.columns:
                    try:
                        # Convert goals to numeric, handling non-numeric values
                        player_df['Gls_numeric'] = pd.to_numeric(player_df['Gls'], errors='coerce')
                        top_scorers = player_df.nlargest(3, 'Gls_numeric')[['Player', 'Squad', 'Gls']].fillna('')
                        print(f"Top 3 scorers in {league_name}:")
                        for _, row in top_scorers.iterrows():
                            print(f"  {row['Player']} ({row['Squad']}) - {row['Gls']} goals")
                    except Exception as e:
                        print(f"Could not display top scorers: {e}")
            
            # Add extra delay between leagues
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\nCollection interrupted by user")
    except Exception as e:
        print(f"\nCollection failed: {e}")
    finally:
        session.close()
    
    # Generate summary
    summary = {
        "collection_date": datetime.now().isoformat(),
        "output_directory": str(output_dir),
        "collected_data": collected_data,
        "total_files": len(collected_data)
    }
    
    # Save summary
    with open(output_dir / "collection_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n" + "=" * 50)
    print("Collection Summary:")
    print(f"Output directory: {output_dir}")
    print(f"Files collected: {len(collected_data)}")
    for key, count in collected_data.items():
        print(f"  {key}: {count} records")
    
    print(f"\nData saved to: {output_dir}")
    print("Summary saved to: collection_summary.json")


if __name__ == "__main__":
    main()
