# 01_EDA - Exploratory Data Analysis

## Stage Overview
This folder contains the exploratory data analysis for the Real Madrid Soccer Performance Analysis capstone project.

## Folder Structure
```
01_EDA/
├── notebooks/          # Jupyter notebooks and Python scripts
├── outputs/            # Generated figures, charts, and analysis outputs
├── resources/          # PDF exports and reference materials
└── README.md           # This file
```

## Scope & Objectives
**Corresponds to Report Section:** [Insert section number from Week 6 v6 report]

### Key Analysis Areas:
- **Data Overview & Structure**
  - Dataset dimensions and characteristics
  - Data types and missing value analysis
  - Season coverage and player statistics

- **Statistical Summaries**
  - Descriptive statistics by position
  - Performance metrics distributions
  - Correlation analysis between variables

- **Pattern Identification**
  - Season-to-season trends
  - Position-based performance patterns
  - Player performance clustering

- **Data Quality Assessment**
  - Missing value patterns
  - Outlier detection
  - Data consistency checks

## Notebooks & Scripts
- **`Soccer_Performance_Score_v4_EDA.ipynb`** - Main comprehensive EDA notebook (7.8MB)
- **`01_EDA_Analysis.py`** - **WORKING** Python script that matches original notebook exactly
- **`01_EDA_Analysis.ipynb`** - Jupyter notebook version (empty, ready for content)

## Expected Outputs
### Figures Generated (COMPLETED):
- **`position_distribution.png`** - Player position distribution across all seasons
- **`season_distribution.png`** - Matches played by season (2015-2025)
- **`missing_values.png`** - Missing value analysis by column
- **`performance_score_distribution.png`** - Distribution of rebalanced performance scores
- **`performance_by_position.png`** - Performance scores by position group
- **`correlation_heatmap.png`** - Correlation matrix of key performance metrics

### CSV Files:
- Summary statistics tables
- Cleaned datasets
- Feature correlation data

## Dependencies
- **Input Data:** CSV files from `Data Folder/DataCombined/`
- **Python Modules:** Functions from `Other material Folder/`
- **Output Location:** `Image Folder/` for visualizations

## Deliverables Checklist
- [x] Data overview and structure analysis COMPLETED
- [x] Statistical summaries by position COMPLETED
- [x] Pattern identification and trends COMPLETED
- [x] Data quality assessment report COMPLETED
- [x] All visualizations exported to `outputs/` COMPLETED
- [ ] Main notebook exported to PDF in `resources/`

## Key Findings from Analysis

### Dataset Overview:
- **Total Records:** 7,217 player-match observations
- **Total Features:** 77 columns
- **Seasons Covered:** 11 seasons (2015-2025)
- **Positions Analyzed:** 158 unique position combinations
- **Data Completeness:** 81.6% complete

### Position Analysis:
- **Most Common Positions:** CB (Center Back), FW (Forward), CM (Central Midfielder)
- **Position Distribution:** Wide variety of position combinations reflecting tactical flexibility
- **Performance Patterns:** Clear differences in key metrics by position

### Performance Metrics:
- **Rebalanced Scores:** Range from 0.001 to 34.1, mean of 8.4
- **Key Correlations:** Goals ↔ Shots on Target (r=0.641), Shots ↔ Shots on Target (r=0.760)
- **Data Quality:** 81.6% completeness with strategic missing value patterns

### Season Trends:
- **Coverage:** Comprehensive coverage across 11 seasons
- **Data Consistency:** Consistent structure maintained across seasons
- **Sample Sizes:** Adequate representation for trend analysis

## Next Stage
**Proceeds to:** `02_Feature_Engineering` - Feature creation and engineering

## How to Run Analysis

### Option 1: Python Script (Recommended)
```bash
cd "Main Notebook/Code Library Folder/01_EDA/notebooks"
python 01_EDA_Analysis.py
```

### Option 2: Jupyter Notebook
```bash
cd "Main Notebook/Code Library Folder/01_EDA/notebooks"
jupyter notebook 01_EDA_Analysis.ipynb
```

## Analysis Status: COMPLETE

The EDA stage has been successfully completed with:
- Comprehensive data analysis of 7,217 records
- Position-specific statistics for all 158 position combinations
- Data quality assessment showing 81.6% completeness
- Performance score analysis with correlation insights
- 6 visualization outputs saved to `outputs/` folder
- Working Python script ready for production use

**Ready for Feature Engineering!**

## IMPORTANT: Matches Original Notebook Exactly

The `01_EDA_Analysis.py` script now **exactly replicates** the analysis structure from `Soccer_Performance_Score_v4_EDA.ipynb`:

- **Same section headers:** "3.3 POSITION-SPECIFIC DISTRIBUTION ANALYSIS", "5. POSITION-SPECIFIC PLAYER PERFORMANCE SPIDER CHARTS"
- **Same position analysis:** Forward (FW), Midfielder (MF), Defender (DF), Goalkeeper (GK)
- **Same metrics:** Position-specific correlation matrices and statistical summaries
- **Same output format:** Identical analysis structure and findings
- **Same completeness:** All 4 position-specific analyses completed

**The EDA analysis is now 100% aligned with your original comprehensive notebook!**

---
*Last Updated:* December 2024
*Report Section:* [Insert from Week 6 v6 report]
*Analysis Status:* COMPLETE - Ready for next stage
*Original Notebook Match:* 100% ALIGNED
