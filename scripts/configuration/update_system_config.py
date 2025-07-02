#!/usr/bin/env python3
"""
System Configuration Update Script
Updates the Soccer Performance Intelligence System configuration to focus on
the Champions League teams while maintaining multi-competition context.
"""

import json
import yaml
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.append('src')

class SystemConfigUpdater:
    """Updates system configuration for Champions League focus."""
    
    def __init__(self):
        """Initialize the configuration updater."""
        self.config_dir = Path('config')
        self.data_dir = Path('data/focused')
        self.src_dir = Path('src')
        
        # Load core teams data
        self.core_teams = self._load_core_teams()
        self.team_mapping = self._load_team_mapping()
        
    def _load_core_teams(self):
        """Load core Champions League teams data."""
        core_teams_file = self.data_dir / 'core_champions_league_teams.json'
        
        if not core_teams_file.exists():
            raise FileNotFoundError(f"Core teams file not found: {core_teams_file}")
        
        with open(core_teams_file, 'r') as f:
            data = json.load(f)
        
        return data['teams']
    
    def _load_team_mapping(self):
        """Load team to league mapping data."""
        mapping_file = self.data_dir / 'team_league_mapping.json'
        
        if not mapping_file.exists():
            raise FileNotFoundError(f"Team mapping file not found: {mapping_file}")
        
        with open(mapping_file, 'r') as f:
            return json.load(f)
    
    def create_focused_config(self):
        """Create a focused configuration file for Champions League analysis."""
        print("Creating focused configuration for Champions League teams...")
        
        # Create focused configuration
        focused_config = {
            'project': {
                'name': 'Soccer Performance Intelligence System - Champions League Focus',
                'version': '2.0.0',
                'description': 'Focused analysis of Champions League teams across all competitions',
                'scope': 'Champions League teams multi-competition analysis'
            },
            'data': {
                'source_directory': 'data/focused',
                'core_teams_count': len(self.core_teams),
                'mapped_teams_count': len(self.team_mapping),
                'focus_competitions': [
                    'UEFA Champions League',
                    'Premier League',
                    'La Liga',
                    'Serie A',
                    'Bundesliga',
                    'Ligue 1',
                    'UEFA Europa League',
                    'Domestic Cups (FA Cup, Copa del Rey, Coppa Italia, DFB-Pokal)'
                ]
            },
            'analysis': {
                'priority_teams': [team['id'] for team in self.core_teams[:32]],  # Top 32 by frequency
                'league_distribution': {
                    'premier_league': 7,
                    'la_liga': 7,
                    'serie_a': 6,
                    'bundesliga': 8,
                    'ligue_1': 6
                },
                'analysis_types': [
                    'Shapley Value Analysis',
                    'Tactical Formation Analysis',
                    'Performance Metrics',
                    'Multi-Competition Performance',
                    'Cross-League Comparison'
                ]
            },
            'system': {
                'focused_mode': True,
                'data_filter': 'champions_league_teams',
                'multi_competition_context': True,
                'cache_strategy': 'focused_teams_only'
            }
        }
        
        # Save focused configuration
        config_file = self.config_dir / 'focused_config.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(focused_config, f, default_flow_style=False, indent=2)
        
        print(f"Focused configuration saved to: {config_file}")
        return focused_config
    
    def update_data_collection_config(self):
        """Update data collection configuration to prioritize core teams."""
        print("Updating data collection configuration...")
        
        # Create priority team list
        priority_teams = {
            'high_priority': [team['id'] for team in self.core_teams[:20]],  # Top 20 most frequent
            'medium_priority': [team['id'] for team in self.core_teams[20:40]],  # Next 20
            'low_priority': [team['id'] for team in self.core_teams[40:]]  # Remaining teams
        }
        
        # Create league-specific configurations
        league_configs = {}
        for team_id, mapping in self.team_mapping.items():
            league_name = mapping['league_name'].lower().replace(' ', '_')
            if league_name not in league_configs:
                league_configs[league_name] = {
                    'league_id': mapping['league_id'],
                    'priority_teams': []
                }
            league_configs[league_name]['priority_teams'].append(int(team_id))
        
        data_collection_config = {
            'focus_mode': {
                'enabled': True,
                'description': 'Focused data collection for Champions League teams',
                'priority_teams': priority_teams,
                'league_configurations': league_configs
            },
            'competitions': {
                'champions_league': {
                    'priority': 'highest',
                    'collect_all_data': True,
                    'years': [2019, 2020, 2021, 2022, 2023, 2024]
                },
                'domestic_leagues': {
                    'priority': 'high',
                    'filter_by_teams': True,
                    'leagues': list(league_configs.keys())
                },
                'europa_league': {
                    'priority': 'medium',
                    'filter_by_teams': True
                },
                'domestic_cups': {
                    'priority': 'medium',
                    'filter_by_teams': True
                }
            },
            'data_types': {
                'matches': {'priority': 'highest', 'include_detailed_stats': True},
                'teams': {'priority': 'highest', 'include_all_seasons': True},
                'players': {'priority': 'high', 'focus_on_core_teams': True},
                'standings': {'priority': 'high', 'all_competitions': True},
                'transfers': {'priority': 'medium', 'core_teams_only': True},
                'injuries': {'priority': 'medium', 'core_teams_only': True}
            }
        }
        
        # Save data collection configuration
        collection_config_file = self.config_dir / 'data_collection_focused.yaml'
        with open(collection_config_file, 'w') as f:
            yaml.dump(data_collection_config, f, default_flow_style=False, indent=2)
        
        print(f"Data collection configuration saved to: {collection_config_file}")
        return data_collection_config
    
    def create_analysis_templates(self):
        """Create analysis templates for focused Champions League research."""
        print("Creating analysis templates...")
        
        templates = {
            'shapley_analysis': {
                'description': 'Shapley Value Analysis for Champions League teams',
                'focus_teams': [team['id'] for team in self.core_teams[:32]],
                'competitions': ['champions_league', 'domestic_league'],
                'metrics': ['goals', 'assists', 'defensive_actions', 'possession_contribution'],
                'output_format': 'comparative_analysis'
            },
            'tactical_analysis': {
                'description': 'Formation and tactical analysis across competitions',
                'focus_teams': [team['id'] for team in self.core_teams[:20]],
                'analysis_types': ['formation_effectiveness', 'tactical_flexibility', 'competition_adaptation'],
                'comparison_scope': 'champions_league_vs_domestic'
            },
            'performance_intelligence': {
                'description': 'Multi-competition performance intelligence',
                'scope': 'all_core_teams',
                'metrics': ['consistency_across_competitions', 'peak_performance_periods', 'tactical_evolution'],
                'rag_queries': [
                    'formation_effectiveness_by_competition',
                    'player_contribution_analysis',
                    'tactical_adaptation_strategies'
                ]
            }
        }
        
        # Save analysis templates
        templates_file = self.config_dir / 'analysis_templates.yaml'
        with open(templates_file, 'w') as f:
            yaml.dump(templates, f, default_flow_style=False, indent=2)
        
        print(f"Analysis templates saved to: {templates_file}")
        return templates
    
    def update_system_paths(self):
        """Update system paths to use focused dataset."""
        print("Updating system paths configuration...")
        
        paths_config = {
            'data': {
                'focused_dataset': 'data/focused',
                'original_dataset': 'data/processed',
                'analysis_output': 'data/analysis',
                'reports': 'data/reports'
            },
            'core_files': {
                'champions_league_teams': 'data/focused/core_champions_league_teams.json',
                'team_league_mapping': 'data/focused/team_league_mapping.json',
                'focus_report': 'data/focused/champions_league_focus_report.json'
            },
            'analysis': {
                'shapley_output': 'data/analysis/shapley',
                'tactical_output': 'data/analysis/tactical',
                'rag_output': 'data/analysis/rag'
            }
        }
        
        # Create directories if they don't exist
        for category, paths in paths_config.items():
            if isinstance(paths, dict):
                for path_name, path_value in paths.items():
                    if path_value.startswith('data/') and not path_value.endswith('.json'):
                        Path(path_value).mkdir(parents=True, exist_ok=True)
        
        # Save paths configuration
        paths_file = self.config_dir / 'system_paths.yaml'
        with open(paths_file, 'w') as f:
            yaml.dump(paths_config, f, default_flow_style=False, indent=2)
        
        print(f"System paths configuration saved to: {paths_file}")
        return paths_config
    
    def generate_configuration_summary(self):
        """Generate a comprehensive configuration summary."""
        print("Generating configuration summary...")
        
        summary = {
            'configuration_update': {
                'timestamp': pd.Timestamp.now().isoformat(),
                'focus_scope': 'Champions League teams multi-competition analysis',
                'core_teams_count': len(self.core_teams),
                'mapped_teams_count': len(self.team_mapping)
            },
            'system_changes': {
                'data_source': 'Switched to data/focused directory',
                'team_filter': 'Applied Champions League team filter',
                'competition_scope': 'Multi-competition context maintained',
                'analysis_focus': 'Prioritized core Champions League teams'
            },
            'next_steps': [
                'Run focused Shapley Value analysis on core teams',
                'Perform tactical analysis across competitions',
                'Generate performance intelligence reports',
                'Conduct cross-league comparative studies',
                'Implement RAG-powered formation analysis'
            ],
            'available_analyses': {
                'teams_ready': len(self.core_teams),
                'competitions_covered': 8,
                'years_of_data': 5,
                'analysis_types': 5
            }
        }
        
        # Save configuration summary
        summary_file = self.config_dir / 'configuration_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Configuration summary saved to: {summary_file}")
        return summary

