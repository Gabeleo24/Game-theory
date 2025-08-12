# Real Madrid Player Performance Analysis

A comprehensive machine learning analysis of Real Madrid player performance data from 2017-2025, featuring position-specific modeling, weighted scoring systems, and predictive analytics.

## Table of Contents

- [Profile](#profile)
- [Overview](#overview)
- [Navigation](#navigation)
- [Data](#data)
- [Features](#features)
- [Models](#models)
- [Installation](#installation)
- [Usage](#usage)
- [Results](#results)
- [Visuals](#visuals)
- [File Structure](#file-structure)
- [Repository Management](#repository-management)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Overview

This project provides an in-depth analysis of Real Madrid player performance using advanced machine learning techniques. The system creates position-specific models to predict player performance scores and analyze team dynamics across different seasons.
## Profile

Introduce yourself to readers and provide links for quick context.

- **Name**: Gabriel Elohi Mancillas Gallardo (Gabi), Mauricio Espinoza Acevedo (Mau), Maria Mora Mora
- **Program**: University of San Diego — MAS Data Science
- **Bio**:
  - **Gabi**: Bridging the gap between raw data and actionable intelligence, my passion for soccer is the catalyst for developing precise analytical frameworks and practical, impactful applications.
  - **Mau**: As a former semi‑pro footballer, I have always wanted to stay involved in the sport. Football has yet to truly adopt data analytics the way baseball and other sports have—and I hope to change that.
  - **Maria**: In a world saturated with shallow match predictions, my passion for soccer emerges as a driving force for revolutionary analytics and comprehensive real‑world applications.
- **Links**: [LinkedIn](https://www.linkedin.com/), [Website](https://example.com), [Portfolio](https://example.com/portfolio)
- **Contact**: your.email@example.com

Add a profile image by placing it in `Main Notebook/Image Folder/Images/` and referencing it like:
`![Profile](Main%20Notebook/Image%20Folder/Images/profile.png)`

### Team

| Gabriel (Gabi) | Mauricio (Mau) | Maria |
| --- | --- | --- |
| ![Gabi](Main%20Notebook/Image%20Folder/Images/Gabe.png) | ![Mau](Main%20Notebook/Image%20Folder/Images/mau.png) | ![Maria](Main%20Notebook/Image%20Folder/Images/maria.png) |

## Navigation

Quick links to the most relevant parts of the repository.

- **Main Notebook**: [`Main Notebook/`](Main%20Notebook/)
  - **Code Library Folder**: [`Main Notebook/Code Library Folder/`](Main%20Notebook/Code%20Library%20Folder/)
    - Data Acquisition: [`00_Data_Aquisition/`](Main%20Notebook/Code%20Library%20Folder/00_Data_Aquisition/)
    - EDA: [`01_EDA/notebooks/`](Main%20Notebook/Code%20Library%20Folder/01_EDA/notebooks/)
    - Feature Engineering: [`02_Feature_Engineering/notebooks/`](Main%20Notebook/Code%20Library%20Folder/02_Feature_Engineering/notebooks/)
    - Modeling & Validation: [`04_Modeling_Benchmarks_Validation/notebooks/`](Main%20Notebook/Code%20Library%20Folder/04_Modeling_Benchmarks_Validation/notebooks/)
    - Forecasting: [`05_Forecasting/notebooks/`](Main%20Notebook/Code%20Library%20Folder/05_Forecasting/notebooks/)
  - **Image Folder**: [`Main Notebook/Image Folder/Images/`](Main%20Notebook/Image%20Folder/Images/)
  - **Data Folder**: [`Main Notebook/Data Folder/`](Main%20Notebook/Data%20Folder/)
  - **Docs**: [`Main Notebook/Code Library Folder/06_Docs/`](Main%20Notebook/Code%20Library%20Folder/06_Docs/)


### Key Objectives

- Develop position-specific performance scoring systems
- Create predictive models for player performance
- Analyze team performance trends over time
- Provide actionable insights for player evaluation

## Data

### Dataset Information

- **Size**: 5,737 observations across 8 seasons (2017-2025)
- **Players**: 54 unique players with 200+ minutes played
- **Positions**: Forward, Midfielder, Defender, Goalkeeper
- **Features**: 69 performance metrics per match

### Data Sources

- Match performance statistics
- Expected goals (xG) and advanced metrics
- Position-specific defensive and offensive statistics
- Season schedules and match results

### Key Metrics by Position

#### Forwards
- Goals, Assists, Shots on Target
- Expected Goals (xG), Expected Assists (xAG)
- Take-ons Success

#### Midfielders
- Pass Completion %, Key Passes, Tackles
- Progressive Passes, Carries, Touches

#### Defenders
- Interceptions, Blocks, Clearances
- Tackles Won, Defensive Actions

#### Goalkeepers
- Distribution Accuracy, Errors
- Progressive Distance, Pass Completion

## Features

### 1. Data Processing Pipeline

- **Missing Value Handling**: Player-specific averages with fallback to position means
- **Outlier Detection**: Statistical methods and box plot analysis
- **Feature Engineering**: Per-90 minute rates and position-specific metrics
- **Multicollinearity Analysis**: VIF testing and correlation matrix analysis

### 2. Weighted Scoring System

Position-specific weighted formulas based on SHAP analysis:

#### Forward Scoring
```python
Score = 3.0×Goals + 2.0×Assists + 1.0×SoT + 1.5×xG + 1.0×xAG + 0.5×TakeOns
```

#### Midfielder Scoring
```python
Score = 2.5×PassCmp% + 1.2×KP + 1.5×Tkl + 0.8×ProgCarries + 1.8×ProgPasses + 0.3×Touches
```

#### Defender Scoring
```python
Score = 2.5×Int + 2.0×Blocks + 1.0×Clr + 2.0×TklW + 1.3×TklDef + 0.8×TklMid
```

#### Goalkeeper Scoring
```python
Score = 3.0×TotalCmp% - 2.0×Err + 1.0×PrgDist + 1.5×ShortCmp% + 1.0×MedCmp% + 0.5×TotalCmp
```
#### Logistic Regression Validation
```python
Logistic Regression Loss Wins
```

### 3. Machine Learning Models

#### Random Forest
- Position-specific models
- Feature importance analysis
- Cross-validation with time-based splits

#### XGBoost
- Gradient boosting implementation
- Hyperparameter optimization
- Raw statistics approach

#### Neural Networks
- Multi-layer perceptron architecture
- Fast hyperparameter tuning (20s vs 104+ minutes)
- Standardized feature scaling

#### Ensemble Methods
- Voting regressor combining RF, XGBoost, and Gradient Boosting
- Model averaging for improved predictions

### 4. SHAP Analysis

- Position-specific feature importance
- Per-90 minute rate analysis
- Player-level performance drivers
- Bias-free efficiency metrics

### 5. Logistic Regression Validation

- Win/Loss prediction based on team performance
- S-curve visualization (0% to 100% win probability)
- Threshold identification for performance levels

## Installation

### Requirements

```bash
pip install pandas numpy matplotlib seaborn scikit-learn xgboost shap
```

### Additional Dependencies

```bash
pip install scipy plotly statsmodels
```

### Setup

```bash
git clone https://github.com/your-repo/real-madrid-analysis
cd real-madrid-analysis
pip install -r requirements.txt
```

## Usage

### 1. Data Loading and Preprocessing

```python
# Load and clean data
from data_processing import load_and_clean_data
df = load_and_clean_data('path/to/real_madrid_data.csv')

# Create position-specific features
from feature_engineering import create_per90_features
df_per90 = create_per90_features(df)
```

### 2. Model Training

```python
# Train position-specific models
from models import train_position_models
models = train_position_models(df_per90)

# Fast neural network tuning
from neural_network import tune_neural_network_fast
tuned_models = tune_neural_network_fast(position_datasets)
```

### 3. Performance Analysis

```python
# Generate SHAP analysis
from shap_analysis import analyze_player_per90
analyze_player_per90('Player Name')

# Create performance visualizations
from visualization import plot_performance_trends
plot_performance_trends(df)
```


### 4. Prediction

```python
# Predict player performance
from prediction import predict_performance
score = predict_performance(player_stats, position='Forward')
```

## Results

### Model Performance Summary

| Model | Forward R² | Midfield R² | Defense R² | Goalkeeper R² |
|-------|------------|-------------|------------|---------------|
| Random Forest | 0.987 | 0.336 | 0.935 | 0.823 |
| XGBoost | 0.985 | 0.302 | 0.929 | 0.904 |
| Neural Network | 0.989 | 0.435 | 0.933 | 0.919 |
| Ensemble | 0.987 | 0.325 | 0.933 | 0.864 |

### Key Findings

- **Forward Models**: Excellent performance (R² > 0.98) across all algorithms
- **Goalkeeper Models**: Strong performance with Neural Networks (R² = 0.919)
- **Defense Models**: Consistent high performance (R² > 0.93)
- **Midfield Models**: Most challenging position to predict (R² ≈ 0.3-0.4)

### Feature Importance (Top 3 by Position)

#### Forward
1. Goals per 90: 3.320
2. Assists per 90: 2.060
3. Expected xG per 90: 1.738

#### Midfielder
1. Progressive Passes per 90: 1.793
2. Tackles per 90: 1.178
3. Pass Completion %: 0.913

#### Defender
1. Blocks per 90: 2.309
2. Interceptions per 90: 1.517
3. Tackles Won per 90: 1.492

#### Goalkeeper
1. Total Completion %: 1.718
2. Short Completion %: 0.138
3. Progressive Distance per 90: 0.101

### Win Prediction Analysis

- **Logistic Regression AUC**: 0.842
- **50% Win Probability Threshold**: 5.94 team rebalanced score
- **Strong Discrimination**: 0.843 probability range (0.155 to 0.999)

## Visuals

Selected outputs to give readers quick intuition.

| Description | Image |
| --- | --- |
| Position distribution | ![Position Distribution](Main%20Notebook/Image%20Folder/Images/01_EDA/position_distribution.png) |
| Correlation heatmap | ![Correlation Heatmap](Main%20Notebook/Image%20Folder/Images/01_EDA/correlation_heatmap.png) |
| SHAP summary (dot) | ![SHAP Summary Dot](Main%20Notebook/Code%20Library%20Folder/03_SPPS_Calibration_SHAP/outputs/shap_summary_dot.png) |
| Calibration curve | ![Calibration Curve](Main%20Notebook/Code%20Library%20Folder/03_SPPS_Calibration_SHAP/outputs/calibration_curves_test.png) |

## File Structure

```
Main Notebook/
├── Data Folder/
│   ├── DataCombined/               # Data raw combined in seasons
│   ├── DataExtracted/              # Raw data extracted
├── Code Library Folder/
│   ├── 00_Data_Aquisition/
│   ├── 01_EDA/
│   ├── 02_Feature_Engineering/
│   ├── 03_SPPS_Calibration_SHAP/
│   ├── 04_Modeling_Benchmarks_Validation/
│   ├── 05_Forecasting/
└── README.md
```

## Key Insights

### Position-Specific Trends (2022-2025)

#### Forwards: Becoming more clinical but less creative
- Goal scoring: 0.34 → 0.37 per match (+8.8%)
- Assists declining: 0.20 → 0.14 per match (-30%)

#### Midfielders: Maintaining stability with defensive focus
- Pass accuracy stable: ~87-89%
- Increased defensive responsibility
- Less adventurous attacking play

#### Defenders: More proactive defending
- Clearances increased: 1.77 → 2.32 per match (+31%)
- Better tackle success rates
- More aggressive positioning

#### Goalkeepers: Conservative distribution
- Passing accuracy declining: 86.25% → 83.39%
- More safety-first approach
- Excellent error rates (0.02-0.04 per game)

### Model Efficiency

- **Fast Neural Network Tuning**: 20.2 seconds vs 104+ minutes (99.7% time reduction)
- **Average Improvement**: +2.9% over baseline neural networks
- **Best Architecture**: (150, 75, 35) hidden layer configuration

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-analysis`)
3. Commit changes (`git commit -am 'Add new analysis'`)
4. Push to branch (`git push origin feature/new-analysis`)
5. Create Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include unit tests for new features
- Update documentation for API changes

## Repository Management

Guidelines to keep this repository clear and professional.

- **Descriptions**: Add concise descriptions for the repository and major branches (e.g., `main`, `dev`, `experiments`) so visitors understand their purpose.
- **Branches**: Remove unused branches/forks. Adopt a simple workflow: `main` (stable), `dev` (active work), feature branches `feature/<short-name>`.
- **Projects/Kanban**: Use GitHub Projects to track tasks. Recommended columns: Backlog → In Progress → Review → Done. Link issues to milestones where relevant.
- **Issues**: Create well-scoped issues with clear acceptance criteria and labels (data, modeling, docs, bug).
- **Code Quality**: Follow PEP 8, include docstrings, and prefer modular functions in the Code Library over long notebook cells. Add unit tests in `test_modules.py` for new utilities.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Real Madrid performance data sources
- scikit-learn and XGBoost communities
- SHAP library for model interpretability
- Academic research in sports analytics
- Faculty at University of San Diego MAS Data Science Program
