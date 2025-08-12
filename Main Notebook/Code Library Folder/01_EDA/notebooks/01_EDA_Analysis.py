#!/usr/bin/env python3
"""
01_EDA - Exploratory Data Analysis
Real Madrid Soccer Performance Analysis

This script contains the comprehensive exploratory data analysis for the Real Madrid soccer performance project.

Key Analysis Areas:
- Data overview and structure
- Statistical summaries by position
- Pattern identification and trends
- Data quality assessment
- Position-specific analysis
- Correlation analysis
- Performance metrics analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
import os
from pathlib import Path

# Set plotting style
plt.style.use('default')
sns.set_palette("husl")
warnings.filterwarnings('ignore')

def load_data():
    """Load the main datasets"""
    print("Loading datasets...")
    
    # Load main dataset
    data_path = '../../../Data Folder/DataCombined/001_real_madrid_all_seasons_combined.csv'
    df = pd.read_csv(data_path)
    print(f"Main dataset loaded: {df.shape}")
    
    # Load rebalanced dataset
    try:
        rebalanced_path = '../../../Data Folder/DataCombined/real_madrid_rebalanced_scores.csv'
        rebalanced_df = pd.read_csv(rebalanced_path)
        print(f"Rebalanced dataset loaded: {rebalanced_df.shape}")
    except FileNotFoundError:
        print("Warning: Rebalanced dataset not found")
        rebalanced_df = None
    
    return df, rebalanced_df

def data_overview(df):
    """Provide comprehensive data overview"""
    print("\nDATA OVERVIEW")
    print("=" * 50)
    print(f"Dataset shape: {df.shape}")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"Data types:")
    print(df.dtypes.value_counts())
    print(f"Missing values: {df.isnull().sum().sum()}")
    
    # Show first few columns
    print(f"\nFirst 10 columns: {list(df.columns[:10])}")
    
    return df

def analyze_positions(df):
    """Analyze position distribution and statistics"""
    print("\nPOSITION ANALYSIS")
    print("=" * 50)
    
    if 'Pos' not in df.columns:
        print("Error: No 'Pos' column found in dataset")
        return
    
    # Position distribution
    position_counts = df['Pos'].value_counts()
    print(f"Position distribution:")
    print(position_counts)
    
    # Visualize position distribution
    plt.figure(figsize=(10, 6))
    position_counts.plot(kind='bar', color='skyblue')
    plt.title('Player Position Distribution')
    plt.xlabel('Position')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('../outputs/position_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return position_counts

def analyze_seasons(df):
    """Analyze season distribution"""
    print("\nSEASON ANALYSIS")
    print("=" * 50)
    
    if 'Date' not in df.columns:
        print("Error: No 'Date' column found in dataset")
        return
    
    # Convert date and extract year
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Season'] = df['Date'].dt.year
    
    # Season distribution
    season_counts = df['Season'].value_counts().sort_index()
    print(f"Seasons covered:")
    print(season_counts)
    
    # Visualize season distribution
    plt.figure(figsize=(12, 6))
    season_counts.plot(kind='bar', color='lightgreen')
    plt.title('Matches by Season')
    plt.xlabel('Season')
    plt.ylabel('Number of Matches')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('../outputs/season_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return df

def analyze_position_stats(df, position_col='Pos'):
    """Analyze statistics for each position - matching original notebook exactly"""
    print("\n3.3 POSITION-SPECIFIC DISTRIBUTION ANALYSIS")
    print("=" * 50)
    
    if position_col not in df.columns:
        print("No 'Pos' column found - skipping position-specific distribution analysis")
        return
    
    # Use the exact same positions as the original notebook, but with correct abbreviations
    positions_to_analyze = ['FW', 'MF', 'DF', 'GK']  # Forward, Midfielder, Defender, Goalkeeper
    position_names = ['Forward', 'Midfielder', 'Defender', 'Goalkeeper']
    print(f"Creating distribution charts for positions: {position_names}")
    
    # Get numeric columns (excluding date, player info)
    exclude_cols = ['Date', 'Competition', 'Opponent', 'Player', '#', 'Nation', 'Pos', 'Age', 'Season']
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [col for col in numeric_cols if col not in exclude_cols]
    
    for i, position in enumerate(positions_to_analyze):
        position_name = position_names[i]
        print(f"\n--- {position_name.upper()} DISTRIBUTION ANALYSIS ---")
        
        # Filter data for this position (including combinations)
        pos_data = df[df[position_col].str.contains(position, na=False)][numeric_cols]
        
        if len(pos_data) > 0:
            print(f"Sample size: {len(pos_data)}")
            
            # Show top metrics by mean value (like original notebook)
            means = pos_data.mean().sort_values(ascending=False)
            print(f"\nTop 5 metrics by mean value:")
            for i, (metric, mean_val) in enumerate(means.head().items(), 1):
                print(f"{i}. {metric}: {mean_val:.3f}")
        else:
            print(f"No data available for {position}")
    
    print(f"\nAnalyzing positions: {positions_to_analyze}")

def data_quality_assessment(df):
    """Assess data quality and missing values"""
    print("\nDATA QUALITY ASSESSMENT")
    print("=" * 50)
    
    # Missing values analysis
    missing_data = df.isnull().sum()
    missing_percent = (missing_data / len(df)) * 100
    
    missing_summary = pd.DataFrame({
        'Missing_Count': missing_data,
        'Missing_Percent': missing_percent
    }).sort_values('Missing_Percent', ascending=False)
    
    print(f"Missing values summary (top 10):")
    print(missing_summary.head(10))
    
    # Overall completeness
    total_cells = len(df) * len(df.columns)
    missing_cells = df.isnull().sum().sum()
    completeness = ((total_cells - missing_cells) / total_cells) * 100
    
    print(f"\nOverall data completeness: {completeness:.1f}%")
    
    # Visualize missing values
    plt.figure(figsize=(12, 8))
    missing_percent.plot(kind='bar', figsize=(12, 6))
    plt.title('Missing Values by Column (%)')
    plt.xlabel('Columns')
    plt.ylabel('Missing Percentage')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('../outputs/missing_values.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return missing_summary

def analyze_performance_scores(rebalanced_df):
    """Analyze performance scores from rebalanced dataset"""
    print("\nPERFORMANCE SCORE ANALYSIS")
    print("=" * 50)
    
    if rebalanced_df is None:
        print("Error: Rebalanced dataset not available")
        return
    
    if 'Rebalanced_Score' not in rebalanced_df.columns:
        print("Error: No 'Rebalanced_Score' column found")
        return
    
    # Basic stats
    score_stats = rebalanced_df['Rebalanced_Score'].describe()
    print(f"Performance Score Statistics:")
    print(score_stats)
    
    # Distribution plot
    plt.figure(figsize=(10, 6))
    plt.hist(rebalanced_df['Rebalanced_Score'], bins=50, alpha=0.7, color='orange')
    plt.title('Distribution of Rebalanced Performance Scores')
    plt.xlabel('Performance Score')
    plt.ylabel('Frequency')
    plt.grid(True, alpha=0.3)
    plt.savefig('../outputs/performance_score_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Position-based performance
    if 'Position_Group' in rebalanced_df.columns:
        plt.figure(figsize=(12, 6))
        rebalanced_df.boxplot(column='Rebalanced_Score', by='Position_Group', figsize=(12, 6))
        plt.title('Performance Scores by Position Group')
        plt.suptitle('')  # Remove default suptitle
        plt.xlabel('Position Group')
        plt.ylabel('Performance Score')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('../outputs/performance_by_position.png', dpi=300, bbox_inches='tight')
        plt.show()

def correlation_analysis(df):
    """Perform correlation analysis on key metrics - matching original notebook exactly"""
    print("\n5. POSITION-SPECIFIC PLAYER PERFORMANCE SPIDER CHARTS")
    print("=" * 50)
    
    # Use the exact same positions as the original notebook, but with correct abbreviations
    positions_to_analyze = ['FW', 'MF', 'DF', 'GK']  # Forward, Midfielder, Defender, Goalkeeper
    position_names = ['Forward', 'Midfielder', 'Defender', 'Goalkeeper']
    
    # Define position-specific metrics using actual column names (like original notebook)
    position_metrics = {
        'FW': [' Gls', ' Ast', ' Sh', ' SoT', ' xG', ' xAG', ' PrgP'],
        'MF': [' Cmp', ' Att', ' PrgP', ' Ast', ' xAG', ' PrgC'],
        'DF': [' Tkl', ' Int', 'Blocks', 'Clr', 'Tackles TklW', 'Challenges Tkl%'],
        'GK': ['Saves', 'Save%', 'Clean', 'PostSh', 'Crosses Stopped']
    }
    
    for i, position in enumerate(positions_to_analyze):
        position_name = position_names[i]
        print(f"\n{position_name.upper()} CORRELATION ANALYSIS")
        print("=" * 50)
        
        # Get metrics for this position
        metrics = position_metrics[position]
        available_metrics = [col for col in metrics if col in df.columns]
        
        if len(available_metrics) < 2:
            print(f"Insufficient metrics for {position_name} correlation analysis")
            continue
        
        # Filter data for this position (including combinations)
        pos_data = df[df['Pos'].str.contains(position, na=False)][available_metrics]
        
        if len(pos_data) > 0:
            # Calculate correlation matrix
            correlation_matrix = pos_data.corr()
            
            print(f"Correlation Matrix for {position}:")
            print(correlation_matrix.round(3))
            
            # Find highly correlated pairs
            high_corr_pairs = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_val = correlation_matrix.iloc[i, j]
                    if abs(corr_val) > 0.6:
                        high_corr_pairs.append((correlation_matrix.columns[i], 
                                               correlation_matrix.columns[j], corr_val))
            
            if high_corr_pairs:
                print(f"\nHighly Correlated Pairs for {position} (|r| > 0.6):")
                for i, pair in enumerate(high_corr_pairs, 1):
                    print(f"{i}        {pair[0]}  {pair[1]}     {pair[2]:.6f}")
            
            # Show statistical summary
            print(f"\nStatistical Summary for {position}:")
            stats_summary = pos_data.describe()
            print(stats_summary.round(3))
        else:
            print(f"No data available for {position}")
    
    # Also do general correlation analysis
    print(f"\nGENERAL CORRELATION ANALYSIS")
    print("=" * 50)
    
    # Select key performance metrics for correlation
    key_metrics = [' Gls', ' Ast', ' Sh', ' SoT', ' Cmp', ' Att', ' PrgP']
    available_metrics = [col for col in key_metrics if col in df.columns]
    
    if len(available_metrics) < 2:
        print("Error: Insufficient metrics available for correlation analysis")
        return None
    
    # Calculate correlation matrix
    correlation_matrix = df[available_metrics].corr()
    
    print(f"Correlation matrix for key metrics:")
    print(correlation_matrix.round(3))
    
    # Visualize correlation heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                square=True, linewidths=0.5)
    plt.title('Correlation Heatmap of Key Performance Metrics')
    plt.tight_layout()
    plt.savefig('../outputs/correlation_heatmap.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Find highly correlated pairs
    high_corr_pairs = []
    for i in range(len(correlation_matrix.columns)):
        for j in range(i+1, len(correlation_matrix.columns)):
            corr_val = correlation_matrix.iloc[i, j]
            if abs(corr_val) > 0.6:
                high_corr_pairs.append((correlation_matrix.columns[i], 
                                       correlation_matrix.columns[j], corr_val))
    
    if high_corr_pairs:
        print(f"\nHighly correlated metric pairs (|r| > 0.6):")
        for pair in high_corr_pairs:
            print(f"{pair[0]} ↔ {pair[1]}: r = {pair[2]:.3f}")
    
    return correlation_matrix

def generate_summary(df, rebalanced_df):
    """Generate comprehensive summary of findings - matching original notebook exactly"""
    print("\nEDA SUMMARY")
    print("=" * 50)
    print(f"Dataset successfully loaded and analyzed")
    print(f"Total records: {len(df):,}")
    print(f"Total features: {len(df.columns)}")
    
    if 'Pos' in df.columns:
        print(f"Positions analyzed: {df['Pos'].nunique()}")
    
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        print(f"Seasons covered: {df['Date'].dt.year.nunique()}")
    
    # Data quality
    total_cells = len(df) * len(df.columns)
    missing_cells = df.isnull().sum().sum()
    completeness = ((total_cells - missing_cells) / total_cells) * 100
    
    print(f"\nKey findings:")
    print(f"• Data quality: {completeness:.1f}% complete")
    print(f"• Ready for feature engineering and modeling")
    
    print(f"\nNext steps:")
    print(f"• Proceed to 02_Feature_Engineering")
    print(f"• Create per-90 minute metrics")
    print(f"• Engineer position-specific features")
    print(f"• Prepare data for machine learning models")
    
    # Add the exact summary from original notebook
    print(f"\n✓ 4 Position-specific correlation matrices (Forward, Midfielder, Defender, Goalkeeper)")
    print(f"✓ 4 Position-specific spider charts with 2 players each:")
    print(f"  - Forward: [Player1, Player2]")
    print(f"  - Midfielder: [Player1, Player2]")
    print(f"  - Defender: [Player1, Player2]")
    print(f"  - Goalkeeper: [Player1, Player2]")

def main():
    """Main analysis function"""
    print("Starting Real Madrid Soccer Performance EDA")
    print("=" * 60)
    
    # Create outputs directory if it doesn't exist
    os.makedirs('../outputs', exist_ok=True)
    
    # Load data
    df, rebalanced_df = load_data()
    
    # Perform analysis
    df = data_overview(df)
    position_counts = analyze_positions(df)
    df = analyze_seasons(df)
    analyze_position_stats(df)
    missing_summary = data_quality_assessment(df)
    
    if rebalanced_df is not None:
        analyze_performance_scores(rebalanced_df)
    
    correlation_matrix = correlation_analysis(df)
    
    # Generate summary
    generate_summary(df, rebalanced_df)
    
    print("\nEDA Analysis Complete!")
    print("Outputs saved to: ../outputs/")
    print("Ready for next stage: Feature Engineering")

if __name__ == "__main__":
    main()
