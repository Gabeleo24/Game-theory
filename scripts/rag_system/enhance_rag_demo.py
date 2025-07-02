#!/usr/bin/env python3
"""
Enhanced RAG System Demo

Demonstrates how FBref statistical content enhances the RAG system
for richer soccer intelligence queries.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.soccer_intelligence.rag_system.fbref_rag_enhancer import FBrefRAGEnhancer
import json


def demo_rag_enhancement():
    """Demonstrate RAG system enhancement with FBref data"""
    print("=== RAG System Enhancement Demo ===")
    
    enhancer = FBrefRAGEnhancer(cache_dir="data/processed/rag_enhanced")
    
    try:
        # Enhance RAG knowledge base
        print("Enhancing RAG knowledge base with FBref statistical content...")
        enhanced_content = enhancer.enhance_rag_knowledge_base(leagues=["Premier League", "La Liga"])
        
        if enhanced_content:
            print("✓ RAG enhancement successful!")
            
            # Display content summary
            print("\nEnhanced Content Summary:")
            for content_type, items in enhanced_content.items():
                print(f"  {content_type}: {len(items)} items")
            
            # Show sample content
            print("\n=== Sample Enhanced Content ===")
            
            # Player profile sample
            if enhanced_content['player_profiles']:
                player_sample = enhanced_content['player_profiles'][0]
                print(f"\nPlayer Profile Sample:")
                print(f"Player: {player_sample.get('player_name')} ({player_sample.get('team')})")
                print(f"League: {player_sample.get('league')}")
                print("Content preview:")
                print(player_sample['content'][:300] + "...")
            
            # Team analysis sample
            if enhanced_content['team_analyses']:
                team_sample = enhanced_content['team_analyses'][0]
                print(f"\nTeam Analysis Sample:")
                print(f"Team: {team_sample.get('team_name')}")
                print(f"League: {team_sample.get('league')}")
                print("Content preview:")
                print(team_sample['content'][:300] + "...")
            
            # Tactical insights sample
            if enhanced_content['tactical_insights']:
                tactical_sample = enhanced_content['tactical_insights'][0]
                print(f"\nTactical Insights Sample:")
                print(f"League: {tactical_sample.get('league')}")
                print("Content preview:")
                print(tactical_sample['content'][:300] + "...")
        
        else:
            print("✗ RAG enhancement failed")
            
    except Exception as e:
        print(f"✗ Enhancement error: {e}")
    finally:
        enhancer.close()


def demo_content_types():
    """Demonstrate different types of enhanced content"""
    print("\n=== Enhanced Content Types Demo ===")
    
    enhancer = FBrefRAGEnhancer(cache_dir="data/processed/rag_enhanced")
    
    try:
        # Load existing enhanced content
        print("Loading enhanced RAG content...")
        content = enhancer.load_enhanced_content()
        
        if content:
            print("✓ Enhanced content loaded successfully")
            
            # Analyze content types
            print("\nContent Type Analysis:")
            
            for content_type, items in content.items():
                if items:
                    print(f"\n{content_type.upper()}:")
                    print(f"  Total items: {len(items)}")
                    
                    # Show unique leagues covered
                    leagues = set(item.get('league', 'Unknown') for item in items)
                    print(f"  Leagues covered: {', '.join(leagues)}")
                    
                    # Show sample metadata
                    if items[0].get('metadata'):
                        print(f"  Sample metadata keys: {list(items[0]['metadata'].keys())}")
                    
                    # Content length analysis
                    content_lengths = [len(item['content']) for item in items]
                    avg_length = sum(content_lengths) / len(content_lengths)
                    print(f"  Average content length: {avg_length:.0f} characters")
        
        else:
            print("✗ No enhanced content found. Run enhancement first.")
            
    except Exception as e:
        print(f"✗ Content analysis error: {e}")
    finally:
        enhancer.close()


def demo_query_scenarios():
    """Demonstrate how enhanced content supports different query scenarios"""
    print("\n=== Query Scenario Support Demo ===")
    
    enhancer = FBrefRAGEnhancer(cache_dir="data/processed/rag_enhanced")
    
    try:
        content = enhancer.load_enhanced_content()
        
        if not content:
            print("✗ No enhanced content available")
            return
        
        # Simulate different query scenarios
        query_scenarios = [
            {
                'query': "Tell me about Mohamed Salah's performance this season",
                'relevant_content': 'player_profiles',
                'description': "Player-specific performance queries"
            },
            {
                'query': "How is Liverpool performing tactically this season?",
                'relevant_content': 'team_analyses',
                'description': "Team tactical analysis queries"
            },
            {
                'query': "What are the main tactical trends in the Premier League?",
                'relevant_content': 'tactical_insights',
                'description': "League-wide tactical pattern queries"
            },
            {
                'query': "Compare the top scorers in La Liga vs Premier League",
                'relevant_content': 'performance_comparisons',
                'description': "Cross-league performance comparison queries"
            },
            {
                'query': "What are the key statistics for this season?",
                'relevant_content': 'statistical_summaries',
                'description': "Statistical overview and summary queries"
            }
        ]
        
        print("Enhanced content supports these query scenarios:")
        
        for scenario in query_scenarios:
            content_type = scenario['relevant_content']
            available_items = len(content.get(content_type, []))
            
            print(f"\n{scenario['description']}:")
            print(f"  Example query: \"{scenario['query']}\"")
            print(f"  Relevant content type: {content_type}")
            print(f"  Available content items: {available_items}")
            
            if available_items > 0:
                # Show how content would be used
                sample_item = content[content_type][0]
                print(f"  Sample content source: {sample_item.get('league', 'Unknown')} data")
                print(f"  Content length: {len(sample_item['content'])} characters")
                print("  ✓ Query can be answered with enhanced content")
            else:
                print("  ✗ No content available for this query type")
    
    except Exception as e:
        print(f"✗ Query scenario analysis error: {e}")
    finally:
        enhancer.close()


def demo_rag_integration_benefits():
    """Demonstrate the benefits of FBref integration for RAG"""
    print("\n=== RAG Integration Benefits Demo ===")
    
    print("Benefits of FBref Integration for RAG System:")
    
    benefits = [
        {
            'benefit': "Rich Statistical Context",
            'description': "FBref provides detailed xG, xA, and advanced metrics that enable more nuanced player and team analysis",
            'example': "Instead of just 'Player X scored 20 goals', RAG can say 'Player X scored 20 goals with an xG of 18.5, showing clinical finishing'"
        },
        {
            'benefit': "Tactical Depth",
            'description': "Formation-specific data and positional analysis support tactical queries",
            'example': "RAG can answer 'How effective is a 4-3-3 formation?' using actual performance data"
        },
        {
            'benefit': "Comparative Analysis",
            'description': "Cross-league and cross-player comparisons with standardized metrics",
            'example': "RAG can compare 'Premier League vs La Liga attacking efficiency' using xG data"
        },
        {
            'benefit': "Historical Context",
            'description': "Season-long data provides context for current performance trends",
            'example': "RAG can identify if a team's current form represents improvement or decline"
        },
        {
            'benefit': "Shapley Value Support",
            'description': "Detailed individual metrics support advanced contribution analysis",
            'example': "RAG can explain individual player value using comprehensive performance data"
        }
    ]
    
    for i, benefit in enumerate(benefits, 1):
        print(f"\n{i}. {benefit['benefit']}:")
        print(f"   Description: {benefit['description']}")
        print(f"   Example: {benefit['example']}")
    
    print(f"\nTotal Enhanced Capabilities: {len(benefits)}")
    print("✓ RAG system now supports comprehensive soccer intelligence queries")


def main():
    """Run all RAG enhancement demos"""
    print("FBref RAG Enhancement Demonstration")
    print("=" * 60)
    print("This demo shows how FBref statistical content enhances the RAG system")
    print("for more comprehensive soccer intelligence queries")
    print()
    
    try:
        # Run demos
        demo_rag_enhancement()
        demo_content_types()
        demo_query_scenarios()
        demo_rag_integration_benefits()
        
        print("\n" + "=" * 60)
        print("RAG enhancement demo completed!")
        print("The RAG system now has rich statistical content for comprehensive queries")
        print("Check data/processed/rag_enhanced/ for enhanced content files")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")


if __name__ == "__main__":
    main()
