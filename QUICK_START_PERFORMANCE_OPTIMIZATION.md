# Quick Start: Performance Optimization Setup

This guide helps you quickly set up the performance optimizations for your ADS599 Capstone Soccer Intelligence System.

## Prerequisites

1. **Docker Desktop**: Make sure Docker Desktop is installed and running
2. **Python 3.11+**: Ensure you have Python 3.11 or later
3. **System Resources**: Recommended 8GB+ RAM, 4+ CPU cores, 10GB+ free disk space

## Step 1: Start Docker Desktop

Make sure Docker Desktop is running on your Mac:

1. Open Docker Desktop application
2. Wait for it to fully start (Docker icon in menu bar should be stable)
3. Verify Docker is running:
   ```bash
   docker --version
   docker-compose --version
   ```

## Step 2: Fix Dependencies (if needed)

If you encountered the Keras/TensorFlow error, run the dependency fix script:

```bash
# Fix dependency issues
python scripts/fix_dependencies.py
```

This will:
- Fix Keras/TensorFlow compatibility issues
- Install performance-optimized dependencies
- Create a minimal requirements file

## Step 3: Run Performance Optimization Setup

Run the simplified setup script:

```bash
# Run performance optimization setup
python scripts/setup_performance_optimization.py
```

This will:
- Check system requirements
- Create optimized environment configuration
- Start Docker containers with performance optimizations
- Run basic connectivity tests
- Generate a setup report

## Step 4: Verify Setup

After the setup completes, verify everything is working:

```bash
# Check container status
docker-compose ps

# Check container logs
docker-compose logs soccer-intelligence-app

# Test database connection
docker exec soccer-intelligence-db pg_isready -U soccerapp

# Test Redis connection
docker exec soccer-intelligence-cache redis-cli ping
```

## Step 5: Test Performance Optimizations

Once containers are running, you can test the performance optimizations:

```bash
# Test system monitoring (if containers are running)
docker exec soccer-intelligence-app python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
"

# Test basic Python performance
docker exec soccer-intelligence-app python -c "
import pandas as pd
import numpy as np
import time

# Create test data
start = time.time()
df = pd.DataFrame(np.random.randn(10000, 10))
df['sum'] = df.sum(axis=1)
end = time.time()

print(f'Processed 10,000 rows in {end-start:.3f} seconds')
print(f'Throughput: {10000/(end-start):.0f} rows/second')
"
```

## Troubleshooting

### Docker Issues

**Problem**: "Cannot connect to the Docker daemon"
**Solution**: 
1. Start Docker Desktop
2. Wait for it to fully initialize
3. Try the command again

**Problem**: "docker-compose command not found"
**Solution**: 
- Use `docker compose` instead of `docker-compose` (newer syntax)
- Or install docker-compose separately

### Memory Issues

**Problem**: Containers fail to start due to memory
**Solution**:
1. Edit `.env` file and reduce `MEMORY_LIMIT` from `8g` to `4g`
2. Restart containers: `docker-compose down && docker-compose up -d`

### Dependency Issues

**Problem**: Import errors or package conflicts
**Solution**:
1. Run the dependency fix script: `python scripts/fix_dependencies.py`
2. Or install minimal requirements: `pip install -r requirements_minimal.txt`

### Performance Issues

**Problem**: Still slow performance
**Solution**:
1. Check system resources: `docker stats`
2. Increase worker processes in `.env` file
3. Consider hardware upgrade if consistently below targets

## Performance Targets

After optimization, you should see:

| Metric | Target | How to Check |
|--------|--------|--------------|
| Data Processing | 3,000+ rows/sec | Run test scripts |
| Memory Usage | <80% system memory | `docker stats` |
| Container Startup | <45 seconds | Time `docker-compose up` |
| Cache Hit Rate | >80% | Check Redis stats |

## Next Steps

Once setup is complete:

1. **Run your data processing workflows** with the optimized containers
2. **Monitor performance** using the built-in monitoring tools
3. **Adjust settings** in `.env` file based on your specific needs
4. **Scale workers** if needed: `docker-compose up -d --scale data-collector=2`

## Monitoring and Maintenance

### Daily Monitoring
```bash
# Check container health
docker-compose ps

# Check resource usage
docker stats --no-stream

# Check logs for errors
docker-compose logs --tail=50
```

### Weekly Maintenance
```bash
# Clean up old containers and images
docker system prune -f

# Restart containers for fresh state
docker-compose restart

# Check disk space
df -h
```

## Getting Help

If you encounter issues:

1. **Check the setup report**: `performance_setup_report.md`
2. **Review container logs**: `docker-compose logs [service-name]`
3. **Check system resources**: `docker stats`
4. **Verify configuration**: Review `.env` file settings

## Manual Container Management

If you prefer manual control:

```bash
# Start specific services
docker-compose up -d postgres redis
docker-compose up -d soccer-intelligence

# Scale workers
docker-compose up -d --scale data-collector=2 --scale analysis-worker=2

# Stop all services
docker-compose down

# Start with monitoring
docker-compose --profile monitoring up -d
```

## Performance Configuration Files

Key files for performance optimization:

- `.env` - Environment variables and resource limits
- `docker-compose.yml` - Container configuration with optimizations
- `config/performance_config.yaml` - Application performance settings
- `docker/postgres/postgresql.conf` - Database optimization settings

You can modify these files to fine-tune performance for your specific workload.

## Success Indicators

Your optimization is successful when:

- ✅ All containers start within 45 seconds
- ✅ Data processing achieves 3,000+ rows/second
- ✅ Memory usage stays below 80%
- ✅ No frequent container restarts
- ✅ Cache hit rates above 80%

Enjoy your optimized Soccer Intelligence System! 🚀⚽
