# Multi-stage Dockerfile for ADS599 Capstone Soccer Intelligence System
# Optimized for data collection, analysis, and Shapley value computation

# ============================================================================
# Stage 1: Base Python Environment with System Dependencies
# ============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libffi-dev \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create application user for security
RUN groupadd -r soccerapp && useradd -r -g soccerapp soccerapp

# Create application directories
RUN mkdir -p /app /app/data /app/logs /app/config \
    && chown -R soccerapp:soccerapp /app

# ============================================================================
# Stage 2: Dependencies Installation
# ============================================================================
FROM base as dependencies

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# ============================================================================
# Stage 3: Application Build
# ============================================================================
FROM dependencies as application

# Copy application source code
COPY --chown=soccerapp:soccerapp src/ ./src/
COPY --chown=soccerapp:soccerapp scripts/ ./scripts/
COPY --chown=soccerapp:soccerapp config/ ./config/
COPY --chown=soccerapp:soccerapp docs/ ./docs/

# Copy configuration templates
COPY --chown=soccerapp:soccerapp config/config_template.yaml ./config/config.yaml
COPY --chown=soccerapp:soccerapp config/api_keys_template.yaml ./config/api_keys_template.yaml

# Create necessary directories with proper permissions
RUN mkdir -p \
    data/focused/players \
    data/focused/teams \
    data/cache \
    data/analysis \
    data/reports \
    data/models \
    data/processed \
    data/raw \
    logs/player_collection \
    logs/team_collection \
    logs/analysis \
    && chown -R soccerapp:soccerapp /app

# Make scripts executable
RUN find scripts/ -name "*.py" -exec chmod +x {} \;

# ============================================================================
# Stage 4: Production Image
# ============================================================================
FROM application as production

# Switch to non-root user
USER soccerapp

# Set working directory
WORKDIR /app

# Add src to Python path
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.append('src'); from soccer_intelligence.utils.config import Config; Config()" || exit 1

# Default command - keep container running for interactive use
CMD ["tail", "-f", "/dev/null"]

# ============================================================================
# Stage 5: Development Image with Additional Tools
# ============================================================================
FROM application as development

# Install development dependencies
RUN pip install \
    jupyter \
    ipython \
    pytest-xdist \
    pre-commit \
    bandit \
    safety

# Install additional analysis tools
RUN pip install \
    plotly-dash \
    streamlit \
    fastapi \
    uvicorn

# Switch to non-root user
USER soccerapp

# Set working directory
WORKDIR /app

# Add src to Python path
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# Expose ports for development services
EXPOSE 8888 8501 8000

# Default command for development
CMD ["bash"]
