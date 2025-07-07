# YAML Configuration Guide

## Overview

This directory contains YAML configuration files for the ADS599 Capstone Soccer Intelligence System. YAML (YAML Ain't Markup Language) is a human-readable data serialization standard used for configuration files, data exchange, and more.

## Configuration Files in This Project

### Core Configuration Files

| File | Purpose | Required |
|------|---------|----------|
| `focused_config.yaml` | Main system configuration for Champions League focus | ✅ Yes |
| `api_keys.yaml` | API keys and credentials (create from template) | ✅ Yes |
| `system_paths.yaml` | File paths and directory structure | ✅ Yes |
| `performance_config.yaml` | Performance optimization settings | ⚠️ Optional |

### Data Collection Configuration

| File | Purpose | Required |
|------|---------|----------|
| `data_collection_focused.yaml` | Focused data collection strategy | ✅ Yes |
| `player_statistics_collection_config.yaml` | Player data collection settings | ⚠️ Optional |
| `team_statistics_collection_config.yaml` | Team data collection settings | ⚠️ Optional |
| `optimized_collection_config.yaml` | Optimized collection parameters | ⚠️ Optional |

### Template Files

| File | Purpose | Usage |
|------|---------|-------|
| `api_keys_template.yaml` | Template for API keys | Copy to `api_keys.yaml` |
| `config_template.yaml` | General configuration template | Reference only |

## YAML Syntax Basics

### Basic Structure
```yaml
# Comments start with #
key: value
string_value: "Hello World"
number_value: 42
boolean_value: true
null_value: null
```

### Lists/Arrays
```yaml
# Method 1: Dash notation
teams:
  - Manchester City
  - Real Madrid
  - Bayern Munich

# Method 2: Bracket notation
teams: [Manchester City, Real Madrid, Bayern Munich]
```

### Nested Objects
```yaml
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
    password: secret
```

### Multi-line Strings
```yaml
# Literal block (preserves line breaks)
description: |
  This is a multi-line
  description that preserves
  line breaks.

# Folded block (folds line breaks into spaces)
summary: >
  This is a long text
  that will be folded
  into a single line.
```

## Project-Specific YAML Examples

### API Configuration
```yaml
# api_keys.yaml
api_football:
  key: "your_api_key_here"
  base_url: "https://v3.football.api-sports.io"
  rate_limit: 100  # requests per minute

openai:
  api_key: "your_openai_key_here"
  model: "gpt-4"
  max_tokens: 4000
```

### Team Configuration
```yaml
# focused_config.yaml
analysis:
  priority_teams:
    - 85   # Manchester City
    - 541  # Real Madrid
    - 157  # Bayern Munich
  
  league_distribution:
    premier_league: 7
    la_liga: 7
    bundesliga: 8
    serie_a: 6
    ligue_1: 6
```

### Performance Settings
```yaml
# performance_config.yaml
data_processing:
  chunk_processing:
    enabled: true
    chunk_size: 10000
    parallel_chunks: true
  
  memory:
    max_memory_usage_gb: 6
    garbage_collection_threshold: 0.8
```

## Common YAML Pitfalls

### 1. Indentation Issues
```yaml
# ❌ Wrong - inconsistent indentation
config:
  database:
    host: localhost
     port: 5432  # Wrong indentation

# ✅ Correct - consistent 2-space indentation
config:
  database:
    host: localhost
    port: 5432
```

### 2. String Quoting
```yaml
# ❌ Problematic - special characters
password: my:password@123

# ✅ Safe - quoted strings
password: "my:password@123"
```

### 3. Boolean Values
```yaml
# ❌ Wrong - strings that look like booleans
enabled: "true"    # This is a string
debug: "false"     # This is a string

# ✅ Correct - actual booleans
enabled: true      # This is a boolean
debug: false       # This is a boolean
```

## Environment-Specific Configuration

### Development vs Production
```yaml
# Use environment variables
database:
  host: ${DB_HOST:-localhost}
  port: ${DB_PORT:-5432}
  name: ${DB_NAME:-soccer_intelligence}

# Or separate files
# config_dev.yaml
# config_prod.yaml
```

## Security Best Practices

### 1. API Keys
```yaml
# ❌ Never commit actual keys
api_football:
  key: "5ced20dec7f4b2226c8944c88c6d86aa"

# ✅ Use templates and environment variables
api_football:
  key: ${API_FOOTBALL_KEY}
```

### 2. Sensitive Data
- Keep `api_keys.yaml` in `.gitignore`
- Use environment variables for production
- Provide templates for setup

## Validation and Testing

### YAML Syntax Validation
```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Or use online validators
# https://yamlchecker.com/
```

### Configuration Validation
```python
# In your Python code
import yaml
from pathlib import Path

def load_config(config_path):
    """Load and validate YAML configuration."""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        return None
```

## Loading YAML in Python

### Basic Loading
```python
import yaml

# Load configuration
with open('config/focused_config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Access values
teams = config['analysis']['priority_teams']
```

### Advanced Loading with Error Handling
```python
import yaml
from pathlib import Path

class ConfigLoader:
    def __init__(self, config_dir='config'):
        self.config_dir = Path(config_dir)
    
    def load_config(self, filename):
        """Load YAML config with error handling."""
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {filename}: {e}")

# Usage
loader = ConfigLoader()
config = loader.load_config('focused_config.yaml')
```

## Quick Setup Guide

### 1. Copy Template Files
```bash
# Copy API keys template
cp config/api_keys_template.yaml config/api_keys.yaml

# Edit with your actual keys
nano config/api_keys.yaml
```

### 2. Verify Configuration
```bash
# Check all YAML files
python -c "
import yaml
from pathlib import Path

for yaml_file in Path('config').glob('*.yaml'):
    try:
        with open(yaml_file) as f:
            yaml.safe_load(f)
        print(f'✅ {yaml_file.name} - Valid')
    except Exception as e:
        print(f'❌ {yaml_file.name} - Error: {e}')
"
```

### 3. Environment Variables (Optional)
```bash
# Set environment variables
export API_FOOTBALL_KEY="your_key_here"
export OPENAI_API_KEY="your_key_here"
```

## Troubleshooting

### Common Errors

1. **IndentationError**: Check consistent spacing (use 2 spaces)
2. **ParserError**: Check for special characters in unquoted strings
3. **FileNotFoundError**: Ensure file paths are correct
4. **KeyError**: Verify configuration structure matches code expectations

### Debug Tips

1. Use YAML validators online
2. Check indentation with a text editor that shows spaces
3. Quote strings with special characters
4. Use `yaml.safe_load()` instead of `yaml.load()`

## Project Configuration Examples

### Complete API Setup
```yaml
# api_keys.yaml (create from template)
api_football:
  key: "your_api_football_key"
  base_url: "https://v3.football.api-sports.io"
  rate_limit: 100
  timeout: 30

openai:
  api_key: "your_openai_key"
  model: "gpt-4"
  max_tokens: 4000
  temperature: 0.7

# Optional APIs
sportmonks:
  api_key: "your_sportmonks_key"
  base_url: "https://soccer.sportmonks.com/api/v2.0"
```

### Data Collection Configuration
```yaml
# data_collection_focused.yaml
collection:
  target_teams: 67
  seasons: [2019, 2020, 2021, 2022, 2023, 2024]
  competitions:
    - champions_league
    - domestic_league
    - domestic_cup

  rate_limiting:
    requests_per_minute: 100
    retry_attempts: 3
    backoff_factor: 2

  caching:
    enabled: true
    cache_duration_days: 30
    cache_directory: "data/cache"
```

### Performance Optimization
```yaml
# performance_config.yaml
optimization:
  parallel_processing:
    enabled: true
    max_workers: 4
    chunk_size: 1000

  memory_management:
    max_memory_gb: 8
    garbage_collection: true
    memory_monitoring: true

  caching:
    redis_enabled: false
    file_cache_enabled: true
    cache_ttl_hours: 24
```

## Configuration Management Tips

### 1. Environment-Specific Configs
```yaml
# config_base.yaml
defaults: &defaults
  timeout: 30
  retry_attempts: 3

# config_development.yaml
<<: *defaults
debug: true
log_level: DEBUG
api_rate_limit: 10

# config_production.yaml
<<: *defaults
debug: false
log_level: INFO
api_rate_limit: 100
```

### 2. Configuration Inheritance
```yaml
# Use YAML anchors and aliases
database_defaults: &db_defaults
  host: localhost
  port: 5432
  timeout: 30

development:
  database:
    <<: *db_defaults
    name: soccer_dev
    debug: true

production:
  database:
    <<: *db_defaults
    name: soccer_prod
    debug: false
```

### 3. Dynamic Configuration
```yaml
# Use environment variable substitution
app:
  name: ${APP_NAME:-Soccer Intelligence}
  version: ${APP_VERSION:-1.0.0}
  debug: ${DEBUG:-false}

database:
  url: ${DATABASE_URL:-postgresql://localhost/soccer}
  pool_size: ${DB_POOL_SIZE:-10}
```

## Integration with Python Code

### Configuration Class Example
```python
import yaml
from pathlib import Path
from typing import Dict, Any
import os

class Config:
    """Configuration manager for the Soccer Intelligence System."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._configs = {}
        self.load_all_configs()

    def load_all_configs(self):
        """Load all YAML configuration files."""
        yaml_files = [
            'focused_config.yaml',
            'api_keys.yaml',
            'system_paths.yaml',
            'performance_config.yaml'
        ]

        for yaml_file in yaml_files:
            try:
                self._configs[yaml_file.replace('.yaml', '')] = self.load_yaml(yaml_file)
            except FileNotFoundError:
                print(f"Warning: {yaml_file} not found")
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")

    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load a specific YAML file with environment variable substitution."""
        file_path = self.config_dir / filename

        with open(file_path, 'r') as file:
            content = file.read()

        # Simple environment variable substitution
        content = self._substitute_env_vars(content)

        return yaml.safe_load(content)

    def _substitute_env_vars(self, content: str) -> str:
        """Substitute environment variables in YAML content."""
        import re

        def replace_env_var(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) else ""
            return os.getenv(var_name, default_value)

        # Pattern: ${VAR_NAME:-default_value}
        pattern = r'\$\{([^}:]+)(?::-([^}]*))?\}'
        return re.sub(pattern, replace_env_var, content)

    def get(self, config_name: str, key_path: str = None):
        """Get configuration value using dot notation."""
        config = self._configs.get(config_name)
        if not config:
            return None

        if not key_path:
            return config

        # Navigate nested keys using dot notation
        keys = key_path.split('.')
        value = config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None

        return value

# Usage example
config = Config()
api_key = config.get('api_keys', 'api_football.key')
priority_teams = config.get('focused_config', 'analysis.priority_teams')
```

## Best Practices Summary

### ✅ Do's
- Use consistent 2-space indentation
- Quote strings with special characters
- Use meaningful key names
- Keep sensitive data in separate files
- Validate YAML syntax before deployment
- Use environment variables for secrets
- Document configuration options
- Use templates for setup

### ❌ Don'ts
- Don't mix tabs and spaces
- Don't commit API keys to version control
- Don't use complex nested structures unnecessarily
- Don't forget to handle missing configuration files
- Don't use YAML for large data files
- Don't ignore YAML parsing errors

## Additional Resources

- [YAML Official Specification](https://yaml.org/spec/)
- [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [YAML Validator](https://yamlchecker.com/)
- [YAML Tutorial](https://learnxinyminutes.com/docs/yaml/)
- [YAML Best Practices](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html)
