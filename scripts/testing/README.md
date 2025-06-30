# Testing Scripts

Testing and validation scripts for the Soccer Performance Intelligence System.

## Scripts Overview

### test_api_setup.py
**Purpose**: Comprehensive API configuration and connectivity testing
**Features**:
- API-Football connectivity validation
- Twitter API authentication testing
- OpenAI API key verification
- Rate limit testing and validation
- Error handling and response validation
- Credential security verification
- API endpoint accessibility testing

**Test Categories**:
1. **Connectivity Tests**: Basic API endpoint accessibility
2. **Authentication Tests**: API key validation and permissions
3. **Rate Limit Tests**: API usage limits and throttling
4. **Response Tests**: Data format and content validation
5. **Error Handling Tests**: Invalid request and error response testing

**Usage**:
```bash
python test_api_setup.py
```

**Expected Output**:
- API connectivity status for each service
- Authentication validation results
- Rate limit information and current usage
- Response format validation
- Error handling test results
- Overall API setup health report

### test_basic_setup.py
**Purpose**: Basic system setup and configuration validation
**Features**:
- System configuration validation
- Module import testing
- Basic functionality verification
- Environment setup checking
- Dependency validation
- File system permissions testing
- Configuration file validation

**Test Categories**:
1. **Environment Tests**: Python version, virtual environment validation
2. **Dependency Tests**: Required package installation verification
3. **Configuration Tests**: Config file existence and format validation
4. **Module Tests**: Core module import and initialization testing
5. **File System Tests**: Directory structure and permissions validation

**Usage**:
```bash
python test_basic_setup.py
```

**Expected Output**:
- System environment validation results
- Dependency installation status
- Configuration file validation
- Module import test results
- File system setup verification
- Overall system health summary

## Testing Strategy

### Pre-Deployment Testing
1. **Basic Setup Validation**: Run `test_basic_setup.py` first
2. **API Configuration Testing**: Run `test_api_setup.py` after basic setup
3. **Integration Testing**: Verify all components work together
4. **Performance Testing**: Validate system performance under load

### Continuous Testing
- Regular API connectivity monitoring
- Periodic configuration validation
- Automated health checks
- Performance regression testing

## Test Results Interpretation

### test_api_setup.py Results:
- **PASS**: API is properly configured and accessible
- **FAIL**: Configuration issues or connectivity problems
- **WARNING**: Partial functionality or rate limit concerns
- **ERROR**: Critical configuration or connectivity failures

### test_basic_setup.py Results:
- **PASS**: System is properly configured and ready
- **FAIL**: Missing dependencies or configuration issues
- **WARNING**: Non-critical issues that may affect performance
- **ERROR**: Critical system setup failures

## Troubleshooting Guide

### API Setup Issues:
1. **Invalid API Key**: Verify API keys in `config/api_keys.yaml`
2. **Network Connectivity**: Check internet connection and firewall settings
3. **Rate Limits**: Verify API usage limits and current consumption
4. **Permissions**: Ensure API keys have required permissions

### Basic Setup Issues:
1. **Missing Dependencies**: Install packages via `pip install -r requirements.txt`
2. **Python Version**: Ensure Python 3.8+ is installed
3. **Virtual Environment**: Activate proper virtual environment
4. **File Permissions**: Check read/write permissions for data directories

## Test Configuration

### API Testing Configuration:
```python
# Modify these settings in test_api_setup.py
TEST_ENDPOINTS = {
    'api_football': True,
    'twitter': True,
    'openai': True
}

RATE_LIMIT_TESTS = True
RESPONSE_VALIDATION = True
ERROR_HANDLING_TESTS = True
```

### Basic Testing Configuration:
```python
# Modify these settings in test_basic_setup.py
VERBOSE_OUTPUT = True
QUICK_TEST_MODE = False
SKIP_OPTIONAL_TESTS = False
```

## Automated Testing

### Continuous Integration:
```bash
# Run all tests in sequence
python scripts/testing/test_basic_setup.py
python scripts/testing/test_api_setup.py
```

### Scheduled Testing:
- Daily API connectivity checks
- Weekly configuration validation
- Monthly comprehensive system testing

## Test Data Management

### Test Data Requirements:
- Minimal API calls for connectivity testing
- Sample configuration files for validation
- Test datasets for functionality verification

### Test Data Cleanup:
- Automatic cleanup of test data after completion
- Preservation of test logs for analysis
- Secure handling of test credentials

## Performance Testing

### API Performance Metrics:
- Response time measurement
- Throughput testing
- Rate limit compliance
- Error rate monitoring

### System Performance Metrics:
- Module loading time
- Memory usage validation
- CPU utilization monitoring
- Disk I/O performance

## Security Testing

### Credential Security:
- API key validation without exposure
- Secure configuration file handling
- Authentication token management
- Access permission verification

### Data Security:
- Secure data transmission testing
- Data encryption validation
- Access control verification
- Privacy compliance checking

## Best Practices

1. **Run tests regularly** to ensure system health
2. **Monitor test results** for performance trends
3. **Update tests** when system components change
4. **Document test failures** for troubleshooting
5. **Maintain test environments** separate from production
6. **Automate testing** where possible for consistency

## Maintenance

- Tests are updated with system changes
- New tests are added for new functionality
- Performance benchmarks are regularly updated
- Documentation is maintained for all test procedures
