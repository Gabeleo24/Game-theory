# Implementation Tutorial - Step-by-Step Guide

## Overview

This tutorial provides step-by-step instructions for implementing and extending the Soccer Performance Intelligence System. Each section includes practical examples and code snippets you can study and adapt.

## **Getting Started - Basic Implementation**

### **Step 1: Setting Up Data Collection**

**File**: `scripts/data_collection/custom_collector.py`

```python
#!/usr/bin/env python3
"""
Custom Data Collector Implementation
Study this pattern for creating your own data collectors
"""

import requests
import json
import time
from pathlib import Path

class CustomSoccerDataCollector:
    def __init__(self, api_key, output_dir='data/custom'):
        """
        Initialize your custom collector
        
        Study Points:
        - Configuration management
        - Directory setup
        - Error handling initialization
        """
        self.api_key = api_key
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': 'v3.football.api-sports.io'
        }
        
        # Create output directory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Request tracking
        self.request_count = 0
        self.daily_limit = 1000  # Set your limit
        
        print(f"Custom Collector initialized")
        print(f"Output directory: {self.output_dir}")
        print(f"Daily limit: {self.daily_limit}")
    
    def make_api_request(self, endpoint, params=None, description="API call"):
        """
        Core API request method
        
        Study Points:
        - Rate limiting implementation
        - Error handling strategies
        - Response validation
        - Request tracking
        """
        
        # Check rate limit
        if self.request_count >= self.daily_limit:
            raise Exception(f"Daily limit of {self.daily_limit} requests reached")
        
        # Construct URL
        url = f"{self.base_url}/{endpoint}"
        
        try:
            # Make request
            response = requests.get(url, headers=self.headers, params=params)
            self.request_count += 1
            
            print(f"Request {self.request_count}: {description}")
            
            # Handle response
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if 'response' in data:
                    return data['response']
                else:
                    print(f"Warning: Unexpected response structure for {description}")
                    return data
            
            elif response.status_code == 429:
                print(f"Rate limit hit. Waiting 60 seconds...")
                time.sleep(60)
                return self.make_api_request(endpoint, params, description)
            
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Request failed for {description}: {e}")
            return None
    
    def collect_league_teams(self, league_id, season):
        """
        Collect teams for a specific league and season
        
        Study Points:
        - Data collection patterns
        - File naming conventions
        - JSON serialization
        - Error recovery
        """
        
        print(f"\nCollecting teams for league {league_id}, season {season}")
        
        # Make API request
        teams_data = self.make_api_request(
            'teams',
            {'league': league_id, 'season': season},
            f"League {league_id} teams {season}"
        )
        
        if teams_data:
            # Save to file
            filename = f"league_{league_id}_teams_{season}.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(teams_data, f, indent=2, default=str)
            
            print(f"Saved {len(teams_data)} teams to {filename}")
            return teams_data
        
        return None
    
    def collect_team_statistics(self, team_id, league_id, season):
        """
        Collect detailed statistics for a specific team
        
        Study Points:
        - Parameter validation
        - Nested data structures
        - Data enrichment
        """
        
        print(f"Collecting statistics for team {team_id}")
        
        # Get team statistics
        stats_data = self.make_api_request(
            'teams/statistics',
            {'team': team_id, 'league': league_id, 'season': season},
            f"Team {team_id} statistics"
        )
        
        if stats_data:
            # Enrich with additional data
            enriched_data = {
                'team_id': team_id,
                'league_id': league_id,
                'season': season,
                'collection_timestamp': time.time(),
                'statistics': stats_data
            }
            
            # Save to file
            filename = f"team_{team_id}_stats_{season}.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(enriched_data, f, indent=2, default=str)
            
            print(f"Saved statistics to {filename}")
            return enriched_data
        
        return None

# Usage Example
if __name__ == "__main__":
    # Initialize collector
    collector = CustomSoccerDataCollector(
        api_key="your_api_key_here",
        output_dir="data/custom_collection"
    )
    
    # Collect Premier League teams for 2023
    teams = collector.collect_league_teams(league_id=39, season=2023)
    
    # Collect statistics for first few teams
    if teams:
        for team in teams[:3]:  # First 3 teams only
            team_id = team['team']['id']
            collector.collect_team_statistics(team_id, 39, 2023)
            time.sleep(1)  # Rate limiting
```

