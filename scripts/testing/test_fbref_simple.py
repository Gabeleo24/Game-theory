#!/usr/bin/env python3
"""
Simple FBref Test

Test FBref data collection without importing the full project
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from pathlib import Path


def test_fbref_connection():
    """Test basic connection to FBref"""
    print("Testing FBref connection...")

    try:
        # Create session with proper headers
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

        # Test basic connection
        response = session.get("https://fbref.com/en/", timeout=30)
        response.raise_for_status()

        print(f"✓ Successfully connected to FBref (status: {response.status_code})")

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title')

        if title:
            print(f"✓ Page title: {title.get_text().strip()}")

        session.close()
        return True

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def test_premier_league_table():
    """Test collecting Premier League table"""
    print("\nTesting Premier League table collection...")

    try:
        url = "https://fbref.com/en/comps/9/Premier-League-Stats"

        # Create session with proper headers
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

        # Add delay for respectful scraping
        time.sleep(3)

        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the league table
        table = soup.find('table', {'class': 'stats_table'})
        
        if table:
            print("✓ Found Premier League table")
            
            # Extract headers
            headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')]
            print(f"✓ Table headers: {headers[:5]}...")
            
            # Extract first few rows
            rows = []
            tbody = table.find('tbody')
            if tbody:
                for i, tr in enumerate(tbody.find_all('tr')[:3]):  # First 3 teams
                    row_data = []
                    for td in tr.find_all(['td', 'th']):
                        text = td.get_text(strip=True)
                        row_data.append(text)
                    if row_data:
                        rows.append(row_data)
                
                if rows:
                    print(f"✓ Extracted {len(rows)} sample rows")
                    for i, row in enumerate(rows):
                        if len(row) >= 2:
                            print(f"  {i+1}. {row[1]} - {row[0] if row[0] else 'N/A'}")  # Team name and rank
                    return True
                else:
                    print("✗ No data rows found")
                    return False
            else:
                print("✗ No table body found")
                return False
        else:
            print("✗ No league table found")
            return False
            
    except Exception as e:
        print(f"✗ Premier League table test failed: {e}")
        return False


def test_data_parsing():
    """Test parsing different types of data"""
    print("\nTesting data parsing capabilities...")
    
    try:
        # Test with a simple page
        url = "https://fbref.com/en/comps/"
        
        time.sleep(2)
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find competition links
        competition_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/en/comps/' in href and href.count('/') >= 4:
                text = link.get_text(strip=True)
                if text and len(text) > 3:  # Filter out short/empty texts
                    competition_links.append({
                        'name': text,
                        'url': href
                    })
        
        # Remove duplicates
        seen = set()
        unique_competitions = []
        for comp in competition_links:
            if comp['url'] not in seen:
                seen.add(comp['url'])
                unique_competitions.append(comp)
        
        if unique_competitions:
            print(f"✓ Found {len(unique_competitions)} competitions")
            print("Sample competitions:")
            for comp in unique_competitions[:5]:
                print(f"  - {comp['name']}")
            return True
        else:
            print("✗ No competitions found")
            return False
            
    except Exception as e:
        print(f"✗ Data parsing test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("FBref Simple Connection Test")
    print("=" * 40)
    
    tests = [
        test_fbref_connection,
        test_premier_league_table,
        test_data_parsing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! FBref data collection should work.")
        return True
    else:
        print("✗ Some tests failed. Check your internet connection and FBref availability.")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)
