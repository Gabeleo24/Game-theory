# Real Madrid Soccer Analysis - ADS599 Capstone Project

## 🏆 Project Overview

This project provides a comprehensive analysis of Real Madrid soccer data across multiple seasons, featuring modular code architecture, automated data processing, and advanced machine learning capabilities.

## 📁 Project Structure

```
ADS599_Capstone/
├── Main Notebook/
│   ├── Code Library Folder/    # Separate Python notebook files
│   │   ├── Data Preparation.ipynb    # Data preparation functions
│   │   ├── Data Exploration.ipynb    # Data exploration functions
│   │   └── Modeling.ipynb           # Modeling functions
│   ├── Image Folder/           # Generated visualizations
│   ├── Other material Folder/  # Python library with reusable functions
│   │   ├── __init__.py        # Package initialization
│   │   ├── data_acquisition.py # Web scraping and data collection
│   │   ├── data_processing.py  # Data cleaning and analysis
│   │   ├── visualization.py    # Charts and plots
│   │   └── modeling.py        # Machine learning models
│   ├── Main Code Library/      # Original notebooks (for reference)
│   ├── Data Folder/            # All CSV data files
│   └── Main_Analysis.ipynb    # Clean, organized main notebook
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Multi-service orchestration
└── README.md                   # This file
```

## 🚀 Quick Start

### Option 1: Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ADS599_Capstone
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the main analysis**
   ```bash
   jupyter notebook "Main Notebook/Main_Analysis.ipynb"
   ```

### Option 2: Docker (Recommended)

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access Jupyter Notebook**
   - Open your browser and go to: `http://localhost:8888`
   - Navigate to `Main Notebook/Main_Analysis.ipynb`

3. **Stop the services**
   ```bash
   docker-compose down
   ```

## 🔧 Code Library Modules

### 📊 Data Acquisition (`data_acquisition.py`)
- **FBrefScraper**: Web scraping class for soccer statistics
- **quick_schedule_pull()**: Fast team schedule retrieval
- **quick_match_stats()**: Match statistics extraction

### 🧹 Data Processing (`data_processing.py`)
- **SoccerDataProcessor**: Main data processing class
- **quick_data_load()**: Load and combine multiple seasons
- **quick_analysis()**: Comprehensive data analysis pipeline

### 📈 Visualization (`visualization.py`)
- **SoccerVisualizer**: Chart and plot creation
- **quick_visualization()**: Generate common visualizations
- **create_comprehensive_report()**: Full visualization suite

### 🤖 Modeling (`modeling.py`)
- **SoccerModeler**: Machine learning pipeline
- **quick_regression_analysis()**: Regression model training
- **quick_classification_analysis()**: Classification model training

## 📊 Data Sources

The project analyzes Real Madrid data from multiple seasons:
- **Seasons**: 2015-16 through 2024-25
- **Data Types**: Player statistics, match results, team performance
- **Sources**: FBref.com, official statistics, web scraping

## 🎯 Key Features

- **Modular Architecture**: Clean, reusable functions organized by purpose
- **Automated Processing**: Streamlined data pipeline from raw data to insights
- **Comprehensive Analysis**: EDA, visualization, and machine learning
- **Docker Support**: Containerized for easy deployment and reproducibility
- **Professional Quality**: PEP 8 compliant, well-documented code

## 📈 Analysis Capabilities

### Data Exploration
- Multi-season data combination and cleaning
- Position-based analysis
- Performance metrics calculation
- Statistical summaries

### Visualization
- Season performance trends
- Position-based comparisons
- Player performance rankings
- Correlation analysis
- Time series plots

### Machine Learning
- Regression analysis for performance prediction
- Classification for player categorization
- Clustering for player grouping
- Feature importance analysis

## 🐳 Docker Details

### Services
- **jupyter**: Main Jupyter notebook server
- **data_processor**: Background data processing service

### Ports
- **8888**: Jupyter notebook access

### Volumes
- Project files are mounted for live editing
- Images folder for visualization output
- Data folder for CSV files

## 🔍 Usage Examples

### Basic Data Loading
```python
from Other_material_Folder.data_processing import quick_data_load

# Load data from multiple seasons
seasons = ['15_16', '16_17', '17_18', '18_19', '19_20']
match_data, schedule_data = quick_data_load("Data Folder/DataExtracted", seasons)
```

### Quick Analysis
```python
from Other_material_Folder.data_processing import quick_analysis

# Run comprehensive analysis
results = quick_analysis(match_data)
```

### Visualization
```python
from Other_material_Folder.visualization import create_comprehensive_report

# Create all visualizations
create_comprehensive_report(match_data, "Image Folder")
```

### Machine Learning
```python
from Other_material_Folder.modeling import quick_regression_analysis

# Train regression models
regression_results = quick_regression_analysis(match_data, 'goals')
```

## 📋 Requirements

- **Python**: 3.8+
- **Key Libraries**: pandas, numpy, matplotlib, seaborn, scikit-learn
- **Web Scraping**: requests, beautifulsoup4
- **Jupyter**: notebook, ipykernel

## 🚧 Development

### Adding New Functions
1. Add your function to the appropriate module in `Code Library/`
2. Update the `__init__.py` file to export the function
3. Test with the example functions
4. Update this README if needed

### Code Style
- Follow PEP 8 guidelines
- Use type hints for function parameters
- Include comprehensive docstrings
- Add example usage in docstrings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the ADS599 Capstone course at [Your University].

## 👥 Team

- **Gabe**: Project coordination and data analysis
- **Mau**: Code development and optimization
- **ADS599 Team**: Collaborative development

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're in the correct directory
   - Check that `Code Library` folder exists
   - Verify Python path includes the project directory

2. **Docker Issues**
   - Check if ports 8888 is available
   - Ensure Docker and Docker Compose are installed
   - Try rebuilding with `docker-compose up --build`

3. **Data Loading Issues**
   - Verify CSV files exist in `Data Folder/DataExtracted/`
   - Check file naming conventions
   - Ensure proper file permissions

### Getting Help
- Check the example functions in each module
- Review the main analysis notebook
- Check Docker logs: `docker-compose logs jupyter`

## 🎉 Success!

You've successfully set up a professional, modular soccer analysis project! The code is now:
- ✅ **Organized** into logical modules
- ✅ **Reusable** for other teams or sports
- ✅ **Containerized** for easy deployment
- ✅ **Documented** with clear examples
- ✅ **Professional** quality ready for production

Happy analyzing! ⚽📊
