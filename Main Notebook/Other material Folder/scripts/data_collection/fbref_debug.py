#!/usr/bin/env python3
"""
FBRef Debug Script
Quick script to debug FBRef page structure
"""

import requests
from bs4 import BeautifulSoup
import time

def debug_fbref_page():
    """Debug FBRef page structure."""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    # Try the Premier League stats page
    url = "https://fbref.com/en/comps/9/2023-24/stats/2023-24-Premier-League-Stats"
    
    print(f"🔍 Debugging: {url}")
    
    try:
        response = session.get(url, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            
            print("✅ Page loaded successfully")
            print(f"📄 Page title: {soup.title.text if soup.title else 'No title'}")
            
            # Find all tables
            tables = soup.find_all('table')
            print(f"📊 Found {len(tables)} tables")
            
            for i, table in enumerate(tables):
                table_id = table.get('id', 'No ID')
                table_class = table.get('class', 'No class')
                print(f"   Table {i+1}: ID='{table_id}', Class='{table_class}'")
                
                # Check if this looks like a stats table
                if 'stats' in table_id.lower() or 'standard' in table_id.lower():
                    print(f"      🎯 This looks like a stats table!")
                    
                    # Get first few rows to see structure
                    rows = table.find_all('tr')[:5]
                    for j, row in enumerate(rows):
                        cells = row.find_all(['td', 'th'])
                        cell_texts = [cell.text.strip()[:20] for cell in cells[:5]]
                        print(f"         Row {j}: {cell_texts}")
            
            # Also check for any divs that might contain team data
            divs_with_team = soup.find_all('div', string=lambda text: text and 'manchester city' in text.lower())
            print(f"🔍 Found {len(divs_with_team)} divs mentioning Manchester City")
            
            # Look for links that might be team links
            team_links = soup.find_all('a', href=lambda href: href and '/squads/' in href)
            print(f"🔗 Found {len(team_links)} potential team links")
            
            for link in team_links[:5]:
                print(f"   Team link: {link.text.strip()} → {link.get('href')}")
                
        else:
            print(f"❌ Failed to load page: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_fbref_page()