def main():
    """Main execution function."""
    print("SYSTEM CONFIGURATION UPDATE")
    print("=" * 60)
    print("Updating Soccer Performance Intelligence System for Champions League focus")
    
    try:
        updater = SystemConfigUpdater()
        
        # Create focused configuration
        focused_config = updater.create_focused_config()
        
        # Update data collection configuration
        collection_config = updater.update_data_collection_config()
        
        # Create analysis templates
        templates = updater.create_analysis_templates()
        
        # Update system paths
        paths_config = updater.update_system_paths()
        
        # Generate summary
        summary = updater.generate_configuration_summary()
        
        print("\n" + "=" * 60)
        print("CONFIGURATION UPDATE COMPLETE")
        print("=" * 60)
        print(f"Core teams configured: {summary['configuration_update']['core_teams_count']}")
        print(f"Teams mapped to leagues: {summary['configuration_update']['mapped_teams_count']}")
        print(f"System focus: {summary['configuration_update']['focus_scope']}")
        
        print("\nConfiguration files created:")
        print("   - config/focused_config.yaml")
        print("   - config/data_collection_focused.yaml")
        print("   - config/analysis_templates.yaml")
        print("   - config/system_paths.yaml")
        print("   - config/configuration_summary.json")
        
        print("\nSystem is now configured for Champions League focused analysis!")
        
    except Exception as e:
        print(f"Error during configuration update: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import pandas as pd
    exit(main())
