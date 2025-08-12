#!/usr/bin/env python3
"""
Test Script for Real Madrid Soccer Analysis Modules
Tests all Code Library modules to ensure they work correctly
"""

import sys
import os

# Add the Other material Folder (Python library) to the Python path
sys.path.append('Main Notebook/Other material Folder')

def test_imports():
    """Test that all modules can be imported successfully"""
    print("🧪 Testing module imports...")
    
    try:
        # Test data acquisition module
        from data_acquisition import FBrefScraper, quick_schedule_pull
        print("✅ data_acquisition module imported successfully")
        
        # Test data processing module
        from data_processing import SoccerDataProcessor, quick_data_load, quick_analysis
        print("✅ data_processing module imported successfully")
        
        # Test visualization module
        from visualization import SoccerVisualizer, quick_visualization, create_comprehensive_report
        print("✅ visualization module imported successfully")
        
        # Test modeling module
        from modeling import SoccerModeler, quick_regression_analysis, quick_classification_analysis
        print("✅ modeling module imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_processing():
    """Test data processing functionality"""
    print("\n🧪 Testing data processing...")
    
    try:
        from data_processing import SoccerDataProcessor
        
        # Create processor instance
        processor = SoccerDataProcessor()
        print("✅ SoccerDataProcessor created successfully")
        
        # Test with sample data
        import pandas as pd
        sample_data = pd.DataFrame({
            'season': ['15_16', '16_17'],
            'goals': [10, 15],
            'assists': [5, 8],
            'position': ['FW', 'MF']
        })
        
        # Test cleaning
        cleaned_data = processor.clean_match_data(sample_data)
        print(f"✅ Data cleaning successful: {len(cleaned_data)} rows")
        
        # Test metrics calculation
        metrics_data = processor.calculate_performance_metrics(cleaned_data)
        print(f"✅ Metrics calculation successful: {len(metrics_data.columns)} columns")
        
        return True
        
    except Exception as e:
        print(f"❌ Data processing error: {e}")
        return False

def test_visualization():
    """Test visualization functionality"""
    print("\n🧪 Testing visualization...")
    
    try:
        from visualization import SoccerVisualizer
        
        # Create visualizer instance
        visualizer = SoccerVisualizer()
        print("✅ SoccerVisualizer created successfully")
        
        # Test with sample data
        import pandas as pd
        sample_data = pd.DataFrame({
            'season': ['15_16', '16_17', '17_18'],
            'goals': [85, 92, 88],
            'assists': [45, 52, 48]
        })
        
        # Test season performance plot
        fig = visualizer.plot_season_performance(sample_data, save_path="test_season.png")
        print("✅ Season performance plot created successfully")
        
        # Clean up test file
        if os.path.exists("test_season.png"):
            os.remove("test_season.png")
            print("✅ Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Visualization error: {e}")
        return False

def test_modeling():
    """Test modeling functionality"""
    print("\n🧪 Testing modeling...")
    
    try:
        from modeling import SoccerModeler
        
        # Create modeler instance
        modeler = SoccerModeler()
        print("✅ SoccerModeler created successfully")
        
        # Test with sample data
        import pandas as pd
        import numpy as np
        
        np.random.seed(42)
        sample_data = pd.DataFrame({
            'goals': np.random.poisson(15, 50),
            'assists': np.random.poisson(8, 50),
            'minutes': np.random.uniform(500, 3000, 50),
            'position': np.random.choice(['FW', 'MF', 'DF'], 50)
        })
        
        # Test feature preparation
        X, y = modeler.prepare_features(sample_data, 'goals')
        print(f"✅ Feature preparation successful: {X.shape[1]} features, {X.shape[0]} samples")
        
        return True
        
    except Exception as e:
        print(f"❌ Modeling error: {e}")
        return False

def test_quick_functions():
    """Test quick function wrappers"""
    print("\n🧪 Testing quick functions...")
    
    try:
        from data_processing import quick_analysis
        from visualization import quick_visualization
        
        # Create sample data
        import pandas as pd
        sample_data = pd.DataFrame({
            'season': ['15_16', '16_17', '17_18'],
            'goals': [85, 92, 88],
            'assists': [45, 52, 48],
            'position': ['FW', 'MF', 'DF'],
            'player': ['Player1', 'Player2', 'Player3']
        })
        
        # Test quick analysis
        results = quick_analysis(sample_data)
        print(f"✅ Quick analysis successful: {len(results)} result types")
        
        # Test quick visualization
        figures = quick_visualization(sample_data, "Main Notebook/Images")
        print(f"✅ Quick visualization successful: {len(figures)} figures created")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick functions error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Real Madrid Soccer Analysis Module Tests")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Data Processing", test_data_processing),
        ("Visualization", test_visualization),
        ("Modeling", test_modeling),
        ("Quick Functions", test_quick_functions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} test PASSED")
        else:
            print(f"❌ {test_name} test FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Code Library is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
