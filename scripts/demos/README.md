# Demo Scripts

Demonstration scripts showcasing the capabilities of the Soccer Performance Intelligence System.

## Scripts Overview

### demo_soccer_intelligence.py
**Purpose**: Comprehensive demonstration of the complete Soccer Performance Intelligence System
**Features**:
- Multi-source data collection demonstration
- Shapley value analysis examples
- Tactical analysis and formation recommendations
- RAG system query demonstrations
- Performance metrics calculation
- Social media sentiment analysis
- Wikipedia data integration
- Complete system workflow showcase

**Capabilities Demonstrated**:
- API-Football data collection and processing
- Twitter sentiment analysis for teams and players
- Wikipedia historical context extraction
- Advanced tactical analysis with formation recommendations
- Player contribution analysis using Shapley values
- RAG-powered intelligent query system
- Performance visualization and reporting

**Usage**:
```bash
python demo_soccer_intelligence.py
```

**Expected Output**:
- System initialization and configuration validation
- Data collection from multiple sources
- Advanced analytics processing
- Tactical insights and recommendations
- Performance reports and visualizations

### working_demo.py
**Purpose**: Basic working demonstration of core system features
**Features**:
- Core system functionality validation
- Basic data collection demonstration
- Simple analytics examples
- System health checks
- Quick feature overview
- Setup verification

**Capabilities Demonstrated**:
- System configuration and setup
- Basic API connectivity
- Core data processing functions
- Simple analytics calculations
- Error handling and logging
- System status reporting

**Usage**:
```bash
python working_demo.py
```

**Expected Output**:
- System status and configuration report
- Basic data collection examples
- Core functionality validation
- Simple analytics demonstrations
- System health summary

## Demo Scenarios

### Scenario 1: Complete System Showcase
Use `demo_soccer_intelligence.py` to demonstrate:
1. **Data Collection**: Multi-source data acquisition
2. **Data Processing**: Cleaning and feature engineering
3. **Advanced Analytics**: Shapley values and tactical analysis
4. **Intelligence Queries**: RAG system demonstrations
5. **Visualization**: Performance reports and insights

### Scenario 2: Quick System Validation
Use `working_demo.py` to demonstrate:
1. **System Setup**: Configuration and connectivity
2. **Basic Operations**: Core functionality testing
3. **Data Processing**: Simple analytics examples
4. **Status Reporting**: System health and performance

## Demo Data Requirements

### For demo_soccer_intelligence.py:
- API-Football credentials configured
- Twitter API credentials (optional for full demo)
- OpenAI API key (for RAG system)
- Internet connectivity for data collection

### For working_demo.py:
- Basic system configuration
- API-Football credentials (minimal)
- Local data files (if available)

## Demo Outputs

### Comprehensive Demo Outputs:
- Data collection reports
- Tactical analysis results
- Shapley value calculations
- Formation recommendations
- Performance visualizations
- RAG query responses
- System performance metrics

### Basic Demo Outputs:
- System configuration status
- Basic data collection examples
- Core functionality validation
- Simple analytics results
- System health summary

## Customization Options

### demo_soccer_intelligence.py Customization:
```python
# Modify these parameters for different demonstrations
DEMO_LEAGUE = 140  # La Liga (change for different leagues)
DEMO_SEASON = 2023  # Current season
DEMO_TEAM = 529  # Barcelona (change for different teams)
ENABLE_SOCIAL_MEDIA = True  # Enable/disable Twitter analysis
ENABLE_RAG_SYSTEM = True  # Enable/disable RAG demonstrations
```

### working_demo.py Customization:
```python
# Basic demo parameters
QUICK_TEST = True  # Enable quick testing mode
VERBOSE_OUTPUT = False  # Control output verbosity
TEST_DATA_ONLY = False  # Use only test data
```

## Troubleshooting

### Common Issues:
1. **API Credentials**: Ensure all API keys are properly configured
2. **Network Connectivity**: Verify internet connection for data collection
3. **Dependencies**: Check that all required packages are installed
4. **Data Availability**: Ensure sufficient data exists for demonstrations

### Error Resolution:
- Check logs for detailed error information
- Verify API key configuration in `config/api_keys.yaml`
- Ensure all dependencies are installed via `requirements.txt`
- Test basic connectivity with testing scripts first

## Performance Considerations

- Demo scripts may take several minutes to complete
- Data collection depends on API response times
- Complex analytics may require significant processing time
- Large datasets may impact demonstration performance

## Educational Use

These demos are designed for:
- Academic presentations and coursework
- System capability demonstrations
- Research methodology showcases
- Technical documentation and training
- Capstone project presentations

## Best Practices

1. **Test connectivity** before running demos
2. **Prepare demo environment** with proper configuration
3. **Allow sufficient time** for complete demonstrations
4. **Monitor API usage** during data collection demos
5. **Document demo results** for analysis and reporting
6. **Customize parameters** for specific demonstration needs
