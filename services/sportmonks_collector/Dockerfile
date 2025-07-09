# SportMonks API Data Collector Service
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    psycopg2-binary==2.9.7 \
    requests==2.31.0 \
    python-dotenv==1.0.0 \
    redis==5.0.1 \
    pyyaml==6.0.1

# Copy collector services
COPY collector.py /app/
COPY enhanced_collector.py /app/
COPY requirements.txt /app/

# Create logs directory
RUN mkdir -p /app/logs

# Create health check script
RUN echo '#!/bin/bash\n\
# Health check for SportMonks collector\n\
if [ -f "/app/logs/sportmonks_collector.log" ]; then\n\
    # Check if collector is running or completed successfully\n\
    if grep -q "Collection session finished: COMPLETED" /app/logs/sportmonks_collector.log; then\n\
        echo "Collection completed successfully"\n\
        exit 0\n\
    elif grep -q "Collection session finished: FAILED" /app/logs/sportmonks_collector.log; then\n\
        echo "Collection failed"\n\
        exit 1\n\
    elif pgrep -f "collector.py" > /dev/null; then\n\
        echo "Collection in progress"\n\
        exit 0\n\
    else\n\
        echo "Collection not running"\n\
        exit 1\n\
    fi\n\
else\n\
    echo "No log file found"\n\
    exit 1\n\
fi' > /app/health_check.sh && chmod +x /app/health_check.sh

# Create entrypoint script with database wait
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "🏆 SportMonks Data Collector for Real Madrid 2023-2024"\n\
echo "Waiting for PostgreSQL to be ready..."\n\
\n\
# Wait for PostgreSQL\n\
while ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do\n\
  echo "Waiting for database..."\n\
  sleep 2\n\
done\n\
\n\
echo "✅ Database is ready!"\n\
echo "🚀 Starting SportMonks data collection..."\n\
\n\
# Run the collector\n\
exec python collector.py' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/health_check.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