### **Step 2: Data Processing and Filtering**

**File**: `scripts/processing/custom_filter.py`

```python
#!/usr/bin/env python3
"""
Custom Data Filtering Implementation
Study this pattern for processing and filtering collected data
"""

import json
from pathlib import Path
from collections import defaultdict

class CustomDataFilter:
    def __init__(self, input_dir='data/custom', output_dir='data/filtered'):
        """
        Initialize data filter
        
        Study Points:
        - Directory management
        - File discovery patterns
        - Output organization
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Criteria for filtering
        self.filter_criteria = {
            'min_matches_played': 10,
            'target_leagues': [39, 140, 135, 78, 61],  # Top 5 leagues
            'performance_threshold': 0.5  # Win rate threshold
        }
    
    def load_data_files(self, pattern="*.json"):
        """
        Load all JSON files matching pattern
        
        Study Points:
        - File pattern matching
        - Bulk data loading
        - Error handling for corrupted files
        """
        
        data_files = {}
        
        for file_path in self.input_dir.glob(pattern):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data_files[file_path.name] = data
                    print(f"Loaded {file_path.name}")
            
            except Exception as e:
                print(f"Error loading {file_path.name}: {e}")
        
        print(f"Loaded {len(data_files)} data files")
        return data_files
    
    def filter_teams_by_performance(self, teams_data):
        """
        Filter teams based on performance criteria
        
        Study Points:
        - Multi-criteria filtering
        - Performance metric calculation
        - Data validation
        """
        
        filtered_teams = []
        
        for team_data in teams_data:
            if self.meets_performance_criteria(team_data):
                filtered_teams.append(team_data)
        
        print(f"Filtered {len(filtered_teams)} teams from {len(teams_data)} total")
        return filtered_teams
    
    def meets_performance_criteria(self, team_data):
        """
        Check if team meets filtering criteria
        
        Study Points:
        - Criteria evaluation logic
        - Safe data access patterns
        - Boolean logic implementation
        """
        
        try:
            # Extract team statistics
            stats = team_data.get('statistics', {})
            
            # Check matches played
            matches_played = stats.get('fixtures', {}).get('played', {}).get('total', 0)
            if matches_played < self.filter_criteria['min_matches_played']:
                return False
            
            # Check league
            league_id = team_data.get('league_id')
            if league_id not in self.filter_criteria['target_leagues']:
                return False
            
            # Check performance (win rate)
            wins = stats.get('fixtures', {}).get('wins', {}).get('total', 0)
            win_rate = wins / matches_played if matches_played > 0 else 0
            
            if win_rate < self.filter_criteria['performance_threshold']:
                return False
            
            return True
            
        except Exception as e:
            print(f"Error evaluating criteria: {e}")
            return False
    
    def create_focused_dataset(self, filtered_data):
        """
        Create focused dataset with enhanced structure
        
        Study Points:
        - Data restructuring
        - Metadata addition
        - Summary statistics
        """
        
        focused_dataset = {
            'metadata': {
                'creation_timestamp': time.time(),
                'filter_criteria': self.filter_criteria,
                'total_teams': len(filtered_data),
                'data_sources': list(self.input_dir.glob("*.json"))
            },
            'teams': filtered_data,
            'summary_statistics': self.calculate_summary_stats(filtered_data)
        }
        
        # Save focused dataset
        output_file = self.output_dir / 'focused_dataset.json'
        with open(output_file, 'w') as f:
            json.dump(focused_dataset, f, indent=2, default=str)
        
        print(f"Created focused dataset: {output_file}")
        return focused_dataset
    
    def calculate_summary_stats(self, teams_data):
        """
        Calculate summary statistics for the dataset
        
        Study Points:
        - Aggregation patterns
        - Statistical calculations
        - Data summarization
        """
        
        stats = {
            'total_teams': len(teams_data),
            'leagues_represented': set(),
            'avg_matches_played': 0,
            'avg_win_rate': 0,
            'performance_distribution': defaultdict(int)
        }
        
        total_matches = 0
        total_win_rate = 0
        
        for team in teams_data:
            # League tracking
            league_id = team.get('league_id')
            if league_id:
                stats['leagues_represented'].add(league_id)
            
            # Performance calculations
            team_stats = team.get('statistics', {})
            matches = team_stats.get('fixtures', {}).get('played', {}).get('total', 0)
            wins = team_stats.get('fixtures', {}).get('wins', {}).get('total', 0)
            
            total_matches += matches
            win_rate = wins / matches if matches > 0 else 0
            total_win_rate += win_rate
            
            # Performance distribution
            if win_rate >= 0.7:
                stats['performance_distribution']['high'] += 1
            elif win_rate >= 0.5:
                stats['performance_distribution']['medium'] += 1
            else:
                stats['performance_distribution']['low'] += 1
        
        # Calculate averages
        if len(teams_data) > 0:
            stats['avg_matches_played'] = total_matches / len(teams_data)
            stats['avg_win_rate'] = total_win_rate / len(teams_data)
        
        # Convert set to list for JSON serialization
        stats['leagues_represented'] = list(stats['leagues_represented'])
        
        return stats

# Usage Example
if __name__ == "__main__":
    import time
    
    # Initialize filter
    filter_system = CustomDataFilter(
        input_dir="data/custom_collection",
        output_dir="data/custom_filtered"
    )
    
    # Load all data files
    all_data = filter_system.load_data_files("team_*_stats_*.json")
    
    # Extract team data from files
    teams_data = []
    for filename, data in all_data.items():
        teams_data.append(data)
    
    # Filter teams by performance
    filtered_teams = filter_system.filter_teams_by_performance(teams_data)
    
    # Create focused dataset
    focused_dataset = filter_system.create_focused_dataset(filtered_teams)
    
    print(f"\nDataset Summary:")
    print(f"Total teams: {focused_dataset['summary_statistics']['total_teams']}")
    print(f"Leagues: {focused_dataset['summary_statistics']['leagues_represented']}")
    print(f"Avg win rate: {focused_dataset['summary_statistics']['avg_win_rate']:.2f}")
```

