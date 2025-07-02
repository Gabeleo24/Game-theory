#!/usr/bin/env python3
"""
Enhanced Shapley Analysis Demo

Demonstrates how FBref metrics enhance Shapley value analysis
for comprehensive player contribution assessment.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.soccer_intelligence.analysis.enhanced_shapley_analysis import EnhancedShapleyAnalyzer
import pandas as pd
import numpy as np


def demo_enhanced_shapley_analysis():
    """Demonstrate enhanced Shapley analysis with FBref metrics"""
    print("=== Enhanced Shapley Analysis Demo ===")
    
    analyzer = EnhancedShapleyAnalyzer(cache_dir="data/processed/shapley_enhanced")
    
    try:
        # Analyze Premier League team success
        print("Analyzing Premier League team success factors...")
        results = analyzer.analyze_player_contributions(
            league="Premier League", 
            season=2024, 
            analysis_type="team_success"
        )
        
        if results:
            print("✓ Shapley analysis completed successfully!")
            
            # Display summary
            summary = results.get('summary', {})
            print(f"\nAnalysis Summary:")
            print(f"  Analysis type: {summary.get('analysis_type')}")
            print(f"  Total features: {summary.get('total_features')}")
            print(f"  Total teams: {summary.get('total_teams')}")
            
            # Show feature categories
            feature_categories = summary.get('feature_categories', {})
            print(f"\nFeature Categories:")
            for category, features in feature_categories.items():
                print(f"  {category}: {len(features)} features")
                if len(features) <= 3:
                    print(f"    {', '.join(features)}")
                else:
                    print(f"    {', '.join(features[:3])}...")
            
            # Show results for each target variable
            for target, result in results.items():
                if target in ['summary', 'interpretation']:
                    continue
                
                print(f"\n=== {target.upper()} ANALYSIS ===")
                
                # Model performance
                performance = result.get('model_performance', {})
                print(f"Model Performance:")
                print(f"  R² Score: {performance.get('r2_score', 0):.3f}")
                print(f"  MSE: {performance.get('mse', 0):.3f}")
                
                # Top contributors
                top_contributors = result.get('top_contributors', [])
                print(f"\nTop Contributing Factors:")
                for contributor in top_contributors:
                    print(f"  {contributor['rank']}. {contributor['feature']} "
                          f"({contributor['category']}) - {contributor['contribution']:.3f}")
            
            # Show interpretation
            interpretation = results.get('interpretation', {})
            if interpretation:
                print(f"\n=== INSIGHTS AND INTERPRETATION ===")
                
                key_insights = interpretation.get('key_insights', [])
                if key_insights:
                    print("Key Insights:")
                    for insight in key_insights:
                        print(f"  • {insight}")
                
                tactical_implications = interpretation.get('tactical_implications', [])
                if tactical_implications:
                    print("\nTactical Implications:")
                    for implication in tactical_implications:
                        print(f"  • {implication}")
                
                player_value_insights = interpretation.get('player_value_insights', [])
                if player_value_insights:
                    print("\nPlayer Value Insights:")
                    for insight in player_value_insights:
                        print(f"  • {insight}")
            
            # Save results
            analyzer.save_analysis_results(results, "Premier League", 2024, "team_success")
            print(f"\n✓ Results saved to data/processed/shapley_enhanced/")
        
        else:
            print("✗ Shapley analysis failed")
            
    except Exception as e:
        print(f"✗ Analysis error: {e}")
        import traceback
        traceback.print_exc()


def demo_different_analysis_types():
    """Demonstrate different types of Shapley analysis"""
    print("\n=== Different Analysis Types Demo ===")
    
    analyzer = EnhancedShapleyAnalyzer(cache_dir="data/processed/shapley_enhanced")
    
    analysis_types = [
        ("attacking_output", "Attacking Performance Analysis"),
        ("defensive_solidity", "Defensive Performance Analysis")
    ]
    
    for analysis_type, description in analysis_types:
        print(f"\n{description}:")
        
        try:
            results = analyzer.analyze_player_contributions(
                league="Premier League",
                season=2024,
                analysis_type=analysis_type
            )
            
            if results:
                print(f"✓ {description} completed")
                
                # Show top contributors for first target
                first_target = None
                for target, result in results.items():
                    if target not in ['summary', 'interpretation']:
                        first_target = target
                        break
                
                if first_target:
                    top_contributors = results[first_target].get('top_contributors', [])[:3]
                    print(f"  Top 3 factors for {first_target}:")
                    for contributor in top_contributors:
                        print(f"    {contributor['rank']}. {contributor['feature']} "
                              f"({contributor['category']})")
                
                # Save results
                analyzer.save_analysis_results(results, "Premier League", 2024, analysis_type)
            
            else:
                print(f"✗ {description} failed")
                
        except Exception as e:
            print(f"✗ {description} error: {e}")


def demo_cross_league_comparison():
    """Demonstrate cross-league Shapley analysis comparison"""
    print("\n=== Cross-League Comparison Demo ===")
    
    analyzer = EnhancedShapleyAnalyzer(cache_dir="data/processed/shapley_enhanced")
    
    leagues = ["Premier League", "La Liga"]
    league_results = {}
    
    for league in leagues:
        print(f"\nAnalyzing {league}...")
        
        try:
            results = analyzer.analyze_player_contributions(
                league=league,
                season=2024,
                analysis_type="team_success"
            )
            
            if results:
                league_results[league] = results
                print(f"✓ {league} analysis completed")
            else:
                print(f"✗ {league} analysis failed")
                
        except Exception as e:
            print(f"✗ {league} analysis error: {e}")
    
    # Compare results
    if len(league_results) >= 2:
        print(f"\n=== CROSS-LEAGUE COMPARISON ===")
        
        for target in ['Pts', 'GD']:  # Common targets
            print(f"\nComparison for {target}:")
            
            for league, results in league_results.items():
                if target in results:
                    top_contributor = results[target].get('top_contributors', [{}])[0]
                    if top_contributor:
                        print(f"  {league}: Top factor is {top_contributor.get('feature', 'Unknown')} "
                              f"({top_contributor.get('category', 'Unknown')})")
                    
                    r2_score = results[target].get('model_performance', {}).get('r2_score', 0)
                    print(f"    Model accuracy (R²): {r2_score:.3f}")


def demo_shapley_benefits():
    """Demonstrate the benefits of enhanced Shapley analysis"""
    print("\n=== Enhanced Shapley Analysis Benefits ===")
    
    benefits = [
        {
            'benefit': "Comprehensive Metric Coverage",
            'description': "Uses FBref's detailed statistics including xG, xA, defensive actions, and possession metrics",
            'advantage': "More accurate player contribution assessment than basic goal/assist metrics"
        },
        {
            'benefit': "Multi-dimensional Analysis",
            'description': "Analyzes different aspects: team success, attacking output, defensive solidity",
            'advantage': "Identifies what drives success in different tactical areas"
        },
        {
            'benefit': "Advanced Statistical Foundation",
            'description': "Leverages expected metrics (xG, xA) and advanced performance indicators",
            'advantage': "Distinguishes between luck and skill in player performance"
        },
        {
            'benefit': "Tactical Insights",
            'description': "Provides formation-specific and positional contribution analysis",
            'advantage': "Supports tactical decision-making and formation optimization"
        },
        {
            'benefit': "Player Valuation Support",
            'description': "Quantifies individual player value using comprehensive contribution metrics",
            'advantage': "Enables data-driven player recruitment and contract decisions"
        }
    ]
    
    print("Enhanced Shapley Analysis with FBref Metrics provides:")
    
    for i, benefit in enumerate(benefits, 1):
        print(f"\n{i}. {benefit['benefit']}:")
        print(f"   Description: {benefit['description']}")
        print(f"   Advantage: {benefit['advantage']}")
    
    print(f"\nTotal Enhanced Capabilities: {len(benefits)}")
    print("✓ Comprehensive player contribution analysis now available")


def main():
    """Run all enhanced Shapley analysis demos"""
    print("Enhanced Shapley Analysis with FBref Metrics")
    print("=" * 60)
    print("This demo shows how FBref detailed statistics enhance Shapley value analysis")
    print("for comprehensive player contribution assessment")
    print()
    
    try:
        # Run demos
        demo_enhanced_shapley_analysis()
        demo_different_analysis_types()
        demo_cross_league_comparison()
        demo_shapley_benefits()
        
        print("\n" + "=" * 60)
        print("Enhanced Shapley analysis demo completed!")
        print("The system now provides comprehensive player contribution analysis")
        print("Check data/processed/shapley_enhanced/ for analysis results")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")


if __name__ == "__main__":
    main()
