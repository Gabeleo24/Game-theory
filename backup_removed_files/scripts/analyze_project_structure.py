#!/usr/bin/env python3
"""
Project Structure Analysis Script
Analyzes the current project structure to identify files that can be safely removed
after Champions League focus implementation.
"""

import json
import os
from pathlib import Path
from collections import defaultdict
import sys

class ProjectStructureAnalyzer:
    """Analyzes project structure for cleanup recommendations."""
    
    def __init__(self):
        """Initialize the analyzer."""
        self.project_root = Path('.')
        self.data_processed = Path('data/processed')
        self.data_focused = Path('data/focused')
        self.scripts_dir = Path('scripts')
        
        # Load core teams for reference
        self.core_teams = self._load_core_teams()
        self.team_mapping = self._load_team_mapping()
        
    def _load_core_teams(self):
        """Load core Champions League teams."""
        try:
            core_teams_file = self.data_focused / 'core_champions_league_teams.json'
            with open(core_teams_file, 'r') as f:
                data = json.load(f)
            return {team['id']: team['name'] for team in data['teams']}
        except Exception as e:
            print(f"Warning: Could not load core teams: {e}")
            return {}
    
    def _load_team_mapping(self):
        """Load team to league mapping."""
        try:
            mapping_file = self.data_focused / 'team_league_mapping.json'
            with open(mapping_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load team mapping: {e}")
            return {}
    
    def analyze_data_files(self):
        """Analyze data files to identify redundant ones."""
        print("Analyzing data files in data/processed/...")
        
        analysis = {
            'champions_league_related': [],
            'core_team_leagues': [],
            'other_leagues': [],
            'transfer_injury_data': [],
            'cup_competitions': [],
            'non_essential': [],
            'total_files': 0,
            'total_size_mb': 0
        }
        
        if not self.data_processed.exists():
            print("data/processed/ directory not found")
            return analysis
        
        for file_path in self.data_processed.glob('*.json'):
            file_name = file_path.name
            file_size = file_path.stat().st_size / (1024 * 1024)  # MB
            
            analysis['total_files'] += 1
            analysis['total_size_mb'] += file_size
            
            # Categorize files
            if 'champions_league' in file_name:
                analysis['champions_league_related'].append({
                    'file': file_name,
                    'size_mb': round(file_size, 2),
                    'essential': True
                })
            elif any(league in file_name for league in ['premier_league', 'la_liga', 'serie_a', 'bundesliga', 'ligue_1']):
                analysis['core_team_leagues'].append({
                    'file': file_name,
                    'size_mb': round(file_size, 2),
                    'essential': True
                })
            elif any(comp in file_name for comp in ['europa_league', 'fa_cup', 'copa_del_rey', 'coppa_italia', 'dfb_pokal']):
                analysis['cup_competitions'].append({
                    'file': file_name,
                    'size_mb': round(file_size, 2),
                    'essential': True  # Keep for multi-competition context
                })
            elif any(data_type in file_name for data_type in ['transfers', 'injuries']):
                analysis['transfer_injury_data'].append({
                    'file': file_name,
                    'size_mb': round(file_size, 2),
                    'essential': self._is_transfer_injury_essential(file_name)
                })
            else:
                # Other leagues/competitions not directly related to core teams
                analysis['non_essential'].append({
                    'file': file_name,
                    'size_mb': round(file_size, 2),
                    'essential': False
                })
        
        return analysis
    
    def _is_transfer_injury_essential(self, file_name):
        """Check if transfer/injury file is essential for core teams."""
        # Check if file contains core team IDs
        essential_patterns = [
            'team_50_', 'team_40_', 'team_49_', 'team_529_', 'team_541_',  # Major teams
            'team_157_', 'team_85_', 'team_496_', 'team_530_', 'team_33_',
            'league_39_', 'league_140_', 'league_135_', 'league_78_', 'league_61_'  # Major leagues
        ]
        return any(pattern in file_name for pattern in essential_patterns)
    
    def analyze_scripts(self):
        """Analyze Python scripts to identify temporary/redundant ones."""
        print("Analyzing Python scripts...")
        
        analysis = {
            'core_scripts': [],
            'analysis_scripts': [],
            'temporary_scripts': [],
            'debug_scripts': [],
            'total_scripts': 0
        }
        
        for script_dir in ['scripts/analysis', 'scripts/data_collection', 'scripts/configuration', 'scripts/maintenance']:
            script_path = Path(script_dir)
            if not script_path.exists():
                continue
                
            for file_path in script_path.glob('*.py'):
                file_name = file_path.name
                analysis['total_scripts'] += 1
                
                # Categorize scripts
                if any(temp in file_name for temp in ['debug', 'test', 'temp', 'analyze_champions', 'debug_cl']):
                    analysis['debug_scripts'].append({
                        'file': str(file_path),
                        'essential': False,
                        'reason': 'Debug/temporary script'
                    })
                elif file_name in ['clean_data_collection.py', 'update_system_config.py']:
                    analysis['core_scripts'].append({
                        'file': str(file_path),
                        'essential': True,
                        'reason': 'Core system functionality'
                    })
                elif 'filter' in file_name or 'analysis' in file_name:
                    analysis['analysis_scripts'].append({
                        'file': str(file_path),
                        'essential': True,
                        'reason': 'Analysis functionality'
                    })
                else:
                    analysis['temporary_scripts'].append({
                        'file': str(file_path),
                        'essential': False,
                        'reason': 'May be temporary'
                    })
        
        return analysis
    
    def check_focused_dataset_integrity(self):
        """Check integrity of the focused dataset."""
        print("Checking focused dataset integrity...")
        
        integrity_check = {
            'core_files_present': True,
            'missing_files': [],
            'file_count': 0,
            'total_size_mb': 0,
            'essential_files': [
                'core_champions_league_teams.json',
                'team_league_mapping.json',
                'champions_league_focus_report.json'
            ]
        }
        
        if not self.data_focused.exists():
            integrity_check['core_files_present'] = False
            integrity_check['missing_files'].append('data/focused/ directory')
            return integrity_check
        
        # Check essential files
        for essential_file in integrity_check['essential_files']:
            file_path = self.data_focused / essential_file
            if not file_path.exists():
                integrity_check['core_files_present'] = False
                integrity_check['missing_files'].append(essential_file)
        
        # Count all files
        for file_path in self.data_focused.glob('*.json'):
            integrity_check['file_count'] += 1
            integrity_check['total_size_mb'] += file_path.stat().st_size / (1024 * 1024)
        
        integrity_check['total_size_mb'] = round(integrity_check['total_size_mb'], 2)
        
        return integrity_check
    
    def generate_cleanup_recommendations(self):
        """Generate cleanup recommendations based on analysis."""
        print("Generating cleanup recommendations...")
        
        data_analysis = self.analyze_data_files()
        script_analysis = self.analyze_scripts()
        integrity_check = self.check_focused_dataset_integrity()
        
        recommendations = {
            'data_files': {
                'safe_to_remove': [],
                'keep_essential': [],
                'potential_savings_mb': 0
            },
            'scripts': {
                'safe_to_remove': [],
                'keep_essential': []
            },
            'integrity_status': integrity_check,
            'summary': {
                'total_files_analyzed': data_analysis['total_files'] + script_analysis['total_scripts'],
                'files_recommended_for_removal': 0,
                'estimated_space_savings_mb': 0
            }
        }
        
        # Data file recommendations
        for category, files in data_analysis.items():
            if isinstance(files, list):
                for file_info in files:
                    if isinstance(file_info, dict) and not file_info.get('essential', True):
                        recommendations['data_files']['safe_to_remove'].append(file_info)
                        recommendations['data_files']['potential_savings_mb'] += file_info['size_mb']
                    elif isinstance(file_info, dict):
                        recommendations['data_files']['keep_essential'].append(file_info)
        
        # Script recommendations
        for category, scripts in script_analysis.items():
            if isinstance(scripts, list):
                for script_info in scripts:
                    if not script_info.get('essential', True):
                        recommendations['scripts']['safe_to_remove'].append(script_info)
                    else:
                        recommendations['scripts']['keep_essential'].append(script_info)
        
        # Update summary
        recommendations['summary']['files_recommended_for_removal'] = (
            len(recommendations['data_files']['safe_to_remove']) +
            len(recommendations['scripts']['safe_to_remove'])
        )
        recommendations['summary']['estimated_space_savings_mb'] = round(
            recommendations['data_files']['potential_savings_mb'], 2
        )
        
        return recommendations
    
    def save_analysis_report(self, recommendations):
        """Save the analysis report."""
        report_file = Path('data/analysis/project_cleanup_analysis.json')
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(recommendations, f, indent=2)
        
        print(f"Analysis report saved to: {report_file}")
        return report_file

def main():
    """Main execution function."""
    print("PROJECT STRUCTURE ANALYSIS")
    print("=" * 60)
    
    analyzer = ProjectStructureAnalyzer()
    
    try:
        # Generate recommendations
        recommendations = analyzer.generate_cleanup_recommendations()
        
        # Save report
        report_file = analyzer.save_analysis_report(recommendations)
        
        # Print summary
        print("\n" + "=" * 60)
        print("ANALYSIS SUMMARY")
        print("=" * 60)
        
        print(f"Total files analyzed: {recommendations['summary']['total_files_analyzed']}")
        print(f"Files recommended for removal: {recommendations['summary']['files_recommended_for_removal']}")
        print(f"Estimated space savings: {recommendations['summary']['estimated_space_savings_mb']} MB")
        
        print(f"\nFocused dataset integrity: {'✅ GOOD' if recommendations['integrity_status']['core_files_present'] else '❌ ISSUES'}")
        print(f"Focused dataset files: {recommendations['integrity_status']['file_count']}")
        print(f"Focused dataset size: {recommendations['integrity_status']['total_size_mb']} MB")
        
        if recommendations['integrity_status']['missing_files']:
            print(f"Missing files: {', '.join(recommendations['integrity_status']['missing_files'])}")
        
        print(f"\nDetailed analysis saved to: {report_file}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
