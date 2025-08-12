# 02_Feature_Engineering - Feature Creation & Engineering

## 📊 **Stage Overview**
This folder contains feature engineering and creation for the Real Madrid Soccer Performance Analysis capstone project.

## 📁 **Folder Structure**
```
02_Feature_Engineering/
├── notebooks/          # Jupyter notebooks and Python scripts
├── outputs/            # Generated features, engineered datasets
├── resources/          # PDF exports and reference materials
└── README.md           # This file
```

## 🎯 **Scope & Objectives**
**Corresponds to Report Section:** [Insert section number from Week 6 v6 report]

### **Key Feature Engineering Areas:**
- **Per-90 Minute Metrics**
  - Goals per 90 minutes
  - Assists per 90 minutes
  - Shots per 90 minutes
  - Passes per 90 minutes

- **Position-Specific Features**
  - Forward-specific metrics (xG, xAG, take-ons)
  - Midfielder-specific metrics (pass completion %, key passes)
  - Defender-specific metrics (tackles, interceptions, blocks)
  - Goalkeeper-specific metrics (distribution accuracy, errors)

- **Composite Performance Scores**
  - Weighted scoring systems by position
  - Performance indices and rankings
  - Relative performance metrics

- **Temporal Features**
  - Season-based features
  - Match context features
  - Performance trend indicators

## 📚 **Notebooks & Scripts**
- **`Feature_Creation.ipynb`** - Main feature engineering notebook
- **`Per90_Calculations.ipynb`** - Per-90 minute metric calculations
- **`Position_Features.ipynb`** - Position-specific feature creation
- **`Performance_Scoring.ipynb`** - Composite score calculations

## 📈 **Expected Outputs**
### **Engineered Datasets:**
- `features_per90.csv` - Per-90 minute metrics
- `position_features.csv` - Position-specific features
- `performance_scores.csv` - Composite performance scores
- `temporal_features.csv` - Time-based features

### **Feature Documentation:**
- Feature definitions and formulas
- Data quality metrics for engineered features
- Feature importance rankings

## 🔗 **Dependencies**
- **Input Data:** Cleaned data from `01_EDA/outputs/`
- **Python Modules:** Functions from `Other material Folder/`
- **Output Location:** `outputs/` for feature datasets

## 📋 **Deliverables Checklist**
- [x] Per-90 minute metrics calculated
- [x] Position-specific features created
- [x] Composite performance scores computed
- [x] Temporal features engineered
- [x] Feature quality assessment completed
- [x] All engineered datasets saved to `outputs/`
- [ ] Main notebook exported to PDF in `resources/`

## 🚀 **Next Stage**
**Proceeds to:** `03_SPPS_Calibration_SHAP` - SPPS calibration and SHAP analysis

---
*Last Updated:* [Date]
*Report Section:* [Insert from Week 6 v6 report]
