#!/usr/bin/env python3
"""
Test individual player page structure
"""

import requests
from bs4 import BeautifulSoup
import time

def test_player_page():
    """Test Erling Haaland's page structure."""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    # Erling Haaland's FBRef page
    url = "https://fbref.com/en/players/1f44ac21/Erling-Haaland"
    
    print(f"🔍 Testing: {url}")
    
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
                
                # Check for stats tables
                if any(keyword in table_id.lower() for keyword in ['stats', 'standard', 'shooting', 'passing', 'defense']):
                    print(f"      🎯 This looks like a stats table!")
                    
                    # Get first few rows to see structure
                    rows = table.find_all('tr')[:3]
                    for j, row in enumerate(rows):
                        cells = row.find_all(['td', 'th'])
                        cell_texts = [cell.text.strip()[:15] for cell in cells[:8]]
                        print(f"         Row {j}: {cell_texts}")
                        
                        # Look for 2023-24 season data specifically
                        if any('2023-24' in cell.text for cell in cells):
                            print(f"         🎯 Found 2023-24 season data in row {j}!")
                            full_row = [cell.text.strip() for cell in cells]
                            print(f"         Full row: {full_row}")
                    print()
                    
        else:
            print(f"❌ Failed to load page: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_player_page()