### **Step 3: Analysis Implementation**

**File**: `scripts/analysis/custom_analysis.py`

```python
#!/usr/bin/env python3
"""
Custom Analysis Implementation
Study this pattern for implementing your own analytical methods
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

class CustomSoccerAnalyzer:
    def __init__(self, data_dir='data/filtered'):
        """
        Initialize analyzer
        
        Study Points:
        - Analysis framework setup
        - Data loading strategies
        - Configuration management
        """
        self.data_dir = Path(data_dir)
        self.results_dir = Path('results/custom_analysis')
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Load focused dataset
        self.dataset = self.load_dataset()
        
    def load_dataset(self):
        """Load the focused dataset for analysis"""
        dataset_file = self.data_dir / 'focused_dataset.json'
        
        if dataset_file.exists():
            with open(dataset_file, 'r') as f:
                return json.load(f)
        else:
            print(f"Dataset not found: {dataset_file}")
            return None
    
    def analyze_team_performance(self):
        """
        Analyze team performance patterns
        
        Study Points:
        - Performance metric extraction
        - Statistical analysis
        - Comparative analysis
        """
        
        if not self.dataset:
            return None
        
        teams = self.dataset['teams']
        performance_data = []
        
        for team in teams:
            team_stats = team.get('statistics', {})
            fixtures = team_stats.get('fixtures', {})
            
            # Extract key metrics
            played = fixtures.get('played', {}).get('total', 0)
            wins = fixtures.get('wins', {}).get('total', 0)
            draws = fixtures.get('draws', {}).get('total', 0)
            losses = fixtures.get('losses', {}).get('total', 0)
            
            goals = team_stats.get('goals', {})
            goals_for = goals.get('for', {}).get('total', {}).get('total', 0)
            goals_against = goals.get('against', {}).get('total', {}).get('total', 0)
            
            # Calculate derived metrics
            win_rate = wins / played if played > 0 else 0
            goal_difference = goals_for - goals_against
            points = (wins * 3) + draws
            points_per_game = points / played if played > 0 else 0
            
            performance_data.append({
                'team_id': team.get('team_id'),
                'league_id': team.get('league_id'),
                'played': played,
                'wins': wins,
                'draws': draws,
                'losses': losses,
                'goals_for': goals_for,
                'goals_against': goals_against,
                'win_rate': win_rate,
                'goal_difference': goal_difference,
                'points': points,
                'points_per_game': points_per_game
            })
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(performance_data)
        
        # Perform statistical analysis
        analysis_results = {
            'descriptive_stats': df.describe().to_dict(),
            'correlation_matrix': df.corr().to_dict(),
            'league_comparison': self.compare_leagues(df),
            'performance_clusters': self.identify_performance_clusters(df)
        }
        
        # Save results
        results_file = self.results_dir / 'team_performance_analysis.json'
        with open(results_file, 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        print(f"Performance analysis saved to {results_file}")
        return analysis_results
    
    def compare_leagues(self, df):
        """
        Compare performance across different leagues
        
        Study Points:
        - Groupby operations
        - Comparative statistics
        - League-level analysis
        """
        
        league_stats = df.groupby('league_id').agg({
            'win_rate': ['mean', 'std', 'count'],
            'goal_difference': ['mean', 'std'],
            'points_per_game': ['mean', 'std']
        }).round(3)
        
        return league_stats.to_dict()
    
    def identify_performance_clusters(self, df):
        """
        Identify performance clusters using simple thresholds
        
        Study Points:
        - Clustering logic
        - Performance categorization
        - Data segmentation
        """
        
        clusters = {
            'elite': df[df['win_rate'] >= 0.7],
            'good': df[(df['win_rate'] >= 0.5) & (df['win_rate'] < 0.7)],
            'average': df[(df['win_rate'] >= 0.3) & (df['win_rate'] < 0.5)],
            'poor': df[df['win_rate'] < 0.3]
        }
        
        cluster_summary = {}
        for cluster_name, cluster_data in clusters.items():
            cluster_summary[cluster_name] = {
                'count': len(cluster_data),
                'avg_win_rate': cluster_data['win_rate'].mean(),
                'avg_goal_difference': cluster_data['goal_difference'].mean(),
                'team_ids': cluster_data['team_id'].tolist()
            }
        
        return cluster_summary

# Usage Example
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = CustomSoccerAnalyzer(data_dir="data/custom_filtered")
    
    # Run performance analysis
    results = analyzer.analyze_team_performance()
    
    if results:
        print("\nAnalysis Results Summary:")
        print(f"Leagues analyzed: {len(results['league_comparison'])}")
        print(f"Performance clusters identified: {len(results['performance_clusters'])}")
        
        # Print cluster summary
        for cluster_name, cluster_info in results['performance_clusters'].items():
            print(f"{cluster_name.title()}: {cluster_info['count']} teams, "
                  f"avg win rate: {cluster_info['avg_win_rate']:.2f}")
```

This implementation tutorial provides practical, step-by-step examples that you can study, modify, and extend for your own research projects. Each code section includes detailed comments explaining the techniques and methodologies used.
