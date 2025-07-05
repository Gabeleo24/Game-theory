# Docker Configuration for ADS599 Capstone Soccer Intelligence System

This directory contains Docker configuration files and scripts for containerizing the Soccer Intelligence System.

## Directory Structure

```
docker/
├── README.md                           # This file
├── docker-compose.override.yml         # Development environment overrides
├── postgres/
│   ├── init.sql                       # PostgreSQL initialization script
│   └── dev-init.sql                   # Development database setup
└── scripts/
    ├── optimize-container.sh           # Container performance optimization
    ├── run-workflows.sh               # Workflow orchestration script
    └── monitor-performance.py         # Performance monitoring script
```

## Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.template .env

# Edit environment variables (add your API keys)
nano .env

# Copy API keys template
cp config/api_keys_template.yaml config/api_keys.yaml
nano config/api_keys.yaml
```

### 2. Build and Start Services

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f soccer-intelligence
```

### 3. Run Workflows

```bash
# Quick validation workflow
./docker/scripts/run-workflows.sh quick

# Full data collection and analysis
./docker/scripts/run-workflows.sh full

# Specific workflows
./docker/scripts/run-workflows.sh shapley
./docker/scripts/run-workflows.sh multi-season
```

## Available Services

### Production Services

- **soccer-intelligence**: Main application container
- **postgres**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)
- **data-collector**: Scalable data collection workers
- **analysis-worker**: Scalable analysis workers

### Development Services (--profile development)

- **soccer-intelligence-dev**: Development container with source mounting
- **jupyter**: Jupyter Lab (port 8888)
- **streamlit-dashboard**: Data visualization (port 8501)
- **fastapi-service**: REST API (port 8000)
- **pgadmin**: Database admin (port 8080)
- **redis-commander**: Cache management (port 8081)

### Monitoring Services (--profile monitoring)

- **prometheus**: Metrics collection (port 9090)
- **grafana**: Metrics visualization (port 3000)

## Environment Profiles

### Production Profile (Default)

```bash
# Start production services
docker-compose up -d
```

### Development Profile

```bash
# Start development environment
docker-compose --profile development up -d

# Access services:
# - Jupyter: http://localhost:8888 (token: soccer-intelligence-dev)
# - Streamlit: http://localhost:8501
# - FastAPI: http://localhost:8000
# - pgAdmin: http://localhost:8080 (admin@soccerapp.com / admin123)
# - Redis Commander: http://localhost:8081
```

### Scaling Profile

```bash
# Start with worker scaling
docker-compose --profile scaling up -d

# Scale workers manually
docker-compose up -d --scale data-collector=3 --scale analysis-worker=2
```

### Monitoring Profile

```bash
# Start with monitoring
docker-compose --profile monitoring up -d

# Access monitoring:
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin / admin123)
```

## Configuration Files

### Main Configuration

- **Dockerfile**: Multi-stage build for production and development
- **docker-compose.yml**: Main service orchestration
- **docker-compose.override.yml**: Development overrides
- **.env.template**: Environment variables template

### Database Configuration

- **postgres/init.sql**: Database schema and initial data
- **postgres/dev-init.sql**: Development-specific setup

### Scripts

- **scripts/optimize-container.sh**: Performance optimization
- **scripts/run-workflows.sh**: Workflow orchestration
- **scripts/monitor-performance.py**: Performance monitoring

## Volume Mapping

### Application Data

```yaml
volumes:
  # Persistent data storage
  - ./data/focused:/app/data/focused          # UEFA Champions League data
  - ./data/cache:/app/data/cache              # API response cache
  - ./data/analysis:/app/data/analysis        # Analysis results
  - ./data/reports:/app/data/reports          # Generated reports
  - ./logs:/app/logs                          # Application logs
  
  # Configuration files
  - ./config/api_keys.yaml:/app/config/api_keys.yaml:ro
  - ./config/team_statistics_collection_config.yaml:/app/config/team_statistics_collection_config.yaml:ro
```

### Database Data

```yaml
volumes:
  # PostgreSQL data
  - postgres_data:/var/lib/postgresql/data
  
  # Redis data
  - redis_data:/data
```

## Common Commands

### Service Management

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d soccer-intelligence

# Stop all services
docker-compose down

# Restart service
docker-compose restart soccer-intelligence

# View service logs
docker-compose logs -f soccer-intelligence

# Scale services
docker-compose up -d --scale data-collector=3
```

### Container Access

```bash
# Access main container shell
docker-compose exec soccer-intelligence bash

# Run specific command
docker-compose run --rm soccer-intelligence python scripts/analysis/simple_shapley_analysis.py

# Access database
docker-compose exec postgres psql -U soccerapp -d soccer_intelligence

# Access Redis
docker-compose exec redis redis-cli
```

### Data Management

```bash
# Backup data
docker run --rm -v soccer-intelligence-postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data

# Restore data
docker run --rm -v soccer-intelligence-postgres-data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres-backup.tar.gz -C /

# Clear cache
docker-compose exec redis redis-cli FLUSHALL
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in docker-compose.yml
2. **Memory issues**: Increase Docker memory limit
3. **Permission issues**: Check file ownership and permissions
4. **API rate limits**: Adjust rate limiting in environment variables

### Debug Commands

```bash
# Check container status
docker-compose ps

# View container resource usage
docker stats

# Check container logs
docker-compose logs soccer-intelligence

# Test database connection
docker-compose exec soccer-intelligence python -c "
import psycopg2
import os
conn = psycopg2.connect(
    host='postgres',
    database='soccer_intelligence',
    user='soccerapp',
    password='soccerpass123'
)
print('Database connection successful')
"

# Test Redis connection
docker-compose exec redis redis-cli ping
```

### Performance Monitoring

```bash
# Run performance optimization
./docker/scripts/optimize-container.sh

# Monitor performance
docker-compose exec soccer-intelligence python scripts/monitor-performance.py

# View performance logs
docker-compose exec soccer-intelligence tail -f logs/performance.log
```

## Security Notes

- Never commit `.env` or `config/api_keys.yaml` files
- Use Docker secrets for production deployments
- Regularly update base images for security patches
- Implement proper network isolation in production
- Use non-root users in containers (already configured)

## Support

For detailed documentation, see:
- [Docker Deployment Guide](../docs/DOCKER_DEPLOYMENT_GUIDE.md)
- [Project README](../README.md)
- [Implementation Tutorial](../docs/IMPLEMENTATION_TUTORIAL.md)

For issues or questions, refer to the project documentation or contact the development team.
