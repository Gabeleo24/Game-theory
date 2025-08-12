# 03_SPPS_Calibration_SHAP - SPPS Calibration & SHAP Analysis

## 📊 **Stage Overview**
This folder contains SPPS (Soccer Performance Prediction System) calibration and SHAP (SHapley Additive exPlanations) analysis for the Real Madrid Soccer Performance Analysis capstone project.

## 📁 **Folder Structure**
```
03_SPPS_Calibration_SHAP/
├── notebooks/          # Jupyter notebooks and Python scripts
├── outputs/            # SHAP plots, calibration results, model explanations
├── resources/          # PDF exports and reference materials
└── README.md           # This file
```

## 🎯 **Scope & Objectives**
**Corresponds to Report Section:** [Insert section number from Week 6 v6 report]

### **Key Analysis Areas:**
- **SPPS Calibration**
  - Model calibration and validation
  - Performance threshold optimization
  - Calibration curve analysis

- **SHAP Analysis**
  - Feature importance analysis
  - Individual prediction explanations
  - Position-specific SHAP insights
  - Per-90 minute rate SHAP analysis

- **Model Interpretability**
  - Global feature importance
  - Local explanation methods
  - Bias detection and analysis

## 📚 **Notebooks & Scripts**
- **`SPPS_Calibration.ipynb`** - Main SPPS calibration notebook
- **`SHAP_Analysis.ipynb`** - SHAP analysis and visualizations
- **`Model_Interpretability.ipynb`** - Model explanation methods
- **`Calibration_Validation.ipynb`** - Calibration curve analysis

## 📈 **Expected Outputs**
### **SHAP Visualizations:**
- Feature importance plots
- Individual prediction explanations
- Position-specific SHAP summaries
- Per-90 minute rate SHAP analysis

### **Calibration Results:**
- Calibration curves
- Performance thresholds
- Validation metrics

## 🔗 **Dependencies**
- **Input Data:** Engineered features from `02_Feature_Engineering/outputs/`
- **Python Modules:** Functions from `Other material Folder/`
- **Output Location:** `outputs/` for SHAP plots and results
 - **Packages:** Requires `shap` (added in project `requirements.txt`)

## 📋 **Deliverables Checklist**
- [x] SPPS model calibration completed
- [ ] SHAP analysis for all positions
- [ ] Feature importance rankings generated
- [x] Calibration curves created
- [ ] Model interpretability analysis completed
- [ ] All SHAP plots saved to `outputs/`
- [ ] Main notebook exported to PDF in `resources/`

## 📄 **References**
- Week 6 report: `ADS599 Capstone Article Week 6 v6.pdf`
- Original EDA reference: `01_EDA/notebooks/Soccer_Performance_Score_v4_EDA.pdf`

## 🚀 **Next Stage**
**Proceeds to:** `04_Modeling_Benchmarks` - Machine learning modeling and benchmarks

---
*Last Updated:* 2025-08-12
*Report Section:* Cal/SHAP per Week 6 v6
